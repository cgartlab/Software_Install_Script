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
from sis.i18n import t

console = Console()

def _install():
    """Install software from configuration (internal function)"""
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

def _config():
    """Configure software list (internal function)"""
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

def _search_software():
    """Search software using available package managers"""
    console.print(f"\n[bold cyan]{t('search_software')}[/bold cyan]")
    
    # Get search query from user
    query = Prompt.ask(t('enter_search_query'))
    if not query:
        console.print(f"[yellow]{t('search_query_empty')}[/yellow]")
        return
    
    # Detect platform and available package managers
    if sys.platform.startswith('darwin'):
        # macOS: Check for Homebrew
        import subprocess
        try:
            result = subprocess.run(
                ['brew', '--version'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                console.print(f"[cyan]{t('using_homebrew')}[/cyan]")
                _search_with_brew(query)
            else:
                console.print(f"[red]{t('brew_not_available')}[/red]")
        except Exception as e:
            console.print(f"[red]{t('error_checking_brew')}: {e}[/red]")
    
    elif sys.platform.startswith('win32'):
        # Windows: Check for Winget
        import subprocess
        try:
            result = subprocess.run(
                ['winget', '--version'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                console.print(f"[cyan]{t('using_winget')}[/cyan]")
                _search_with_winget(query)
            else:
                console.print(f"[red]{t('winget_not_available')}[/red]")
        except Exception as e:
            console.print(f"[red]{t('error_checking_winget')}: {e}[/red]")
    
    else:
        console.print(f"[red]{t('unsupported_platform')}[/red]")

def _search_with_brew(query):
    """Search software using Homebrew"""
    import subprocess
    
    try:
        # Run brew search command
        result = subprocess.run(
            ['brew', 'search', '--desc', query],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            console.print("[yellow]No results found or error searching[/yellow]")
            if result.stderr:
                console.print(f"[dim]{result.stderr}[/dim]")
            return
        
        # Parse search results
        results = []
        lines = result.stdout.strip().split('\n')
        
        for line in lines:
            if not line or line.startswith('==>') or line.startswith('Warning:'):
                continue
            
            # Parse Homebrew search result format: package_name: (Description)
            if ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    package_name = parts[0].strip()
                    description_part = parts[1].strip()
                    # Extract description from parentheses
                    if description_part.startswith('(') and description_part.endswith(')'):
                        description = description_part[1:-1].strip()
                    else:
                        description = description_part
                    # Check if package is installed
                    is_installed = _is_brew_package_installed(package_name)
                    results.append({
                        'name': package_name,
                        'description': description,
                        'installed': is_installed
                    })
        
        # Display results
        _display_search_results(results)
        
    except Exception as e:
        console.print(f"[red]Error searching with Homebrew: {e}[/red]")

def _is_brew_package_installed(package_name):
    """Check if a Homebrew package is installed"""
    import subprocess
    try:
        result = subprocess.run(
            ['brew', 'list', '--versions', package_name],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except:
        return False

def _search_with_winget(query):
    """Search software using Winget"""
    import subprocess
    
    try:
        # Run winget search command
        result = subprocess.run(
            ['winget', 'search', query],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            console.print("[yellow]No results found or error searching[/yellow]")
            if result.stderr:
                console.print(f"[dim]{result.stderr}[/dim]")
            return
        
        # Parse search results
        results = []
        lines = result.stdout.strip().split('\n')
        
        # Skip header lines
        header_skipped = False
        for line in lines:
            if not header_skipped:
                if 'Id' in line and 'Name' in line:
                    header_skipped = True
                continue
            
            if not line:
                continue
            
            # Parse winget output format
            # Example: Microsoft.VisualStudioCode   Visual Studio Code   Microsoft Corporation    1.83.1
            parts = line.split('\t')
            if len(parts) >= 3:
                # Handle cases where description might contain tabs
                software_id = parts[0].strip()
                name = parts[1].strip()
                publisher = parts[2].strip() if len(parts) > 2 else ''
                
                # Check if software is installed
                is_installed = _is_winget_package_installed(software_id)
                results.append({
                    'name': name,
                    'description': f"Publisher: {publisher}",
                    'id': software_id,
                    'installed': is_installed
                })
        
        # Display results
        _display_search_results(results)
        
    except Exception as e:
        console.print(f"[red]Error searching with Winget: {e}[/red]")

def _is_winget_package_installed(software_id):
    """Check if a Winget package is installed"""
    import subprocess
    try:
        result = subprocess.run(
            ['winget', 'list', software_id],
            capture_output=True,
            text=True
        )
        # Check if the output contains the software ID
        return software_id in result.stdout
    except:
        return False

def _display_search_results(results):
    """Display search results in an interactive interface"""
    if not results:
        console.print(f"[yellow]{t('no_results')}[/yellow]")
        return
    
    console.print(f"\n[bold cyan]{t('found_results', count=len(results))}[/bold cyan]")
    
    # First display results in a table
    table = Table(show_header=True, header_style="bold green")
    table.add_column("#", style="dim", width=3)
    table.add_column("Name", style="dim", width=20)
    table.add_column("Description", max_width=50)
    table.add_column("ID/Package", style="dim", width=20)
    table.add_column("Installed", justify="center", width=10)
    
    for i, item in enumerate(results, 1):
        installed_status = "✓" if item.get('installed') else "✗"
        name = item.get('name', 'N/A')
        description = item.get('description', 'N/A')
        package_id = item.get('id', item.get('name', 'N/A'))
        table.add_row(
            str(i),
            name,
            description,
            package_id,
            installed_status
        )
    
    console.print(table)
    console.print(f"[dim]{t('how_to_select')}[/dim]")
    console.print(f"[dim]{t('hint_arrow_keys')}[/dim]")
    console.print(f"[dim]{t('hint_enter')}[/dim]")
    console.print(f"[dim]{t('hint_type_number')}[/dim]")
    console.print(f"[dim]{t('hint_quit')}[/dim]")
    
    # Create choice options (just numbers and 'q')
    choice_options = [str(i) for i in range(1, len(results) + 1)] + ['q']
    
    # Use Prompt with choices to allow navigation and selection
    while True:
        try:
            # Get user input with auto-complete and navigation
            choice = Prompt.ask(
                f"\n{t('select_an_option')}",
                choices=choice_options,
                show_choices=False
            )
            
            if choice == 'q':
                console.print(f"[green]{t('exiting_search')}[/green]")
                break
            
            # Handle number input
            if choice.isdigit():
                index = int(choice) - 1
                if 0 <= index < len(results):
                    selected_software = results[index]
                    # Add to installation queue
                    _add_to_install_queue(selected_software)
                    break
            
            # If we get here, input was invalid
            console.print(f"[red]{t('invalid_selection')}[/red]")
        except (ValueError, IndexError):
            # Handle invalid input
            console.print(f"[red]{t('invalid_selection')}[/red]")

def _add_to_install_queue(software):
    """Add selected software to installation queue"""
    console.print(f"\n[bold cyan]{t('adding_to_queue')}[/bold cyan]")
    console.print(f"Name: {software.get('name', 'N/A')}")
    console.print(f"Description: {software.get('description', 'N/A')}")
    console.print(f"Package: {software.get('id', software.get('name', 'N/A'))}")
    
    # Get confirmation from user
    if Confirm.ask(t('confirm_add')):
        # Add to config
        config = Config()
        
        # Determine software ID based on platform
        if sys.platform.startswith('win32'):
            # Windows: use 'id' for winget
            software_id = software.get('id', software.get('name'))
            config.add_software({
                'name': software.get('name', software_id),
                'id': software_id,
                'category': 'Other'
            })
        else:
            # macOS: use 'name' for brew (since brew uses package names)
            package_name = software.get('name')
            config.add_software({
                'name': software.get('name', package_name),
                'package': package_name,
                'category': 'Other'
            })
        
        # Save config
        config.save()
        console.print(f"[green]{t('added_successfully')}[/green]")
        
        # Show current queue
        _show_install_queue()
    else:
        console.print(f"[yellow]{t('not_added')}[/yellow]")

def _show_install_queue():
    """Show current installation queue"""
    config = Config()
    software_list = config.get_software_list()
    
    if not software_list:
        console.print(f"[yellow]{t('queue_empty')}[/yellow]")
        return
    
    console.print(f"\n[bold cyan]{t('installation_queue')}[/bold cyan]")
    table = Table(show_header=True, header_style="bold green")
    table.add_column("#", style="dim")
    table.add_column("Name", style="dim")
    table.add_column("ID/Package")
    table.add_column("Category")
    
    for i, software in enumerate(software_list, 1):
        table.add_row(
            str(i),
            software.get('name', 'N/A'),
            software.get('id', software.get('package', 'N/A')),
            software.get('category', 'N/A')
        )
    
    console.print(table)
    
    # Offer to remove software from queue
    if Confirm.ask(t('remove_from_queue')):
        _remove_from_install_queue()

def _remove_from_install_queue():
    """Remove software from installation queue"""
    config = Config()
    software_list = config.get_software_list()
    
    if not software_list:
        console.print(f"[yellow]{t('queue_empty')}[/yellow]")
        return
    
    # Get user input for software to remove
    while True:
        try:
            index = Prompt.ask(
                t('enter_remove_number'),
                choices=[str(i) for i in range(1, len(software_list) + 1)] + ['q']
            )
            
            if index == 'q':
                console.print(f"[green]{t('exiting_remove')}[/green]")
                break
            
            # Convert to zero-based index
            remove_index = int(index) - 1
            if 0 <= remove_index < len(software_list):
                removed_software = software_list[remove_index]
                if config.remove_software(remove_index):
                    config.save()
                    console.print(f"[green]{t('removed_successfully', name=removed_software.get('name', 'Software'))}[/green]")
                    # Show updated queue
                    _show_install_queue()
                    break
                else:
                    console.print(f"[red]{t('failed_remove')}[/red]")
            else:
                console.print(f"[red]{t('invalid_software_number')}[/red]")
        except ValueError:
            console.print(f"[red]{t('invalid_input')}[/red]")

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
    _install()

@cli.command()
def config():
    """Configure software list"""
    _config()

@cli.command()
def tui():
    """Launch text-based user interface"""
    console.print(f"\n[bold cyan]{t('main_menu_title')}[/bold cyan]")
    console.print("=======================================")
    
    while True:
        console.print(f"\n[bold green]{t('main_menu')}[/bold green]")
        console.print(t('menu_install'))
        console.print(t('menu_config'))
        console.print(t('menu_search'))
        console.print(t('menu_settings'))
        console.print(t('menu_exit'))
        
        choice = Prompt.ask(t('enter_choice'), choices=["1", "2", "3", "4", "5"])
        
        if choice == "1":
            _install()
        elif choice == "2":
            _config()
        elif choice == "3":
            _search_software()
        elif choice == "4":
            console.print(f"\n[bold yellow]{t('settings_not_implemented')}[/bold yellow]")
        elif choice == "5":
            console.print(f"\n[green]{t('exiting')}[/green]")
            break

if __name__ == '__main__':
    cli()
