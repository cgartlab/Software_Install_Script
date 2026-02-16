#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main CLI module for Software Install Script
"""

import click
import sys
import os
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich import print as rprint

from sis.installer import WindowsInstaller, MacOSInstaller
from sis.config import Config

console = Console()

@click.group()
def cli():
    """Software Install Script (SIS)"""
    pass

@cli.command()
def version():
    """Show version information"""
    from sis import __version__
    rprint(f"Software Install Script v{__version__}")

@cli.command()
def install():
    """Install software from configuration"""
    config = Config()
    
    # Detect platform
    if sys.platform.startswith('win32'):
        installer = WindowsInstaller(config)
    elif sys.platform.startswith('darwin'):
        installer = MacOSInstaller(config)
    else:
        console.error("Unsupported platform")
        return
    
    # Show software list
    console.print("\n[bold cyan]Software to install:[/bold cyan]")
    table = Table(show_header=True, header_style="bold green")
    table.add_column("Name", style="dim")
    table.add_column("ID")
    table.add_column("Category")
    
    for software in config.get_software_list():
        table.add_row(
            software.get('name', 'N/A'),
            software.get('id', software.get('package', 'N/A')),
            software.get('category', 'N/A')
        )
    
    console.print(table)
    
    # Confirm installation
    if not Confirm.ask("\nDo you want to proceed with installation?"):
        console.print("Installation cancelled.")
        return
    
    # Run installation
    installer.install_all()

@cli.command()
def config():
    """Configure software list"""
    config = Config()
    
    while True:
        console.print("\n[bold cyan]Configuration Menu[/bold cyan]")
        console.print("1. View current software list")
        console.print("2. Add software")
        console.print("3. Remove software")
        console.print("4. Save and exit")
        console.print("5. Exit without saving")
        
        choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4", "5"])
        
        if choice == "1":
            # View software list
            console.print("\n[bold cyan]Current software list:[/bold cyan]")
            table = Table(show_header=True, header_style="bold green")
            table.add_column("#", style="dim")
            table.add_column("Name", style="dim")
            table.add_column("ID/Package")
            table.add_column("Category")
            
            for i, software in enumerate(config.get_software_list(), 1):
                table.add_row(
                    str(i),
                    software.get('name', 'N/A'),
                    software.get('id', software.get('package', 'N/A')),
                    software.get('category', 'N/A')
                )
            
            console.print(table)
            
        elif choice == "2":
            # Add software
            name = Prompt.ask("Enter software name")
            if sys.platform.startswith('win32'):
                software_id = Prompt.ask("Enter winget ID")
            else:
                software_id = Prompt.ask("Enter brew package name")
            category = Prompt.ask("Enter category", default="Other")
            
            if sys.platform.startswith('win32'):
                config.add_software({'name': name, 'id': software_id, 'category': category})
            else:
                config.add_software({'name': name, 'package': software_id, 'category': category})
            
            console.print("[green]Software added successfully![/green]")
            
        elif choice == "3":
            # Remove software
            index = Prompt.ask("Enter software number to remove", convert=int)
            if config.remove_software(index - 1):
                console.print("[green]Software removed successfully![/green]")
            else:
                console.print("[red]Invalid software number![/red]")
                
        elif choice == "4":
            # Save and exit
            config.save()
            console.print("[green]Configuration saved successfully![/green]")
            break
            
        elif choice == "5":
            # Exit without saving
            if Confirm.ask("Are you sure you want to exit without saving?"):
                break

@cli.command()
def tui():
    """Launch text-based user interface"""
    console.print("\n[bold cyan]Software Install Script - TUI Mode[/bold cyan]")
    console.print("=======================================")
    
    while True:
        console.print("\n[bold green]Main Menu[/bold green]")
        console.print("1. Install software")
        console.print("2. Configure software list")
        console.print("3. Settings")
        console.print("4. Exit")
        
        choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4"])
        
        if choice == "1":
            install.callback()
        elif choice == "2":
            config.callback()
        elif choice == "3":
            console.print("\n[bold yellow]Settings not implemented yet[/bold yellow]")
        elif choice == "4":
            console.print("\n[green]Exiting...[/green]")
            break

if __name__ == '__main__':
    cli()
