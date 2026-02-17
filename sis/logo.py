#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SwiftInstall Logo and Brand Assets
Provides ASCII art logos and brand visual elements
"""

from typing import List
from rich.text import Text
from rich.align import Align


# Main SwiftInstall ASCII Logo
# Features: Lightning bolt (⚡) + Package (📦) concept
SWIFTINSTALL_LOGO = """
    ╭────────────────────────────────────────────╮
    │                                            │
    │     ⚡  ╭──────────╮  ⚡                   │
    │        │  📦📦📦  │                        │
    │     ═══╡  📦📦📦  ╞═══                    │
    │        │  📦📦📦  │                        │
    │     ⚡  ╰──────────╯  ⚡                   │
    │                                            │
    │        SwiftInstall                        │
    │        ─────────────────                   │
    │        Fast • Simple • Reliable            │
    │                                            │
    ╰────────────────────────────────────────────╯
"""

# Alternative compact logo
COMPACT_LOGO = """
        ⚡ ╭──────╮ ⚡
          │ 📦📦📦 │
        ══╡ 📦📦📦 ╞══
          │ 📦📦📦 │
        ⚡ ╰──────╯ ⚡
          SwiftInstall
"""

# Minimal logo for small screens
MINIMAL_LOGO = """
    ⚡ 📦 SwiftInstall 📦 ⚡
"""

# Loading animation frames
LOADING_FRAMES = [
    "[    ]",
    "[=   ]",
    "[==  ]",
    "[=== ]",
    "[ ===]",
    "[  ==]",
    "[   =]",
    "[    ]",
    "[   =]",
    "[  ==]",
    "[ ===]",
    "[====]",
]

# Success animation
SUCCESS_FRAMES = [
    "     ",
    "    ✓",
    "   ✓ ",
    "  ✓  ",
    " ✓   ",
    "✓    ",
    " ✓   ",
    "  ✓  ",
    "   ✓ ",
    "    ✓",
    "   ✓✓",
    "  ✓✓✓",
    " ✓✓✓✓",
    "✓✓✓✓✓",
]

# Decorative elements
DECORATIVE_TOP = "╭" + "─" * 58 + "╮"
DECORATIVE_BOTTOM = "╰" + "─" * 58 + "╯"
DECORATIVE_LINE = "│" + " " * 58 + "│"

# Brand colors (for reference)
BRAND_COLORS = {
    "primary": "#00D4AA",      # Cyan - Speed & Energy
    "secondary": "#1A1A2E",    # Deep Blue - Professional
    "accent": "#FF6B35",       # Orange - Action
    "success": "#00C853",      # Green - Success
    "warning": "#FFD600",      # Yellow - Warning
    "error": "#FF1744",        # Red - Error
}


def get_logo(variant: str = "full") -> List[str]:
    """
    Get logo lines based on variant
    
    Args:
        variant: Logo variant - "full", "compact", or "minimal"
    
    Returns:
        List of logo lines
    """
    logos = {
        "full": SWIFTINSTALL_LOGO,
        "compact": COMPACT_LOGO,
        "minimal": MINIMAL_LOGO,
    }
    
    logo = logos.get(variant, SWIFTINSTALL_LOGO)
    return [line for line in logo.split('\n') if line]


def get_rich_logo(variant: str = "full") -> Text:
    """
    Get Rich Text formatted logo
    
    Args:
        variant: Logo variant
    
    Returns:
        Rich Text object
    """
    logo_text = Text()
    
    if variant == "full":
        # Full logo with color styling
        logo_text.append("    ╭────────────────────────────────────────────╮\n", style="cyan")
        logo_text.append("    │                                            │\n", style="cyan")
        logo_text.append("    │     ", style="cyan")
        logo_text.append("⚡", style="bright_yellow")
        logo_text.append("  ╭──────────╮  ", style="cyan")
        logo_text.append("⚡", style="bright_yellow")
        logo_text.append("                   │\n", style="cyan")
        logo_text.append("    │        │  ", style="cyan")
        logo_text.append("📦📦📦", style="bright_cyan")
        logo_text.append("  │                        │\n", style="cyan")
        logo_text.append("    │     ═══╡  ", style="cyan")
        logo_text.append("📦📦📦", style="bright_cyan")
        logo_text.append("  ╞═══                    │\n", style="cyan")
        logo_text.append("    │        │  ", style="cyan")
        logo_text.append("📦📦📦", style="bright_cyan")
        logo_text.append("  │                        │\n", style="cyan")
        logo_text.append("    │     ", style="cyan")
        logo_text.append("⚡", style="bright_yellow")
        logo_text.append("  ╰──────────╯  ", style="cyan")
        logo_text.append("⚡", style="bright_yellow")
        logo_text.append("                   │\n", style="cyan")
        logo_text.append("    │                                            │\n", style="cyan")
        logo_text.append("    │        ", style="cyan")
        logo_text.append("SwiftInstall\n", style="bold bright_cyan")
        logo_text.append("    │        ", style="cyan")
        logo_text.append("─────────────────\n", style="dim")
        logo_text.append("    │        ", style="cyan")
        logo_text.append("Fast • Simple • Reliable\n", style="dim")
        logo_text.append("    │                                            │\n", style="cyan")
        logo_text.append("    ╰────────────────────────────────────────────╯", style="cyan")
    
    elif variant == "compact":
        logo_text.append("        ", style="cyan")
        logo_text.append("⚡", style="bright_yellow")
        logo_text.append(" ╭──────╮ ", style="cyan")
        logo_text.append("⚡\n", style="bright_yellow")
        logo_text.append("          │ ", style="cyan")
        logo_text.append("📦📦📦", style="bright_cyan")
        logo_text.append(" │\n", style="cyan")
        logo_text.append("        ══╡ ", style="cyan")
        logo_text.append("📦📦📦", style="bright_cyan")
        logo_text.append(" ╞══\n", style="cyan")
        logo_text.append("          │ ", style="cyan")
        logo_text.append("📦📦📦", style="bright_cyan")
        logo_text.append(" │\n", style="cyan")
        logo_text.append("        ", style="cyan")
        logo_text.append("⚡", style="bright_yellow")
        logo_text.append(" ╰──────╯ ", style="cyan")
        logo_text.append("⚡\n", style="bright_yellow")
        logo_text.append("          ", style="cyan")
        logo_text.append("SwiftInstall\n", style="bold bright_cyan")
    
    else:  # minimal
        logo_text.append("    ", style="cyan")
        logo_text.append("⚡", style="bright_yellow")
        logo_text.append(" 📦 ", style="cyan")
        logo_text.append("SwiftInstall", style="bold bright_cyan")
        logo_text.append(" 📦 ", style="cyan")
        logo_text.append("⚡", style="bright_yellow")
    
    return logo_text


def get_loading_frame(frame_index: int) -> str:
    """Get a loading animation frame"""
    return LOADING_FRAMES[frame_index % len(LOADING_FRAMES)]


def get_success_frame(frame_index: int) -> str:
    """Get a success animation frame"""
    return SUCCESS_FRAMES[min(frame_index, len(SUCCESS_FRAMES) - 1)]


# ASCII Art decorations
BORDER_TOP = "╔" + "═" * 60 + "╗"
BORDER_BOTTOM = "╚" + "═" * 60 + "╝"
BORDER_MIDDLE = "║" + " " * 60 + "║"

# Section dividers
SECTION_DIVIDER = "─" * 62
DOUBLE_DIVIDER = "═" * 62

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

# Bullet points
BULLET = "•"
BULLET_STAR = "★"
BULLET_DIAMOND = "◆"
BULLET_CIRCLE = "●"


def create_box(content: str, width: int = 60, title: str = "") -> str:
    """Create a boxed content area"""
    lines = content.split('\n')
    result = []
    
    # Top border
    if title:
        title_str = f" {title} "
        padding = (width - len(title_str)) // 2
        top = "╭" + "─" * padding + title_str + "─" * (width - padding - len(title_str)) + "╮"
    else:
        top = BORDER_TOP[:width + 2]
    result.append(top)
    
    # Content
    for line in lines:
        padded = line[:width].ljust(width)
        result.append("│" + padded + "│")
    
    # Bottom border
    result.append(BORDER_BOTTOM[:width + 2])
    
    return '\n'.join(result)


def get_brand_tagline() -> str:
    """Get the brand tagline"""
    return "Fast • Simple • Reliable"


def get_welcome_message() -> str:
    """Get the welcome message"""
    return """
    Welcome to SwiftInstall - Your Cross-Platform Software Installer!
    
    SwiftInstall helps you quickly install and manage software packages
    across different platforms using your system's package manager.
    
    Features:
    • Automatic package manager detection (Homebrew/Winget)
    • Software search and discovery
    • Batch installation with progress tracking
    • Simple configuration management
    """
