#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Installer module for different platforms with enhanced visual feedback
"""

import subprocess
import sys
import os
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TaskProgressColumn
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich import box

from sis.ui import Colors, Icons

console = Console()


class BaseInstaller:
    """Base installer class"""
    
    def __init__(self, config):
        """Initialize installer"""
        self.config = config
    
    def install_all(self):
        """Install all software"""
        pass
    
    def uninstall_all(self):
        """Uninstall all software"""
        pass
    
    def _run_command(self, command, shell=True):
        """Run command and return output"""
        try:
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=True,
                text=True,
                check=False
            )
            return result
        except Exception as e:
            console.print(f"[{Colors.ERROR}]Error running command: {e}[/]")
            return None


class WindowsInstaller(BaseInstaller):
    """Windows installer using winget"""
    
    def __init__(self, config):
        """Initialize Windows installer"""
        super().__init__(config)
        self._check_winget()
    
    def _check_winget(self):
        """Check if winget is available"""
        result = self._run_command('winget --version')
        if result and result.returncode == 0:
            console.print(f"[{Colors.SUCCESS}]{Icons.SUCCESS} Winget found and ready[/]")
        else:
            console.print(f"[{Colors.ERROR}]{Icons.ERROR} Winget not found. Please install Windows Package Manager.[/]")
            sys.exit(1)
    
    def install_all(self):
        """Install all software using winget with enhanced visual feedback"""
        software_list = self.config.get_software_list()
        
        if not software_list:
            console.print(f"[{Colors.WARNING}]{Icons.WARNING} No software to install[/]")
            return
        
        # Create installation summary panel
        summary_text = Text()
        summary_text.append(f"{Icons.PACKAGE} Total packages: ", style=Colors.TEXT)
        summary_text.append(f"{len(software_list)}\n", style=f"bold {Colors.PRIMARY}")
        summary_text.append(f"{Icons.INFO} Platform: ", style=Colors.TEXT)
        summary_text.append("Windows (Winget)\n", style=Colors.SECONDARY)
        
        summary_panel = Panel(
            summary_text,
            title=f"[bold {Colors.PRIMARY}]{Icons.INSTALL} Installation Summary[/bold {Colors.PRIMARY}]",
            border_style=Colors.PRIMARY,
            box=box.ROUNDED,
            padding=(1, 2)
        )
        console.print(summary_panel)
        console.print()
        
        # Installation progress
        success_count = 0
        failed_count = 0
        skipped_count = 0
        
        with Progress(
            SpinnerColumn(style=Colors.PRIMARY),
            TextColumn(f"[bold {Colors.PRIMARY}]{{task.description}}"),
            BarColumn(
                complete_style=Colors.SUCCESS,
                finished_style=Colors.SUCCESS_BRIGHT,
                pulse_style=Colors.PRIMARY
            ),
            TaskProgressColumn(text_format=f"[bold {Colors.TEXT}]{{task.percentage:>3.0f}}%"),
            console=console,
            expand=True
        ) as progress:
            
            overall_task = progress.add_task("Overall progress", total=len(software_list))
            
            for i, software in enumerate(software_list, 1):
                software_id = software.get('id')
                software_name = software.get('name', software_id)
                
                # Update progress description
                progress.update(overall_task, description=f"Installing {software_name} ({i}/{len(software_list)})")
                
                # Show current installation card
                install_card = Panel(
                    f"[{Colors.SECONDARY}]{Icons.DOWNLOAD} {software_name}\n"
                    f"[{Colors.TEXT_DIM}]ID: {software_id}[/]",
                    title=f"[bold {Colors.PRIMARY}]{Icons.RUNNING} Current Installation[/bold {Colors.PRIMARY}]",
                    border_style=Colors.PRIMARY,
                    box=box.ROUNDED,
                    padding=(1, 2)
                )
                console.print(install_card)
                
                # Run winget install command
                command = f'winget install --id "{software_id}" --silent --accept-source-agreements --accept-package-agreements'
                result = self._run_command(command)
                
                if result:
                    if result.returncode == 0:
                        console.print(f"[{Colors.SUCCESS}]{Icons.SUCCESS} {software_name} installed successfully![/]")
                        success_count += 1
                    elif "already installed" in (result.stdout or "").lower() or "already installed" in (result.stderr or "").lower():
                        console.print(f"[{Colors.WARNING}]{Icons.WARNING} {software_name} is already installed[/]")
                        skipped_count += 1
                    else:
                        console.print(f"[{Colors.ERROR}]{Icons.ERROR} {software_name} installation failed[/]")
                        if result.stderr:
                            console.print(f"[dim]{result.stderr[:200]}[/dim]")
                        failed_count += 1
                else:
                    console.print(f"[{Colors.ERROR}]{Icons.ERROR} {software_name} installation failed (no response)[/]")
                    failed_count += 1
                
                console.print()
                progress.update(overall_task, advance=1)
        
        # Show final results
        self._show_results(success_count, failed_count, skipped_count)
    
    def _show_results(self, success: int, failed: int, skipped: int):
        """Show installation results"""
        results_text = Text()
        results_text.append(f"{Icons.SUCCESS} Successful: ", style=Colors.TEXT)
        results_text.append(f"{success}\n", style=f"bold {Colors.SUCCESS}")
        results_text.append(f"{Icons.ERROR} Failed: ", style=Colors.TEXT)
        results_text.append(f"{failed}\n", style=f"bold {Colors.ERROR}")
        results_text.append(f"{Icons.WARNING} Skipped: ", style=Colors.TEXT)
        results_text.append(f"{skipped}", style=f"bold {Colors.WARNING}")
        
        results_panel = Panel(
            results_text,
            title=f"[bold {Colors.PRIMARY}]{Icons.PACKAGE} Installation Results[/bold {Colors.PRIMARY}]",
            border_style=Colors.PRIMARY,
            box=box.ROUNDED,
            padding=(1, 2)
        )
        console.print(results_panel)
        
        if failed == 0:
            console.print(f"\n[bold {Colors.SUCCESS}]{Icons.SUCCESS} All installations completed successfully![/]")
        else:
            console.print(f"\n[bold {Colors.WARNING}]{Icons.WARNING} Installation completed with some issues.[/]")
    
    def uninstall_all(self):
        """Uninstall all software using winget with enhanced visual feedback"""
        software_list = self.config.get_software_list()
        
        if not software_list:
            console.print(f"[{Colors.WARNING}]{Icons.WARNING} No software to uninstall[/]")
            return
        
        # Create uninstallation summary panel
        summary_text = Text()
        summary_text.append(f"{Icons.PACKAGE} Total packages: ", style=Colors.TEXT)
        summary_text.append(f"{len(software_list)}\n", style=f"bold {Colors.PRIMARY}")
        summary_text.append(f"{Icons.INFO} Platform: ", style=Colors.TEXT)
        summary_text.append("Windows (Winget)\n", style=Colors.SECONDARY)
        
        summary_panel = Panel(
            summary_text,
            title=f"[bold {Colors.PRIMARY}]{Icons.UNINSTALL} Uninstallation Summary[/bold {Colors.PRIMARY}]",
            border_style=Colors.PRIMARY,
            box=box.ROUNDED,
            padding=(1, 2)
        )
        console.print(summary_panel)
        console.print()
        
        # Uninstallation progress
        success_count = 0
        failed_count = 0
        skipped_count = 0
        
        with Progress(
            SpinnerColumn(style=Colors.PRIMARY),
            TextColumn(f"[bold {Colors.PRIMARY}]{{task.description}}"),
            BarColumn(
                complete_style=Colors.SUCCESS,
                finished_style=Colors.SUCCESS_BRIGHT,
                pulse_style=Colors.PRIMARY
            ),
            TaskProgressColumn(text_format=f"[bold {Colors.TEXT}]{{task.percentage:>3.0f}}%"),
            console=console,
            expand=True
        ) as progress:
            
            overall_task = progress.add_task("Overall progress", total=len(software_list))
            
            for i, software in enumerate(software_list, 1):
                software_id = software.get('id')
                software_name = software.get('name', software_id)
                
                # Update progress description
                progress.update(overall_task, description=f"Uninstalling {software_name} ({i}/{len(software_list)})")
                
                # Show current uninstallation card
                uninstall_card = Panel(
                    f"[{Colors.SECONDARY}]{Icons.UNINSTALL} {software_name}\n"
                    f"[{Colors.TEXT_DIM}]ID: {software_id}[/]",
                    title=f"[bold {Colors.PRIMARY}]{Icons.RUNNING} Current Uninstallation[/bold {Colors.PRIMARY}]",
                    border_style=Colors.PRIMARY,
                    box=box.ROUNDED,
                    padding=(1, 2)
                )
                console.print(uninstall_card)
                
                # Run winget uninstall command
                command = f'winget uninstall --id "{software_id}" --silent'
                result = self._run_command(command)
                
                if result:
                    if result.returncode == 0:
                        console.print(f"[{Colors.SUCCESS}]{Icons.SUCCESS} {software_name} uninstalled successfully![/]")
                        success_count += 1
                    elif "not installed" in (result.stdout or "").lower() or "not installed" in (result.stderr or "").lower():
                        console.print(f"[{Colors.WARNING}]{Icons.WARNING} {software_name} is not installed[/]")
                        skipped_count += 1
                    else:
                        console.print(f"[{Colors.ERROR}]{Icons.ERROR} {software_name} uninstallation failed[/]")
                        if result.stderr:
                            console.print(f"[dim]{result.stderr[:200]}[/dim]")
                        failed_count += 1
                else:
                    console.print(f"[{Colors.ERROR}]{Icons.ERROR} {software_name} uninstallation failed (no response)[/]")
                    failed_count += 1
                
                console.print()
                progress.update(overall_task, advance=1)
        
        # Show final results
        self._show_uninstall_results(success_count, failed_count, skipped_count)
    
    def _show_uninstall_results(self, success: int, failed: int, skipped: int):
        """Show uninstallation results"""
        results_text = Text()
        results_text.append(f"{Icons.SUCCESS} Successful: ", style=Colors.TEXT)
        results_text.append(f"{success}\n", style=f"bold {Colors.SUCCESS}")
        results_text.append(f"{Icons.ERROR} Failed: ", style=Colors.TEXT)
        results_text.append(f"{failed}\n", style=f"bold {Colors.ERROR}")
        results_text.append(f"{Icons.WARNING} Skipped: ", style=Colors.TEXT)
        results_text.append(f"{skipped}", style=f"bold {Colors.WARNING}")
        
        results_panel = Panel(
            results_text,
            title=f"[bold {Colors.PRIMARY}]{Icons.PACKAGE} Uninstallation Results[/bold {Colors.PRIMARY}]",
            border_style=Colors.PRIMARY,
            box=box.ROUNDED,
            padding=(1, 2)
        )
        console.print(results_panel)
        
        if failed == 0:
            console.print(f"\n[bold {Colors.SUCCESS}]{Icons.SUCCESS} All uninstallations completed successfully![/]")
        else:
            console.print(f"\n[bold {Colors.WARNING}]{Icons.WARNING} Uninstallation completed with some issues.[/]")


class MacOSInstaller(BaseInstaller):
    """macOS installer using homebrew"""
    
    def __init__(self, config):
        """Initialize macOS installer"""
        super().__init__(config)
        self._check_brew()
    
    def _check_brew(self):
        """Check if homebrew is available"""
        result = self._run_command('brew --version')
        if result and result.returncode == 0:
            console.print(f"[{Colors.SUCCESS}]{Icons.SUCCESS} Homebrew found and ready[/]")
        else:
            console.print(f"[{Colors.ERROR}]{Icons.ERROR} Homebrew not found. Please install Homebrew.[/]")
            # Offer to install homebrew
            from rich.prompt import Confirm
            if Confirm.ask(f"[{Colors.PRIMARY}]Do you want to install Homebrew?[/]"):
                self._install_brew()
            else:
                sys.exit(1)
    
    def _install_brew(self):
        """Install homebrew"""
        console.print(f"[{Colors.PRIMARY}]{Icons.DOWNLOAD} Installing Homebrew...[/]")
        command = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
        result = self._run_command(command)
        if result and result.returncode == 0:
            console.print(f"[{Colors.SUCCESS}]{Icons.SUCCESS} Homebrew installed successfully![/]")
        else:
            console.print(f"[{Colors.ERROR}]{Icons.ERROR} Failed to install Homebrew[/]")
            sys.exit(1)
    
    def install_all(self):
        """Install all software using homebrew with enhanced visual feedback"""
        software_list = self.config.get_software_list()
        
        if not software_list:
            console.print(f"[{Colors.WARNING}]{Icons.WARNING} No software to install[/]")
            return
        
        # Update homebrew first
        console.print(f"[{Colors.PRIMARY}]{Icons.DOWNLOAD} Updating Homebrew...[/]")
        with console.status(f"[bold {Colors.PRIMARY}]Running brew update...", spinner="dots"):
            self._run_command('brew update')
        console.print(f"[{Colors.SUCCESS}]{Icons.SUCCESS} Homebrew updated[/]")
        console.print()
        
        # Create installation summary panel
        summary_text = Text()
        summary_text.append(f"{Icons.PACKAGE} Total packages: ", style=Colors.TEXT)
        summary_text.append(f"{len(software_list)}\n", style=f"bold {Colors.PRIMARY}")
        summary_text.append(f"{Icons.INFO} Platform: ", style=Colors.TEXT)
        summary_text.append("macOS (Homebrew)\n", style=Colors.SECONDARY)
        
        summary_panel = Panel(
            summary_text,
            title=f"[bold {Colors.PRIMARY}]{Icons.INSTALL} Installation Summary[/bold {Colors.PRIMARY}]",
            border_style=Colors.PRIMARY,
            box=box.ROUNDED,
            padding=(1, 2)
        )
        console.print(summary_panel)
        console.print()
        
        # Installation progress
        success_count = 0
        failed_count = 0
        skipped_count = 0
        
        with Progress(
            SpinnerColumn(style=Colors.PRIMARY),
            TextColumn(f"[bold {Colors.PRIMARY}]{{task.description}}"),
            BarColumn(
                complete_style=Colors.SUCCESS,
                finished_style=Colors.SUCCESS_BRIGHT,
                pulse_style=Colors.PRIMARY
            ),
            TaskProgressColumn(text_format=f"[bold {Colors.TEXT}]{{task.percentage:>3.0f}}%"),
            console=console,
            expand=True
        ) as progress:
            
            overall_task = progress.add_task("Overall progress", total=len(software_list))
            
            for i, software in enumerate(software_list, 1):
                package_name = software.get('package')
                software_name = software.get('name', package_name)
                
                # Update progress description
                progress.update(overall_task, description=f"Installing {software_name} ({i}/{len(software_list)})")
                
                # Check if already installed
                check_command = f'brew list --versions {package_name}'
                with console.status(f"[bold {Colors.PRIMARY}]Checking {software_name}...", spinner="dots"):
                    check_result = self._run_command(check_command)
                
                if check_result and check_result.returncode == 0:
                    console.print(f"[{Colors.WARNING}]{Icons.WARNING} {software_name} is already installed[/]")
                    skipped_count += 1
                    progress.update(overall_task, advance=1)
                    continue
                
                # Show current installation card
                install_card = Panel(
                    f"[{Colors.SECONDARY}]{Icons.DOWNLOAD} {software_name}\n"
                    f"[{Colors.TEXT_DIM}]Package: {package_name}[/]",
                    title=f"[bold {Colors.PRIMARY}]{Icons.RUNNING} Current Installation[/bold {Colors.PRIMARY}]",
                    border_style=Colors.PRIMARY,
                    box=box.ROUNDED,
                    padding=(1, 2)
                )
                console.print(install_card)
                
                # Run brew install command
                install_command = f'brew install {package_name}'
                result = self._run_command(install_command)
                
                if result:
                    if result.returncode == 0:
                        console.print(f"[{Colors.SUCCESS}]{Icons.SUCCESS} {software_name} installed successfully![/]")
                        success_count += 1
                    else:
                        console.print(f"[{Colors.ERROR}]{Icons.ERROR} {software_name} installation failed[/]")
                        if result.stderr:
                            console.print(f"[dim]{result.stderr[:200]}[/dim]")
                        failed_count += 1
                else:
                    console.print(f"[{Colors.ERROR}]{Icons.ERROR} {software_name} installation failed (no response)[/]")
                    failed_count += 1
                
                console.print()
                progress.update(overall_task, advance=1)
        
        # Run brew cleanup
        console.print(f"[{Colors.PRIMARY}]{Icons.RUNNING} Running brew cleanup...[/]")
        with console.status(f"[bold {Colors.PRIMARY}]Cleaning up...", spinner="dots"):
            self._run_command('brew cleanup')
        console.print(f"[{Colors.SUCCESS}]{Icons.SUCCESS} Cleanup complete[/]")
        
        # Show final results
        self._show_results(success_count, failed_count, skipped_count)
    
    def _show_results(self, success: int, failed: int, skipped: int):
        """Show installation results"""
        results_text = Text()
        results_text.append(f"{Icons.SUCCESS} Successful: ", style=Colors.TEXT)
        results_text.append(f"{success}\n", style=f"bold {Colors.SUCCESS}")
        results_text.append(f"{Icons.ERROR} Failed: ", style=Colors.TEXT)
        results_text.append(f"{failed}\n", style=f"bold {Colors.ERROR}")
        results_text.append(f"{Icons.WARNING} Skipped: ", style=Colors.TEXT)
        results_text.append(f"{skipped}", style=f"bold {Colors.WARNING}")
        
        results_panel = Panel(
            results_text,
            title=f"[bold {Colors.PRIMARY}]{Icons.PACKAGE} Installation Results[/bold {Colors.PRIMARY}]",
            border_style=Colors.PRIMARY,
            box=box.ROUNDED,
            padding=(1, 2)
        )
        console.print(results_panel)
        
        if failed == 0:
            console.print(f"\n[bold {Colors.SUCCESS}]{Icons.SUCCESS} All installations completed successfully![/]")
        else:
            console.print(f"\n[bold {Colors.WARNING}]{Icons.WARNING} Installation completed with some issues.[/]")
    
    def uninstall_all(self):
        """Uninstall all software using homebrew with enhanced visual feedback"""
        software_list = self.config.get_software_list()
        
        if not software_list:
            console.print(f"[{Colors.WARNING}]{Icons.WARNING} No software to uninstall[/]")
            return
        
        # Create uninstallation summary panel
        summary_text = Text()
        summary_text.append(f"{Icons.PACKAGE} Total packages: ", style=Colors.TEXT)
        summary_text.append(f"{len(software_list)}\n", style=f"bold {Colors.PRIMARY}")
        summary_text.append(f"{Icons.INFO} Platform: ", style=Colors.TEXT)
        summary_text.append("macOS (Homebrew)\n", style=Colors.SECONDARY)
        
        summary_panel = Panel(
            summary_text,
            title=f"[bold {Colors.PRIMARY}]{Icons.UNINSTALL} Uninstallation Summary[/bold {Colors.PRIMARY}]",
            border_style=Colors.PRIMARY,
            box=box.ROUNDED,
            padding=(1, 2)
        )
        console.print(summary_panel)
        console.print()
        
        # Uninstallation progress
        success_count = 0
        failed_count = 0
        skipped_count = 0
        
        with Progress(
            SpinnerColumn(style=Colors.PRIMARY),
            TextColumn(f"[bold {Colors.PRIMARY}]{{task.description}}"),
            BarColumn(
                complete_style=Colors.SUCCESS,
                finished_style=Colors.SUCCESS_BRIGHT,
                pulse_style=Colors.PRIMARY
            ),
            TaskProgressColumn(text_format=f"[bold {Colors.TEXT}]{{task.percentage:>3.0f}}%"),
            console=console,
            expand=True
        ) as progress:
            
            overall_task = progress.add_task("Overall progress", total=len(software_list))
            
            for i, software in enumerate(software_list, 1):
                package_name = software.get('package')
                software_name = software.get('name', package_name)
                
                # Update progress description
                progress.update(overall_task, description=f"Uninstalling {software_name} ({i}/{len(software_list)})")
                
                # Check if not installed
                check_command = f'brew list --versions {package_name}'
                with console.status(f"[bold {Colors.PRIMARY}]Checking {software_name}...", spinner="dots"):
                    check_result = self._run_command(check_command)
                
                if not (check_result and check_result.returncode == 0):
                    console.print(f"[{Colors.WARNING}]{Icons.WARNING} {software_name} is not installed[/]")
                    skipped_count += 1
                    progress.update(overall_task, advance=1)
                    continue
                
                # Show current uninstallation card
                uninstall_card = Panel(
                    f"[{Colors.SECONDARY}]{Icons.UNINSTALL} {software_name}\n"
                    f"[{Colors.TEXT_DIM}]Package: {package_name}[/]",
                    title=f"[bold {Colors.PRIMARY}]{Icons.RUNNING} Current Uninstallation[/bold {Colors.PRIMARY}]",
                    border_style=Colors.PRIMARY,
                    box=box.ROUNDED,
                    padding=(1, 2)
                )
                console.print(uninstall_card)
                
                # Run brew uninstall command
                uninstall_command = f'brew uninstall {package_name}'
                result = self._run_command(uninstall_command)
                
                if result:
                    if result.returncode == 0:
                        console.print(f"[{Colors.SUCCESS}]{Icons.SUCCESS} {software_name} uninstalled successfully![/]")
                        success_count += 1
                    else:
                        console.print(f"[{Colors.ERROR}]{Icons.ERROR} {software_name} uninstallation failed[/]")
                        if result.stderr:
                            console.print(f"[dim]{result.stderr[:200]}[/dim]")
                        failed_count += 1
                else:
                    console.print(f"[{Colors.ERROR}]{Icons.ERROR} {software_name} uninstallation failed (no response)[/]")
                    failed_count += 1
                
                console.print()
                progress.update(overall_task, advance=1)
        
        # Run brew cleanup
        console.print(f"[{Colors.PRIMARY}]{Icons.RUNNING} Running brew cleanup...[/]")
        with console.status(f"[bold {Colors.PRIMARY}]Cleaning up...", spinner="dots"):
            self._run_command('brew cleanup')
        console.print(f"[{Colors.SUCCESS}]{Icons.SUCCESS} Cleanup complete[/]")
        
        # Show final results
        self._show_uninstall_results(success_count, failed_count, skipped_count)
    
    def _show_uninstall_results(self, success: int, failed: int, skipped: int):
        """Show uninstallation results"""
        results_text = Text()
        results_text.append(f"{Icons.SUCCESS} Successful: ", style=Colors.TEXT)
        results_text.append(f"{success}\n", style=f"bold {Colors.SUCCESS}")
        results_text.append(f"{Icons.ERROR} Failed: ", style=Colors.TEXT)
        results_text.append(f"{failed}\n", style=f"bold {Colors.ERROR}")
        results_text.append(f"{Icons.WARNING} Skipped: ", style=Colors.TEXT)
        results_text.append(f"{skipped}", style=f"bold {Colors.WARNING}")
        
        results_panel = Panel(
            results_text,
            title=f"[bold {Colors.PRIMARY}]{Icons.PACKAGE} Uninstallation Results[/bold {Colors.PRIMARY}]",
            border_style=Colors.PRIMARY,
            box=box.ROUNDED,
            padding=(1, 2)
        )
        console.print(results_panel)
        
        if failed == 0:
            console.print(f"\n[bold {Colors.SUCCESS}]{Icons.SUCCESS} All uninstallations completed successfully![/]")
        else:
            console.print(f"\n[bold {Colors.WARNING}]{Icons.WARNING} Uninstallation completed with some issues.[/]")
