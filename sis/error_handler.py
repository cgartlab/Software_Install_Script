#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Error Handling and Logging Module
Provides comprehensive error capture, logging, and recovery mechanisms
"""

import os
import sys
import traceback
import json
import time
import functools
import threading
from typing import Dict, List, Optional, Any, Callable, TypeVar, ParamSpec
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from enum import Enum
from contextlib import contextmanager
import queue

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box

console = Console()

P = ParamSpec('P')
T = TypeVar('T')


class ErrorSeverity(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    NETWORK = "network"
    PERMISSION = "permission"
    DEPENDENCY = "dependency"
    INSTALLATION = "installation"
    CONFIGURATION = "configuration"
    SYSTEM = "system"
    USER_INPUT = "user_input"
    UNKNOWN = "unknown"


@dataclass
class ErrorContext:
    timestamp: str
    operation: str
    details: Dict[str, Any] = field(default_factory=dict)
    stack_trace: Optional[str] = None
    suggestions: List[str] = field(default_factory=list)


@dataclass
class InstallationError:
    error_id: str
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    context: ErrorContext
    recoverable: bool = True
    retry_count: int = 0
    max_retries: int = 3


class Logger:
    """Enhanced logging system with file and console output"""
    
    LOG_DIR = Path.home() / '.sis' / 'logs'
    MAX_LOG_SIZE = 10 * 1024 * 1024
    MAX_LOG_FILES = 10
    
    def __init__(self, name: str = "sis"):
        self.name = name
        self._ensure_log_dir()
        self._log_queue: queue.Queue = queue.Queue()
        self._stop_event = threading.Event()
        self._writer_thread: Optional[threading.Thread] = None
        self._start_async_writer()
    
    def _ensure_log_dir(self):
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    def _start_async_writer(self):
        self._writer_thread = threading.Thread(
            target=self._async_log_writer,
            daemon=True
        )
        self._writer_thread.start()
    
    def _async_log_writer(self):
        while not self._stop_event.is_set():
            try:
                entry = self._log_queue.get(timeout=1.0)
                if entry:
                    self._write_to_file(entry)
            except queue.Empty:
                continue
            except Exception:
                pass
    
    def _get_log_file(self) -> Path:
        date_str = datetime.now().strftime('%Y-%m-%d')
        return self.LOG_DIR / f"{self.name}_{date_str}.log"
    
    def _rotate_logs(self):
        log_files = sorted(
            self.LOG_DIR.glob(f"{self.name}_*.log"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        while len(log_files) > self.MAX_LOG_FILES:
            log_files.pop().unlink()
    
    def _write_to_file(self, entry: str):
        log_file = self._get_log_file()
        
        try:
            if log_file.exists() and log_file.stat().st_size > self.MAX_LOG_SIZE:
                self._rotate_logs()
            
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(entry + '\n')
        except Exception:
            pass
    
    def _format_entry(
        self,
        level: str,
        message: str,
        details: Optional[Dict] = None
    ) -> str:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        entry = f"[{timestamp}] [{level.upper()}] {message}"
        
        if details:
            entry += f" | {json.dumps(details, ensure_ascii=False)}"
        
        return entry
    
    def debug(self, message: str, details: Optional[Dict] = None):
        entry = self._format_entry('DEBUG', message, details)
        self._log_queue.put(entry)
    
    def info(self, message: str, details: Optional[Dict] = None):
        entry = self._format_entry('INFO', message, details)
        self._log_queue.put(entry)
    
    def warning(self, message: str, details: Optional[Dict] = None):
        entry = self._format_entry('WARNING', message, details)
        self._log_queue.put(entry)
    
    def error(self, message: str, details: Optional[Dict] = None):
        entry = self._format_entry('ERROR', message, details)
        self._log_queue.put(entry)
    
    def critical(self, message: str, details: Optional[Dict] = None):
        entry = self._format_entry('CRITICAL', message, details)
        self._log_queue.put(entry)
    
    def exception(
        self,
        message: str,
        exc: Optional[Exception] = None,
        details: Optional[Dict] = None
    ):
        exc_info = exc or sys.exc_info()[1]
        stack_trace = traceback.format_exc() if exc_info else ""
        
        all_details = details or {}
        if exc_info:
            all_details['exception_type'] = type(exc_info).__name__
            all_details['exception_message'] = str(exc_info)
        
        entry = self._format_entry('ERROR', message, all_details)
        if stack_trace:
            entry += f"\n{stack_trace}"
        
        self._log_queue.put(entry)
    
    def stop(self):
        self._stop_event.set()
        if self._writer_thread:
            self._writer_thread.join(timeout=5.0)


class ErrorManager:
    """Centralized error management and recovery"""
    
    ERROR_SOLUTIONS: Dict[ErrorCategory, Dict[str, List[str]]] = {
        ErrorCategory.NETWORK: {
            "connection_refused": [
                "Check your internet connection",
                "Verify firewall settings",
                "Try using a VPN or proxy",
                "Check if the server is accessible"
            ],
            "timeout": [
                "Check your network speed",
                "Try again later",
                "Use a mirror source if available"
            ],
            "ssl_error": [
                "Update your system certificates",
                "Check system time and date",
                "Disable SSL verification temporarily (not recommended)"
            ],
            "404": [
                "The requested resource was not found",
                "Check if the URL is correct",
                "Try using a mirror source",
                "The package may have been removed or renamed"
            ]
        },
        ErrorCategory.PERMISSION: {
            "access_denied": [
                "Run the application as administrator",
                "Check file/folder permissions",
                "Disable antivirus temporarily"
            ],
            "write_protected": [
                "Run as administrator",
                "Check if the file is in use",
                "Verify disk is not write-protected"
            ]
        },
        ErrorCategory.DEPENDENCY: {
            "missing_dependency": [
                "Install the required dependency",
                "Run: pip install <package>",
                "Check requirements.txt"
            ],
            "version_conflict": [
                "Update the conflicting package",
                "Use a virtual environment",
                "Check compatibility requirements"
            ]
        },
        ErrorCategory.INSTALLATION: {
            "install_failed": [
                "Check error message for details",
                "Try installing manually",
                "Check available disk space",
                "Verify package source"
            ],
            "already_installed": [
                "The software is already installed",
                "Use --force to reinstall",
                "Update instead of install"
            ]
        },
        ErrorCategory.CONFIGURATION: {
            "invalid_config": [
                "Check configuration file format",
                "Reset to default configuration",
                "Verify all required fields are present"
            ],
            "missing_config": [
                "Create configuration file",
                "Run setup wizard",
                "Use default configuration"
            ]
        },
        ErrorCategory.SYSTEM: {
            "insufficient_memory": [
                "Close other applications",
                "Free up disk space",
                "Increase virtual memory"
            ],
            "unsupported_os": [
                "Check system requirements",
                "Use a supported operating system"
            ]
        },
        ErrorCategory.USER_INPUT: {
            "invalid_input": [
                "Check input format",
                "Refer to documentation",
                "Use suggested values"
            ]
        },
        ErrorCategory.UNKNOWN: {
            "unknown": [
                "Check error details",
                "Search for the error message online",
                "Contact support"
            ]
        }
    }
    
    def __init__(self, logger: Optional[Logger] = None):
        self.logger = logger or Logger()
        self.errors: List[InstallationError] = []
        self._error_handlers: Dict[ErrorCategory, Callable] = {}
        self._recovery_strategies: Dict[str, Callable] = {}
    
    def register_handler(self, category: ErrorCategory, handler: Callable):
        self._error_handlers[category] = handler
    
    def register_recovery_strategy(self, error_type: str, strategy: Callable):
        self._recovery_strategies[error_type] = strategy
    
    def categorize_error(self, error: Exception) -> ErrorCategory:
        error_str = str(error).lower()
        error_type = type(error).__name__.lower()
        
        network_indicators = [
            'connection', 'network', 'timeout', 'socket', 'ssl',
            'http', 'url', 'download', 'fetch', '404', '403', '500'
        ]
        if any(ind in error_str or ind in error_type for ind in network_indicators):
            return ErrorCategory.NETWORK
        
        permission_indicators = [
            'permission', 'access', 'denied', 'unauthorized', 'forbidden',
            'privilege', 'admin', 'elevated'
        ]
        if any(ind in error_str or ind in error_type for ind in permission_indicators):
            return ErrorCategory.PERMISSION
        
        dependency_indicators = [
            'import', 'module', 'package', 'dependency', 'not found',
            'missing', 'no module'
        ]
        if any(ind in error_str or ind in error_type for ind in dependency_indicators):
            return ErrorCategory.DEPENDENCY
        
        install_indicators = [
            'install', 'setup', 'deploy', 'package', 'winget', 'brew',
            'already installed'
        ]
        if any(ind in error_str or ind in error_type for ind in install_indicators):
            return ErrorCategory.INSTALLATION
        
        config_indicators = [
            'config', 'setting', 'yaml', 'json', 'parse', 'syntax',
            'invalid', 'missing'
        ]
        if any(ind in error_str or ind in error_type for ind in config_indicators):
            return ErrorCategory.CONFIGURATION
        
        system_indicators = [
            'memory', 'disk', 'space', 'os', 'system', 'platform',
            'unsupported'
        ]
        if any(ind in error_str or ind in error_type for ind in system_indicators):
            return ErrorCategory.SYSTEM
        
        return ErrorCategory.UNKNOWN
    
    def get_suggestions(self, category: ErrorCategory, error_message: str) -> List[str]:
        error_lower = error_message.lower()
        
        solutions = self.ERROR_SOLUTIONS.get(category, {})
        
        for key, suggestions in solutions.items():
            if key in error_lower:
                return suggestions
        
        return solutions.get('unknown', [
            "Check the error message for details",
            "Try again or contact support"
        ])
    
    def create_error(
        self,
        error: Exception,
        operation: str,
        details: Optional[Dict] = None,
        recoverable: bool = True
    ) -> InstallationError:
        category = self.categorize_error(error)
        suggestions = self.get_suggestions(category, str(error))
        
        context = ErrorContext(
            timestamp=datetime.now().isoformat(),
            operation=operation,
            details=details or {},
            stack_trace=traceback.format_exc(),
            suggestions=suggestions
        )
        
        error_id = f"{category.value}_{int(time.time() * 1000)}"
        
        severity = ErrorSeverity.ERROR
        if category == ErrorCategory.NETWORK:
            severity = ErrorSeverity.WARNING
        elif category == ErrorCategory.PERMISSION:
            severity = ErrorSeverity.ERROR
        elif category == ErrorCategory.SYSTEM:
            severity = ErrorSeverity.CRITICAL
        
        return InstallationError(
            error_id=error_id,
            category=category,
            severity=severity,
            message=str(error),
            context=context,
            recoverable=recoverable
        )
    
    def handle_error(
        self,
        error: InstallationError,
        auto_recover: bool = True
    ) -> bool:
        self.errors.append(error)
        
        self.logger.error(
            error.message,
            {
                'error_id': error.error_id,
                'category': error.category.value,
                'severity': error.severity.value,
                'operation': error.context.operation,
                'recoverable': error.recoverable
            }
        )
        
        if auto_recover and error.recoverable:
            return self._attempt_recovery(error)
        
        return False
    
    def _attempt_recovery(self, error: InstallationError) -> bool:
        if error.retry_count >= error.max_retries:
            return False
        
        error.retry_count += 1
        
        handler = self._error_handlers.get(error.category)
        if handler:
            try:
                return handler(error)
            except Exception as e:
                self.logger.exception("Recovery handler failed", e)
                return False
        
        return False
    
    def display_error(self, error: InstallationError, console: Console):
        severity_colors = {
            ErrorSeverity.DEBUG: "dim",
            ErrorSeverity.INFO: "blue",
            ErrorSeverity.WARNING: "yellow",
            ErrorSeverity.ERROR: "red",
            ErrorSeverity.CRITICAL: "bold red"
        }
        
        color = severity_colors.get(error.severity, "white")
        
        content = Text()
        content.append(f"Error ID: ", style="dim")
        content.append(f"{error.error_id}\n", style="cyan")
        content.append(f"Category: ", style="dim")
        content.append(f"{error.category.value}\n", style="yellow")
        content.append(f"Message: ", style="dim")
        content.append(f"{error.message}\n", style=color)
        
        if error.context.details:
            content.append("\nDetails:\n", style="dim")
            for key, value in error.context.details.items():
                content.append(f"  • {key}: ", style="dim")
                content.append(f"{value}\n", style="white")
        
        if error.context.suggestions:
            content.append("\nSuggestions:\n", style="green")
            for suggestion in error.context.suggestions:
                content.append(f"  → {suggestion}\n", style="white")
        
        panel = Panel(
            content,
            title=f"[{color}]Error Report[/{color}]",
            border_style=color,
            box=box.ROUNDED
        )
        
        console.print(panel)
    
    def get_error_summary(self) -> Dict[str, Any]:
        if not self.errors:
            return {'total': 0, 'by_category': {}, 'by_severity': {}}
        
        by_category: Dict[str, int] = {}
        by_severity: Dict[str, int] = {}
        
        for error in self.errors:
            cat = error.category.value
            sev = error.severity.value
            by_category[cat] = by_category.get(cat, 0) + 1
            by_severity[sev] = by_severity.get(sev, 0) + 1
        
        return {
            'total': len(self.errors),
            'by_category': by_category,
            'by_severity': by_severity,
            'recoverable': sum(1 for e in self.errors if e.recoverable),
            'recovered': sum(1 for e in self.errors if e.retry_count > 0)
        }


def error_handler(
    operation: str,
    recoverable: bool = True,
    reraise: bool = False,
    default_return: Any = None
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator for automatic error handling"""
    
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            manager = get_error_manager()
            
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error = manager.create_error(
                    e,
                    operation,
                    details={'function': func.__name__, 'args': str(args)[:200]},
                    recoverable=recoverable
                )
                
                manager.handle_error(error)
                
                if reraise:
                    raise
                
                return default_return
        
        return wrapper
    
    return decorator


@contextmanager
def error_context(
    operation: str,
    recoverable: bool = True,
    logger: Optional[Logger] = None
):
    """Context manager for error handling"""
    manager = get_error_manager()
    log = logger or get_logger()
    
    try:
        log.debug(f"Starting operation: {operation}")
        yield
        log.debug(f"Completed operation: {operation}")
    except Exception as e:
        error = manager.create_error(
            e,
            operation,
            recoverable=recoverable
        )
        manager.handle_error(error)
        raise


_logger_instance: Optional[Logger] = None
_error_manager_instance: Optional[ErrorManager] = None


def get_logger() -> Logger:
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = Logger()
    return _logger_instance


def get_error_manager() -> ErrorManager:
    global _error_manager_instance
    if _error_manager_instance is None:
        _error_manager_instance = ErrorManager(get_logger())
    return _error_manager_instance


def display_error_table(errors: List[InstallationError], console: Console):
    if not errors:
        console.print("[green]No errors recorded[/green]")
        return
    
    table = Table(
        title="Error Summary",
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
        box=box.ROUNDED
    )
    
    table.add_column("ID", style="dim", width=20)
    table.add_column("Category", style="yellow", width=12)
    table.add_column("Severity", justify="center", width=10)
    table.add_column("Message", style="white")
    table.add_column("Recoverable", justify="center", width=12)
    
    for error in errors:
        severity_color = {
            ErrorSeverity.DEBUG: "dim",
            ErrorSeverity.INFO: "blue",
            ErrorSeverity.WARNING: "yellow",
            ErrorSeverity.ERROR: "red",
            ErrorSeverity.CRITICAL: "bold red"
        }.get(error.severity, "white")
        
        table.add_row(
            error.error_id[:20],
            error.category.value,
            f"[{severity_color}]{error.severity.value}[/{severity_color}]",
            error.message[:50] + "..." if len(error.message) > 50 else error.message,
            "✓" if error.recoverable else "✗"
        )
    
    console.print(table)
