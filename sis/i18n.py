#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Internationalization (i18n) module for SwiftInstall
Auto-detects user's locale and timezone to set appropriate language
"""

import locale
import os
import sys
import time
from typing import Dict, Optional

# Language codes
LANG_EN = "en"
LANG_ZH = "zh"

# Default language
DEFAULT_LANG = LANG_EN

# Region to language mapping
REGION_LANG_MAP = {
    # Chinese regions
    "CN": LANG_ZH,  # China
    "HK": LANG_ZH,  # Hong Kong
    "MO": LANG_ZH,  # Macau
    "TW": LANG_ZH,  # Taiwan
    "SG": LANG_ZH,  # Singapore
    # English regions (default for others)
}

# Timezone to language mapping (fallback)
TIMEZONE_LANG_MAP = {
    "Asia/Shanghai": LANG_ZH,
    "Asia/Chongqing": LANG_ZH,
    "Asia/Hong_Kong": LANG_ZH,
    "Asia/Macau": LANG_ZH,
    "Asia/Taipei": LANG_ZH,
    "Asia/Singapore": LANG_ZH,
}

# Translations
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    LANG_EN: {
        # Brand
        "app_name": "SwiftInstall",
        "app_tagline": "Fast • Simple • Reliable",
        
        # Main Menu
        "main_menu_title": "SwiftInstall - TUI Mode",
        "main_menu": "Main Menu",
        "menu_install": "Install Software",
        "menu_config": "Configure Software List",
        "menu_search": "Search Software",
        "menu_settings": "Settings",
        "menu_exit": "Exit",
        "enter_choice": "Enter your choice",
        "exiting": "Thank you for using SwiftInstall!",
        
        # Splash Screen
        "initializing": "Initializing SwiftInstall",
        "system_check": "System Check",
        
        # Software Management
        "software_to_install": "Software to Install",
        "current_software_list": "Current Software List",
        "view_software_list": "View Software List",
        "add_software": "Add Software",
        "add_new_software": "Add New Software",
        "remove_software": "Remove Software",
        "remove_software_title": "Remove Software",
        "save_exit": "Save and Exit",
        "exit_no_save": "Exit Without Saving",
        "config_saved": "Configuration saved successfully!",
        "software_added": "Software added successfully!",
        "software_removed": "Software removed successfully!",
        "confirm_exit_no_save": "Are you sure you want to exit without saving?",
        "enter_software_name": "Enter software name",
        "enter_winget_id": "Enter Winget ID",
        "enter_brew_name": "Enter Homebrew package name",
        "enter_category": "Enter category",
        "enter_number_remove": "Enter software number to remove",
        "invalid_number": "Invalid software number!",
        
        # Installation
        "confirm_proceed": "Do you want to proceed with installation?",
        "installation_cancelled": "Installation cancelled.",
        "installation_complete": "Installation complete!",
        "installing": "Installing",
        
        # Search
        "search_software": "Search Software",
        "searching": "Searching",
        "enter_search_query": "Enter software name or keyword to search",
        "search_query_empty": "Search query cannot be empty",
        "using_homebrew": "Using Homebrew to search...",
        "using_winget": "Using Winget to search...",
        "brew_not_available": "Homebrew is not available",
        "winget_not_available": "Winget is not available",
        "error_checking_brew": "Error checking Homebrew",
        "error_checking_winget": "Error checking Winget",
        "error_searching": "Error searching",
        "unsupported_platform": "Unsupported platform for software search",
        "found_results": "Found {count} results",
        "no_results": "No results found",
        "search_hint": "Type a number to select software, or 'q' to quit",
        "select_option": "Select an option",
        "invalid_selection": "Invalid selection. Please try again.",
        "exiting_search": "Exiting search...",
        
        # Add to queue
        "adding_to_queue": "Adding to installation queue:",
        "name": "Name",
        "description": "Description",
        "package": "Package",
        "confirm_add": "Do you want to add this software to the installation queue?",
        "added_successfully": "Software added to installation queue successfully!",
        "not_added": "Software not added to installation queue",
        
        # Installation queue
        "installation_queue": "Current Installation Queue:",
        "queue_empty": "Installation queue is empty",
        "remove_from_queue": "Do you want to remove any software from the queue?",
        "enter_remove_number": "Enter the number of the software to remove (or 'q' to quit)",
        "removed_successfully": "Successfully removed {name} from queue",
        "failed_remove": "Failed to remove software. Please try again.",
        "invalid_software_number": "Invalid software number. Please try again.",
        "invalid_input": "Invalid input. Please enter a number or 'q'.",
        "exiting_remove": "Exiting remove mode...",
        
        # Status
        "installed": "Installed",
        "available": "Available",
        
        # Settings
        "settings_not_implemented": "Settings feature coming soon!",
        
        # Uninstall
        "menu_uninstall": "Uninstall Software",
        "software_to_uninstall": "Software to Uninstall",
        "confirm_uninstall": "Do you want to proceed with uninstallation?",
        "uninstallation_cancelled": "Uninstallation cancelled.",
        "uninstalling": "Uninstalling",
        "uninstallation_complete": "Uninstallation complete!",
        
        # Update
        "update_available": "Update Available!",
        "current_version": "Current Version",
        "latest_version": "Latest Version",
        "download_from": "Download From",
        "github_releases": "GitHub Releases",
        "update_hint": "Run 'sis update' to check for updates manually",
        "update_notification": "Update Notification",
        "checking_updates": "Checking for updates...",
        "no_updates_available": "No updates available.",
        "update_check_failed": "Failed to check for updates.",
    },
    LANG_ZH: {
        # Brand
        "app_name": "SwiftInstall",
        "app_tagline": "快速 • 简单 • 可靠",
        
        # Main Menu
        "main_menu_title": "SwiftInstall - TUI 模式",
        "main_menu": "主菜单",
        "menu_install": "安装软件",
        "menu_config": "配置软件列表",
        "menu_search": "搜索软件",
        "menu_settings": "设置",
        "menu_exit": "退出",
        "enter_choice": "请输入您的选择",
        "exiting": "感谢使用 SwiftInstall！",
        
        # Splash Screen
        "initializing": "正在初始化 SwiftInstall",
        "system_check": "系统检查",
        
        # Software Management
        "software_to_install": "待安装软件",
        "current_software_list": "当前软件列表",
        "view_software_list": "查看软件列表",
        "add_software": "添加软件",
        "add_new_software": "添加新软件",
        "remove_software": "移除软件",
        "remove_software_title": "移除软件",
        "save_exit": "保存并退出",
        "exit_no_save": "不保存退出",
        "config_saved": "配置保存成功！",
        "software_added": "软件添加成功！",
        "software_removed": "软件移除成功！",
        "confirm_exit_no_save": "确定要不保存就退出吗？",
        "enter_software_name": "请输入软件名称",
        "enter_winget_id": "请输入 Winget ID",
        "enter_brew_name": "请输入 Homebrew 包名",
        "enter_category": "请输入分类",
        "enter_number_remove": "请输入要移除的软件编号",
        "invalid_number": "无效的软件编号！",
        
        # Installation
        "confirm_proceed": "是否要继续安装？",
        "installation_cancelled": "安装已取消。",
        "installation_complete": "安装完成！",
        "installing": "正在安装",
        
        # Search
        "search_software": "搜索软件",
        "searching": "正在搜索",
        "enter_search_query": "请输入要搜索的软件名称或关键词",
        "search_query_empty": "搜索查询不能为空",
        "using_homebrew": "正在使用 Homebrew 搜索...",
        "using_winget": "正在使用 Winget 搜索...",
        "brew_not_available": "Homebrew 不可用",
        "winget_not_available": "Winget 不可用",
        "error_checking_brew": "检查 Homebrew 时出错",
        "error_checking_winget": "检查 Winget 时出错",
        "error_searching": "搜索时出错",
        "unsupported_platform": "不支持的平台，无法搜索软件",
        "found_results": "找到 {count} 个结果",
        "no_results": "未找到结果",
        "search_hint": "输入数字选择软件，或输入 'q' 退出",
        "select_option": "请选择一个选项",
        "invalid_selection": "无效的选择，请重试。",
        "exiting_search": "正在退出搜索...",
        
        # Add to queue
        "adding_to_queue": "正在添加到安装队列：",
        "name": "名称",
        "description": "描述",
        "package": "包名",
        "confirm_add": "是否要将此软件添加到安装队列？",
        "added_successfully": "软件已成功添加到安装队列！",
        "not_added": "软件未添加到安装队列",
        
        # Installation queue
        "installation_queue": "当前安装队列：",
        "queue_empty": "安装队列为空",
        "remove_from_queue": "是否要从队列中移除任何软件？",
        "enter_remove_number": "请输入要移除的软件编号（或 'q' 退出）",
        "removed_successfully": "已成功将 {name} 从队列中移除",
        "failed_remove": "移除软件失败，请重试。",
        "invalid_software_number": "无效的软件编号，请重试。",
        "invalid_input": "无效输入，请输入数字或 'q'。",
        "exiting_remove": "正在退出移除模式...",
        
        # Status
        "installed": "已安装",
        "available": "可安装",
        
        # Settings
        "settings_not_implemented": "设置功能即将推出！",
        
        # Uninstall
        "menu_uninstall": "卸载软件",
        "software_to_uninstall": "待卸载软件",
        "confirm_uninstall": "是否要继续卸载？",
        "uninstallation_cancelled": "卸载已取消。",
        "uninstalling": "正在卸载",
        "uninstallation_complete": "卸载完成！",
        
        # Update
        "update_available": "发现新版本！",
        "current_version": "当前版本",
        "latest_version": "最新版本",
        "download_from": "下载地址",
        "github_releases": "GitHub 发布页",
        "update_hint": "运行 'sis update' 手动检查更新",
        "update_notification": "更新通知",
        "checking_updates": "正在检查更新...",
        "no_updates_available": "暂无更新。",
        "update_check_failed": "检查更新失败。",
    }
}


class I18nManager:
    """Internationalization manager"""
    
    def __init__(self):
        self.current_lang = self._detect_language()
        self._ensure_lang_fallback()
    
    def _detect_language(self) -> str:
        """Detect language from region and timezone"""
        # 1. Check from locale
        lang = self._detect_from_locale()
        if lang:
            return lang
        
        # 2. Check from timezone
        lang = self._detect_from_timezone()
        if lang:
            return lang
        
        # 3. Use default
        return DEFAULT_LANG
    
    def _detect_from_locale(self) -> Optional[str]:
        """Detect language from locale settings"""
        try:
            # Try to get locale
            loc, _ = locale.getdefaultlocale()
            if loc:
                # Extract region from locale (e.g., zh_CN, en_US)
                parts = loc.split('_')
                if len(parts) >= 2:
                    region = parts[1]
                    if region in REGION_LANG_MAP:
                        return REGION_LANG_MAP[region]
                # Check language code directly
                if loc.startswith('zh'):
                    return LANG_ZH
        except Exception:
            pass
        
        return None
    
    def _detect_from_timezone(self) -> Optional[str]:
        """Detect language from timezone settings"""
        try:
            # Try to get timezone
            tz = None
            
            # Try from environment
            for env_var in ['TZ', 'TIMEZONE']:
                if env_var in os.environ:
                    tz = os.environ[env_var]
                    break
            
            # Try from time module
            if not tz:
                try:
                    tz = time.tzname[0]
                except Exception:
                    pass
            
            if tz:
                if tz in TIMEZONE_LANG_MAP:
                    return TIMEZONE_LANG_MAP[tz]
                # Check timezone patterns
                if 'Asia' in tz and ('Shanghai' in tz or 'Beijing' in tz or 'Hong_Kong' in tz or 'Taipei' in tz):
                    return LANG_ZH
        except Exception:
            pass
        
        return None
    
    def _ensure_lang_fallback(self):
        """Ensure we have a valid language with fallback"""
        if self.current_lang not in TRANSLATIONS:
            self.current_lang = DEFAULT_LANG
    
    def set_language(self, lang: str):
        """Set language manually"""
        if lang in TRANSLATIONS:
            self.current_lang = lang
        else:
            self.current_lang = DEFAULT_LANG
    
    def t(self, key: str, **kwargs) -> str:
        """Get translated text"""
        # Try current language
        if key in TRANSLATIONS.get(self.current_lang, {}):
            text = TRANSLATIONS[self.current_lang][key]
        else:
            # Fallback to default language
            if key in TRANSLATIONS.get(DEFAULT_LANG, {}):
                text = TRANSLATIONS[DEFAULT_LANG][key]
            else:
                # If no translation, return key
                return key
        
        # Format with kwargs
        if kwargs:
            try:
                text = text.format(**kwargs)
            except (KeyError, IndexError):
                pass
        
        return text


# Singleton instance
_i18n_instance: Optional[I18nManager] = None


def get_i18n() -> I18nManager:
    """Get i18n manager singleton instance"""
    global _i18n_instance
    if _i18n_instance is None:
        _i18n_instance = I18nManager()
    return _i18n_instance


def t(key: str, **kwargs) -> str:
    """Shortcut for get_i18n().t()"""
    return get_i18n().t(key, **kwargs)
