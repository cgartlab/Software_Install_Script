#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for update checker functionality
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sis.update_checker import get_update_checker
from sis.ui import Colors, Icons

print("Testing update checker functionality...")
print("=" * 60)

# Test 1: Get update checker instance
print("\n1. Testing update checker initialization...")
try:
    update_checker = get_update_checker()
    print(f"   ✓ Update checker initialized successfully")
    print(f"   ✓ Current version: {update_checker.current_version}")
    print(f"   ✓ Cache file: {update_checker.cache_file}")
except Exception as e:
    print(f"   ✗ Failed to initialize update checker: {e}")

# Test 2: Check for updates (force check)
print("\n2. Testing update check...")
try:
    import asyncio
    result = asyncio.run(update_checker.check_for_updates(force=True))
    if result:
        print(f"   ✓ Update available!")
        print(f"   ✓ Current version: {result['current_version']}")
        print(f"   ✓ Latest version: {result['latest_version']}")
        print(f"   ✓ Download URL: {result['download_url']}")
    else:
        print(f"   ✓ No updates available")
except Exception as e:
    print(f"   ✗ Failed to check for updates: {e}")

# Test 3: Test notification
print("\n3. Testing update notification...")
try:
    # Create a mock update info for testing
    mock_update_info = {
        'current_version': update_checker.current_version,
        'latest_version': '0.3.0',  # Mock newer version
        'download_url': 'https://github.com/cgartlab/Software_Install_Script/releases/tag/v0.3.0'
    }
    print("   Showing mock update notification:")
    update_checker.show_update_notification(mock_update_info)
except Exception as e:
    print(f"   ✗ Failed to show notification: {e}")

print("\n" + "=" * 60)
print("Test completed!")
