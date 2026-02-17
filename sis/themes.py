#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Theme System for SwiftInstall
Provides color themes and visual styling management
"""

from enum import Enum
from typing import Dict, Any
from dataclasses import dataclass


class ThemeType(Enum):
    """Available theme types"""
    AUTO = "auto"
    LIGHT = "light"
    DARK = "dark"
    HIGH_CONTRAST = "high_contrast"


@dataclass
class ColorScheme:
    """Color scheme definition"""
    # Primary colors
    primary: str
    primary_bright: str
    secondary: str
    secondary_bright: str
    
    # Accent colors
    success: str
    success_bright: str
    warning: str
    warning_bright: str
    error: str
    error_bright: str
    
    # Neutral colors
    text: str
    text_dim: str
    text_muted: str
    background: str
    
    # Special colors
    accent: str
    highlight: str
    border: str


# Predefined color schemes
THEMES: Dict[ThemeType, ColorScheme] = {
    ThemeType.DARK: ColorScheme(
        primary="cyan",
        primary_bright="bright_cyan",
        secondary="blue",
        secondary_bright="bright_blue",
        success="green",
        success_bright="bright_green",
        warning="yellow",
        warning_bright="bright_yellow",
        error="red",
        error_bright="bright_red",
        text="white",
        text_dim="dim",
        text_muted="bright_black",
        background="black",
        accent="magenta",
        highlight="bright_yellow",
        border="cyan"
    ),
    
    ThemeType.LIGHT: ColorScheme(
        primary="blue",
        primary_bright="bright_blue",
        secondary="cyan",
        secondary_bright="bright_cyan",
        success="green",
        success_bright="bright_green",
        warning="yellow",
        warning_bright="bright_yellow",
        error="red",
        error_bright="bright_red",
        text="black",
        text_dim="dim",
        text_muted="bright_black",
        background="white",
        accent="magenta",
        highlight="bright_cyan",
        border="blue"
    ),
    
    ThemeType.HIGH_CONTRAST: ColorScheme(
        primary="bright_white",
        primary_bright="white",
        secondary="bright_cyan",
        secondary_bright="cyan",
        success="bright_green",
        success_bright="green",
        warning="bright_yellow",
        warning_bright="yellow",
        error="bright_red",
        error_bright="red",
        text="bright_white",
        text_dim="white",
        text_muted="white",
        background="black",
        accent="bright_magenta",
        highlight="bright_yellow",
        border="bright_white"
    )
}


class ThemeManager:
    """Manages application themes"""
    
    def __init__(self):
        self._current_theme = ThemeType.DARK
        self._custom_themes: Dict[str, ColorScheme] = {}
    
    @property
    def current_theme(self) -> ThemeType:
        """Get current theme"""
        return self._current_theme
    
    @property
    def colors(self) -> ColorScheme:
        """Get current color scheme"""
        return THEMES.get(self._current_theme, THEMES[ThemeType.DARK])
    
    def set_theme(self, theme: ThemeType):
        """Set active theme"""
        self._current_theme = theme
    
    def auto_detect_theme(self) -> ThemeType:
        """Auto-detect best theme based on terminal"""
        import os
        
        # Check for environment variables
        colorterm = os.environ.get('COLORTERM', '').lower()
        term = os.environ.get('TERM', '').lower()
        
        # Check for light theme preference
        if 'light' in colorterm or 'light' in term:
            return ThemeType.LIGHT
        
        # Default to dark theme
        return ThemeType.DARK
    
    def add_custom_theme(self, name: str, scheme: ColorScheme):
        """Add a custom theme"""
        self._custom_themes[name] = scheme
    
    def get_style(self, element_type: str) -> str:
        """Get Rich style string for an element type"""
        colors = self.colors
        
        styles = {
            # Headers
            "header": f"bold {colors.primary_bright}",
            "header_subtitle": colors.text_muted,
            
            # Menu
            "menu_title": f"bold {colors.primary}",
            "menu_item": colors.text,
            "menu_item_selected": f"bold {colors.primary_bright}",
            "menu_icon": colors.primary,
            "menu_number": f"bold {colors.primary}",
            
            # Status
            "status_success": f"bold {colors.success}",
            "status_error": f"bold {colors.error}",
            "status_warning": f"bold {colors.warning}",
            "status_info": colors.primary,
            
            # Tables
            "table_header": f"bold {colors.primary_bright}",
            "table_border": colors.text_dim,
            "table_row": colors.text,
            "table_row_alt": colors.text_dim,
            
            # Progress
            "progress_bar": colors.primary,
            "progress_complete": colors.success,
            "progress_text": colors.text,
            
            # Input
            "input_prompt": f"bold {colors.primary}",
            "input_text": colors.text,
            
            # Borders
            "border": colors.border,
            "border_title": f"bold {colors.primary}",
            
            # Highlights
            "highlight": f"bold {colors.highlight}",
            "accent": colors.accent,
            
            # Text
            "text": colors.text,
            "text_dim": colors.text_dim,
            "text_muted": colors.text_muted,
        }
        
        return styles.get(element_type, colors.text)


# Global theme manager instance
_theme_manager: ThemeManager = None


def get_theme_manager() -> ThemeManager:
    """Get the global theme manager instance"""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager


def get_current_colors() -> ColorScheme:
    """Get current color scheme"""
    return get_theme_manager().colors


def get_style(element_type: str) -> str:
    """Get style for an element type"""
    return get_theme_manager().get_style(element_type)
