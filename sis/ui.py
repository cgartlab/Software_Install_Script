#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UI Components and Style Management Module for SwiftInstall
Provides unified UI components, animations, and visual effects
"""

import time
import sys
from typing import List, Optional, Callable
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.table import Table
from rich.align import Align
from rich import box

console = Console()


class Colors:
    """Color palette for SwiftInstall"""
    # Primary colors
    PRIMARY = "cyan"
    PRIMARY_BRIGHT = "bright_cyan"
    SECONDARY = "blue"
    SECONDARY_BRIGHT = "bright_blue"
    
    # Accent colors
    SUCCESS = "green"
    SUCCESS_BRIGHT = "bright_green"
    WARNING = "yellow"
    WARNING_BRIGHT = "bright_yellow"
    ERROR = "red"
    ERROR_BRIGHT = "bright_red"
    
    # Neutral colors
    TEXT = "white"
    TEXT_DIM = "dim"
    TEXT_MUTED = "bright_black"
    
    # Special colors
    ACCENT = "magenta"
    HIGHLIGHT = "bright_yellow"


class Icons:
    """Icon collection for UI elements"""
    # Menu icons
    INSTALL = "⚡"
    CONFIG = "⚙️"
    SEARCH = "🔍"
    SETTINGS = "🛠️"
    EXIT = "🚪"
    BACK = "◀"
    
    # Status icons
    SUCCESS = "✓"
    ERROR = "✗"
    WARNING = "⚠"
    INFO = "ℹ"
    PENDING = "○"
    RUNNING = "◉"
    
    # Software icons
    PACKAGE = "📦"
    DOWNLOAD = "⬇"
    INSTALLED = "✅"
    NOT_INSTALLED = "⬜"
    
    # Navigation icons
    ARROW_RIGHT = "→"
    ARROW_LEFT = "←"
    ARROW_UP = "↑"
    ARROW_DOWN = "↓"
    BULLET = "•"
    STAR = "★"
    HEART = "♥"


class UIComponents:
    """Reusable UI components"""
    
    @staticmethod
    def create_header(title: str, subtitle: Optional[str] = None) -> Panel:
        """Create a styled header panel"""
        content = Text()
        content.append(title, style=f"bold {Colors.PRIMARY_BRIGHT}")
        if subtitle:
            content.append("\n")
            content.append(subtitle, style=Colors.TEXT_MUTED)
        
        return Panel(
            Align.center(content),
            box=box.DOUBLE,
            border_style=Colors.PRIMARY,
            padding=(1, 2)
        )
    
    @staticmethod
    def create_menu_item(number: str, icon: str, text: str, is_selected: bool = False) -> Text:
        """Create a styled menu item"""
        content = Text()
        if is_selected:
            content.append(f"{Icons.ARROW_RIGHT} ", style=Colors.HIGHLIGHT)
            content.append(f"{number}. ", style=f"bold {Colors.PRIMARY_BRIGHT}")
            content.append(f"{icon} ", style=Colors.PRIMARY)
            content.append(text, style=f"bold {Colors.TEXT}")
        else:
            content.append(f"  {number}. ", style=Colors.TEXT_DIM)
            content.append(f"{icon} ", style=Colors.TEXT_MUTED)
            content.append(text, style=Colors.TEXT)
        return content
    
    @staticmethod
    def create_status_badge(status: str, status_type: str = "info") -> Text:
        """Create a status badge"""
        badges = {
            "success": (Colors.SUCCESS, Icons.SUCCESS),
            "error": (Colors.ERROR, Icons.ERROR),
            "warning": (Colors.WARNING, Icons.WARNING),
            "info": (Colors.PRIMARY, Icons.INFO),
            "pending": (Colors.TEXT_DIM, Icons.PENDING),
            "running": (Colors.ACCENT, Icons.RUNNING),
        }
        color, icon = badges.get(status_type, badges["info"])
        return Text(f"{icon} {status}", style=f"bold {color}")
    
    @staticmethod
    def create_info_box(title: str, content: str, style: str = Colors.PRIMARY) -> Panel:
        """Create an info box"""
        return Panel(
            content,
            title=title,
            title_align="left",
            border_style=style,
            box=box.ROUNDED,
            padding=(1, 2)
        )
    
    @staticmethod
    def create_divider(char: str = "─", style: str = Colors.TEXT_DIM) -> Text:
        """Create a horizontal divider"""
        width = console.width - 4
        return Text(char * width, style=style)


class Animations:
    """Animation effects for UI"""
    
    @staticmethod
    def loading_spinner(message: str, duration: float = 2.0):
        """Show a loading spinner with message"""
        with console.status(f"[bold {Colors.PRIMARY}]{message}...", spinner="dots"):
            time.sleep(duration)
    
    @staticmethod
    def typewriter_effect(text: str, delay: float = 0.03, style: str = Colors.TEXT):
        """Display text with typewriter effect"""
        for char in text:
            console.print(char, end="", style=style)
            sys.stdout.flush()
            time.sleep(delay)
        console.print()
    
    @staticmethod
    def fade_in_text(text: str, style: str = Colors.TEXT):
        """Display text with fade-in effect"""
        colors = ["dim", "bright_black", "white"]
        for color in colors:
            console.print(text, style=color, end="\r")
            time.sleep(0.1)
        console.print(text, style=style)
    
    @staticmethod
    def progress_bar(description: str, total: int = 100):
        """Create a styled progress bar"""
        return Progress(
            SpinnerColumn(style=Colors.PRIMARY),
            TextColumn(f"[bold {Colors.PRIMARY}]{{task.description}}"),
            BarColumn(
                complete_style=Colors.SUCCESS,
                finished_style=Colors.SUCCESS_BRIGHT,
                pulse_style=Colors.PRIMARY
            ),
            TextColumn(f"[bold {{task.percentage:>3.0f}}%]", style=Colors.TEXT),
            console=console,
            expand=True
        )


class SwiftInstallUI:
    """Main UI manager for SwiftInstall"""
    
    def __init__(self):
        self.console = console
        self.colors = Colors()
        self.icons = Icons()
        self.components = UIComponents()
        self.animations = Animations()
    
    def clear_screen(self):
        """Clear the terminal screen"""
        console.clear()
    
    def print_logo(self, show_version: bool = True):
        """Print the SwiftInstall logo"""
        from sis.logo import get_logo
        logo_lines = get_logo()
        
        for line in logo_lines:
            console.print(line, style=f"bold {Colors.PRIMARY}")
        
        if show_version:
            from sis import __version__
            version_text = Text(f"v{__version__}", style=f"{Colors.TEXT_MUTED} dim")
            console.print(Align.center(version_text))
    
    def print_welcome(self):
        """Print welcome message"""
        welcome_text = Text()
        welcome_text.append("Welcome to ", style=Colors.TEXT)
        welcome_text.append("SwiftInstall", style=f"bold {Colors.PRIMARY_BRIGHT}")
        welcome_text.append("!", style=Colors.TEXT)
        console.print(Align.center(welcome_text))
        console.print()
    
    def create_main_menu(self, items: List[tuple], selected: int = 0) -> Panel:
        """Create the main menu panel
        
        Args:
            items: List of (number, icon, text) tuples
            selected: Currently selected item index
        """
        menu_text = Text()
        
        for i, (number, icon, text) in enumerate(items):
            is_selected = (i == selected)
            item = self.components.create_menu_item(number, icon, text, is_selected)
            menu_text.append(item)
            if i < len(items) - 1:
                menu_text.append("\n")
        
        return Panel(
            menu_text,
            title=f"[bold {Colors.PRIMARY}]{Icons.STAR} Main Menu[/bold {Colors.PRIMARY}]",
            title_align="center",
            border_style=Colors.PRIMARY,
            box=box.ROUNDED,
            padding=(1, 2)
        )
    
    def create_software_table(self, software_list: List[dict], show_status: bool = True) -> Table:
        """Create a table for software list"""
        table = Table(
            show_header=True,
            header_style=f"bold {Colors.PRIMARY_BRIGHT}",
            border_style=Colors.TEXT_DIM,
            box=box.ROUNDED
        )
        
        table.add_column("#", style=Colors.TEXT_DIM, width=3, justify="center")
        table.add_column("Name", style=f"bold {Colors.TEXT}", min_width=20)
        table.add_column("ID/Package", style=Colors.SECONDARY_BRIGHT, min_width=15)
        table.add_column("Category", style=Colors.ACCENT)
        
        if show_status:
            table.add_column("Status", justify="center", width=10)
        
        for i, software in enumerate(software_list, 1):
            row = [
                str(i),
                software.get('name', 'N/A'),
                software.get('id', software.get('package', 'N/A')),
                software.get('category', 'Other')
            ]
            
            if show_status:
                installed = software.get('installed', False)
                if installed:
                    row.append(f"{Icons.INSTALLED} Installed")
                else:
                    row.append(f"{Icons.NOT_INSTALLED} Available")
            
            table.add_row(*row)
        
        return table
    
    def show_system_check(self, checks: List[tuple]):
        """Show system check results
        
        Args:
            checks: List of (name, status, message) tuples
        """
        console.print(f"\n[bold {Colors.PRIMARY}]{Icons.INFO} System Check[/bold {Colors.PRIMARY}]")
        
        for name, status, message in checks:
            if status == "ok":
                icon = Icons.SUCCESS
                color = Colors.SUCCESS
            elif status == "warning":
                icon = Icons.WARNING
                color = Colors.WARNING
            else:
                icon = Icons.ERROR
                color = Colors.ERROR
            
            console.print(f"  {icon} [{color}]{name}[/{color}]: {message}")
        
        console.print()
    
    def show_tip(self, message: str):
        """Show a helpful tip"""
        tip_text = Text()
        tip_text.append(f"{Icons.BULLET} Tip: ", style=f"bold {Colors.WARNING}")
        tip_text.append(message, style=Colors.TEXT_DIM)
        console.print(tip_text)
    
    def show_footer(self, hints: List[str] = None):
        """Show footer with navigation hints"""
        if hints is None:
            hints = [
                f"{Icons.ARROW_UP}{Icons.ARROW_DOWN} Navigate",
                "Enter Select",
                "q Quit"
            ]
        
        footer_text = Text("  |  ", style=Colors.TEXT_DIM).join([
            Text(hint, style=Colors.TEXT_MUTED) for hint in hints
        ])
        
        console.print()
        console.print(Align.center(footer_text))


# Global UI instance
_ui_instance: Optional[SwiftInstallUI] = None


def get_ui() -> SwiftInstallUI:
    """Get the global UI instance"""
    global _ui_instance
    if _ui_instance is None:
        _ui_instance = SwiftInstallUI()
    return _ui_instance
