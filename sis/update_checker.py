#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Update checker module for SwiftInstall
Handles automatic update checking from GitHub
"""

import asyncio
import httpx
import json
import time
from typing import Optional, Dict, Any
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.align import Align
from rich import box

from sis.i18n import t, get_i18n
from sis.ui import get_ui, Colors, Icons

console = Console()

class UpdateChecker:
    """Update checker for SwiftInstall"""
    
    def __init__(self):
        """Initialize update checker"""
        self.github_repo = "cgartlab/Software_Install_Script"
        self.api_url = f"https://api.github.com/repos/{self.github_repo}/releases/latest"
        self.update_check_interval = 24 * 60 * 60  # 24 hours
        self.cache_file = self._get_cache_file()
        self.current_version = self._get_current_version()
    
    def _get_cache_file(self) -> str:
        """Get path to update cache file"""
        import os
        import tempfile
        cache_dir = os.path.join(tempfile.gettempdir(), "swiftinstall")
        os.makedirs(cache_dir, exist_ok=True)
        return os.path.join(cache_dir, "update_cache.json")
    
    def _get_current_version(self) -> str:
        """Get current version of SwiftInstall"""
        from sis import __version__
        return __version__
    
    def _load_cache(self) -> Optional[Dict[str, Any]]:
        """Load update check cache"""
        import os
        if not os.path.exists(self.cache_file):
            return None
        
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    
    def _save_cache(self, data: Dict[str, Any]):
        """Save update check cache"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass
    
    async def _fetch_latest_version(self) -> Optional[str]:
        """Fetch latest version from GitHub API"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.api_url)
                if response.status_code == 200:
                    data = response.json()
                    return data.get('tag_name', '').lstrip('v')
                return None
        except Exception:
            return None
    
    def _should_check_for_updates(self) -> bool:
        """Check if we should check for updates"""
        cache = self._load_cache()
        if not cache:
            return True
        
        last_check = cache.get('last_check', 0)
        current_time = time.time()
        
        return current_time - last_check >= self.update_check_interval
    
    def _is_newer_version(self, latest_version: str) -> bool:
        """Check if latest version is newer than current version"""
        def version_to_tuple(version: str) -> tuple:
            try:
                return tuple(map(int, version.split('.')))
            except Exception:
                return ()
        
        current = version_to_tuple(self.current_version)
        latest = version_to_tuple(latest_version)
        
        return latest > current
    
    async def check_for_updates(self, force: bool = False) -> Optional[Dict[str, Any]]:
        """Check for updates
        
        Args:
            force: Force check even if within interval
            
        Returns:
            Dict with update info or None if no update
        """
        if not force and not self._should_check_for_updates():
            return None
        
        latest_version = await self._fetch_latest_version()
        
        if not latest_version:
            # Save cache even if check failed
            self._save_cache({
                'last_check': time.time(),
                'current_version': self.current_version
            })
            return None
        
        is_newer = self._is_newer_version(latest_version)
        
        # Save cache
        self._save_cache({
            'last_check': time.time(),
            'current_version': self.current_version,
            'latest_version': latest_version,
            'is_newer': is_newer
        })
        
        if is_newer:
            return {
                'current_version': self.current_version,
                'latest_version': latest_version,
                'download_url': f"https://github.com/{self.github_repo}/releases/tag/v{latest_version}"
            }
        
        return None
    
    def show_update_notification(self, update_info: Dict[str, Any]):
        """Show update notification"""
        ui = get_ui()
        
        panel = Panel(
            Align.center(
                Text.from_markup(
                    f"\n[bold {Colors.PRIMARY}]{Icons.UPDATE} {t('update_available')}[/]\n"\
                    f"[dim {Colors.TEXT_MUTED}]{t('current_version')}:[/] [bold {Colors.TEXT}]{update_info['current_version']}[/]\n"\
                    f"[dim {Colors.TEXT_MUTED}]{t('latest_version')}:[/] [bold {Colors.SUCCESS}]{update_info['latest_version']}[/]\n"\
                    f"[dim {Colors.TEXT_MUTED}]{t('download_from')}:[/] [link={update_info['download_url']}]{t('github_releases')}[/link]\n"\
                    f"\n[bold {Colors.WARNING}]{t('update_hint')}[/]"
                )
            ),
            title=f"[bold {Colors.PRIMARY}]{t('update_notification')}[/]",
            border_style=Colors.PRIMARY,
            box=box.ROUNDED
        )
        
        console.print(panel)
        console.print()
    
    def check_and_notify(self, force: bool = False):
        """Check for updates and notify if available"""
        async def _check():
            update_info = await self.check_for_updates(force)
            if update_info:
                self.show_update_notification(update_info)
        
        try:
            asyncio.run(_check())
        except Exception:
            pass

def get_update_checker() -> UpdateChecker:
    """Get update checker instance"""
    return UpdateChecker()

# Export
__all__ = ['UpdateChecker', 'get_update_checker']
