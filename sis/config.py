#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration management module
"""

import os
import sys
import yaml
from rich.console import Console

console = Console()

class Config:
    """Configuration manager"""
    
    def __init__(self):
        """Initialize configuration"""
        self.config_dir = os.path.expanduser('~/.sis')
        self.config_file = os.path.join(self.config_dir, 'config.yaml')
        self.software_list = []
        
        # Create config directory if it doesn't exist
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Load existing config or create default
        self.load()
    
    def load(self):
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    self.software_list = config.get('software', [])
            except Exception as e:
                console.error(f"Error loading config: {e}")
                self._create_default_config()
        else:
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default configuration"""
        # Create default software list based on platform
        if sys.platform.startswith('win32'):
            self.software_list = [
                {'name': 'Git', 'id': 'Git.Git', 'category': 'Development'},
                {'name': 'Visual Studio Code', 'id': 'Microsoft.VisualStudioCode', 'category': 'Development'},
                {'name': '7-Zip', 'id': '7zip.7zip', 'category': 'Utilities'},
                {'name': 'Google Chrome', 'id': 'Google.Chrome', 'category': 'Browsers'},
            ]
        elif sys.platform.startswith('darwin'):
            self.software_list = [
                {'name': 'Git', 'package': 'git', 'category': 'Development'},
                {'name': 'Visual Studio Code', 'package': 'visual-studio-code', 'category': 'Development'},
                {'name': 'Google Chrome', 'package': 'google-chrome', 'category': 'Browsers'},
            ]
        
        self.save()
    
    def save(self):
        """Save configuration to file"""
        config = {'software': self.software_list}
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            console.error(f"Error saving config: {e}")
    
    def get_software_list(self):
        """Get software list"""
        return self.software_list
    
    def add_software(self, software):
        """Add software to list"""
        self.software_list.append(software)
    
    def remove_software(self, index):
        """Remove software from list by index"""
        if 0 <= index < len(self.software_list):
            self.software_list.pop(index)
            return True
        return False
    
    def clear(self):
        """Clear software list"""
        self.software_list = []
    
    def import_from_legacy(self, file_path):
        """Import software list from legacy text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            category = 'Other'
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if line.startswith('#'):
                    # Extract category from comment
                    category = line[1:].strip()
                else:
                    # Add software
                    if sys.platform.startswith('win32'):
                        self.software_list.append({
                            'name': line,  # Try to extract name from ID
                            'id': line,
                            'category': category
                        })
                    elif sys.platform.startswith('darwin'):
                        self.software_list.append({
                            'name': line,  # Try to extract name from package
                            'package': line,
                            'category': category
                        })
            
            self.save()
            return True
        except Exception as e:
            console.error(f"Error importing legacy config: {e}")
            return False
