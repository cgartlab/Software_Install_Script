#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Batch Installation and Automation Module
Provides parallel installation, remote deployment, and automation capabilities
"""

import os
import sys
import json
import time
import threading
import queue
import subprocess
import socket
import hashlib
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
import tempfile

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TaskProgressColumn
from rich.text import Text
from rich import box

from sis.error_handler import get_logger, get_error_manager, ErrorCategory, error_handler
from sis.env_manager import get_env_manager, hot_refresh_environment

console = Console()


class InstallStatus(Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    INSTALLING = "installing"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class InstallPriority(Enum):
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3


@dataclass
class SoftwarePackage:
    id: str
    name: str
    version: Optional[str] = None
    source: Optional[str] = None
    category: str = "Other"
    priority: InstallPriority = InstallPriority.NORMAL
    dependencies: List[str] = field(default_factory=list)
    post_install: List[str] = field(default_factory=list)
    env_vars: Dict[str, str] = field(default_factory=dict)
    path_additions: List[str] = field(default_factory=list)


@dataclass
class InstallTask:
    package: SoftwarePackage
    status: InstallStatus = InstallStatus.PENDING
    progress: float = 0.0
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    output: List[str] = field(default_factory=list)


@dataclass
class InstallSession:
    session_id: str
    start_time: str
    total_packages: int
    completed: int = 0
    failed: int = 0
    skipped: int = 0
    tasks: Dict[str, InstallTask] = field(default_factory=dict)


class BatchInstaller:
    """Batch installation manager with parallel processing"""
    
    MAX_WORKERS = 4
    RETRY_COUNT = 3
    RETRY_DELAY = 5
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = min(max_workers, self.MAX_WORKERS)
        self.logger = get_logger()
        self.error_manager = get_error_manager()
        self.env_manager = get_env_manager()
        
        self._session: Optional[InstallSession] = None
        self._stop_event = threading.Event()
        self._progress_callback: Optional[Callable] = None
        self._task_queue: queue.Queue = queue.Queue()
    
    def create_session(self, packages: List[SoftwarePackage]) -> InstallSession:
        session_id = hashlib.md5(
            f"{datetime.now().isoformat()}_{len(packages)}".encode()
        ).hexdigest()[:12]
        
        tasks = {}
        for pkg in packages:
            tasks[pkg.id] = InstallTask(package=pkg)
        
        self._session = InstallSession(
            session_id=session_id,
            start_time=datetime.now().isoformat(),
            total_packages=len(packages),
            tasks=tasks
        )
        
        return self._session
    
    def set_progress_callback(self, callback: Callable):
        self._progress_callback = callback
    
    def _update_progress(self, task_id: str, status: InstallStatus, progress: float = 0.0):
        if self._session and task_id in self._session.tasks:
            task = self._session.tasks[task_id]
            task.status = status
            task.progress = progress
            
            if self._progress_callback:
                self._progress_callback(task_id, status, progress)
    
    def _sort_by_priority(self, packages: List[SoftwarePackage]) -> List[SoftwarePackage]:
        return sorted(packages, key=lambda p: p.priority.value)
    
    def _check_dependencies(self, package: SoftwarePackage) -> Tuple[bool, List[str]]:
        missing = []
        
        for dep_id in package.dependencies:
            if self._session and dep_id in self._session.tasks:
                dep_task = self._session.tasks[dep_id]
                if dep_task.status != InstallStatus.SUCCESS:
                    missing.append(dep_id)
        
        return len(missing) == 0, missing
    
    def _install_package(self, task: InstallTask) -> bool:
        package = task.package
        task.start_time = datetime.now().isoformat()
        task.status = InstallStatus.INSTALLING
        
        self._update_progress(package.id, InstallStatus.INSTALLING, 0)
        self.logger.info(f"Starting installation: {package.name}")
        
        try:
            if sys.platform == 'win32':
                success = self._install_with_winget(task)
            elif sys.platform == 'darwin':
                success = self._install_with_brew(task)
            else:
                task.error_message = "Unsupported platform"
                task.status = InstallStatus.FAILED
                return False
            
            if success:
                self._post_install_actions(task)
                task.status = InstallStatus.SUCCESS
                task.end_time = datetime.now().isoformat()
                self._update_progress(package.id, InstallStatus.SUCCESS, 100)
                self.logger.info(f"Successfully installed: {package.name}")
                return True
            else:
                task.status = InstallStatus.FAILED
                task.end_time = datetime.now().isoformat()
                self._update_progress(package.id, InstallStatus.FAILED, 0)
                return False
        
        except Exception as e:
            task.error_message = str(e)
            task.status = InstallStatus.FAILED
            task.end_time = datetime.now().isoformat()
            self._update_progress(package.id, InstallStatus.FAILED, 0)
            self.logger.exception(f"Installation failed: {package.name}", e)
            return False
    
    def _install_with_winget(self, task: InstallTask) -> bool:
        package = task.package
        
        cmd = [
            'winget', 'install',
            '--id', package.id,
            '--silent',
            '--accept-source-agreements',
            '--accept-package-agreements'
        ]
        
        if package.version:
            cmd.extend(['--version', package.version])
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            
            stdout_lines = []
            stderr_lines = []
            
            while True:
                stdout_line = process.stdout.readline()
                stderr_line = process.stderr.readline()
                
                if stdout_line:
                    stdout_lines.append(stdout_line.strip())
                    task.output.append(stdout_line.strip())
                
                if stderr_line:
                    stderr_lines.append(stderr_line.strip())
                    task.output.append(stderr_line.strip())
                
                if process.poll() is not None:
                    break
            
            process.wait()
            
            if process.returncode == 0:
                return True
            
            combined_output = '\n'.join(stdout_lines + stderr_lines)
            
            if 'already installed' in combined_output.lower():
                task.status = InstallStatus.SKIPPED
                return True
            
            task.error_message = combined_output[:500]
            return False
        
        except Exception as e:
            task.error_message = str(e)
            return False
    
    def _install_with_brew(self, task: InstallTask) -> bool:
        package = task.package
        
        cmd = ['brew', 'install', package.id]
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout_lines = []
            stderr_lines = []
            
            while True:
                stdout_line = process.stdout.readline()
                stderr_line = process.stderr.readline()
                
                if stdout_line:
                    stdout_lines.append(stdout_line.strip())
                    task.output.append(stdout_line.strip())
                
                if stderr_line:
                    stderr_lines.append(stderr_line.strip())
                    task.output.append(stderr_line.strip())
                
                if process.poll() is not None:
                    break
            
            process.wait()
            
            if process.returncode == 0:
                return True
            
            combined_output = '\n'.join(stdout_lines + stderr_lines)
            
            if 'already installed' in combined_output.lower():
                task.status = InstallStatus.SKIPPED
                return True
            
            task.error_message = combined_output[:500]
            return False
        
        except Exception as e:
            task.error_message = str(e)
            return False
    
    def _post_install_actions(self, task: InstallTask) -> bool:
        package = task.package
        success = True
        
        for path_add in package.path_additions:
            if not self.env_manager.append_to_path(path_add):
                self.logger.warning(f"Failed to add to PATH: {path_add}")
                success = False
        
        for var_name, var_value in package.env_vars.items():
            if not self.env_manager.set_env(var_name, var_value):
                self.logger.warning(f"Failed to set env var: {var_name}")
                success = False
        
        for cmd in package.post_install:
            try:
                subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    check=True
                )
            except Exception as e:
                self.logger.warning(f"Post-install command failed: {cmd}", {'error': str(e)})
        
        return success
    
    def install_all(
        self,
        packages: List[SoftwarePackage],
        parallel: bool = True,
        stop_on_error: bool = False
    ) -> InstallSession:
        if not self._session:
            self.create_session(packages)
        
        sorted_packages = self._sort_by_priority(packages)
        
        if parallel:
            return self._parallel_install(sorted_packages, stop_on_error)
        else:
            return self._sequential_install(sorted_packages, stop_on_error)
    
    def _parallel_install(
        self,
        packages: List[SoftwarePackage],
        stop_on_error: bool
    ) -> InstallSession:
        completed_count = 0
        failed_count = 0
        skipped_count = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            
            for package in packages:
                if self._stop_event.is_set():
                    break
                
                deps_ok, missing_deps = self._check_dependencies(package)
                
                if not deps_ok:
                    task = self._session.tasks[package.id]
                    task.status = InstallStatus.SKIPPED
                    task.error_message = f"Missing dependencies: {', '.join(missing_deps)}"
                    skipped_count += 1
                    continue
                
                task = self._session.tasks[package.id]
                future = executor.submit(self._install_package, task)
                futures[future] = package.id
            
            for future in as_completed(futures):
                if self._stop_event.is_set():
                    executor.shutdown(wait=False, cancel_futures=True)
                    break
                
                package_id = futures[future]
                try:
                    success = future.result()
                    task = self._session.tasks[package_id]
                    
                    if task.status == InstallStatus.SUCCESS:
                        completed_count += 1
                    elif task.status == InstallStatus.SKIPPED:
                        skipped_count += 1
                    else:
                        failed_count += 1
                        
                        if stop_on_error:
                            self._stop_event.set()
                            executor.shutdown(wait=False, cancel_futures=True)
                            break
                
                except Exception as e:
                    failed_count += 1
                    self.logger.exception(f"Task failed: {package_id}", e)
        
        self._session.completed = completed_count
        self._session.failed = failed_count
        self._session.skipped = skipped_count
        
        hot_refresh_environment()
        
        return self._session
    
    def _sequential_install(
        self,
        packages: List[SoftwarePackage],
        stop_on_error: bool
    ) -> InstallSession:
        completed_count = 0
        failed_count = 0
        skipped_count = 0
        
        for package in packages:
            if self._stop_event.is_set():
                break
            
            task = self._session.tasks[package.id]
            success = self._install_package(task)
            
            if task.status == InstallStatus.SUCCESS:
                completed_count += 1
            elif task.status == InstallStatus.SKIPPED:
                skipped_count += 1
            else:
                failed_count += 1
                if stop_on_error:
                    break
        
        self._session.completed = completed_count
        self._session.failed = failed_count
        self._session.skipped = skipped_count
        
        hot_refresh_environment()
        
        return self._session
    
    def cancel(self):
        self._stop_event.set()
    
    def get_session_report(self) -> str:
        if not self._session:
            return "No active session"
        
        lines = [
            "=" * 60,
            "Installation Session Report",
            f"Session ID: {self._session.session_id}",
            f"Start Time: {self._session.start_time}",
            "=" * 60,
            "",
            "Summary:",
            f"  Total Packages: {self._session.total_packages}",
            f"  Completed: {self._session.completed}",
            f"  Failed: {self._session.failed}",
            f"  Skipped: {self._session.skipped}",
            "",
            "Package Details:",
        ]
        
        for task_id, task in self._session.tasks.items():
            status_icon = {
                InstallStatus.SUCCESS: "✓",
                InstallStatus.FAILED: "✗",
                InstallStatus.SKIPPED: "○",
                InstallStatus.PENDING: "·",
                InstallStatus.INSTALLING: "◉",
                InstallStatus.DOWNLOADING: "↓",
                InstallStatus.CANCELLED: "⊗"
            }.get(task.status, "?")
            
            lines.append(f"  [{status_icon}] {task.package.name}")
            if task.error_message:
                lines.append(f"      Error: {task.error_message[:100]}")
        
        lines.extend(["", "=" * 60])
        
        return "\n".join(lines)


class AutomationScript:
    """Generate and manage automation scripts"""
    
    TEMPLATES = {
        'powershell': '''
# SwiftInstall Automation Script
# Generated: {timestamp}
# Session: {session_id}

param(
    [switch]$Force,
    [switch]$Verbose
)

$ErrorActionPreference = "Continue"

function Write-Log {{
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] $Message"
}}

Write-Log "Starting SwiftInstall Automation..."
Write-Log "Session ID: {session_id}"

{install_commands}

Write-Log "Automation completed."
Write-Log "Success: $successCount, Failed: $failedCount, Skipped: $skippedCount"
''',
        'bash': '''
#!/bin/bash
# SwiftInstall Automation Script
# Generated: {timestamp}
# Session: {session_id}

set -e

log() {{
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}}

log "Starting SwiftInstall Automation..."
log "Session ID: {session_id}"

{install_commands}

log "Automation completed."
log "Success: $success_count, Failed: $failed_count, Skipped: $skipped_count"
''',
        'python': '''
#!/usr/bin/env python3
"""
SwiftInstall Automation Script
Generated: {timestamp}
Session: {session_id}
"""

import subprocess
import sys
from datetime import datetime

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{{timestamp}}] {{message}}")

def install_package(package_id):
    """Install a package using the system package manager"""
    try:
        if sys.platform == "win32":
            result = subprocess.run(
                ["winget", "install", "--id", package_id, "--silent", 
                 "--accept-source-agreements", "--accept-package-agreements"],
                capture_output=True, text=True
            )
        else:
            result = subprocess.run(
                ["brew", "install", package_id],
                capture_output=True, text=True
            )
        return result.returncode == 0
    except Exception as e:
        log(f"Error installing {{package_id}}: {{e}}")
        return False

log("Starting SwiftInstall Automation...")
log("Session ID: {session_id}")

{install_commands}

log("Automation completed.")
log(f"Success: {{success_count}}, Failed: {{failed_count}}, Skipped: {{skipped_count}}")
'''
    }
    
    @classmethod
    def generate_script(
        cls,
        packages: List[SoftwarePackage],
        script_type: str = 'powershell',
        output_path: Optional[str] = None
    ) -> str:
        template = cls.TEMPLATES.get(script_type, cls.TEMPLATES['powershell'])
        
        install_commands = cls._generate_install_commands(packages, script_type)
        
        session_id = hashlib.md5(
            f"{datetime.now().isoformat()}_{len(packages)}".encode()
        ).hexdigest()[:12]
        
        script = template.format(
            timestamp=datetime.now().isoformat(),
            session_id=session_id,
            install_commands=install_commands
        )
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(script)
        
        return script
    
    @classmethod
    def _generate_install_commands(
        cls,
        packages: List[SoftwarePackage],
        script_type: str
    ) -> str:
        commands = []
        
        if script_type == 'powershell':
            commands.append('$successCount = 0')
            commands.append('$failedCount = 0')
            commands.append('$skippedCount = 0')
            commands.append('')
            
            for pkg in packages:
                commands.append(f'# Installing: {pkg.name}')
                commands.append(f'Write-Log "Installing {pkg.name}..."')
                commands.append('$result = winget install --id "{pkg.id}" --silent --accept-source-agreements --accept-package-agreements 2>&1')
                commands.append('if ($LASTEXITCODE -eq 0) {')
                commands.append('    $successCount++')
                commands.append('    Write-Log "Successfully installed: ' + pkg.name + '"')
                commands.append('} elseif ($result -match "already installed") {')
                commands.append('    $skippedCount++')
                commands.append('    Write-Log "Already installed: ' + pkg.name + '"')
                commands.append('} else {')
                commands.append('    $failedCount++')
                commands.append('    Write-Log "Failed to install: ' + pkg.name + '"')
                commands.append('}')
                commands.append('')
        
        elif script_type == 'bash':
            commands.append('success_count=0')
            commands.append('failed_count=0')
            commands.append('skipped_count=0')
            commands.append('')
            
            for pkg in packages:
                commands.append(f'# Installing: {pkg.name}')
                commands.append(f'log "Installing {pkg.name}..."')
                commands.append(f'if brew install {pkg.id} 2>/dev/null; then')
                commands.append('    ((success_count++))')
                commands.append(f'    log "Successfully installed: {pkg.name}"')
                commands.append('elif brew list {pkg.id} &>/dev/null; then')
                commands.append('    ((skipped_count++))')
                commands.append(f'    log "Already installed: {pkg.name}"')
                commands.append('else')
                commands.append('    ((failed_count++))')
                commands.append(f'    log "Failed to install: {pkg.name}"')
                commands.append('fi')
                commands.append('')
        
        elif script_type == 'python':
            commands.append('success_count = 0')
            commands.append('failed_count = 0')
            commands.append('skipped_count = 0')
            commands.append('')
            
            for pkg in packages:
                commands.append(f'# Installing: {pkg.name}')
                commands.append(f'log("Installing {pkg.name}...")')
                commands.append(f'if install_package("{pkg.id}"):')
                commands.append('    success_count += 1')
                commands.append(f'    log("Successfully installed: {pkg.name}")')
                commands.append('else:')
                commands.append('    failed_count += 1')
                commands.append(f'    log("Failed to install: {pkg.name}")')
                commands.append('')
        
        return '\n'.join(commands)
    
    @classmethod
    def generate_config_file(
        cls,
        packages: List[SoftwarePackage],
        output_path: str
    ) -> str:
        config = {
            'version': '1.0',
            'generated': datetime.now().isoformat(),
            'packages': [
                {
                    'id': pkg.id,
                    'name': pkg.name,
                    'version': pkg.version,
                    'category': pkg.category,
                    'priority': pkg.priority.value,
                    'dependencies': pkg.dependencies,
                    'post_install': pkg.post_install,
                    'env_vars': pkg.env_vars,
                    'path_additions': pkg.path_additions
                }
                for pkg in packages
            ]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    @classmethod
    def load_config_file(cls, config_path: str) -> List[SoftwarePackage]:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        packages = []
        for pkg_data in config.get('packages', []):
            packages.append(SoftwarePackage(
                id=pkg_data['id'],
                name=pkg_data['name'],
                version=pkg_data.get('version'),
                category=pkg_data.get('category', 'Other'),
                priority=InstallPriority(pkg_data.get('priority', 2)),
                dependencies=pkg_data.get('dependencies', []),
                post_install=pkg_data.get('post_install', []),
                env_vars=pkg_data.get('env_vars', {}),
                path_additions=pkg_data.get('path_additions', [])
            ))
        
        return packages


def display_install_progress(
    session: InstallSession,
    console: Console
):
    table = Table(
        title=f"Installation Progress - Session {session.session_id}",
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
        box=box.ROUNDED
    )
    
    table.add_column("Package", style="white", min_width=20)
    table.add_column("Status", justify="center", width=12)
    table.add_column("Progress", justify="right", width=10)
    table.add_column("Message", style="dim")
    
    for task_id, task in session.tasks.items():
        status_colors = {
            InstallStatus.SUCCESS: "green",
            InstallStatus.FAILED: "red",
            InstallStatus.SKIPPED: "yellow",
            InstallStatus.PENDING: "dim",
            InstallStatus.INSTALLING: "cyan",
            InstallStatus.DOWNLOADING: "blue",
            InstallStatus.CANCELLED: "red"
        }
        
        status_icons = {
            InstallStatus.SUCCESS: "✓",
            InstallStatus.FAILED: "✗",
            InstallStatus.SKIPPED: "○",
            InstallStatus.PENDING: "·",
            InstallStatus.INSTALLING: "◉",
            InstallStatus.DOWNLOADING: "↓",
            InstallStatus.CANCELLED: "⊗"
        }
        
        color = status_colors.get(task.status, "white")
        icon = status_icons.get(task.status, "?")
        
        table.add_row(
            task.package.name,
            f"[{color}]{icon} {task.status.value}[/{color}]",
            f"{task.progress:.0f}%",
            (task.error_message or "")[:30]
        )
    
    console.print(table)
    
    summary = Text()
    summary.append(f"\nTotal: {session.total_packages} | ")
    summary.append(f"Completed: ", style="green")
    summary.append(f"{session.completed} | ")
    summary.append(f"Failed: ", style="red")
    summary.append(f"{session.failed} | ")
    summary.append(f"Skipped: ", style="yellow")
    summary.append(f"{session.skipped}")
    
    console.print(summary)


_batch_installer_instance: Optional[BatchInstaller] = None


def get_batch_installer(max_workers: int = 4) -> BatchInstaller:
    global _batch_installer_instance
    if _batch_installer_instance is None:
        _batch_installer_instance = BatchInstaller(max_workers)
    return _batch_installer_instance
