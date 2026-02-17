#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sandbox Environment Detection and Handling Module
Provides detection and workarounds for sandbox/virtualized environments
"""

import os
import sys
import subprocess
import ctypes
import json
import tempfile
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

console = Console()


class SandboxType(Enum):
    NONE = "none"
    WINDOWS_SANDBOX = "windows_sandbox"
    VMWARE = "vmware"
    VIRTUALBOX = "virtualbox"
    HYPERV = "hyperv"
    PARALLELS = "parallels"
    QEMU = "qemu"
    DOCKER = "docker"
    WSL = "wsl"
    UNKNOWN = "unknown"


@dataclass
class SandboxInfo:
    sandbox_type: SandboxType
    is_sandbox: bool
    is_vm: bool
    is_container: bool
    restrictions: List[str] = field(default_factory=list)
    workarounds: List[str] = field(default_factory=list)
    env_vars_blocked: List[str] = field(default_factory=list)
    paths_blocked: List[str] = field(default_factory=list)


class SandboxDetector:
    """Detect sandbox and virtualized environments"""
    
    VM_INDICATORS = {
        SandboxType.VMWARE: ['VMware', 'VMW'],
        SandboxType.VIRTUALBOX: ['VirtualBox', 'VBOX'],
        SandboxType.HYPERV: ['Hyper-V', 'Microsoft Corporation', 'Virtual Machine'],
        SandboxType.PARALLELS: ['Parallels'],
        SandboxType.QEMU: ['QEMU', 'Bochs'],
        SandboxType.WINDOWS_SANDBOX: ['Windows Sandbox', 'Sandbox'],
    }
    
    def __init__(self):
        self._info: Optional[SandboxInfo] = None
    
    def detect(self) -> SandboxInfo:
        if self._info:
            return self._info
        
        sandbox_type = self._detect_sandbox_type()
        
        is_sandbox = sandbox_type == SandboxType.WINDOWS_SANDBOX
        is_vm = sandbox_type in [
            SandboxType.VMWARE,
            SandboxType.VIRTUALBOX,
            SandboxType.HYPERV,
            SandboxType.PARALLELS,
            SandboxType.QEMU
        ]
        is_container = sandbox_type in [SandboxType.DOCKER, SandboxType.WSL]
        
        restrictions = self._detect_restrictions(sandbox_type)
        workarounds = self._get_workarounds(sandbox_type, restrictions)
        env_vars_blocked = self._check_blocked_env_vars()
        paths_blocked = self._check_blocked_paths()
        
        self._info = SandboxInfo(
            sandbox_type=sandbox_type,
            is_sandbox=is_sandbox,
            is_vm=is_vm,
            is_container=is_container,
            restrictions=restrictions,
            workarounds=workarounds,
            env_vars_blocked=env_vars_blocked,
            paths_blocked=paths_blocked
        )
        
        return self._info
    
    def _detect_sandbox_type(self) -> SandboxType:
        if sys.platform != 'win32':
            return self._detect_unix_sandbox()
        
        if self._check_windows_sandbox():
            return SandboxType.WINDOWS_SANDBOX
        
        if self._check_wsl():
            return SandboxType.WSL
        
        if self._check_docker():
            return SandboxType.DOCKER
        
        vm_type = self._detect_vm_type()
        if vm_type != SandboxType.NONE:
            return vm_type
        
        return SandboxType.NONE
    
    def _detect_unix_sandbox(self) -> SandboxType:
        if os.path.exists('/.dockerenv'):
            return SandboxType.DOCKER
        
        if os.path.exists('/proc/1/cgroup'):
            try:
                with open('/proc/1/cgroup', 'r') as f:
                    content = f.read()
                    if 'docker' in content or 'kubepods' in content:
                        return SandboxType.DOCKER
            except Exception:
                pass
        
        if 'microsoft' in os.uname().release.lower() if hasattr(os, 'uname') else False:
            return SandboxType.WSL
        
        return SandboxType.NONE
    
    def _check_windows_sandbox(self) -> bool:
        try:
            result = subprocess.run(
                ['cmd', '/c', 'reg', 'query',
                 'HKLM\\SYSTEM\\CurrentControlSet\\Control',
                 '/v', 'SystemStartOptions'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if 'MININT' in result.stdout or 'WINPE' in result.stdout:
                return True
            
            result = subprocess.run(
                ['cmd', '/c', 'wmic', 'computersystem', 'get', 'model'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if 'Windows Sandbox' in result.stdout:
                return True
        
        except Exception:
            pass
        
        sandbox_env_vars = ['SANDBOX', 'CONTAINER']
        for var in sandbox_env_vars:
            if var in os.environ:
                return True
        
        return False
    
    def _check_wsl(self) -> bool:
        if sys.platform != 'win32':
            return False
        
        try:
            result = subprocess.run(
                ['cmd', '/c', 'wsl', '--status'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return result.returncode == 0
        except Exception:
            pass
        
        return False
    
    def _check_docker(self) -> bool:
        if sys.platform != 'win32':
            return False
        
        try:
            result = subprocess.run(
                ['docker', 'info'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return result.returncode == 0
        except Exception:
            pass
        
        return False
    
    def _detect_vm_type(self) -> SandboxType:
        if sys.platform != 'win32':
            return SandboxType.NONE
        
        try:
            result = subprocess.run(
                ['cmd', '/c', 'wmic', 'computersystem', 'get', 'manufacturer,model'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            output = result.stdout.lower()
            
            for vm_type, indicators in self.VM_INDICATORS.items():
                for indicator in indicators:
                    if indicator.lower() in output:
                        return vm_type
        
        except Exception:
            pass
        
        try:
            result = subprocess.run(
                ['powershell', '-Command', 
                 'Get-CimInstance -ClassName Win32_ComputerSystem | Select-Object Manufacturer, Model'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            output = result.stdout.lower()
            
            for vm_type, indicators in self.VM_INDICATORS.items():
                for indicator in indicators:
                    if indicator.lower() in output:
                        return vm_type
        
        except Exception:
            pass
        
        return SandboxType.NONE
    
    def _detect_restrictions(self, sandbox_type: SandboxType) -> List[str]:
        restrictions = []
        
        if sandbox_type == SandboxType.WINDOWS_SANDBOX:
            restrictions.extend([
                "Environment variables may not persist after restart",
                "Some system paths may be redirected",
                "Clipboard integration may be limited",
                "Network isolation may be enabled",
                "No persistent storage by default"
            ])
        
        elif sandbox_type == SandboxType.DOCKER:
            restrictions.extend([
                "Limited system access",
                "Isolated filesystem",
                "Network restrictions may apply",
                "No direct hardware access"
            ])
        
        elif sandbox_type == SandboxType.WSL:
            restrictions.extend([
                "Windows paths accessed via /mnt/",
                "Some Windows executables may not work",
                "Filesystem differences"
            ])
        
        elif sandbox_type in [SandboxType.VMWARE, SandboxType.VIRTUALBOX, 
                              SandboxType.HYPERV, SandboxType.PARALLELS]:
            restrictions.extend([
                "Guest additions/tools may be needed",
                "Shared folders may need configuration",
                "Clipboard may need setup"
            ])
        
        return restrictions
    
    def _get_workarounds(
        self,
        sandbox_type: SandboxType,
        restrictions: List[str]
    ) -> List[str]:
        workarounds = []
        
        if sandbox_type == SandboxType.WINDOWS_SANDBOX:
            workarounds.extend([
                "Use mapped folders for persistent data",
                "Export configuration to host before closing",
                "Use environment variable files (.env)",
                "Run installation scripts with admin privileges"
            ])
        
        elif sandbox_type == SandboxType.DOCKER:
            workarounds.extend([
                "Use volume mounts for persistent data",
                "Pass environment variables via -e flags",
                "Use Dockerfile for reproducible setup"
            ])
        
        elif sandbox_type == SandboxType.WSL:
            workarounds.extend([
                "Use Windows paths via /mnt/c/",
                "Set PATH to include Windows directories",
                "Use wsl.conf for configuration"
            ])
        
        elif sandbox_type in [SandboxType.VMWARE, SandboxType.VIRTUALBOX,
                              SandboxType.HYPERV, SandboxType.PARALLELS]:
            workarounds.extend([
                "Install guest additions/tools",
                "Configure shared folders",
                "Enable clipboard sharing in settings"
            ])
        
        return workarounds
    
    def _check_blocked_env_vars(self) -> List[str]:
        blocked = []
        
        critical_vars = ['PATH', 'PYTHONPATH', 'HOME', 'USERPROFILE', 'APPDATA']
        
        for var in critical_vars:
            value = os.environ.get(var, '')
            if not value:
                blocked.append(var)
        
        return blocked
    
    def _check_blocked_paths(self) -> List[str]:
        blocked = []
        
        test_paths = [
            os.environ.get('APPDATA', ''),
            os.environ.get('LOCALAPPDATA', ''),
            os.environ.get('PROGRAMFILES', ''),
            os.environ.get('PROGRAMFILES(X86)', ''),
        ]
        
        for path in test_paths:
            if path and not Path(path).exists():
                blocked.append(path)
        
        return blocked


class SandboxHandler:
    """Handle sandbox-specific operations and workarounds"""
    
    PERSISTENT_DIR = Path.home() / '.sis' / 'sandbox_persistent'
    
    def __init__(self, sandbox_info: Optional[SandboxInfo] = None):
        self.info = sandbox_info or SandboxDetector().detect()
        self._ensure_persistent_dir()
    
    def _ensure_persistent_dir(self):
        self.PERSISTENT_DIR.mkdir(parents=True, exist_ok=True)
    
    def is_restricted(self) -> bool:
        return self.info.is_sandbox or self.info.is_container
    
    def save_env_state(self, name: str) -> str:
        state_file = self.PERSISTENT_DIR / f"{name}_env.json"
        
        state = {
            'timestamp': str(Path(__file__).stat().st_mtime),
            'environment': dict(os.environ),
            'info': {
                'sandbox_type': self.info.sandbox_type.value,
                'is_sandbox': self.info.is_sandbox,
                'is_vm': self.info.is_vm,
                'is_container': self.info.is_container
            }
        }
        
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        
        return str(state_file)
    
    def load_env_state(self, name: str) -> bool:
        state_file = self.PERSISTENT_DIR / f"{name}_env.json"
        
        if not state_file.exists():
            return False
        
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            for key, value in state.get('environment', {}).items():
                if key not in os.environ:
                    os.environ[key] = value
            
            return True
        
        except Exception:
            return False
    
    def export_config(self, config: Dict[str, Any], name: str) -> str:
        export_file = self.PERSISTENT_DIR / f"{name}_config.json"
        
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        return str(export_file)
    
    def import_config(self, name: str) -> Optional[Dict[str, Any]]:
        import_file = self.PERSISTENT_DIR / f"{name}_config.json"
        
        if not import_file.exists():
            return None
        
        try:
            with open(import_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    
    def get_persistent_path(self, subdir: str = '') -> Path:
        path = self.PERSISTENT_DIR / subdir
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def apply_workaround(self, workaround_id: str) -> bool:
        workarounds = {
            'env_persist': self._workaround_env_persist,
            'path_fix': self._workaround_path_fix,
            'admin_check': self._workaround_admin_check,
        }
        
        handler = workarounds.get(workaround_id)
        if handler:
            return handler()
        
        return False
    
    def _workaround_env_persist(self) -> bool:
        try:
            self.save_env_state('current')
            return True
        except Exception:
            return False
    
    def _workaround_path_fix(self) -> bool:
        try:
            if sys.platform == 'win32':
                python_dir = str(Path(sys.executable).parent)
                scripts_dir = str(Path(sys.executable).parent / 'Scripts')
                
                current_path = os.environ.get('PATH', '')
                
                if python_dir.lower() not in current_path.lower():
                    os.environ['PATH'] = f"{python_dir};{current_path}"
                
                if scripts_dir.lower() not in current_path.lower():
                    os.environ['PATH'] = f"{scripts_dir};{os.environ['PATH']}"
            
            return True
        
        except Exception:
            return False
    
    def _workaround_admin_check(self) -> bool:
        try:
            if sys.platform == 'win32':
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            return os.geteuid() == 0
        except Exception:
            return False
    
    def create_launcher_script(self, output_path: Optional[str] = None) -> str:
        if sys.platform != 'win32':
            return ''
        
        script = f'''@echo off
REM SwiftInstall Sandbox Launcher
REM This script restores environment state and launches the application

SET SIS_PERSISTENT_DIR={self.PERSISTENT_DIR}

REM Restore environment if available
IF EXIST "%SIS_PERSISTENT_DIR%\\current_env.json" (
    echo Restoring environment state...
)

REM Launch the application
python -m sis.main %*
'''
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(script)
        
        return script


def display_sandbox_info(info: SandboxInfo, console: Console):
    content = Text()
    
    content.append("Environment Type: ", style="cyan")
    content.append(f"{info.sandbox_type.value}\n\n", style="white")
    
    if info.is_sandbox or info.is_vm or info.is_container:
        content.append("⚠ Restricted Environment Detected\n\n", style="yellow")
        
        if info.restrictions:
            content.append("Restrictions:\n", style="red")
            for r in info.restrictions:
                content.append(f"  • {r}\n", style="white")
            content.append("\n")
        
        if info.workarounds:
            content.append("Recommended Workarounds:\n", style="green")
            for w in info.workarounds:
                content.append(f"  → {w}\n", style="white")
    else:
        content.append("✓ Standard Environment\n", style="green")
        content.append("All features should work normally.\n", style="dim")
    
    panel = Panel(
        content,
        title="[bold cyan]Sandbox Environment Analysis[/bold cyan]",
        border_style="cyan",
        box=box.ROUNDED
    )
    
    console.print(panel)


_sandbox_detector_instance: Optional[SandboxDetector] = None
_sandbox_handler_instance: Optional[SandboxHandler] = None


def get_sandbox_detector() -> SandboxDetector:
    global _sandbox_detector_instance
    if _sandbox_detector_instance is None:
        _sandbox_detector_instance = SandboxDetector()
    return _sandbox_detector_instance


def get_sandbox_handler() -> SandboxHandler:
    global _sandbox_handler_instance
    if _sandbox_handler_instance is None:
        _sandbox_handler_instance = SandboxHandler()
    return _sandbox_handler_instance


def check_sandbox_environment() -> Tuple[bool, SandboxInfo]:
    detector = get_sandbox_detector()
    info = detector.detect()
    return info.is_sandbox or info.is_container, info
