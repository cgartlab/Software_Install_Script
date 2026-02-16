#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Installer module for different platforms
"""

import subprocess
import sys
import os
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.panel import Panel

console = Console()

class BaseInstaller:
    """Base installer class"""
    
    def __init__(self, config):
        """Initialize installer"""
        self.config = config
    
    def install_all(self):
        """Install all software"""
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
            console.error(f"Error running command: {e}")
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
            console.print("[green]Winget found and ready[/green]")
        else:
            console.error("Winget not found. Please install Windows Package Manager.")
            sys.exit(1)
    
    def install_all(self):
        """Install all software using winget"""
        software_list = self.config.get_software_list()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            task = progress.add_task("Installing software...", total=len(software_list))
            
            for software in software_list:
                software_id = software.get('id')
                software_name = software.get('name', software_id)
                
                progress.update(task, description=f"Installing {software_name}")
                
                console.print(f"\n[bold blue]Installing {software_name} ({software_id})...[/bold blue]")
                
                # Run winget install command
                command = f'winget install --id "{software_id}" --silent --accept-source-agreements --accept-package-agreements'
                result = self._run_command(command)
                
                if result:
                    if result.returncode == 0:
                        console.print(f"[green]✓ {software_name} installed successfully![/green]")
                    else:
                        console.print(f"[yellow]⚠ {software_name} installation failed:[/yellow]")
                        console.print(f"[dim]{result.stderr or result.stdout}[/dim]")
                
                progress.update(task, advance=1)
        
        console.print("\n[bold green]Installation complete![/bold green]")

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
            console.print("[green]Homebrew found and ready[/green]")
        else:
            console.error("Homebrew not found. Please install Homebrew.")
            # Offer to install homebrew
            if input("Do you want to install Homebrew? (y/n): ").lower() == 'y':
                self._install_brew()
            else:
                sys.exit(1)
    
    def _install_brew(self):
        """Install homebrew"""
        console.print("[cyan]Installing Homebrew...[/cyan]")
        command = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
        result = self._run_command(command)
        if result and result.returncode == 0:
            console.print("[green]Homebrew installed successfully![/green]")
        else:
            console.error("Failed to install Homebrew")
            sys.exit(1)
    
    def install_all(self):
        """Install all software using homebrew"""
        software_list = self.config.get_software_list()
        
        # Update homebrew first
        console.print("[cyan]Updating Homebrew...[/cyan]")
        self._run_command('brew update')
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            task = progress.add_task("Installing software...", total=len(software_list))
            
            for software in software_list:
                package_name = software.get('package')
                software_name = software.get('name', package_name)
                
                progress.update(task, description=f"Installing {software_name}")
                
                console.print(f"\n[bold blue]Installing {software_name} ({package_name})...[/bold blue]")
                
                # Check if already installed
                check_command = f'brew list --versions {package_name}'
                check_result = self._run_command(check_command)
                
                if check_result and check_result.returncode == 0:
                    console.print(f"[yellow]⚠ {software_name} is already installed[/yellow]")
                else:
                    # Run brew install command
                    install_command = f'brew install {package_name}'
                    result = self._run_command(install_command)
                    
                    if result:
                        if result.returncode == 0:
                            console.print(f"[green]✓ {software_name} installed successfully![/green]")
                        else:
                            console.print(f"[yellow]⚠ {software_name} installation failed:[/yellow]")
                            console.print(f"[dim]{result.stderr or result.stdout}[/dim]")
                
                progress.update(task, advance=1)
        
        # Run brew cleanup
        console.print("[cyan]Running brew cleanup...[/cyan]")
        self._run_command('brew cleanup')
        
        console.print("\n[bold green]Installation complete![/bold green]")
