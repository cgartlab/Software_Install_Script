#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SwiftInstall - Fast, Simple, Reliable Software Installation
A cross-platform software installation tool with CLI and TUI interfaces

Features:
    - Automatic package manager detection (Homebrew/Winget)
    - Software search and discovery
    - Batch installation with progress tracking
    - Simple configuration management
    - Multi-language support (English/Chinese)
    - Beautiful terminal UI with Rich

Author: SwiftInstall Team
Version: 0.2.0
License: MIT
"""

__version__ = '0.2.0'
__app_name__ = 'SwiftInstall'
__tagline__ = 'Fast • Simple • Reliable'
__author__ = 'SwiftInstall Team'
__license__ = 'MIT'

# Export main components
from sis.ui import get_ui, Colors, Icons
from sis.i18n import t, get_i18n
from sis.logo import get_rich_logo, get_brand_tagline

__all__ = [
    '__version__',
    '__app_name__',
    '__tagline__',
    'get_ui',
    'Colors',
    'Icons',
    't',
    'get_i18n',
    'get_rich_logo',
    'get_brand_tagline',
]
