#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main CLI module for SwiftInstall
A cross-platform software installation tool with enhanced visual interface
"""

import click
import sys
import os
import time
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich import box
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

from sis.installer import WindowsInstaller, MacOSInstaller
from sis.config import Config
from sis.i18n import t
from sis.ui import get_ui, Colors, Icons, UIComponents
from sis.logo import get_rich_logo, get_brand_tagline

console = Console()


def _show_splash_screen():
    """Display the splash screen with logo and loading animation"""
    ui = get_ui()
    ui.clear_screen()
    
    # Print logo
    logo = get_rich_logo("full")
    console.print(logo)
    console.print()
    
    # Show tagline
    tagline = Text(get_brand_tagline(), style=f"dim {Colors.TEXT_MUTED}")
    console.print(Align.center(tagline))
    console.print()
    
    # System check
    checks = _perform_system_check()
    ui.show_system_check(checks)
    
    # Loading animation
    with console.status(f"[bold {Colors.PRIMARY}]Initializing SwiftInstall...", spinner="dots"):
        time.sleep(1.5)
    
    console.print()


def _perform_system_check() -> list:
    """Perform system checks and return results"""
    import subprocess
    checks = []
    
    # Check platform
    if sys.platform.startswith('darwin'):
        checks.append(("Platform", "ok", "macOS detected"))
        # Check Homebrew
        try:
            result = subprocess.run(['brew', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                checks.append(("Homebrew", "ok", "Available"))
            else:
                checks.append(("Homebrew", "warning", "Not installed"))
        except:
            checks.append(("Homebrew", "warning", "Not found"))
    
    elif sys.platform.startswith('win32'):
        checks.append(("Platform", "ok", "Windows detected"))
        # Check Winget
        try:
            result = subprocess.run(['winget', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                checks.append(("Winget", "ok", "Available"))
            else:
                checks.append(("Winget", "warning", "Not installed"))
        except:
            checks.append(("Winget", "warning", "Not found"))
    else:
        checks.append(("Platform", "error", "Unsupported"))
    
    return checks


def _install():
    """Install software from configuration (internal function)"""
    ui = get_ui()
    config = Config()
    
    # Detect platform
    if sys.platform.startswith('win32'):
        installer = WindowsInstaller(config)
    elif sys.platform.startswith('darwin'):
        installer = MacOSInstaller(config)
    else:
        console.print(f"[{Colors.ERROR}]Unsupported platform[/]")
        return
    
    # Show software list
    console.print(f"\n[bold {Colors.PRIMARY}]{Icons.PACKAGE} {t('software_to_install')}[/]")
    table = ui.create_software_table(config.get_software_list(), show_status=False)
    console.print(table)
    
    # Confirm installation
    if not Confirm.ask(f"\n[{Colors.PRIMARY}]{t('confirm_proceed')}[/]"):
        console.print(f"[{Colors.WARNING}]{t('installation_cancelled')}[/]")
        return
    
    # Run installation
    installer.install_all()


def _config():
    """Configure software list (internal function)"""
    ui = get_ui()
    config = Config()
    
    while True:
        ui.clear_screen()
        console.print(get_rich_logo("compact"))
        console.print()
        
        # Create configuration menu
        menu_items = [
            ("1", Icons.BULLET, t('view_software_list')),
            ("2", Icons.BULLET, t('add_software')),
            ("3", Icons.BULLET, t('remove_software')),
            ("4", Icons.BULLET, t('save_exit')),
            ("5", Icons.BULLET, t('exit_no_save')),
        ]
        
        menu_panel = ui.create_main_menu(menu_items)
        console.print(Align.center(menu_panel))
        console.print()
        
        choice = Prompt.ask(
            f"[{Colors.PRIMARY}]{t('enter_choice')}[/]",
            choices=["1", "2", "3", "4", "5"]
        )
        
        if choice == "1":
            # View software list
            console.print(f"\n[bold {Colors.PRIMARY}]{Icons.PACKAGE} {t('current_software_list')}[/]")
            table = ui.create_software_table(config.get_software_list(), show_status=False)
            console.print(table)
            Prompt.ask(f"\n[{Colors.TEXT_MUTED}]Press Enter to continue...[/]")
            
        elif choice == "2":
            # Add software
            console.print(f"\n[bold {Colors.PRIMARY}]{Icons.DOWNLOAD} {t('add_new_software')}[/]")
            name = Prompt.ask(f"[{Colors.SECONDARY}]{t('enter_software_name')}[/]")
            if sys.platform.startswith('win32'):
                software_id = Prompt.ask(f"[{Colors.SECONDARY}]{t('enter_winget_id')}[/]")
            else:
                software_id = Prompt.ask(f"[{Colors.SECONDARY}]{t('enter_brew_name')}[/]")
            category = Prompt.ask(f"[{Colors.SECONDARY}]{t('enter_category')}[/]", default="Other")
            
            if sys.platform.startswith('win32'):
                config.add_software({'name': name, 'id': software_id, 'category': category})
            else:
                config.add_software({'name': name, 'package': software_id, 'category': category})
            
            console.print(f"[bold {Colors.SUCCESS}]{Icons.SUCCESS} {t('software_added')}[/]")
            time.sleep(0.5)
            
        elif choice == "3":
            # Remove software
            console.print(f"\n[bold {Colors.PRIMARY}]{t('remove_software_title')}[/]")
            table = ui.create_software_table(config.get_software_list(), show_status=False)
            console.print(table)
            
            index = Prompt.ask(f"[{Colors.SECONDARY}]{t('enter_number_remove')}[/]", convert=int)
            if config.remove_software(index - 1):
                console.print(f"[bold {Colors.SUCCESS}]{Icons.SUCCESS} {t('software_removed')}[/]")
            else:
                console.print(f"[bold {Colors.ERROR}]{Icons.ERROR} {t('invalid_number')}[/]")
            time.sleep(0.5)
            
        elif choice == "4":
            # Save and exit
            config.save()
            console.print(f"[bold {Colors.SUCCESS}]{Icons.SUCCESS} {t('config_saved')}[/]")
            break
            
        elif choice == "5":
            # Exit without saving
            if Confirm.ask(f"[{Colors.WARNING}]{t('confirm_exit_no_save')}[/]"):
                break


def _search_software():
    """Search software using available package managers"""
    ui = get_ui()
    console.print(f"\n[bold {Colors.PRIMARY}]{Icons.SEARCH} {t('search_software')}[/]")
    
    # Get search query from user
    query = Prompt.ask(f"[{Colors.SECONDARY}]{t('enter_search_query')}[/]")
    if not query:
        console.print(f"[{Colors.WARNING}]{t('search_query_empty')}[/]")
        return
    
    # Detect platform and available package managers
    if sys.platform.startswith('darwin'):
        import subprocess
        try:
            result = subprocess.run(
                ['brew', '--version'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                console.print(f"[{Colors.PRIMARY}]{t('using_homebrew')}[/]")
                _search_with_brew(query)
            else:
                console.print(f"[{Colors.ERROR}]{t('brew_not_available')}[/]")
        except Exception as e:
            console.print(f"[{Colors.ERROR}]{t('error_checking_brew')}: {e}[/]")
    
    elif sys.platform.startswith('win32'):
        import subprocess
        try:
            result = subprocess.run(
                ['winget', '--version'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                console.print(f"[{Colors.PRIMARY}]{t('using_winget')}[/]")
                _search_with_winget(query)
            else:
                console.print(f"[{Colors.ERROR}]{t('winget_not_available')}[/]")
        except Exception as e:
            console.print(f"[{Colors.ERROR}]{t('error_checking_winget')}: {e}[/]")
    else:
        console.print(f"[{Colors.ERROR}]{t('unsupported_platform')}[/]")


def _search_with_brew(query):
    """Search software using Homebrew"""
    import subprocess
    
    try:
        with console.status(f"[bold {Colors.PRIMARY}]{t('searching')}...", spinner="dots"):
            result = subprocess.run(
                ['brew', 'search', '--desc', query],
                capture_output=True,
                text=True
            )
        
        if result.returncode != 0:
            console.print(f"[{Colors.WARNING}]{t('no_results')}[/]")
            if result.stderr:
                console.print(f"[dim]{result.stderr}[/dim]")
            return
        
        # Parse search results
        results = []
        lines = result.stdout.strip().split('\n')
        
        for line in lines:
            if not line or line.startswith('==>') or line.startswith('Warning:'):
                continue
            
            if ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    package_name = parts[0].strip()
                    description_part = parts[1].strip()
                    if description_part.startswith('(') and description_part.endswith(')'):
                        description = description_part[1:-1].strip()
                    else:
                        description = description_part
                    is_installed = _is_brew_package_installed(package_name)
                    results.append({
                        'name': package_name,
                        'description': description,
                        'installed': is_installed
                    })
        
        _display_search_results(results)
        
    except Exception as e:
        console.print(f"[{Colors.ERROR}]{t('error_searching')}: {e}[/]")


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
        with console.status(f"[bold {Colors.PRIMARY}]{t('searching')}...", spinner="dots"):
            result = subprocess.run(
                ['winget', 'search', query],
                capture_output=True,
                text=True
            )
        
        if result.returncode != 0:
            console.print(f"[{Colors.WARNING}]{t('no_results')}[/]")
            if result.stderr:
                console.print(f"[dim]{result.stderr}[/dim]")
            return
        
        # Parse search results
        results = []
        lines = result.stdout.strip().split('\n')
        
        header_skipped = False
        for line in lines:
            if not header_skipped:
                if 'Id' in line and 'Name' in line:
                    header_skipped = True
                continue
            
            if not line:
                continue
            
            parts = line.split('\t')
            if len(parts) >= 3:
                software_id = parts[0].strip()
                name = parts[1].strip()
                publisher = parts[2].strip() if len(parts) > 2 else ''
                
                is_installed = _is_winget_package_installed(software_id)
                results.append({
                    'name': name,
                    'description': f"Publisher: {publisher}",
                    'id': software_id,
                    'installed': is_installed
                })
        
        _display_search_results(results)
        
    except Exception as e:
        console.print(f"[{Colors.ERROR}]{t('error_searching')}: {e}[/]")


def _is_winget_package_installed(software_id):
    """Check if a Winget package is installed"""
    import subprocess
    try:
        result = subprocess.run(
            ['winget', 'list', software_id],
            capture_output=True,
            text=True
        )
        return software_id in result.stdout
    except:
        return False


def _display_search_results(results):
    """Display search results in an interactive interface"""
    ui = get_ui()
    
    if not results:
        console.print(f"[{Colors.WARNING}]{t('no_results')}[/]")
        return
    
    console.print(f"\n[bold {Colors.SUCCESS}]{Icons.SUCCESS} {t('found_results', count=len(results))}[/]")
    
    # Create results table
    table = Table(
        show_header=True,
        header_style=f"bold {Colors.PRIMARY_BRIGHT}",
        border_style=Colors.TEXT_DIM,
        box=box.ROUNDED
    )
    
    table.add_column("#", style=Colors.TEXT_DIM, width=3, justify="center")
    table.add_column("Name", style=f"bold {Colors.TEXT}", min_width=20)
    table.add_column("Description", max_width=40)
    table.add_column("ID/Package", style=Colors.SECONDARY_BRIGHT, min_width=15)
    table.add_column("Status", justify="center", width=12)
    
    for i, item in enumerate(results, 1):
        installed_status = f"{Icons.INSTALLED} {t('installed')}" if item.get('installed') else f"{Icons.NOT_INSTALLED} {t('available')}"
        status_style = Colors.SUCCESS if item.get('installed') else Colors.TEXT_DIM
        
        table.add_row(
            str(i),
            item.get('name', 'N/A'),
            item.get('description', 'N/A')[:50],
            item.get('id', item.get('name', 'N/A')),
            installed_status
        )
    
    console.print(table)
    
    # Show hints
    ui.show_tip(t('search_hint'))
    console.print()
    
    # Create choice options
    choice_options = [str(i) for i in range(1, len(results) + 1)] + ['q']
    
    while True:
        try:
            choice = Prompt.ask(
                f"[{Colors.PRIMARY}]{t('select_option')}[/]",
                choices=choice_options,
                show_choices=False
            )
            
            if choice == 'q':
                console.print(f"[{Colors.SUCCESS}]{t('exiting_search')}[/]")
                break
            
            if choice.isdigit():
                index = int(choice) - 1
                if 0 <= index < len(results):
                    selected_software = results[index]
                    _add_to_install_queue(selected_software)
                    break
            
            console.print(f"[{Colors.ERROR}]{t('invalid_selection')}[/]")
        except (ValueError, IndexError):
            console.print(f"[{Colors.ERROR}]{t('invalid_selection')}[/]")


def _add_to_install_queue(software):
    """Add selected software to installation queue"""
    console.print(f"\n[bold {Colors.PRIMARY}]{Icons.DOWNLOAD} {t('adding_to_queue')}[/]")
    console.print(f"  {Icons.BULLET} {t('name')}: {software.get('name', 'N/A')}")
    console.print(f"  {Icons.BULLET} {t('description')}: {software.get('description', 'N/A')}")
    console.print(f"  {Icons.BULLET} {t('package')}: {software.get('id', software.get('name', 'N/A'))}")
    
    if Confirm.ask(f"\n[{Colors.PRIMARY}]{t('confirm_add')}[/]"):
        config = Config()
        
        if sys.platform.startswith('win32'):
            software_id = software.get('id', software.get('name'))
            config.add_software({
                'name': software.get('name', software_id),
                'id': software_id,
                'category': 'Other'
            })
        else:
            package_name = software.get('name')
            config.add_software({
                'name': software.get('name', package_name),
                'package': package_name,
                'category': 'Other'
            })
        
        config.save()
        console.print(f"[bold {Colors.SUCCESS}]{Icons.SUCCESS} {t('added_successfully')}[/]")
        _show_install_queue()
    else:
        console.print(f"[{Colors.WARNING}]{t('not_added')}[/]")


def _show_install_queue():
    """Show current installation queue"""
    ui = get_ui()
    config = Config()
    software_list = config.get_software_list()
    
    if not software_list:
        console.print(f"[{Colors.WARNING}]{t('queue_empty')}[/]")
        return
    
    console.print(f"\n[bold {Colors.PRIMARY}]{Icons.PACKAGE} {t('installation_queue')}[/]")
    table = ui.create_software_table(software_list, show_status=False)
    console.print(table)
    
    if Confirm.ask(f"\n[{Colors.PRIMARY}]{t('remove_from_queue')}[/]"):
        _remove_from_install_queue()


def _remove_from_install_queue():
    """Remove software from installation queue"""
    config = Config()
    software_list = config.get_software_list()
    
    if not software_list:
        console.print(f"[{Colors.WARNING}]{t('queue_empty')}[/]")
        return
    
    while True:
        try:
            index = Prompt.ask(
                f"[{Colors.SECONDARY}]{t('enter_remove_number')}[/]",
                choices=[str(i) for i in range(1, len(software_list) + 1)] + ['q']
            )
            
            if index == 'q':
                console.print(f"[{Colors.SUCCESS}]{t('exiting_remove')}[/]")
                break
            
            remove_index = int(index) - 1
            if 0 <= remove_index < len(software_list):
                removed_software = software_list[remove_index]
                if config.remove_software(remove_index):
                    config.save()
                    console.print(f"[bold {Colors.SUCCESS}]{Icons.SUCCESS} {t('removed_successfully', name=removed_software.get('name', 'Software'))}[/]")
                    _show_install_queue()
                    break
                else:
                    console.print(f"[bold {Colors.ERROR}]{Icons.ERROR} {t('failed_remove')}[/]")
            else:
                console.print(f"[bold {Colors.ERROR}]{Icons.ERROR} {t('invalid_software_number')}[/]")
        except ValueError:
            console.print(f"[bold {Colors.ERROR}]{Icons.ERROR} {t('invalid_input')}[/]")


@click.group()
def cli():
    """SwiftInstall - Fast, Simple, Reliable Software Installation"""
    pass


@cli.command()
def version():
    """Show version information"""
    from sis import __version__
    
    logo = get_rich_logo("minimal")
    console.print(logo)
    console.print()
    console.print(Align.center(Text(f"Version {__version__}", style=f"bold {Colors.PRIMARY}")))
    console.print(Align.center(Text(get_brand_tagline(), style=Colors.TEXT_MUTED)))


@cli.command()
def install():
    """Install software from configuration"""
    _show_splash_screen()
    _install()


@cli.command()
def config():
    """Configure software list"""
    _config()


@cli.command()
def tui():
    """Launch text-based user interface"""
    ui = get_ui()
    
    # Show splash screen on first launch
    _show_splash_screen()
    
    while True:
        ui.clear_screen()
        
        # Print compact logo
        logo = get_rich_logo("compact")
        console.print(logo)
        console.print()
        
        # Create main menu
        menu_items = [
            ("1", Icons.INSTALL, t('menu_install')),
            ("2", Icons.CONFIG, t('menu_config')),
            ("3", Icons.SEARCH, t('menu_search')),
            ("4", Icons.SETTINGS, t('menu_settings')),
            ("5", Icons.EXIT, t('menu_exit')),
        ]
        
        menu_panel = ui.create_main_menu(menu_items)
        console.print(Align.center(menu_panel))
        console.print()
        
        # Show footer hints
        ui.show_footer()
        
        choice = Prompt.ask(
            f"[{Colors.PRIMARY}]{t('enter_choice')}[/]",
            choices=["1", "2", "3", "4", "5"]
        )
        
        if choice == "1":
            _install()
            Prompt.ask(f"\n[{Colors.TEXT_MUTED}]Press Enter to continue...[/]")
        elif choice == "2":
            _config()
        elif choice == "3":
            _search_software()
            Prompt.ask(f"\n[{Colors.TEXT_MUTED}]Press Enter to continue...[/]")
        elif choice == "4":
            console.print(f"\n[bold {Colors.WARNING}]{Icons.SETTINGS} {t('settings_not_implemented')}[/]")
            Prompt.ask(f"\n[{Colors.TEXT_MUTED}]Press Enter to continue...[/]")
        elif choice == "5":
            console.print(f"\n[bold {Colors.SUCCESS}]{Icons.SUCCESS} {t('exiting')}[/]")
            break


if __name__ == '__main__':
    cli()
