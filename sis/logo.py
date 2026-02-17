#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SwiftInstall Logo and Brand Assets
Professional ASCII art logos with precise alignment and visual hierarchy

Design Specifications:
- Grid System: Monospace character grid with consistent spacing
- Alignment: Center-aligned with symmetrical padding
- Visual Hierarchy: Primary brand name > Tagline > Decorative elements
- Color System: Cyan primary, white secondary, yellow accents
"""

from typing import List, Optional
from rich.text import Text
from rich.align import Align


# =============================================================================
# PRIMARY LOGO - Full Size (75 characters wide)
# =============================================================================
SWIFTINSTALL_LOGO = """
     ███████╗██╗    ██╗██╗████████╗██╗  ██╗██╗███╗   ██╗███████╗████████╗
     ██╔════╝██║    ██║██║╚══██╔══╝██║  ██║██║████╗  ██║██╔════╝╚══██╔══╝
     ███████╗██║ █╗ ██║██║   ██║   ███████║██║██╔██╗ ██║█████╗     ██║
     ╚════██║██║███╗██║██║   ██║   ██╔══██║██║██║╚██╗██║██╔══╝     ██║
     ███████║╚███╔███╔╝██║   ██║   ██║  ██║██║██║ ╚████║███████╗   ██║
     ╚══════╝ ╚══╝╚══╝ ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝

     ██╗███╗   ██╗███████╗████████╗███████╗███╗   ███╗
     ██║████╗  ██║██╔════╝╚══██╔══╝██╔════╝████╗ ████║
     ██║██╔██╗ ██║█████╗     ██║   █████╗  ██╔████╔██║
     ██║██║╚██╗██║╚════██╗   ██║   ██╔══╝  ██║╚██╔╝██║
     ██║██║ ╚████║███████║   ██║   ███████╗██║ ╚═╝ ██║
     ╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚══════╝╚═╝     ╚═╝
"""

# =============================================================================
# BANNER LOGO - With decorative border (77 characters wide)
# =============================================================================
SWIFTINSTALL_BANNER = """
╔═════════════════════════════════════════════════════════════════════════════╗
║                                                                             ║
║      ███████╗██╗    ██╗██╗████████╗██╗  ██╗██╗███╗   ██╗███████╗████████╗   ║
║      ██╔════╝██║    ██║██║╚══██╔══╝██║  ██║██║████╗  ██║██╔════╝╚══██╔══╝   ║
║      ███████╗██║ █╗ ██║██║   ██║   ███████║██║██╔██╗ ██║█████╗     ██║      ║
║      ╚════██║██║███╗██║██║   ██║   ██╔══██║██║██║╚██╗██║██╔══╝     ██║      ║
║      ███████║╚███╔███╔╝██║   ██║   ██║  ██║██║██║ ╚████║███████╗   ██║      ║
║      ╚══════╝ ╚══╝╚══╝ ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝      ║
║                                                                             ║
║      ██╗███╗   ██╗███████╗████████╗███████╗███╗   ███╗                      ║
║      ██║████╗  ██║██╔════╝╚══██╔══╝██╔════╝████╗ ████║                      ║
║      ██║██╔██╗ ██║█████╗     ██║   █████╗  ██╔████╔██║                      ║
║      ██║██║╚██╗██║╚════██╗   ██║   ██╔══╝  ██║╚██╔╝██║                      ║
║      ██║██║ ╚████║███████║   ██║   ███████╗██║ ╚═╝ ██║                      ║
║      ╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚══════╝╚═╝     ╚═╝                      ║
║                                                                             ║
║               ⚡  Fast • Simple • Reliable • Cross-Platform  ⚡             ║
║                                                                             ║
╚═════════════════════════════════════════════════════════════════════════════╝
"""

# =============================================================================
# COMPACT LOGO - Smaller size for menus (53 characters wide)
# =============================================================================
COMPACT_LOGO = """
╔═════════════════════════════════════════════════════╗
║                                                     ║
║   ███████╗██╗    ██╗██╗████████╗██╗  ██╗██╗███╗    ║
║   ██╔════╝██║    ██║██║╚══██╔══╝██║  ██║██║████╗   ║
║   ███████╗██║ █╗ ██║██║   ██║   ███████║██║██╔██╗  ║
║   ╚════██║██║███╗██║██║   ██║   ██╔══██║██║██║╚██╗ ║
║   ███████║╚███╔███╔╝██║   ██║   ██║  ██║██║██║ ╚██╗║
║   ╚══════╝ ╚══╝╚══╝ ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝║
║                                                     ║
║      ⚡  Fast • Simple • Reliable • Cross-Platform  ║
║                                                     ║
╚═════════════════════════════════════════════════════╝
"""

# =============================================================================
# MINIMAL LOGO - Ultra compact (17 characters)
# =============================================================================
MINIMAL_LOGO = """⚡ SwiftInstall ⚡"""

# =============================================================================
# MICRO LOGO - For tight spaces (12 characters)
# =============================================================================
MICRO_LOGO = """[SI]"""

# =============================================================================
# HEADERS - Standardized section headers
# =============================================================================
INSTALL_HEADER = """
╔═════════════════════════════════════════════════════════════════════════════╗
║                        🚀  Installation Started  🚀                         ║
╚═════════════════════════════════════════════════════════════════════════════╝
"""

SUCCESS_HEADER = """
╔═════════════════════════════════════════════════════════════════════════════╗
║                       ✓  Installation Complete  ✓                           ║
╚═════════════════════════════════════════════════════════════════════════════╝
"""

WARNING_HEADER = """
╔═════════════════════════════════════════════════════════════════════════════╗
║                          ⚠  Warning  ⚠                                      ║
╚═════════════════════════════════════════════════════════════════════════════╝
"""

ERROR_HEADER = """
╔═════════════════════════════════════════════════════════════════════════════╗
║                           ✗  Error  ✗                                       ║
╚═════════════════════════════════════════════════════════════════════════════╝
"""

# =============================================================================
# DECORATIVE ELEMENTS - Standardized visual components
# =============================================================================

# Border styles
BORDER_DOUBLE_TOP = "╔" + "═" * 77 + "╗"
BORDER_DOUBLE_BOTTOM = "╚" + "═" * 77 + "╝"
BORDER_DOUBLE_MIDDLE = "║" + " " * 77 + "║"
BORDER_DOUBLE_SEPARATOR = "╠" + "═" * 77 + "╣"

BORDER_SINGLE_TOP = "╭" + "─" * 75 + "╮"
BORDER_SINGLE_BOTTOM = "╰" + "─" * 75 + "╮"
BORDER_SINGLE_MIDDLE = "│" + " " * 75 + "│"
BORDER_SINGLE_SEPARATOR = "├" + "─" * 75 + "┤"

# Divider styles
DIVIDER_SINGLE = "─" * 79
DIVIDER_DOUBLE = "═" * 79
DIVIDER_DOTTED = "┈" * 79
DIVIDER_DASHED = "╌" * 79

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
ARROW_BULLET = "▸"

# Bullet points
BULLET = "•"
BULLET_STAR = "★"
BULLET_DIAMOND = "◆"
BULLET_CIRCLE = "●"

# Status indicators
CHECK_MARK = "✓"
CROSS_MARK = "✗"
WARNING_MARK = "⚠"
INFO_MARK = "ℹ"
QUESTION_MARK = "?"

# Progress indicators
PROGRESS_EMPTY = "░"
PROGRESS_FULL = "█"
PROGRESS_HALF = "▒"
PROGRESS_QUARTER = "▓"

# Animation frames
LOADING_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
SPINNER_FRAMES = ["◐", "◓", "◑", "◒"]

# =============================================================================
# BRAND IDENTITY - Color and typography standards
# =============================================================================

BRAND_COLORS = {
    "primary": "#6366f1",      # Indigo - Primary brand color
    "primary_bright": "#818cf8",  # Light indigo - Highlights
    "secondary": "#0f172a",    # Slate - Dark backgrounds
    "accent": "#10b981",       # Emerald - Success states
    "warning": "#f59e0b",      # Amber - Warnings
    "error": "#ef4444",        # Red - Errors
    "info": "#3b82f6",         # Blue - Information
    "muted": "#6b7280",        # Gray - Secondary text
    "text": "#f8fafc",         # White - Primary text
}

BRAND_TAGLINE = "Fast • Simple • Reliable • Cross-Platform"
BRAND_NAME = "SwiftInstall"
BRAND_VERSION = "v1.0.0"

# =============================================================================
# LOGO RENDERING FUNCTIONS
# =============================================================================

def get_logo(variant: str = "banner") -> str:
    """
    Retrieve logo by variant name.
    
    Args:
        variant: Logo variant name
            - "full": Complete logo without border (75 chars wide)
            - "banner": Logo with decorative border (77 chars wide)
            - "compact": Smaller version for menus (53 chars wide)
            - "minimal": Ultra-compact text version (17 chars)
            - "micro": Tiny version for status bars (12 chars)
    
    Returns:
        Logo string with proper formatting
    """
    logos = {
        "full": SWIFTINSTALL_LOGO,
        "banner": SWIFTINSTALL_BANNER,
        "compact": COMPACT_LOGO,
        "minimal": MINIMAL_LOGO,
        "micro": MICRO_LOGO,
    }
    
    return logos.get(variant, SWIFTINSTALL_BANNER)


def get_rich_logo(variant: str = "banner", show_tagline: bool = True) -> Text:
    """
    Generate Rich Text formatted logo with brand colors.
    
    Args:
        variant: Logo variant name
        show_tagline: Whether to include the tagline
    
    Returns:
        Rich Text object with styled logo
    """
    logo_text = Text()
    
    if variant == "full":
        lines = SWIFTINSTALL_LOGO.strip().split('\n')
        for i, line in enumerate(lines):
            if "██" in line:
                # Brand name in bold cyan
                logo_text.append(line + "\n", style="bold bright_cyan")
            elif line.strip():
                logo_text.append(line + "\n", style="cyan")
            else:
                logo_text.append("\n")
        if show_tagline:
            logo_text.append("\n")
            logo_text.append("    ⚡  ", style="bright_yellow")
            logo_text.append(BRAND_TAGLINE, style="dim italic bright_white")
            logo_text.append("  ⚡", style="bright_yellow")
    
    elif variant == "banner":
        lines = SWIFTINSTALL_BANNER.strip().split('\n')
        for i, line in enumerate(lines):
            if i == 0 or i == len(lines) - 1:
                # Top and bottom borders
                logo_text.append(line + "\n", style="bright_cyan")
            elif "██" in line:
                # Brand name
                logo_text.append(line + "\n", style="bold cyan")
            elif "⚡" in line or "Fast" in line:
                # Tagline with lightning bolts
                logo_text.append(line + "\n", style="dim italic bright_white")
            elif "║" in line:
                # Side borders
                logo_text.append(line + "\n", style="cyan")
            else:
                # Empty space
                logo_text.append(line + "\n", style="dim")
    
    elif variant == "compact":
        lines = COMPACT_LOGO.strip().split('\n')
        for i, line in enumerate(lines):
            if i == 0 or i == len(lines) - 1:
                logo_text.append(line + "\n", style="bright_cyan")
            elif "██" in line:
                logo_text.append(line + "\n", style="bold cyan")
            elif "⚡" in line or "Fast" in line:
                logo_text.append(line + "\n", style="dim italic bright_white")
            else:
                logo_text.append(line + "\n", style="cyan")
    
    elif variant == "minimal":
        logo_text.append("⚡ ", style="bright_yellow")
        logo_text.append(BRAND_NAME, style="bold bright_cyan")
        logo_text.append(" ⚡", style="bright_yellow")
    
    elif variant == "micro":
        logo_text.append("[", style="cyan")
        logo_text.append("SI", style="bold bright_cyan")
        logo_text.append("]", style="cyan")
    
    return logo_text


def get_header(title: str, style: str = "default", width: int = 77) -> str:
    """
    Generate a standardized header with decorative border.
    
    Args:
        title: Header title text
        style: Visual style - "default", "success", "warning", "error", "info"
        width: Header width in characters
    
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
    content_width = width - 2
    total_padding = content_width - len(title) - 4  # 4 for icons and spaces
    left_padding = total_padding // 2
    right_padding = total_padding - left_padding
    
    top_border = "╔" + "═" * content_width + "╗"
    middle = "║" + " " * left_padding + f"{icon}  {title}  {icon}" + " " * right_padding + "║"
    bottom_border = "╚" + "═" * content_width + "╝"
    
    return f"\n{top_border}\n{middle}\n{bottom_border}\n"


def get_menu_item(number: int, text: str, description: str = "", 
                  icon: str = "", indent: int = 2) -> str:
    """
    Generate a formatted menu item.
    
    Args:
        number: Menu item number
        text: Menu item text
        description: Optional description
        icon: Optional icon prefix
        indent: Indentation level
    
    Returns:
        Formatted menu item string
    """
    prefix = " " * indent
    if icon:
        prefix += f"{icon} "
    
    if description:
        return f"{prefix}{ARROW_BULLET} [{number}] {text}\n{' ' * (indent + 2)}{description}"
    else:
        return f"{prefix}{ARROW_BULLET} [{number}] {text}"


def get_progress_bar(percent: int, width: int = 40, show_percent: bool = True) -> str:
    """
    Generate a visual progress bar.
    
    Args:
        percent: Progress percentage (0-100)
        width: Bar width in characters
        show_percent: Whether to show percentage text
    
    Returns:
        Progress bar string
    """
    filled = int(width * percent / 100)
    empty = width - filled
    
    bar = f"{PROGRESS_FULL * filled}{PROGRESS_EMPTY * empty}"
    
    if show_percent:
        return f"[{bar}] {percent:3d}%"
    else:
        return f"[{bar}]"


def get_loading_frame(frame_index: int) -> str:
    """Get a loading animation frame."""
    return LOADING_FRAMES[frame_index % len(LOADING_FRAMES)]


def get_spinner_frame(frame_index: int) -> str:
    """Get a spinner animation frame."""
    return SPINNER_FRAMES[frame_index % len(SPINNER_FRAMES)]


def create_box(content: str, width: int = 75, title: str = "", 
               style: str = "double") -> str:
    """
    Create a boxed content area.
    
    Args:
        content: Box content (multi-line string)
        width: Box width
        title: Optional title (centered at top)
        style: Border style - "double" or "single"
    
    Returns:
        Boxed content string
    """
    lines = content.strip().split('\n')
    result = []
    
    if style == "double":
        corner_tl, corner_tr = "╔", "╗"
        corner_bl, corner_br = "╚", "╝"
        horizontal = "═"
        vertical = "║"
    else:
        corner_tl, corner_tr = "╭", "╮"
        corner_bl, corner_br = "╰", "╯"
        horizontal = "─"
        vertical = "│"
    
    # Top border with optional title
    if title:
        title_str = f" {title} "
        padding = (width - len(title_str)) // 2
        top = corner_tl + horizontal * padding + title_str + horizontal * (width - padding - len(title_str)) + corner_tr
    else:
        top = corner_tl + horizontal * width + corner_tr
    result.append(top)
    
    # Content lines
    for line in lines:
        padded = line[:width].ljust(width)
        result.append(vertical + padded + vertical)
    
    # Bottom border
    result.append(corner_bl + horizontal * width + corner_br)
    
    return '\n'.join(result)


def get_brand_tagline() -> str:
    """Get the brand tagline."""
    return BRAND_TAGLINE


def get_brand_name() -> str:
    """Get the brand name."""
    return BRAND_NAME


def get_welcome_message() -> str:
    """Get the complete welcome message with logo."""
    return f"""
{SWIFTINSTALL_BANNER}

{DIVIDER_DOUBLE}

  {ARROW_BULLET} Welcome to {BRAND_NAME} - Your Cross-Platform Software Installer!
  
  {ARROW_BULLET} {BRAND_NAME} helps you quickly install and manage software packages
    across different platforms using your system's package manager.

{DIVIDER_DOUBLE}

  Features:
  {BULLET} Automatic package manager detection (Homebrew/Winget)
  {BULLET} Software search and discovery
  {BULLET} Batch installation with progress tracking
  {BULLET} Simple configuration management

{DIVIDER_DOUBLE}
"""


def print_title() -> None:
    """Print the SwiftInstall title with decoration."""
    print("\n" + DIVIDER_DOUBLE)
    print(f"  ⚡  {BRAND_NAME}  ⚡")
    print(f"  {BRAND_TAGLINE}")
    print(DIVIDER_DOUBLE + "\n")


def get_install_logo() -> str:
    """
    Get the logo formatted for install.py with ANSI color codes.
    Uses standard ANSI escape sequences for cross-platform compatibility.
    """
    cyan = '\033[96m'
    bright_cyan = '\033[1;96m'
    dim = '\033[2m'
    reset = '\033[0m'
    
    return f"""
   {bright_cyan}███████╗██╗    ██╗██╗████████╗██╗  ██╗██╗███╗   ██╗███████╗████████╗{reset}
   {bright_cyan}██╔════╝██║    ██║██║╚══██╔══╝██║  ██║██║████╗  ██║██╔════╝╚══██╔══╝{reset}
   {bright_cyan}███████╗██║ █╗ ██║██║   ██║   ███████║██║██╔██╗ ██║█████╗     ██║   {reset}
   {bright_cyan}╚════██║██║███╗██║██║   ██║   ██╔══██║██║██║╚██╗██║██╔══╝     ██║   {reset}
   {bright_cyan}███████║╚███╔███╔╝██║   ██║   ██║  ██║██║██║ ╚████║███████╗   ██║   {reset}
   {bright_cyan}╚══════╝ ╚══╝╚══╝ ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   {reset}
   {dim}                                                                        {reset}
   {cyan}██╗███╗   ██╗███████╗████████╗███████╗███╗   ███╗                    {reset}
   {cyan}██║████╗  ██║██╔════╝╚══██╔══╝██╔════╝████╗ ████║                    {reset}
   {cyan}██║██╔██╗ ██║█████╗     ██║   █████╗  ██╔████╔██║                    {reset}
   {cyan}██║██║╚██╗██║╚════██╗   ██║   ██╔══╝  ██║╚██╔╝██║                    {reset}
   {cyan}██║██║ ╚████║███████║   ██║   ███████╗██║ ╚═╝ ██║                    {reset}
   {cyan}╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚══════╝╚═╝     ╚═╝                    {reset}
   {dim}                                                                        {reset}
   {dim}       ⚡  {BRAND_TAGLINE}  ⚡        {reset}
"""


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Logo variants
    'SWIFTINSTALL_LOGO',
    'SWIFTINSTALL_BANNER',
    'COMPACT_LOGO',
    'MINIMAL_LOGO',
    'MICRO_LOGO',
    
    # Headers
    'INSTALL_HEADER',
    'SUCCESS_HEADER',
    'WARNING_HEADER',
    'ERROR_HEADER',
    
    # Brand identity
    'BRAND_NAME',
    'BRAND_TAGLINE',
    'BRAND_VERSION',
    'BRAND_COLORS',
    
    # Decorative elements
    'BORDER_DOUBLE_TOP',
    'BORDER_DOUBLE_BOTTOM',
    'BORDER_SINGLE_TOP',
    'BORDER_SINGLE_BOTTOM',
    'DIVIDER_SINGLE',
    'DIVIDER_DOUBLE',
    'DIVIDER_DOTTED',
    'DIVIDER_DASHED',
    'CORNER_TL',
    'CORNER_TR',
    'CORNER_BL',
    'CORNER_BR',
    
    # Icons
    'ARROW_RIGHT',
    'ARROW_LEFT',
    'ARROW_UP',
    'ARROW_DOWN',
    'ARROW_DOUBLE',
    'ARROW_BULLET',
    'BULLET',
    'BULLET_STAR',
    'BULLET_DIAMOND',
    'BULLET_CIRCLE',
    'CHECK_MARK',
    'CROSS_MARK',
    'WARNING_MARK',
    'INFO_MARK',
    
    # Progress
    'PROGRESS_EMPTY',
    'PROGRESS_FULL',
    'PROGRESS_HALF',
    'PROGRESS_QUARTER',
    'LOADING_FRAMES',
    'SPINNER_FRAMES',
    
    # Functions
    'get_logo',
    'get_rich_logo',
    'get_header',
    'get_menu_item',
    'get_progress_bar',
    'get_loading_frame',
    'get_spinner_frame',
    'create_box',
    'get_brand_tagline',
    'get_brand_name',
    'get_welcome_message',
    'get_install_logo',
    'print_title',
]
