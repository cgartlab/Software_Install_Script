#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SwiftInstall Logo and Brand Assets
Provides ASCII art logos and brand visual elements
"""

from typing import List
from rich.text import Text
from rich.align import Align


# SwiftInstall ASCII Art Logo - Modern Style
SWIFTINSTALL_ASCII_LOGO = """
   _____       _      __      _       _           _   
  / ____|     | |    / _|    | |     | |         | |  
 | (___  _   _| |__ | |_ __ _| | __ _| |__   __ _| |_ 
  \\___ \\| | | | '_ \\|  _/ _` | |/ _` | '_ \\ / _` | __|
  ____) | |_| | |_) | || (_| | | (_| | |_) | (_| | |_ 
 |_____/ \\__,_|_.__/|_| \\__,_|_|\\__,_|_.__/ \\__,_|\\__|
                                                      
                                                      
"""

# Decorative SwiftInstall Banner
SWIFTINSTALL_BANNER = """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   ⚡  ╭──────────────────────────────────────────╮  ⚡           ║
║      │                                          │                ║
║      │   ███████╗██╗    ██╗██╗███████╗████████╗  │                ║
║      │   ██╔════╝██║    ██║██║██╔════╝╚══██╔══╝  │                ║
║      │   ███████╗██║ █╗ ██║██║█████╗     ██║     │                ║
║      │   ╚════██║██║███╗██║██║██╔══╝     ██║     │                ║
║      │   ███████║╚███╔███╔╝██║██║        ██║     │                ║
║      │   ╚══════╝ ╚══╝╚══╝ ╚═╝╚═╝        ╚═╝     │                ║
║      │                                            │                ║
║      │   ██╗███╗   ██╗███████╗████████╗ █████╗ ██╗     ██╗        ║
║      │   ██║████╗  ██║██╔════╝╚══██╔══╝██╔══██╗██║     ██║        ║
║      │   ██║██╔██╗ ██║███████╗   ██║   ███████║██║     ██║        ║
║      │   ██║██║╚██╗██║╚════██║   ██║   ██╔══██║██║     ██║        ║
║      │   ██║██║ ╚████║███████║   ██║   ██║  ██║███████╗██║        ║
║      │   ╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝        ║
║      │                                            │                ║
║      ╰──────────────────────────────────────────╯                ║
║                                                                  ║
║           Fast • Simple • Reliable • Cross-Platform              ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""

# Compact Logo for smaller screens
COMPACT_LOGO = """
╔═══════════════════════════════════════════╗
║                                           ║
║   ⚡  SwiftInstall  ⚡                     ║
║                                           ║
║   Fast • Simple • Reliable                ║
║                                           ║
╚═══════════════════════════════════════════╝
"""

# Minimal Logo
MINIMAL_LOGO = """
⚡ SwiftInstall ⚡
"""

# Installation Header
INSTALL_HEADER = """
╔══════════════════════════════════════════════════════════════════╗
║                    🚀  Installation Started  🚀                  ║
╚══════════════════════════════════════════════════════════════════╝
"""

# Success Header
SUCCESS_HEADER = """
╔══════════════════════════════════════════════════════════════════╗
║                    ✓  Installation Complete  ✓                 ║
╚══════════════════════════════════════════════════════════════════╝
"""

# Menu Border Styles
MENU_BORDER_TOP = "╭" + "─" * 58 + "╮"
MENU_BORDER_BOTTOM = "╰" + "─" * 58 + "╯"
MENU_BORDER_MIDDLE = "│" + " " * 58 + "│"
MENU_SEPARATOR = "├" + "─" * 58 + "┤"

# Box Styles
BOX_TOP = "╔" + "═" * 60 + "╗"
BOX_BOTTOM = "╚" + "═" * 60 + "╝"
BOX_MIDDLE = "║" + " " * 60 + "║"
BOX_SEPARATOR = "╠" + "═" * 60 + "╣"

# Section dividers
SECTION_DIVIDER = "─" * 62
DOUBLE_DIVIDER = "═" * 62
DOTTED_DIVIDER = "┈" * 62

# Corner decorations
CORNER_TL = "╭"
CORNER_TR = "╮"
CORNER_BL = "╰"
CORNER_BR = "╯"

# Arrow decorations
ARROW_RIGHT = "➜"
ARROW_LEFT = "⬅"
ARROW_UP = "⬆"
ARROW_DOWN = "⬇"
ARROW_DOUBLE = "➤"

# Bullet points
BULLET = "•"
BULLET_STAR = "★"
BULLET_DIAMOND = "◆"
BULLET_CIRCLE = "●"
BULLET_ARROW = "▸"

# Check marks and crosses
CHECK_MARK = "✓"
CROSS_MARK = "✗"
WARNING_MARK = "⚠"
INFO_MARK = "ℹ"

# Progress indicators
PROGRESS_EMPTY = "░"
PROGRESS_FULL = "█"
PROGRESS_HALF = "▒"

# Loading animation frames
LOADING_FRAMES = [
    "⠋",
    "⠙",
    "⠹",
    "⠸",
    "⠼",
    "⠴",
    "⠦",
    "⠧",
    "⠇",
    "⠏"
]

# Spinner frames
SPINNER_FRAMES = [
    "◐",
    "◓",
    "◑",
    "◒"
]

# Decorative elements
DECORATIVE_LINE = "─" * 60
DECORATIVE_DOUBLE = "═" * 60
DECORATIVE_STAR = "★" * 30
DECORATIVE_DOT = "•" * 40

# Brand colors (for reference)
BRAND_COLORS = {
    "primary": "#6366f1",      # Indigo - Primary brand
    "secondary": "#0f172a",    # Slate - Dark accent
    "accent": "#10b981",       # Emerald - Success
    "warning": "#f59e0b",      # Amber - Warning
    "error": "#ef4444",        # Red - Error
    "info": "#3b82f6",         # Blue - Info
    "muted": "#6b7280",        # Gray - Muted text
}


def get_logo(variant: str = "full") -> str:
    """
    Get logo based on variant
    
    Args:
        variant: Logo variant - "full", "banner", "compact", or "minimal"
    
    Returns:
        Logo string
    """
    logos = {
        "full": SWIFTINSTALL_ASCII_LOGO,
        "banner": SWIFTINSTALL_BANNER,
        "compact": COMPACT_LOGO,
        "minimal": MINIMAL_LOGO,
    }
    
    return logos.get(variant, SWIFTINSTALL_BANNER)


def get_rich_logo(variant: str = "banner") -> Text:
    """
    Get Rich Text formatted logo
    
    Args:
        variant: Logo variant - "full", "banner", "compact", or "minimal"
    
    Returns:
        Rich Text object
    """
    logo_text = Text()
    
    if variant == "full" or variant == "banner":
        lines = SWIFTINSTALL_BANNER.strip().split('\n')
        for i, line in enumerate(lines):
            if i == 0:  # Top border
                logo_text.append(line + "\n", style="bright_cyan")
            elif i == len(lines) - 1:  # Bottom border
                logo_text.append(line, style="bright_cyan")
            elif "SwiftInstall" in line and "█" in line:
                # Color the ASCII art
                colored_line = line.replace("█", "[bright_cyan]█[/bright_cyan]")
                logo_text.append(colored_line + "\n", style="dim")
            elif "Fast • Simple • Reliable" in line:
                logo_text.append(line + "\n", style="dim italic")
            else:
                logo_text.append(line + "\n", style="cyan")
    
    elif variant == "compact":
        logo_text.append(COMPACT_LOGO, style="cyan")
    
    else:  # minimal
        logo_text.append("⚡ ", style="bright_yellow")
        logo_text.append("SwiftInstall", style="bold bright_cyan")
        logo_text.append(" ⚡", style="bright_yellow")
    
    return logo_text


def get_header(title: str, style: str = "default") -> str:
    """
    Get a decorative header
    
    Args:
        title: Header title
        style: Header style - "default", "success", "warning", "error"
    
    Returns:
        Formatted header string
    """
    icons = {
        "default": "🚀",
        "success": "✓",
        "warning": "⚠",
        "error": "✗",
        "info": "ℹ"
    }
    
    icon = icons.get(style, "🚀")
    padding = (60 - len(title) - 4) // 2
    
    header = f"""
╔══════════════════════════════════════════════════════════════════╗
║{' ' * padding}{icon}  {title}  {icon}{' ' * (60 - padding - len(title) - 4)}║
╚══════════════════════════════════════════════════════════════════╝"""
    
    return header


def get_menu_item(number: int, text: str, description: str = "") -> str:
    """
    Get a formatted menu item
    
    Args:
        number: Menu item number
        text: Menu item text
        description: Optional description
    
    Returns:
        Formatted menu item string
    """
    if description:
        return f"  {BULLET_ARROW} [{number}] {text}\n    {description}"
    else:
        return f"  {BULLET_ARROW} [{number}] {text}"


def get_progress_bar(percent: int, width: int = 40) -> str:
    """
    Get a progress bar
    
    Args:
        percent: Progress percentage (0-100)
        width: Bar width
    
    Returns:
        Progress bar string
    """
    filled = int(width * percent / 100)
    empty = width - filled
    
    bar = f"{PROGRESS_FULL * filled}{PROGRESS_EMPTY * empty}"
    return f"[{bar}] {percent}%"


def get_loading_frame(frame_index: int) -> str:
    """Get a loading animation frame"""
    return LOADING_FRAMES[frame_index % len(LOADING_FRAMES)]


def get_spinner_frame(frame_index: int) -> str:
    """Get a spinner animation frame"""
    return SPINNER_FRAMES[frame_index % len(SPINNER_FRAMES)]


def create_box(content: str, width: int = 60, title: str = "") -> str:
    """
    Create a boxed content area
    
    Args:
        content: Box content
        width: Box width
        title: Optional title
    
    Returns:
        Boxed content string
    """
    lines = content.strip().split('\n')
    result = []
    
    # Top border
    if title:
        title_str = f" {title} "
        padding = (width - len(title_str)) // 2
        top = "╭" + "─" * padding + title_str + "─" * (width - padding - len(title_str)) + "╮"
    else:
        top = BOX_TOP[:width + 2]
    result.append(top)
    
    # Content
    for line in lines:
        padded = line[:width].ljust(width)
        result.append("│" + padded + "│")
    
    # Bottom border
    result.append(BOX_BOTTOM[:width + 2])
    
    return '\n'.join(result)


def get_brand_tagline() -> str:
    """Get the brand tagline"""
    return "Fast • Simple • Reliable"


def get_welcome_message() -> str:
    """Get the welcome message"""
    return f"""
{SWIFTINSTALL_BANNER}

{DOUBLE_DIVIDER}

  {BULLET_ARROW} Welcome to SwiftInstall - Your Cross-Platform Software Installer!
  
  {BULLET_ARROW} SwiftInstall helps you quickly install and manage software packages
    across different platforms using your system's package manager.

{DOUBLE_DIVIDER}

  Features:
  {BULLET} Automatic package manager detection (Homebrew/Winget)
  {BULLET} Software search and discovery
  {BULLET} Batch installation with progress tracking
  {BULLET} Simple configuration management

{DOUBLE_DIVIDER}
"""


def print_title() -> None:
    """Print the SwiftInstall title with decoration"""
    print("\n" + DOUBLE_DIVIDER)
    print("  ⚡  SwiftInstall  ⚡")
    print("  " + get_brand_tagline())
    print(DOUBLE_DIVIDER + "\n")


# Export all logo variants
__all__ = [
    'SWIFTINSTALL_ASCII_LOGO',
    'SWIFTINSTALL_BANNER',
    'COMPACT_LOGO',
    'MINIMAL_LOGO',
    'INSTALL_HEADER',
    'SUCCESS_HEADER',
    'get_logo',
    'get_rich_logo',
    'get_header',
    'get_menu_item',
    'get_progress_bar',
    'get_loading_frame',
    'get_spinner_frame',
    'create_box',
    'get_brand_tagline',
    'get_welcome_message',
    'print_title',
    'LOADING_FRAMES',
    'SPINNER_FRAMES',
    'BRAND_COLORS',
    'MENU_BORDER_TOP',
    'MENU_BORDER_BOTTOM',
    'BOX_TOP',
    'BOX_BOTTOM',
    'SECTION_DIVIDER',
    'DOUBLE_DIVIDER',
    'ARROW_RIGHT',
    'BULLET',
    'CHECK_MARK',
    'CROSS_MARK',
]
