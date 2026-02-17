#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Graphical User Interface Module
Provides an enhanced TUI with step-by-step guidance and bilingual support
"""

import os
import sys
import time
import threading
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TaskProgressColumn
from rich.align import Align
from rich import box
from rich.prompt import Prompt, Confirm
from rich.live import Live
import questionary
from questionary import Style

from sis.i18n import t, get_i18n, LANG_EN, LANG_ZH
from sis.ui import Colors, Icons, get_ui
from sis.env_check import EnvironmentChecker, display_check_results, run_pre_install_check
from sis.error_handler import get_error_manager, get_logger, display_error_table
from sis.env_manager import get_env_manager, display_env_table
from sis.sandbox_handler import get_sandbox_detector, get_sandbox_handler, display_sandbox_info
from sis.batch_installer import get_batch_installer, display_install_progress, SoftwarePackage, InstallPriority

console = Console()


class WizardStep(Enum):
    WELCOME = 0
    LANGUAGE = 1
    ENVIRONMENT_CHECK = 2
    SANDBOX_CHECK = 3
    SOFTWARE_SELECTION = 4
    INSTALLATION = 5
    CONFIGURATION = 6
    COMPLETION = 7


@dataclass
class WizardState:
    current_step: WizardStep = WizardStep.WELCOME
    language: str = LANG_EN
    env_check_passed: bool = False
    sandbox_detected: bool = False
    selected_packages: List[SoftwarePackage] = field(default_factory=list)
    install_parallel: bool = True
    errors: List[Any] = field(default_factory=list)


custom_style = Style([
    ('qmark', 'fg:cyan bold'),
    ('question', 'fg:white bold'),
    ('answer', 'fg:cyan bold'),
    ('pointer', 'fg:cyan bold'),
    ('highlighted', 'fg:cyan bold'),
    ('selected', 'fg:green'),
    ('separator', 'fg:cyan'),
    ('instruction', 'fg:gray'),
    ('text', 'fg:white'),
])


class GuidedWizard:
    """Step-by-step guided installation wizard"""
    
    GUIDE_TEXT = {
        LANG_EN: {
            'welcome': """
Welcome to SwiftInstall!

This wizard will guide you through the software installation process.
You can navigate using arrow keys and Enter to select.

Let's start by checking your system environment.
""",
            'language_select': 'Select your preferred language:',
            'env_check_title': 'System Environment Check',
            'env_check_desc': 'Checking your system for compatibility...',
            'env_check_passed': 'All checks passed! Your system is ready.',
            'env_check_failed': 'Some issues were detected. Please review:',
            'sandbox_title': 'Environment Analysis',
            'sandbox_desc': 'Analyzing your execution environment...',
            'sandbox_warning': 'Restricted environment detected. Some features may be limited.',
            'software_title': 'Software Selection',
            'software_desc': 'Select the software you want to install:',
            'software_categories': {
                'Development': 'Development tools and SDKs',
                'Utilities': 'System utilities and tools',
                'Design': 'Design and creative tools',
                'Social': 'Communication and social media',
                'Other': 'Other applications'
            },
            'install_title': 'Installation',
            'install_desc': 'Installing selected software...',
            'install_parallel': 'Use parallel installation for faster setup?',
            'install_progress': 'Progress',
            'config_title': 'Configuration',
            'config_desc': 'Configuring environment variables...',
            'complete_title': 'Installation Complete!',
            'complete_desc': 'All selected software has been installed.',
            'complete_summary': 'Summary',
            'next': 'Next',
            'back': 'Back',
            'skip': 'Skip',
            'retry': 'Retry',
            'cancel': 'Cancel',
            'finish': 'Finish',
            'yes': 'Yes',
            'no': 'No',
        },
        LANG_ZH: {
            'welcome': """
欢迎使用 SwiftInstall！

本向导将引导您完成软件安装过程。
您可以使用方向键导航，按 Enter 键选择。

让我们先检查您的系统环境。
""",
            'language_select': '选择您的首选语言：',
            'env_check_title': '系统环境检查',
            'env_check_desc': '正在检查您的系统兼容性...',
            'env_check_passed': '所有检查通过！您的系统已准备就绪。',
            'env_check_failed': '检测到一些问题，请查看：',
            'sandbox_title': '环境分析',
            'sandbox_desc': '正在分析您的执行环境...',
            'sandbox_warning': '检测到受限环境。某些功能可能受限。',
            'software_title': '软件选择',
            'software_desc': '选择您要安装的软件：',
            'software_categories': {
                'Development': '开发工具和 SDK',
                'Utilities': '系统工具和实用程序',
                'Design': '设计和创意工具',
                'Social': '通信和社交媒体',
                'Other': '其他应用程序'
            },
            'install_title': '安装',
            'install_desc': '正在安装选定的软件...',
            'install_parallel': '使用并行安装以加快设置速度？',
            'install_progress': '进度',
            'config_title': '配置',
            'config_desc': '正在配置环境变量...',
            'complete_title': '安装完成！',
            'complete_desc': '所有选定的软件已安装。',
            'complete_summary': '摘要',
            'next': '下一步',
            'back': '上一步',
            'skip': '跳过',
            'retry': '重试',
            'cancel': '取消',
            'finish': '完成',
            'yes': '是',
            'no': '否',
        }
    }
    
    DEFAULT_SOFTWARE = {
        'Development': [
            {'id': 'Git.Git', 'name': 'Git', 'priority': InstallPriority.CRITICAL},
            {'id': 'Microsoft.VisualStudioCode', 'name': 'Visual Studio Code', 'priority': InstallPriority.HIGH},
            {'id': 'Python.Python', 'name': 'Python', 'priority': InstallPriority.HIGH},
            {'id': 'OpenJS.NodeJS', 'name': 'Node.js', 'priority': InstallPriority.NORMAL},
            {'id': 'Microsoft.PowerShell', 'name': 'PowerShell', 'priority': InstallPriority.NORMAL},
        ],
        'Utilities': [
            {'id': '7zip.7zip', 'name': '7-Zip', 'priority': InstallPriority.HIGH},
            {'id': 'Microsoft.PowerToys', 'name': 'PowerToys', 'priority': InstallPriority.NORMAL},
            {'id': 'Voidtools.Everything', 'name': 'Everything', 'priority': InstallPriority.NORMAL},
            {'id': 'Microsoft.WindowsTerminal', 'name': 'Windows Terminal', 'priority': InstallPriority.HIGH},
        ],
        'Design': [
            {'id': 'BlenderFoundation.Blender', 'name': 'Blender', 'priority': InstallPriority.NORMAL},
            {'id': 'KDE.Krita', 'name': 'Krita', 'priority': InstallPriority.NORMAL},
            {'id': 'Figma.Figma', 'name': 'Figma', 'priority': InstallPriority.NORMAL},
        ],
        'Social': [
            {'id': 'Telegram.TelegramDesktop', 'name': 'Telegram', 'priority': InstallPriority.LOW},
            {'id': 'Tencent.WeChat.Universal', 'name': 'WeChat', 'priority': InstallPriority.LOW},
        ],
        'Other': []
    }
    
    def __init__(self):
        self.state = WizardState()
        self.ui = get_ui()
        self.logger = get_logger()
        self.error_manager = get_error_manager()
    
    def _g(self, key: str) -> str:
        return self.GUIDE_TEXT.get(self.state.language, self.GUIDE_TEXT[LANG_EN]).get(key, key)
    
    def run(self):
        while True:
            try:
                if self.state.current_step == WizardStep.WELCOME:
                    self._show_welcome()
                elif self.state.current_step == WizardStep.LANGUAGE:
                    self._select_language()
                elif self.state.current_step == WizardStep.ENVIRONMENT_CHECK:
                    self._check_environment()
                elif self.state.current_step == WizardStep.SANDBOX_CHECK:
                    self._check_sandbox()
                elif self.state.current_step == WizardStep.SOFTWARE_SELECTION:
                    self._select_software()
                elif self.state.current_step == WizardStep.INSTALLATION:
                    self._install_software()
                elif self.state.current_step == WizardStep.CONFIGURATION:
                    self._configure_environment()
                elif self.state.current_step == WizardStep.COMPLETION:
                    self._show_completion()
                    break
            except KeyboardInterrupt:
                if self._confirm_exit():
                    break
                continue
    
    def _show_welcome(self):
        console.clear()
        
        from sis.logo import get_rich_logo
        logo = get_rich_logo("full")
        console.print(logo)
        console.print()
        
        welcome_panel = Panel(
            Text(self._g('welcome')),
            border_style=Colors.PRIMARY,
            box=box.ROUNDED,
            padding=(1, 2)
        )
        console.print(welcome_panel)
        console.print()
        
        Prompt.ask(f"\n[{Colors.PRIMARY}]Press Enter to continue...[/]")
        
        self.state.current_step = WizardStep.LANGUAGE
    
    def _select_language(self):
        console.clear()
        
        console.print(f"\n[bold {Colors.PRIMARY}]{self._g('language_select')}[/]\n")
        
        choices = [
            questionary.Choice("English", value=LANG_EN),
            questionary.Choice("中文", value=LANG_ZH),
        ]
        
        selected = questionary.select(
            "",
            choices=choices,
            style=custom_style,
            use_arrow_keys=True
        ).ask()
        
        if selected:
            self.state.language = selected
            i18n = get_i18n()
            i18n.set_language(selected)
        
        self.state.current_step = WizardStep.ENVIRONMENT_CHECK
    
    def _check_environment(self):
        console.clear()
        
        console.print(f"\n[bold {Colors.PRIMARY}]{self._g('env_check_title')}[/]\n")
        
        with console.status(f"[bold {Colors.PRIMARY}]{self._g('env_check_desc')}[/]", spinner="dots"):
            passed, system_info, results = run_pre_install_check()
        
        display_check_results(results, console)
        
        self.state.env_check_passed = passed
        
        if passed:
            console.print(f"\n[green]{Icons.SUCCESS} {self._g('env_check_passed')}[/]")
            Prompt.ask(f"\n[{Colors.PRIMARY}]Press Enter to continue...[/]")
            self.state.current_step = WizardStep.SANDBOX_CHECK
        else:
            console.print(f"\n[red]{Icons.ERROR} {self._g('env_check_failed')}[/]")
            
            action = questionary.select(
                "",
                choices=[
                    questionary.Choice(self._g('next'), value="next"),
                    questionary.Choice(self._g('retry'), value="retry"),
                    questionary.Choice(self._g('cancel'), value="cancel"),
                ],
                style=custom_style
            ).ask()
            
            if action == "next":
                self.state.current_step = WizardStep.SANDBOX_CHECK
            elif action == "retry":
                pass
            else:
                self.state.current_step = WizardStep.COMPLETION
    
    def _check_sandbox(self):
        console.clear()
        
        console.print(f"\n[bold {Colors.PRIMARY}]{self._g('sandbox_title')}[/]\n")
        
        with console.status(f"[bold {Colors.PRIMARY}]{self._g('sandbox_desc')}[/]", spinner="dots"):
            is_restricted, sandbox_info = get_sandbox_detector().detect(), get_sandbox_detector().detect().detect()
        
        is_restricted = sandbox_info.is_sandbox or sandbox_info.is_container
        self.state.sandbox_detected = is_restricted
        
        display_sandbox_info(sandbox_info, console)
        
        if is_restricted:
            console.print(f"\n[yellow]{Icons.WARNING} {self._g('sandbox_warning')}[/]")
        
        Prompt.ask(f"\n[{Colors.PRIMARY}]Press Enter to continue...[/]")
        
        self.state.current_step = WizardStep.SOFTWARE_SELECTION
    
    def _select_software(self):
        console.clear()
        
        console.print(f"\n[bold {Colors.PRIMARY}]{self._g('software_title')}[/]\n")
        
        categories = self._g('software_categories')
        
        all_packages = []
        
        for category, packages in self.DEFAULT_SOFTWARE.items():
            if not packages:
                continue
            
            console.print(f"\n[cyan]{category}[/] - [dim]{categories.get(category, category)}[/]")
            
            choices = []
            for pkg in packages:
                choices.append(questionary.Choice(
                    f"{pkg['name']}",
                    value=pkg,
                    checked=True
                ))
            
            selected = questionary.checkbox(
                "",
                choices=choices,
                style=custom_style
            ).ask()
            
            if selected:
                for pkg in selected:
                    all_packages.append(SoftwarePackage(
                        id=pkg['id'],
                        name=pkg['name'],
                        category=category,
                        priority=pkg.get('priority', InstallPriority.NORMAL)
                    ))
        
        self.state.selected_packages = all_packages
        
        if not all_packages:
            console.print(f"\n[yellow]No software selected.[/yellow]")
            Prompt.ask(f"\n[{Colors.PRIMARY}]Press Enter to continue...[/]")
            self.state.current_step = WizardStep.COMPLETION
            return
        
        console.print(f"\n[bold {Colors.PRIMARY}]{self._g('install_parallel')}[/]")
        
        parallel = questionary.confirm(
            "",
            default=True,
            style=custom_style
        ).ask()
        
        self.state.install_parallel = parallel if parallel is not None else True
        
        self.state.current_step = WizardStep.INSTALLATION
    
    def _install_software(self):
        console.clear()
        
        console.print(f"\n[bold {Colors.PRIMARY}]{self._g('install_title')}[/]\n")
        
        if not self.state.selected_packages:
            console.print("[yellow]No packages to install.[/yellow]")
            self.state.current_step = WizardStep.COMPLETION
            return
        
        installer = get_batch_installer(max_workers=4 if self.state.install_parallel else 1)
        
        session = installer.install_all(
            self.state.selected_packages,
            parallel=self.state.install_parallel,
            stop_on_error=False
        )
        
        display_install_progress(session, console)
        
        self.state.errors = [
            task for task in session.tasks.values()
            if task.status.value == 'failed'
        ]
        
        Prompt.ask(f"\n[{Colors.PRIMARY}]Press Enter to continue...[/]")
        
        self.state.current_step = WizardStep.CONFIGURATION
    
    def _configure_environment(self):
        console.clear()
        
        console.print(f"\n[bold {Colors.PRIMARY}]{self._g('config_title')}[/]\n")
        
        with console.status(f"[bold {Colors.PRIMARY}]{self._g('config_desc')}[/]", spinner="dots"):
            from sis.env_manager import hot_refresh_environment
            hot_refresh_environment()
            
            env_manager = get_env_manager()
            modified = env_manager.get_modified_vars()
        
        if modified:
            display_env_table(env_manager, console)
        else:
            console.print("[green]No environment modifications needed.[/green]")
        
        Prompt.ask(f"\n[{Colors.PRIMARY}]Press Enter to continue...[/]")
        
        self.state.current_step = WizardStep.COMPLETION
    
    def _show_completion(self):
        console.clear()
        
        from sis.logo import get_rich_logo
        logo = get_rich_logo("compact")
        console.print(logo)
        console.print()
        
        console.print(f"\n[bold {Colors.SUCCESS}]{self._g('complete_title')}[/]\n")
        
        summary_table = Table(
            title=self._g('complete_summary'),
            show_header=True,
            header_style="bold cyan",
            border_style="dim",
            box=box.ROUNDED
        )
        
        summary_table.add_column("Metric", style="white")
        summary_table.add_column("Value", style="cyan", justify="right")
        
        summary_table.add_row("Total Packages", str(len(self.state.selected_packages)))
        summary_table.add_row("Environment Check", "Passed" if self.state.env_check_passed else "Failed")
        summary_table.add_row("Sandbox Detected", "Yes" if self.state.sandbox_detected else "No")
        summary_table.add_row("Errors", str(len(self.state.errors)))
        
        console.print(summary_table)
        
        if self.state.errors:
            console.print(f"\n[yellow]Some packages failed to install. Check logs for details.[/yellow]")
        
        console.print(f"\n[green]{self._g('complete_desc')}[/]")
        
        Prompt.ask(f"\n[{Colors.PRIMARY}]Press Enter to exit...[/]")
    
    def _confirm_exit(self) -> bool:
        console.print(f"\n[yellow]Do you want to exit the wizard?[/yellow]")
        return Confirm.ask("", default=False)


def run_guided_installation():
    wizard = GuidedWizard()
    wizard.run()


class QuickInstall:
    """Quick installation without wizard"""
    
    @staticmethod
    def install_from_list(packages: List[Dict], parallel: bool = True) -> bool:
        software_packages = [
            SoftwarePackage(
                id=p.get('id', p.get('package', '')),
                name=p.get('name', p.get('id', '')),
                category=p.get('category', 'Other'),
                priority=InstallPriority(p.get('priority', 2))
            )
            for p in packages
        ]
        
        installer = get_batch_installer(max_workers=4 if parallel else 1)
        session = installer.install_all(software_packages, parallel=parallel)
        
        display_install_progress(session, console)
        
        return session.failed == 0
    
    @staticmethod
    def install_from_file(file_path: str) -> bool:
        from sis.batch_installer import AutomationScript
        
        packages = AutomationScript.load_config_file(file_path)
        
        installer = get_batch_installer()
        session = installer.install_all(packages)
        
        display_install_progress(session, console)
        
        return session.failed == 0
