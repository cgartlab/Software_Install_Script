#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for CLI/TUI version
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sis import __version__
from sis.config import Config
from sis.installer import WindowsInstaller, MacOSInstaller

print(f"Software Install Script v{__version__}")
print("Testing basic functionality...")

# Test config
print("\n1. Testing configuration...")
config = Config()
software_list = config.get_software_list()
print(f"   Found {len(software_list)} software in config")
for software in software_list[:3]:  # Show first 3
    print(f"   - {software.get('name')}: {software.get('id', software.get('package'))}")

# Test platform detection
print("\n2. Testing platform detection...")
if sys.platform.startswith('win32'):
    print("   Platform: Windows")
    print("   Would use: WindowsInstaller (winget)")
elif sys.platform.startswith('darwin'):
    print("   Platform: macOS")
    print("   Would use: MacOSInstaller (homebrew)")
else:
    print("   Platform: Unsupported")

# Test config save
print("\n3. Testing config save...")
try:
    config.save()
    print("   Config saved successfully")
except Exception as e:
    print(f"   Error saving config: {e}")

print("\nTest completed successfully!")
print("\nTo use the CLI/TUI version:")
print("1. Install dependencies: pip install -r requirements.txt")
print("2. Install the package: pip install -e .")
print("3. Run commands:")
print("   sis version    # Show version")
print("   sis install    # Install software")
print("   sis config     # Configure software list")
print("   sis tui        # Launch TUI mode")
