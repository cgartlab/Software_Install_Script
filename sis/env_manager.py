#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Environment Variable Hot-Refresh Module
Enables runtime environment variable updates without terminal restart
"""

import os
import sys
import ctypes
import subprocess
import re
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
from enum import Enum

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()


class EnvScope(Enum):
    USER = "user"
    SYSTEM = "system"
    PROCESS = "process"
    VOLATILE = "volatile"


@dataclass
class EnvVariable:
    name: str
    value: str
    scope: EnvScope
    previous_value: Optional[str] = None
    modified_at: Optional[str] = None


class EnvironmentManager:
    """Manage environment variables with hot-refresh capability"""
    
    if sys.platform == 'win32':
        HWND_BROADCAST = 0xFFFF
        WM_SETTINGCHANGE = 0x1A
        SMTO_ABORTIFHUNG = 0x0002
    
    def __init__(self):
        self._modified_vars: Dict[str, EnvVariable] = {}
        self._original_env: Dict[str, str] = dict(os.environ)
        self._is_sandbox: Optional[bool] = None
    
    def detect_sandbox(self) -> bool:
        if self._is_sandbox is not None:
            return self._is_sandbox
        
        indicators = []
        
        if sys.platform == 'win32':
            try:
                result = subprocess.run(
                    ['cmd', '/c', 'wmic', 'computersystem', 'get', 'model'],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                if 'Windows Sandbox' in result.stdout or 'Virtual' in result.stdout:
                    indicators.append(True)
            except Exception:
                pass
        
        sandbox_vars = ['SANDBOX', 'CONTAINER', 'DOCKER']
        for var in sandbox_vars:
            if var in os.environ:
                indicators.append(True)
        
        self._is_sandbox = len(indicators) > 0
        return self._is_sandbox
    
    def get_env(self, name: str, scope: EnvScope = EnvScope.PROCESS) -> Optional[str]:
        if scope == EnvScope.PROCESS:
            return os.environ.get(name)
        
        if sys.platform == 'win32':
            return self._get_windows_env(name, scope)
        
        return os.environ.get(name)
    
    def _get_windows_env(self, name: str, scope: EnvScope) -> Optional[str]:
        try:
            if scope == EnvScope.USER:
                result = subprocess.run(
                    ['powershell', '-Command', 
                     f'[Environment]::GetEnvironmentVariable("{name}", "User")'],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                return result.stdout.strip() if result.returncode == 0 else None
            
            elif scope == EnvScope.SYSTEM:
                result = subprocess.run(
                    ['powershell', '-Command', 
                     f'[Environment]::GetEnvironmentVariable("{name}", "Machine")'],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                return result.stdout.strip() if result.returncode == 0 else None
        
        except Exception:
            pass
        
        return None
    
    def set_env(
        self,
        name: str,
        value: str,
        scope: EnvScope = EnvScope.PROCESS,
        persist: bool = True,
        broadcast: bool = True
    ) -> bool:
        previous_value = self.get_env(name, scope)
        
        if scope == EnvScope.PROCESS:
            os.environ[name] = value
            self._modified_vars[name] = EnvVariable(
                name=name,
                value=value,
                scope=scope,
                previous_value=previous_value,
                modified_at=datetime.now().isoformat()
            )
            return True
        
        if sys.platform == 'win32':
            return self._set_windows_env(name, value, scope, persist, broadcast)
        
        return False
    
    def _set_windows_env(
        self,
        name: str,
        value: str,
        scope: EnvScope,
        persist: bool,
        broadcast: bool
    ) -> bool:
        try:
            target = "User" if scope == EnvScope.USER else "Machine"
            
            if persist:
                ps_cmd = f'[Environment]::SetEnvironmentVariable("{name}", "{value}", "{target}")'
                result = subprocess.run(
                    ['powershell', '-Command', ps_cmd],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                if result.returncode != 0:
                    return False
            
            os.environ[name] = value
            
            previous_value = self._get_windows_env(name, scope)
            self._modified_vars[name] = EnvVariable(
                name=name,
                value=value,
                scope=scope,
                previous_value=previous_value,
                modified_at=datetime.now().isoformat()
            )
            
            if broadcast:
                self._broadcast_environment_change()
            
            return True
        
        except Exception as e:
            console.print(f"[red]Error setting environment variable: {e}[/red]")
            return False
    
    def _broadcast_environment_change(self):
        if sys.platform != 'win32':
            return
        
        try:
            ctypes.windll.user32.SendMessageTimeoutW(
                self.HWND_BROADCAST,
                self.WM_SETTINGCHANGE,
                0,
                "Environment",
                self.SMTO_ABORTIFHUNG,
                5000,
                None
            )
        except Exception:
            pass
    
    def append_to_path(
        self,
        path_to_add: str,
        scope: EnvScope = EnvScope.USER,
        position: str = "end"
    ) -> bool:
        path_to_add = str(Path(path_to_add).resolve())
        
        current_path = self.get_env("PATH", scope) or ""
        
        if path_to_add in current_path.split(';'):
            return True
        
        if position == "start":
            new_path = f"{path_to_add};{current_path}"
        else:
            new_path = f"{current_path};{path_to_add}"
        
        new_path = new_path.replace(";;", ";").strip(";")
        
        return self.set_env("PATH", new_path, scope, persist=True)
    
    def remove_from_path(
        self,
        path_to_remove: str,
        scope: EnvScope = EnvScope.USER
    ) -> bool:
        path_to_remove = str(Path(path_to_remove).resolve())
        
        current_path = self.get_env("PATH", scope) or ""
        paths = [p.strip() for p in current_path.split(';') if p.strip()]
        
        paths = [p for p in paths if p.lower() != path_to_remove.lower()]
        
        new_path = ";".join(paths)
        
        return self.set_env("PATH", new_path, scope, persist=True)
    
    def refresh_process_env(self) -> bool:
        if sys.platform != 'win32':
            return True
        
        try:
            user_env = self._get_all_windows_env(EnvScope.USER)
            system_env = self._get_all_windows_env(EnvScope.SYSTEM)
            
            merged_env = {}
            merged_env.update(system_env)
            merged_env.update(user_env)
            
            for name, value in merged_env.items():
                if name and value is not None:
                    os.environ[name] = value
            
            return True
        
        except Exception as e:
            console.print(f"[red]Error refreshing environment: {e}[/red]")
            return False
    
    def _get_all_windows_env(self, scope: EnvScope) -> Dict[str, str]:
        env_dict = {}
        
        try:
            target = "User" if scope == EnvScope.USER else "Machine"
            
            result = subprocess.run(
                ['powershell', '-Command', 
                 f'[Environment]::GetEnvironmentVariables("{target}") | ConvertTo-Json'],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0 and result.stdout.strip():
                data = json.loads(result.stdout)
                if isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, str):
                            env_dict[key] = value
                        elif isinstance(value, dict) and 'value' in value:
                            env_dict[key] = value['value']
        
        except Exception:
            pass
        
        return env_dict
    
    def get_python_paths(self) -> List[str]:
        paths = []
        
        for p in os.environ.get('PATH', '').split(';'):
            p = p.strip()
            if not p:
                continue
            
            if 'Python' in p:
                paths.append(p)
            elif 'python' in p.lower():
                paths.append(p)
        
        return paths
    
    def ensure_python_in_path(self) -> Tuple[bool, List[str]]:
        if sys.platform != 'win32':
            return True, []
        
        added_paths = []
        
        python_exe = sys.executable
        python_dir = str(Path(python_exe).parent)
        scripts_dir = str(Path(python_exe).parent / "Scripts")
        
        current_path = self.get_env("PATH", EnvScope.USER) or ""
        
        if python_dir.lower() not in current_path.lower():
            if self.append_to_path(python_dir, EnvScope.USER, "end"):
                added_paths.append(python_dir)
        
        if scripts_dir.lower() not in current_path.lower():
            if self.append_to_path(scripts_dir, EnvScope.USER, "end"):
                added_paths.append(scripts_dir)
        
        if added_paths:
            self.refresh_process_env()
        
        return len(added_paths) > 0, added_paths
    
    def get_modified_vars(self) -> Dict[str, EnvVariable]:
        return self._modified_vars.copy()
    
    def restore_env(self, name: str) -> bool:
        if name not in self._modified_vars:
            return False
        
        var = self._modified_vars[name]
        
        if var.previous_value is not None:
            return self.set_env(name, var.previous_value, var.scope)
        else:
            return self.unset_env(name, var.scope)
    
    def unset_env(self, name: str, scope: EnvScope = EnvScope.PROCESS) -> bool:
        if scope == EnvScope.PROCESS:
            if name in os.environ:
                del os.environ[name]
            return True
        
        if sys.platform == 'win32':
            try:
                target = "User" if scope == EnvScope.USER else "Machine"
                
                result = subprocess.run(
                    ['powershell', '-Command', 
                     f'[Environment]::SetEnvironmentVariable("{name}", $null, "{target}")'],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                if result.returncode == 0:
                    if name in os.environ:
                        del os.environ[name]
                    return True
            
            except Exception:
                pass
        
        return False
    
    def export_env_report(self) -> str:
        lines = [
            "=" * 60,
            "Environment Variables Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 60,
            "",
            "Modified Variables:",
        ]
        
        if self._modified_vars:
            for name, var in self._modified_vars.items():
                lines.append(f"  {name}:")
                lines.append(f"    Current: {var.value}")
                lines.append(f"    Previous: {var.previous_value or '(not set)'}")
                lines.append(f"    Scope: {var.scope.value}")
                lines.append(f"    Modified: {var.modified_at}")
                lines.append("")
        else:
            lines.append("  No modifications recorded")
            lines.append("")
        
        lines.extend([
            "",
            "Python Paths in PATH:",
        ])
        
        python_paths = self.get_python_paths()
        if python_paths:
            for p in python_paths:
                lines.append(f"  • {p}")
        else:
            lines.append("  No Python paths found in PATH")
        
        lines.extend(["", "=" * 60])
        
        return "\n".join(lines)


class PathManager:
    """Specialized PATH environment management"""
    
    def __init__(self, env_manager: Optional[EnvironmentManager] = None):
        self.env_manager = env_manager or EnvironmentManager()
    
    def get_paths(self, scope: EnvScope = EnvScope.PROCESS) -> List[str]:
        path_str = self.env_manager.get_env("PATH", scope) or ""
        return [p.strip() for p in path_str.split(';') if p.strip()]
    
    def find_in_path(self, executable: str) -> Optional[str]:
        for path_dir in self.get_paths():
            exe_path = Path(path_dir) / executable
            if exe_path.exists():
                return str(exe_path)
        
        if sys.platform == 'win32':
            for ext in ['.exe', '.bat', '.cmd', '.ps1']:
                for path_dir in self.get_paths():
                    exe_path = Path(path_dir) / (executable + ext)
                    if exe_path.exists():
                        return str(exe_path)
        
        return None
    
    def validate_paths(self) -> Dict[str, bool]:
        results = {}
        
        for path_dir in self.get_paths():
            results[path_dir] = Path(path_dir).exists()
        
        return results
    
    def cleanup_path(
        self,
        scope: EnvScope = EnvScope.USER,
        remove_invalid: bool = False,
        remove_duplicates: bool = True
    ) -> Tuple[int, List[str]]:
        paths = self.get_paths(scope)
        original_count = len(paths)
        removed = []
        
        if remove_duplicates:
            seen = set()
            unique_paths = []
            for p in paths:
                p_lower = p.lower()
                if p_lower not in seen:
                    seen.add(p_lower)
                    unique_paths.append(p)
            paths = unique_paths
        
        if remove_invalid:
            valid_paths = []
            for p in paths:
                if Path(p).exists():
                    valid_paths.append(p)
                else:
                    removed.append(p)
            paths = valid_paths
        
        if len(paths) != original_count:
            new_path = ";".join(paths)
            self.env_manager.set_env("PATH", new_path, scope, persist=True)
        
        return original_count - len(paths), removed
    
    def add_software_path(
        self,
        software_name: str,
        path: str,
        scope: EnvScope = EnvScope.USER
    ) -> bool:
        path = str(Path(path).resolve())
        
        if not Path(path).exists():
            console.print(f"[yellow]Warning: Path does not exist: {path}[/yellow]")
        
        return self.env_manager.append_to_path(path, scope)


def display_env_table(env_manager: EnvironmentManager, console: Console):
    modified = env_manager.get_modified_vars()
    
    if not modified:
        console.print("[green]No environment modifications[/green]")
        return
    
    table = Table(
        title="Modified Environment Variables",
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
        box=box.ROUNDED
    )
    
    table.add_column("Name", style="white")
    table.add_column("Previous", style="dim")
    table.add_column("Current", style="green")
    table.add_column("Scope", style="yellow")
    
    for name, var in modified.items():
        table.add_row(
            name,
            var.previous_value or "(not set)",
            var.value,
            var.scope.value
        )
    
    console.print(table)


_env_manager_instance: Optional[EnvironmentManager] = None
_path_manager_instance: Optional[PathManager] = None


def get_env_manager() -> EnvironmentManager:
    global _env_manager_instance
    if _env_manager_instance is None:
        _env_manager_instance = EnvironmentManager()
    return _env_manager_instance


def get_path_manager() -> PathManager:
    global _path_manager_instance
    if _path_manager_instance is None:
        _path_manager_instance = PathManager(get_env_manager())
    return _path_manager_instance


def hot_refresh_environment() -> bool:
    """Perform a complete environment hot-refresh"""
    manager = get_env_manager()
    
    success = manager.refresh_process_env()
    
    if success:
        manager._broadcast_environment_change()
    
    return success
