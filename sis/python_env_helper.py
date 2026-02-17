#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Python Environment Setup Helper Module
Provides comprehensive Python environment detection and setup for Windows
"""

import os
import sys
import subprocess
import shutil
import platform
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class PythonEnvironmentType(Enum):
    SYSTEM = "system"
    VIRTUALENV = "virtualenv"
    CONDA = "conda"
    VENV = "venv"
    UV = "uv"
    POETRY = "poetry"
    UNKNOWN = "unknown"


@dataclass
class PythonInstallation:
    path: str
    version: str
    version_tuple: Tuple[int, int, int]
    executable: str
    is_64bit: bool
    environment_type: PythonEnvironmentType
    pip_available: bool
    pip_version: Optional[str] = None


@dataclass
class EnvironmentCheckResult:
    python_installations: List[PythonInstallation]
    recommended_installation: Optional[PythonInstallation]
    issues: List[str]
    suggestions: List[str]


class PythonEnvironmentDetector:
    """Detect and analyze Python installations"""

    MIN_PYTHON_VERSION = (3, 8, 0)

    def __init__(self):
        self.installations: List[PythonInstallation] = []
        self.issues: List[str] = []
        self.suggestions: List[str] = []

    def detect_all(self) -> EnvironmentCheckResult:
        """Detect all Python installations on the system"""
        self.installations = []
        self.issues = []
        self.suggestions = []

        self._detect_system_python()
        self._detect_py_launcher()
        self._detect_common_locations()
        self._detect_conda()
        self._detect_uv()

        self._analyze_issues()

        recommended = self._get_recommended_installation()

        return EnvironmentCheckResult(
            python_installations=self.installations,
            recommended_installation=recommended,
            issues=self.issues,
            suggestions=self.suggestions
        )

    def _detect_system_python(self):
        """Detect system Python via PATH"""
        python_commands = ['python', 'python3', 'py']

        for cmd in python_commands:
            path = shutil.which(cmd)
            if path:
                info = self._get_python_info(path, cmd)
                if info and not self._is_duplicate(info):
                    self.installations.append(info)

    def _detect_py_launcher(self):
        """Detect Python via py launcher (Windows)"""
        if sys.platform != 'win32':
            return

        py_path = shutil.which('py')
        if not py_path:
            return

        try:
            result = subprocess.run(
                ['py', '-0'],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )

            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    match = re.match(r'(\d+\.\d+)\s+-\s+(.+)', line)
                    if match:
                        version = match.group(1)
                        path = match.group(2).strip()

                        if path.startswith('*'):
                            path = path[1:].strip()

                        if path and os.path.exists(path):
                            info = self._create_installation_from_path(path, version)
                            if info and not self._is_duplicate(info):
                                self.installations.append(info)
        except Exception:
            pass

    def _detect_common_locations(self):
        """Detect Python in common installation locations"""
        common_paths = []

        if sys.platform == 'win32':
            program_files = os.environ.get('ProgramFiles', 'C:\\Program Files')
            program_files_x86 = os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)')

            common_paths.extend([
                os.path.join(program_files, 'Python'),
                os.path.join(program_files_x86, 'Python'),
                os.path.join(os.environ.get('LocalAppData', ''), 'Programs', 'Python'),
                os.path.join(os.environ.get('AppData', ''), 'Local', 'Programs', 'Python'),
            ])

            for base in common_paths:
                if os.path.exists(base):
                    for item in os.listdir(base):
                        python_dir = os.path.join(base, item)
                        python_exe = os.path.join(python_dir, 'python.exe')

                        if os.path.isdir(python_dir) and os.path.exists(python_exe):
                            info = self._get_python_info(python_exe, f'python in {python_dir}')
                            if info and not self._is_duplicate(info):
                                self.installations.append(info)

        elif sys.platform == 'darwin':
            common_paths = [
                '/usr/bin/python3',
                '/usr/local/bin/python3',
                os.path.expanduser('~/Library/Python/*/bin/python3'),
            ]

            for pattern in common_paths:
                if '*' in pattern:
                    import glob
                    matches = glob.glob(pattern)
                    for match in matches:
                        if os.path.exists(match):
                            info = self._get_python_info(match, match)
                            if info and not self._is_duplicate(info):
                                self.installations.append(info)
                elif os.path.exists(pattern):
                    info = self._get_python_info(pattern, pattern)
                    if info and not self._is_duplicate(info):
                        self.installations.append(info)

    def _detect_conda(self):
        """Detect Conda installations"""
        conda_commands = ['conda', 'micromamba']

        for cmd in conda_commands:
            conda_path = shutil.which(cmd)
            if not conda_path:
                continue

            try:
                result = subprocess.run(
                    [conda_path, 'env', 'list'],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
                )

                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if line.startswith('*'):
                            line = line[1:].strip()

                        parts = line.split()
                        if parts:
                            env_path = parts[0]
                            if os.path.exists(env_path):
                                python_exe = os.path.join(env_path, 'python.exe' if sys.platform == 'win32' else 'python')
                                if os.path.exists(python_exe):
                                    info = self._get_python_info(python_exe, f'conda env: {env_path}')
                                    if info:
                                        info.environment_type = PythonEnvironmentType.CONDA
                                        if not self._is_duplicate(info):
                                            self.installations.append(info)
            except Exception:
                pass

    def _detect_uv(self):
        """Detect uv virtual environments"""
        uv_path = shutil.which('uv')
        if not uv_path:
            return

        try:
            result = subprocess.run(
                [uv_path, 'venv', '--help'],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                self.suggestions.append(
                    "uv is available - consider using 'uv venv' for faster virtual environment creation"
                )
        except Exception:
            pass

    def _get_python_info(self, python_path: str, source: str = "") -> Optional[PythonInstallation]:
        """Get detailed Python installation information"""
        try:
            result = subprocess.run(
                [python_path, '-c',
                 'import sys, platform; '
                 'print(sys.executable); '
                 'print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"); '
                 'print(platform.architecture()[0]); '
                 'print(sys.prefix)'],
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )

            if result.returncode != 0:
                return None

            lines = result.stdout.strip().split('\n')
            if len(lines) < 4:
                return None

            executable = lines[0]
            version = lines[1]
            architecture = lines[2]
            prefix = lines[3]

            version_parts = version.split('.')
            version_tuple = (
                int(version_parts[0]),
                int(version_parts[1]) if len(version_parts) > 1 else 0,
                int(version_parts[2]) if len(version_parts) > 2 else 0
            )

            is_64bit = '64' in architecture

            env_type = self._detect_environment_type(prefix)

            pip_info = self._get_pip_info(python_path)

            return PythonInstallation(
                path=prefix,
                version=version,
                version_tuple=version_tuple,
                executable=executable,
                is_64bit=is_64bit,
                environment_type=env_type,
                pip_available=pip_info[0],
                pip_version=pip_info[1]
            )

        except Exception:
            return None

    def _create_installation_from_path(self, path: str, version: str) -> Optional[PythonInstallation]:
        """Create PythonInstallation from path and version"""
        if not os.path.exists(path):
            return None

        version_parts = version.split('.')
        version_tuple = (
            int(version_parts[0]),
            int(version_parts[1]) if len(version_parts) > 1 else 0,
            int(version_parts[2]) if len(version_parts) > 2 else 0
        )

        return PythonInstallation(
            path=os.path.dirname(path),
            version=version,
            version_tuple=version_tuple,
            executable=path,
            is_64bit=True,
            environment_type=PythonEnvironmentType.SYSTEM,
            pip_available=False,
            pip_version=None
        )

    def _detect_environment_type(self, prefix: str) -> PythonEnvironmentType:
        """Detect the type of Python environment"""
        if sys.platform == 'win32':
            conda_meta = os.path.join(prefix, 'conda-meta')
            if os.path.exists(conda_meta):
                return PythonEnvironmentType.CONDA

            venvScripts = os.path.join(prefix, 'Scripts')
            if os.path.exists(venvScripts):
                activate = os.path.join(venvScripts, 'activate.bat')
                if os.path.exists(activate):
                    return PythonEnvironmentType.VIRTUALENV

        else:
            if os.path.exists(os.path.join(prefix, 'conda-meta')):
                return PythonEnvironmentType.CONDA

            venv_bin = os.path.join(prefix, 'bin')
            if os.path.exists(venv_bin):
                activate = os.path.join(venv_bin, 'activate')
                if os.path.exists(activate):
                    return PythonEnvironmentType.VIRTUALENV

        pyproject_toml = os.path.join(prefix, 'pyproject.toml')
        if os.path.exists(pyproject_toml):
            return PythonEnvironmentType.POETRY

        return PythonEnvironmentType.SYSTEM

    def _get_pip_info(self, python_path: str) -> Tuple[bool, Optional[str]]:
        """Check if pip is available and get its version"""
        try:
            result = subprocess.run(
                [python_path, '-m', 'pip', '--version'],
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )

            if result.returncode == 0:
                version = result.stdout.strip().split()[1] if result.stdout else None
                return True, version
        except Exception:
            pass

        return False, None

    def _is_duplicate(self, installation: PythonInstallation) -> bool:
        """Check if installation is a duplicate"""
        for existing in self.installations:
            if existing.executable.lower() == installation.executable.lower():
                return True

            if existing.version_tuple == installation.version_tuple:
                if os.path.dirname(existing.executable).lower() == os.path.dirname(installation.executable).lower():
                    return True

        return False

    def _analyze_issues(self):
        """Analyze detected installations for issues"""
        if not self.installations:
            self.issues.append("No Python installation found on this system")
            self.suggestions.append(
                "Install Python from https://www.python.org/downloads/ or use Microsoft Store"
            )
            return

        has_modern = any(
            inst.version_tuple >= self.MIN_PYTHON_VERSION
            for inst in self.installations
        )

        if not has_modern:
            self.issues.append(
                f"No Python {self.MIN_PYTHON_VERSION[0]}.{self.MIN_PYTHON_VERSION[1]}+ installation found"
            )
            self.suggestions.append(
                f"Please upgrade to Python {self.MIN_PYTHON_VERSION[0]}.{self.MIN_PYTHON_VERSION[1]} or higher"
            )

        has_pip = any(inst.pip_available for inst in self.installations)

        if not has_pip:
            self.issues.append("pip is not available in any Python installation")
            self.suggestions.append(
                "Run 'python -m ensurepip' or 'python -m pip' to install pip"
            )

    def _get_recommended_installation(self) -> Optional[PythonInstallation]:
        """Get the recommended Python installation"""
        if not self.installations:
            return None

        valid_installations = [
            inst for inst in self.installations
            if inst.version_tuple >= self.MIN_PYTHON_VERSION
            and inst.pip_available
        ]

        if not valid_installations:
            return None

        return max(valid_installations, key=lambda x: x.version_tuple)


class PythonEnvironmentSetup:
    """Setup and configure Python environment"""

    def __init__(self):
        self.detector = PythonEnvironmentDetector()

    def check_and_suggest(self) -> EnvironmentCheckResult:
        """Check environment and return suggestions"""
        return self.detector.detect_all()

    def install_pip(self, python_path: str) -> Tuple[bool, str]:
        """Install pip if not available"""
        try:
            result = subprocess.run(
                [python_path, '-m', 'ensurepip', '--upgrade'],
                capture_output=True,
                text=True,
                timeout=120,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )

            if result.returncode == 0:
                return True, "pip installed successfully"

            if 'already' in result.stdout.lower() or 'already' in result.stderr.lower():
                return True, "pip is already installed"

            return False, f"Failed to install pip: {result.stderr}"

        except Exception as e:
            return False, f"Error installing pip: {str(e)}"

    def upgrade_pip(self, python_path: str) -> Tuple[bool, str]:
        """Upgrade pip to latest version"""
        try:
            result = subprocess.run(
                [python_path, '-m', 'pip', 'install', '--upgrade', 'pip'],
                capture_output=True,
                text=True,
                timeout=120,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )

            if result.returncode == 0:
                return True, "pip upgraded successfully"

            return False, f"Failed to upgrade pip: {result.stderr}"

        except Exception as e:
            return False, f"Error upgrading pip: {str(e)}"

    def create_venv(self, path: str, python_path: Optional[str] = None) -> Tuple[bool, str]:
        """Create a virtual environment"""
        if python_path is None:
            python_path = sys.executable

        try:
            result = subprocess.run(
                [python_path, '-m', 'venv', path],
                capture_output=True,
                text=True,
                timeout=60,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )

            if result.returncode == 0:
                return True, f"Virtual environment created at {path}"

            return False, f"Failed to create venv: {result.stderr}"

        except Exception as e:
            return False, f"Error creating venv: {str(e)}"

    def get_pip_install_command(self, python_path: str) -> List[str]:
        """Get the appropriate pip install command with flags"""
        base_cmd = [python_path, '-m', 'pip', 'install']

        if sys.platform == 'win32':
            try:
                result = subprocess.run(
                    [python_path, '-m', 'pip', 'install', '--dry-run', 'click'],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )

                if 'externally-managed-environment' in result.stderr:
                    base_cmd.append('--break-system-packages')
            except Exception:
                pass

        return base_cmd


def get_environment_checker() -> PythonEnvironmentSetup:
    """Get a Python environment checker instance"""
    return PythonEnvironmentSetup()


if __name__ == '__main__':
    checker = PythonEnvironmentSetup()
    result = checker.check_and_suggest()

    print(f"Found {len(result.python_installations)} Python installation(s):")
    print()

    for inst in result.python_installations:
        print(f"  - {inst.executable}")
        print(f"    Version: {inst.version}")
        print(f"    Type: {inst.environment_type.value}")
        print(f"    pip: {'Yes' if inst.pip_available else 'No'} ({inst.pip_version or 'N/A'})")
        print()

    if result.issues:
        print("Issues found:")
        for issue in result.issues:
            print(f"  - {issue}")
        print()

    if result.suggestions:
        print("Suggestions:")
        for suggestion in result.suggestions:
            print(f"  - {suggestion}")
        print()

    if result.recommended_installation:
        print(f"Recommended: {result.recommended_installation.executable}")
