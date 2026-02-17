#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
System Environment Detection and Compatibility Check Module
Provides comprehensive system analysis before installation
"""

import os
import sys
import platform
import subprocess
import shutil
import re
import json
import socket
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

console = Console()


class CheckStatus(Enum):
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"
    SKIP = "skip"


class EnvironmentType(Enum):
    STANDARD = "standard"
    SANDBOX = "sandbox"
    VM = "virtual_machine"
    CONTAINER = "container"
    UNKNOWN = "unknown"


@dataclass
class CheckResult:
    name: str
    status: CheckStatus
    message: str
    details: Optional[str] = None
    suggestion: Optional[str] = None
    critical: bool = False


@dataclass
class SystemInfo:
    os_name: str
    os_version: str
    os_build: str
    architecture: str
    python_version: str
    processor: str
    total_memory: float
    available_memory: float
    disk_space: float
    environment_type: EnvironmentType
    is_admin: bool
    locale: str
    timezone: str
    hostname: str
    network_interfaces: List[Dict] = field(default_factory=list)


class EnvironmentChecker:
    """Comprehensive system environment checker"""
    
    MIN_WINDOWS_VERSION = (10, 0, 10240)
    MIN_MACOS_VERSION = (10, 15, 0)
    MIN_PYTHON_VERSION = (3, 7, 0)
    MIN_MEMORY_GB = 2.0
    MIN_DISK_SPACE_GB = 5.0
    
    def __init__(self):
        self.results: List[CheckResult] = []
        self.system_info: Optional[SystemInfo] = None
        self.warnings: List[str] = []
        self.errors: List[str] = []
        
    def run_all_checks(self) -> Tuple[bool, List[CheckResult]]:
        """Run all environment checks"""
        self.results = []
        
        self._check_os_compatibility()
        self._check_python_version()
        self._check_admin_privileges()
        self._check_memory()
        self._check_disk_space()
        self._check_package_manager()
        self._check_network()
        self._check_sandbox_environment()
        self._check_dependencies()
        self._check_environment_variables()
        self._check_security_software()
        
        has_errors = any(r.status == CheckStatus.ERROR and r.critical for r in self.results)
        return not has_errors, self.results
    
    def get_system_info(self) -> SystemInfo:
        """Collect comprehensive system information"""
        if self.system_info:
            return self.system_info
        
        self.system_info = SystemInfo(
            os_name=self._get_os_name(),
            os_version=self._get_os_version(),
            os_build=self._get_os_build(),
            architecture=platform.machine() or platform.processor(),
            python_version=platform.python_version(),
            processor=platform.processor() or "Unknown",
            total_memory=self._get_total_memory(),
            available_memory=self._get_available_memory(),
            disk_space=self._get_disk_space(),
            environment_type=self._detect_environment_type(),
            is_admin=self._is_admin(),
            locale=self._get_locale(),
            timezone=self._get_timezone(),
            hostname=socket.gethostname(),
            network_interfaces=self._get_network_interfaces()
        )
        return self.system_info
    
    def _get_os_name(self) -> str:
        if sys.platform == 'win32':
            return 'Windows'
        elif sys.platform == 'darwin':
            return 'macOS'
        elif sys.platform.startswith('linux'):
            return 'Linux'
        return platform.system()
    
    def _get_os_version(self) -> str:
        try:
            if sys.platform == 'win32':
                result = subprocess.run(
                    ['cmd', '/c', 'ver'],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                match = re.search(r'(\d+\.\d+\.\d+)', result.stdout)
                if match:
                    return match.group(1)
            return platform.version()
        except Exception:
            return platform.version()
    
    def _get_os_build(self) -> str:
        try:
            if sys.platform == 'win32':
                result = subprocess.run(
                    ['cmd', '/c', 'reg', 'query', 
                     'HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion',
                     '/v', 'CurrentBuild'],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                match = re.search(r'CurrentBuild\s+REG_SZ\s+(\S+)', result.stdout)
                if match:
                    return match.group(1)
        except Exception:
            pass
        return "Unknown"
    
    def _get_total_memory(self) -> float:
        try:
            if sys.platform == 'win32':
                import ctypes
                kernel32 = ctypes.windll.kernel32
                c_ulonglong = ctypes.c_ulonglong
                
                class MEMORYSTATUSEX(ctypes.Structure):
                    _fields_ = [
                        ('dwLength', ctypes.c_ulong),
                        ('dwMemoryLoad', ctypes.c_ulong),
                        ('ullTotalPhys', c_ulonglong),
                        ('ullAvailPhys', c_ulonglong),
                        ('ullTotalPageFile', c_ulonglong),
                        ('ullAvailPageFile', c_ulonglong),
                        ('ullTotalVirtual', c_ulonglong),
                        ('ullAvailVirtual', c_ulonglong),
                        ('ullAvailExtendedVirtual', c_ulonglong),
                    ]
                
                stat = MEMORYSTATUSEX()
                stat.dwLength = ctypes.sizeof(stat)
                kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
                return stat.ullTotalPhys / (1024 ** 3)
            else:
                with open('/proc/meminfo', 'r') as f:
                    for line in f:
                        if line.startswith('MemTotal'):
                            return int(line.split()[1]) / (1024 ** 2)
        except Exception:
            pass
        return 0.0
    
    def _get_available_memory(self) -> float:
        try:
            if sys.platform == 'win32':
                import ctypes
                kernel32 = ctypes.windll.kernel32
                c_ulonglong = ctypes.c_ulonglong
                
                class MEMORYSTATUSEX(ctypes.Structure):
                    _fields_ = [
                        ('dwLength', ctypes.c_ulong),
                        ('dwMemoryLoad', ctypes.c_ulong),
                        ('ullTotalPhys', c_ulonglong),
                        ('ullAvailPhys', c_ulonglong),
                        ('ullTotalPageFile', c_ulonglong),
                        ('ullAvailPageFile', c_ulonglong),
                        ('ullTotalVirtual', c_ulonglong),
                        ('ullAvailVirtual', c_ulonglong),
                        ('ullAvailExtendedVirtual', c_ulonglong),
                    ]
                
                stat = MEMORYSTATUSEX()
                stat.dwLength = ctypes.sizeof(stat)
                kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
                return stat.ullAvailPhys / (1024 ** 3)
        except Exception:
            pass
        return 0.0
    
    def _get_disk_space(self) -> float:
        try:
            if sys.platform == 'win32':
                import ctypes
                free_bytes = ctypes.c_ulonglong(0)
                ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                    ctypes.c_wchar_p(os.getcwd()),
                    None, None, ctypes.pointer(free_bytes)
                )
                return free_bytes.value / (1024 ** 3)
            else:
                stat = os.statvfs('/')
                return (stat.f_bavail * stat.f_frsize) / (1024 ** 3)
        except Exception:
            pass
        return 0.0
    
    def _detect_environment_type(self) -> EnvironmentType:
        indicators = []
        
        if sys.platform == 'win32':
            if self._check_windows_sandbox():
                indicators.append(EnvironmentType.SANDBOX)
            if self._check_windows_vm():
                indicators.append(EnvironmentType.VM)
        elif sys.platform == 'darwin':
            if self._check_macos_vm():
                indicators.append(EnvironmentType.VM)
        
        sandbox_env_vars = [
            'SANDBOX', 'CONTAINER', 'DOCKER', 'KUBERNETES',
            'CHROOT', 'JAIL', 'VIRTUALIZ'
        ]
        for var in sandbox_env_vars:
            for env_key in os.environ:
                if var in env_key.upper():
                    indicators.append(EnvironmentType.SANDBOX)
                    break
        
        if os.path.exists('/.dockerenv'):
            indicators.append(EnvironmentType.CONTAINER)
        if os.path.exists('/proc/1/cgroup'):
            try:
                with open('/proc/1/cgroup', 'r') as f:
                    content = f.read()
                    if 'docker' in content or 'kubepods' in content:
                        indicators.append(EnvironmentType.CONTAINER)
            except Exception:
                pass
        
        if EnvironmentType.SANDBOX in indicators:
            return EnvironmentType.SANDBOX
        elif EnvironmentType.CONTAINER in indicators:
            return EnvironmentType.CONTAINER
        elif EnvironmentType.VM in indicators:
            return EnvironmentType.VM
        elif indicators:
            return EnvironmentType.UNKNOWN
        
        return EnvironmentType.STANDARD
    
    def _check_windows_sandbox(self) -> bool:
        try:
            result = subprocess.run(
                ['cmd', '/c', 'reg', 'query',
                 'HKLM\\SYSTEM\\CurrentControlSet\\Control',
                 '/v', 'SystemStartOptions'],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if 'MININT' in result.stdout or 'WINPE' in result.stdout:
                return True
            
            result = subprocess.run(
                ['cmd', '/c', 'wmic', 'computersystem', 'get', 'model'],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if 'Virtual' in result.stdout or 'Sandbox' in result.stdout:
                return True
        except Exception:
            pass
        return False
    
    def _check_windows_vm(self) -> bool:
        vm_indicators = [
            'VMware', 'VirtualBox', 'QEMU', 'Xen', 'Hyper-V',
            'Parallels', 'Virtual Machine'
        ]
        try:
            result = subprocess.run(
                ['cmd', '/c', 'wmic', 'computersystem', 'get', 'manufacturer,model'],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            for indicator in vm_indicators:
                if indicator.lower() in result.stdout.lower():
                    return True
        except Exception:
            pass
        return False
    
    def _check_macos_vm(self) -> bool:
        try:
            result = subprocess.run(
                ['system_profiler', 'SPHardwareDataType'],
                capture_output=True,
                text=True
            )
            vm_indicators = ['VMware', 'Parallels', 'VirtualBox', 'QEMU']
            for indicator in vm_indicators:
                if indicator in result.stdout:
                    return True
        except Exception:
            pass
        return False
    
    def _is_admin(self) -> bool:
        try:
            if sys.platform == 'win32':
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.geteuid() == 0
        except Exception:
            return False
    
    def _get_locale(self) -> str:
        import locale
        try:
            return locale.getdefaultlocale()[0] or "Unknown"
        except Exception:
            return "Unknown"
    
    def _get_timezone(self) -> str:
        try:
            import time
            return time.tzname[0]
        except Exception:
            return "Unknown"
    
    def _get_network_interfaces(self) -> List[Dict]:
        interfaces = []
        try:
            hostname = socket.gethostname()
            for info in socket.getaddrinfo(hostname, None):
                family, _, _, _, sockaddr = info
                if family == socket.AF_INET:
                    interfaces.append({
                        'family': 'IPv4',
                        'address': sockaddr[0]
                    })
                elif family == socket.AF_INET6:
                    interfaces.append({
                        'family': 'IPv6',
                        'address': sockaddr[0]
                    })
        except Exception:
            pass
        return interfaces
    
    def _check_os_compatibility(self):
        if sys.platform == 'win32':
            try:
                version = sys.getwindowsversion()
                version_tuple = (version.major, version.minor, version.build)
                
                if version_tuple >= self.MIN_WINDOWS_VERSION:
                    self.results.append(CheckResult(
                        name="OS Compatibility",
                        status=CheckStatus.OK,
                        message=f"Windows {version.major}.{version.minor}.{version.build}",
                        details="System meets minimum requirements"
                    ))
                else:
                    self.results.append(CheckResult(
                        name="OS Compatibility",
                        status=CheckStatus.WARNING,
                        message=f"Windows {version.major}.{version.minor}.{version.build}",
                        details="System may have limited compatibility",
                        suggestion="Consider upgrading to Windows 10 1809 or later"
                    ))
            except Exception as e:
                self.results.append(CheckResult(
                    name="OS Compatibility",
                    status=CheckStatus.WARNING,
                    message="Could not determine Windows version",
                    details=str(e)
                ))
        
        elif sys.platform == 'darwin':
            try:
                result = subprocess.run(
                    ['sw_vers', '-productVersion'],
                    capture_output=True,
                    text=True
                )
                version_str = result.stdout.strip()
                version_tuple = tuple(map(int, version_str.split('.')))
                
                if version_tuple >= self.MIN_MACOS_VERSION:
                    self.results.append(CheckResult(
                        name="OS Compatibility",
                        status=CheckStatus.OK,
                        message=f"macOS {version_str}",
                        details="System meets minimum requirements"
                    ))
                else:
                    self.results.append(CheckResult(
                        name="OS Compatibility",
                        status=CheckStatus.WARNING,
                        message=f"macOS {version_str}",
                        details="System may have limited compatibility",
                        suggestion="Consider upgrading to macOS 10.15 or later"
                    ))
            except Exception as e:
                self.results.append(CheckResult(
                    name="OS Compatibility",
                    status=CheckStatus.WARNING,
                    message="Could not determine macOS version",
                    details=str(e)
                ))
        else:
            self.results.append(CheckResult(
                name="OS Compatibility",
                status=CheckStatus.ERROR,
                message="Unsupported operating system",
                details=f"Platform: {sys.platform}",
                suggestion="This tool supports Windows 10+ and macOS 10.15+",
                critical=True
            ))
    
    def _check_python_version(self):
        version = sys.version_info
        version_tuple = (version.major, version.minor, version.micro)
        
        if version_tuple >= self.MIN_PYTHON_VERSION:
            self.results.append(CheckResult(
                name="Python Version",
                status=CheckStatus.OK,
                message=f"Python {version.major}.{version.minor}.{version.micro}",
                details="Python version meets requirements"
            ))
        else:
            self.results.append(CheckResult(
                name="Python Version",
                status=CheckStatus.ERROR,
                message=f"Python {version.major}.{version.minor}.{version.micro}",
                details=f"Minimum required: {'.'.join(map(str, self.MIN_PYTHON_VERSION))}",
                suggestion="Please upgrade Python to version 3.7 or higher",
                critical=True
            ))
    
    def _check_admin_privileges(self):
        is_admin = self._is_admin()
        
        if is_admin:
            self.results.append(CheckResult(
                name="Admin Privileges",
                status=CheckStatus.OK,
                message="Running with administrator privileges",
                details="Full system access available"
            ))
        else:
            self.results.append(CheckResult(
                name="Admin Privileges",
                status=CheckStatus.WARNING,
                message="Not running as administrator",
                details="Some operations may require elevated privileges",
                suggestion="Right-click and 'Run as administrator' for full functionality"
            ))
    
    def _check_memory(self):
        total_memory = self._get_total_memory()
        available_memory = self._get_available_memory()
        
        if total_memory >= self.MIN_MEMORY_GB:
            if available_memory >= 1.0:
                self.results.append(CheckResult(
                    name="Memory",
                    status=CheckStatus.OK,
                    message=f"Total: {total_memory:.1f} GB, Available: {available_memory:.1f} GB",
                    details="Sufficient memory available"
                ))
            else:
                self.results.append(CheckResult(
                    name="Memory",
                    status=CheckStatus.WARNING,
                    message=f"Total: {total_memory:.1f} GB, Available: {available_memory:.1f} GB",
                    details="Low available memory",
                    suggestion="Close some applications to free up memory"
                ))
        else:
            self.results.append(CheckResult(
                name="Memory",
                status=CheckStatus.WARNING,
                message=f"Total: {total_memory:.1f} GB",
                details=f"Minimum recommended: {self.MIN_MEMORY_GB} GB",
                suggestion="Consider adding more RAM for better performance"
            ))
    
    def _check_disk_space(self):
        disk_space = self._get_disk_space()
        
        if disk_space >= self.MIN_DISK_SPACE_GB:
            self.results.append(CheckResult(
                name="Disk Space",
                status=CheckStatus.OK,
                message=f"{disk_space:.1f} GB available",
                details="Sufficient disk space"
            ))
        else:
            self.results.append(CheckResult(
                name="Disk Space",
                status=CheckStatus.ERROR,
                message=f"{disk_space:.1f} GB available",
                details=f"Minimum required: {self.MIN_DISK_SPACE_GB} GB",
                suggestion="Free up disk space before installation",
                critical=True
            ))
    
    def _check_package_manager(self):
        if sys.platform == 'win32':
            self._check_winget()
        elif sys.platform == 'darwin':
            self._check_homebrew()
    
    def _check_winget(self):
        try:
            result = subprocess.run(
                ['winget', '--version'],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                self.results.append(CheckResult(
                    name="Winget",
                    status=CheckStatus.OK,
                    message=f"Winget {version}",
                    details="Windows Package Manager is available"
                ))
                
                self._check_winget_source()
            else:
                self.results.append(CheckResult(
                    name="Winget",
                    status=CheckStatus.ERROR,
                    message="Winget not available",
                    details="Windows Package Manager is not installed or not working",
                    suggestion="Install 'App Installer' from Microsoft Store",
                    critical=True
                ))
        except FileNotFoundError:
            self.results.append(CheckResult(
                name="Winget",
                status=CheckStatus.ERROR,
                message="Winget not found",
                details="Windows Package Manager is not installed",
                suggestion="Install 'App Installer' from Microsoft Store",
                critical=True
            ))
        except Exception as e:
            self.results.append(CheckResult(
                name="Winget",
                status=CheckStatus.ERROR,
                message="Winget check failed",
                details=str(e),
                suggestion="Ensure Windows Package Manager is properly installed",
                critical=True
            ))
    
    def _check_winget_source(self):
        try:
            result = subprocess.run(
                ['winget', 'source', 'list'],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            
            if 'winget' in result.stdout:
                if 'ustc.edu.cn' in result.stdout.lower() or 'mirrors' in result.stdout.lower():
                    self.results.append(CheckResult(
                        name="Winget Source",
                        status=CheckStatus.OK,
                        message="Using mirror source",
                        details="Winget is configured to use a mirror source for faster downloads"
                    ))
                else:
                    self.results.append(CheckResult(
                        name="Winget Source",
                        status=CheckStatus.OK,
                        message="Using default source",
                        details="Winget is using the default Microsoft source"
                    ))
            else:
                self.results.append(CheckResult(
                    name="Winget Source",
                    status=CheckStatus.WARNING,
                    message="No winget source configured",
                    suggestion="Run 'winget source reset --force' to reset sources"
                ))
        except Exception as e:
            self.results.append(CheckResult(
                name="Winget Source",
                status=CheckStatus.WARNING,
                message="Could not check winget source",
                details=str(e)
            ))
    
    def _check_homebrew(self):
        try:
            result = subprocess.run(
                ['brew', '--version'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                version = result.stdout.strip().split('\n')[0]
                self.results.append(CheckResult(
                    name="Homebrew",
                    status=CheckStatus.OK,
                    message=version,
                    details="Homebrew package manager is available"
                ))
            else:
                self.results.append(CheckResult(
                    name="Homebrew",
                    status=CheckStatus.ERROR,
                    message="Homebrew not available",
                    suggestion="Install Homebrew: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"",
                    critical=True
                ))
        except FileNotFoundError:
            self.results.append(CheckResult(
                name="Homebrew",
                status=CheckStatus.ERROR,
                message="Homebrew not found",
                suggestion="Install Homebrew from https://brew.sh",
                critical=True
            ))
    
    def _check_network(self):
        test_hosts = [
            ('api.github.com', 443),
            ('raw.githubusercontent.com', 443),
            ('pypi.org', 443),
        ]
        
        reachable = 0
        details = []
        
        for host, port in test_hosts:
            try:
                sock = socket.create_connection((host, port), timeout=5)
                sock.close()
                reachable += 1
                details.append(f"{host}: OK")
            except Exception as e:
                details.append(f"{host}: Failed ({str(e)[:30]})")
        
        if reachable == len(test_hosts):
            self.results.append(CheckResult(
                name="Network",
                status=CheckStatus.OK,
                message="All network tests passed",
                details=", ".join(details)
            ))
        elif reachable > 0:
            self.results.append(CheckResult(
                name="Network",
                status=CheckStatus.WARNING,
                message=f"Partial network connectivity ({reachable}/{len(test_hosts)})",
                details=", ".join(details),
                suggestion="Some hosts are unreachable. Check firewall or proxy settings"
            ))
        else:
            self.results.append(CheckResult(
                name="Network",
                status=CheckStatus.ERROR,
                message="No network connectivity",
                details=", ".join(details),
                suggestion="Check your internet connection",
                critical=True
            ))
    
    def _check_sandbox_environment(self):
        env_type = self._detect_environment_type()
        
        if env_type == EnvironmentType.STANDARD:
            self.results.append(CheckResult(
                name="Environment Type",
                status=CheckStatus.OK,
                message="Standard environment",
                details="Running in a standard system environment"
            ))
        elif env_type == EnvironmentType.SANDBOX:
            self.results.append(CheckResult(
                name="Environment Type",
                status=CheckStatus.WARNING,
                message="Sandbox environment detected",
                details="Some features may be limited in sandbox mode",
                suggestion="For full functionality, run outside of sandbox environment"
            ))
        elif env_type == EnvironmentType.VM:
            self.results.append(CheckResult(
                name="Environment Type",
                status=CheckStatus.OK,
                message="Virtual machine detected",
                details="Running in a virtualized environment"
            ))
        elif env_type == EnvironmentType.CONTAINER:
            self.results.append(CheckResult(
                name="Environment Type",
                status=CheckStatus.WARNING,
                message="Container environment detected",
                details="Some system-level operations may be restricted",
                suggestion="Ensure proper permissions for container operations"
            ))
        else:
            self.results.append(CheckResult(
                name="Environment Type",
                status=CheckStatus.WARNING,
                message="Unknown environment type",
                details="Could not determine the execution environment"
            ))
    
    def _check_dependencies(self):
        required_modules = [
            ('click', 'Click'),
            ('rich', 'Rich'),
            ('yaml', 'PyYAML'),
            ('colorama', 'Colorama'),
        ]
        
        missing = []
        installed = []
        
        for module, name in required_modules:
            try:
                __import__(module)
                installed.append(name)
            except ImportError:
                missing.append(name)
        
        if not missing:
            self.results.append(CheckResult(
                name="Python Dependencies",
                status=CheckStatus.OK,
                message="All dependencies installed",
                details=f"Installed: {', '.join(installed)}"
            ))
        else:
            self.results.append(CheckResult(
                name="Python Dependencies",
                status=CheckStatus.WARNING,
                message=f"Missing: {', '.join(missing)}",
                details=f"Installed: {', '.join(installed)}",
                suggestion=f"Run: pip install {' '.join(missing)}"
            ))
    
    def _check_environment_variables(self):
        important_vars = ['PATH', 'PYTHONPATH', 'HOME', 'USERPROFILE']
        issues = []
        
        for var in important_vars:
            value = os.environ.get(var, '')
            if not value:
                issues.append(f"{var}: Not set")
        
        if sys.platform == 'win32':
            path = os.environ.get('PATH', '')
            python_scripts = None
            
            for p in path.split(';'):
                if 'Python' in p and 'Scripts' in p:
                    python_scripts = p
                    break
            
            if not python_scripts:
                issues.append("Python Scripts not in PATH")
        
        if not issues:
            self.results.append(CheckResult(
                name="Environment Variables",
                status=CheckStatus.OK,
                message="All critical variables set",
                details="PATH and other variables are properly configured"
            ))
        else:
            self.results.append(CheckResult(
                name="Environment Variables",
                status=CheckStatus.WARNING,
                message="Some variables may need attention",
                details="; ".join(issues),
                suggestion="Check your environment variable configuration"
            ))
    
    def _check_security_software(self):
        if sys.platform != 'win32':
            self.results.append(CheckResult(
                name="Security Software",
                status=CheckStatus.SKIP,
                message="Check skipped for non-Windows platform"
            ))
            return
        
        try:
            result = subprocess.run(
                ['powershell', '-Command', 
                 'Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntiVirusProduct | Select-Object displayName'],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            av_products = []
            for line in result.stdout.strip().split('\n')[1:]:
                line = line.strip()
                if line and line != 'displayName':
                    av_products.append(line)
            
            if av_products:
                self.results.append(CheckResult(
                    name="Security Software",
                    status=CheckStatus.OK,
                    message=f"Detected: {', '.join(av_products)}",
                    details="Antivirus software may scan downloaded files"
                ))
            else:
                self.results.append(CheckResult(
                    name="Security Software",
                    status=CheckStatus.WARNING,
                    message="No antivirus detected",
                    details="Consider enabling Windows Defender or other security software"
                ))
        except Exception as e:
            self.results.append(CheckResult(
                name="Security Software",
                status=CheckStatus.SKIP,
                message="Could not check security software",
                details=str(e)[:50]
            ))
    
    def generate_report(self) -> str:
        report_lines = [
            "=" * 60,
            "System Environment Check Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 60,
            ""
        ]
        
        system_info = self.get_system_info()
        report_lines.extend([
            "System Information:",
            f"  OS: {system_info.os_name} {system_info.os_version}",
            f"  Architecture: {system_info.architecture}",
            f"  Python: {system_info.python_version}",
            f"  Memory: {system_info.total_memory:.1f} GB total, {system_info.available_memory:.1f} GB available",
            f"  Disk Space: {system_info.disk_space:.1f} GB available",
            f"  Environment: {system_info.environment_type.value}",
            f"  Admin: {'Yes' if system_info.is_admin else 'No'}",
            ""
        ])
        
        report_lines.append("Check Results:")
        for result in self.results:
            status_icon = {
                CheckStatus.OK: "[OK]",
                CheckStatus.WARNING: "[WARN]",
                CheckStatus.ERROR: "[ERROR]",
                CheckStatus.SKIP: "[SKIP]"
            }.get(result.status, "[?]")
            
            report_lines.append(f"  {status_icon} {result.name}: {result.message}")
            if result.details:
                report_lines.append(f"       Details: {result.details}")
            if result.suggestion:
                report_lines.append(f"       Suggestion: {result.suggestion}")
        
        report_lines.extend(["", "=" * 60])
        
        return "\n".join(report_lines)


def display_check_results(results: List[CheckResult], console: Console):
    """Display check results in a formatted table"""
    table = Table(
        title="System Environment Check",
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
        box=box.ROUNDED
    )
    
    table.add_column("Check", style="white", min_width=20)
    table.add_column("Status", justify="center", width=8)
    table.add_column("Message", style="white")
    table.add_column("Suggestion", style="dim")
    
    for result in results:
        status_style = {
            CheckStatus.OK: "green",
            CheckStatus.WARNING: "yellow",
            CheckStatus.ERROR: "red",
            CheckStatus.SKIP: "dim"
        }.get(result.status, "white")
        
        status_icon = {
            CheckStatus.OK: "✓",
            CheckStatus.WARNING: "⚠",
            CheckStatus.ERROR: "✗",
            CheckStatus.SKIP: "○"
        }.get(result.status, "?")
        
        table.add_row(
            result.name,
            f"[{status_style}]{status_icon}[/{status_style}]",
            result.message,
            result.suggestion or ""
        )
    
    console.print(table)


def run_pre_install_check() -> Tuple[bool, SystemInfo, List[CheckResult]]:
    """Run pre-installation environment check"""
    checker = EnvironmentChecker()
    system_info = checker.get_system_info()
    success, results = checker.run_all_checks()
    
    return success, system_info, results
