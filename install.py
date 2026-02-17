#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Software Install Script - Online Installer

This script provides an interactive, one-line installation method
for the Software Install Script (SIS) tool.

Usage (Recommended - Using Custom Domain):
  curl -fsSL https://cgartlab.com/Software_Install_Script/install.py | python3 -
  
  # Or for Windows PowerShell:
  irm https://cgartlab.com/Software_Install_Script/install.py | python3 -

Usage (GitHub Raw):
  curl -fsSL https://raw.githubusercontent.com/cgartlab/Software_Install_Script/main/install.py | python3 -
  
  # Or for Windows PowerShell:
  Invoke-WebRequest -Uri "https://raw.githubusercontent.com/cgartlab/Software_Install_Script/main/install.py" -OutFile "install.py"; python install.py
"""

import os
import sys
import uuid
import subprocess
import platform
import shutil
import urllib.request
import tempfile
import zipfile
from pathlib import Path

# ANSI color codes for better output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

# Check if color is supported
if platform.system() == 'Windows':
    try:
        import colorama
        colorama.init()
    except ImportError:
        # If colorama is not available, disable colors
        class Colors:
            GREEN = ''
            YELLOW = ''
            RED = ''
            BLUE = ''
            CYAN = ''
            RESET = ''

# Print functions with colors
def print_info(msg):
    print(f"{Colors.BLUE}[INFO]{Colors.RESET} {msg}")

def print_success(msg):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.RESET} {msg}")

def print_warning(msg):
    print(f"{Colors.YELLOW}[WARNING]{Colors.RESET} {msg}")

def print_error(msg):
    print(f"{Colors.RED}[ERROR]{Colors.RESET} {msg}")

def print_header(msg):
    print(f"\n{Colors.CYAN}=== {msg} ==={Colors.RESET}")

# Check if Python is installed and meets version requirements
def check_python():
    print_header("Checking Python Installation")
    
    if not shutil.which('python3') and not shutil.which('python'):
        print_error("Python is not installed. Please install Python 3.7 or higher first.")
        sys.exit(1)
    
    # Determine which Python command to use
    python_cmd = 'python3' if shutil.which('python3') else 'python'
    
    try:
        result = subprocess.run(
            [python_cmd, '--version'], 
            capture_output=True, 
            text=True
        )
        version_str = result.stdout.strip().split(' ')[1]
        major, minor, _ = map(int, version_str.split('.'))
        
        if major < 3 or (major == 3 and minor < 7):
            print_error(f"Python version {version_str} is too old. Please install Python 3.7 or higher.")
            sys.exit(1)
        
        print_success(f"Python {version_str} is installed and ready to use.")
        return python_cmd
        
    except Exception as e:
        print_error(f"Failed to check Python version: {e}")
        sys.exit(1)

# Check if pip is available
def check_pip(python_cmd):
    print_header("Checking pip Installation")
    
    try:
        # Try pip3 first, then pip
        pip_cmds = ['pip3', 'pip']
        pip_cmd = None
        
        for cmd in pip_cmds:
            result = subprocess.run(
                [python_cmd, '-m', cmd, '--version'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                pip_cmd = cmd
                version_str = result.stdout.strip().split(' ')[1]
                print_success(f"{cmd} {version_str} is available.")
                break
        
        if not pip_cmd:
            print_error("pip is not available. Please install pip first.")
            sys.exit(1)
        
        return pip_cmd
        
    except Exception as e:
        print_error(f"Failed to check pip: {e}")
        sys.exit(1)

# Clone the repository or use current directory
def get_project_files():
    print_header("Getting Project Files")
    
    # Check if we're already in the project directory
    if os.path.exists('setup.py') and os.path.exists('sis'):
        print_info("Already in the project directory. Using existing files.")
        return os.getcwd()
    
    target_dir = "Software_Install_Script"
    
    # Check if git is available
    if shutil.which('git'):
        print_info("Cloning the repository from GitHub...")
        try:
            repo_url = "https://github.com/cgartlab/Software_Install_Script.git"
            
            # Remove existing directory if it exists
            if os.path.exists(target_dir):
                try:
                    shutil.rmtree(target_dir)
                except Exception as rm_err:
                    print_warning(f"Could not remove existing directory: {rm_err}")
                    # Use a temporary directory name instead
                    target_dir = f"Software_Install_Script_{uuid.uuid4().hex[:8]}"
            
            subprocess.run(
                ['git', 'clone', repo_url, target_dir],
                check=True
            )
            
            print_success(f"Repository cloned to {target_dir}/")
            return os.path.abspath(target_dir)
            
        except Exception as e:
            print_warning(f"Failed to clone repository: {e}")
            print_info("Trying to download zip file instead...")
    
    # Fallback: Download zip file
    print_info("Downloading zip file from GitHub...")
    try:
        zip_url = "https://github.com/cgartlab/Software_Install_Script/archive/refs/heads/main.zip"
        zip_path = os.path.join(tempfile.gettempdir(), "Software_Install_Script.zip")
        
        # Download the zip file
        urllib.request.urlretrieve(zip_url, zip_path)
        print_success("Zip file downloaded successfully.")
        
        # Extract the zip file
        print_info("Extracting zip file...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(tempfile.gettempdir())
        
        # Find the extracted directory name
        extracted_dir = os.path.join(tempfile.gettempdir(), "Software_Install_Script-main")
        
        # Move to target directory
        if os.path.exists(target_dir):
            try:
                shutil.rmtree(target_dir)
            except Exception:
                target_dir = f"Software_Install_Script_{uuid.uuid4().hex[:8]}"
        
        shutil.move(extracted_dir, target_dir)
        
        # Clean up zip file
        try:
            os.remove(zip_path)
        except Exception:
            pass
        
        print_success(f"Project files extracted to {target_dir}/")
        return os.path.abspath(target_dir)
        
    except Exception as e:
        print_error(f"Failed to download or extract zip file: {e}")
        print_error("Could not get project files. Please manually clone or download the repository.")
        sys.exit(1)

# Install the project and its dependencies
def install_project(python_cmd, pip_cmd, project_dir):
    print_header("Installing Project and Dependencies")
    
    os.chdir(project_dir)
    
    try:
        # Check if we need to use --break-system-packages flag
        # This is needed for newer Python versions on some systems
        pip_flags = []
        
        # Test if we're in an externally managed environment
        test_result = subprocess.run(
            [python_cmd, '-m', pip_cmd, 'install', '--dry-run', 'click'],
            capture_output=True,
            text=True
        )
        
        if "externally-managed-environment" in test_result.stderr:
            print_info("Detected externally managed environment. Using --break-system-packages flag.")
            pip_flags.append('--break-system-packages')
        
        # Install the project in editable mode
        print_info("Installing project dependencies...")
        install_cmd = [python_cmd, '-m', pip_cmd, 'install', '-e', '.'] + pip_flags
        
        print_info(f"Running command: {' '.join(install_cmd)}")
        
        # Run the installation with live output
        process = subprocess.Popen(
            install_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        for line in process.stdout:
            print(line.strip())
        
        process.wait()
        
        if process.returncode != 0:
            print_error("Installation failed.")
            sys.exit(1)
        
        print_success("Project installed successfully!")
        
    except Exception as e:
        print_error(f"Installation failed: {e}")
        sys.exit(1)

def main():
    print("\n" + "="*60)
    print(f"{Colors.GREEN}Software Install Script (SIS) - Online Installer{Colors.RESET}")
    print("="*60)
    
    print_info("This script will install the Software Install Script tool and its dependencies.")
    print_info("It will:")
    print_info("  1. Check Python installation")
    print_info("  2. Check pip installation")
    print_info("  3. Get project files")
    print_info("  4. Install dependencies")
    
    # Interactive prompt
    if sys.stdin.isatty():
        response = input("\nDo you want to continue? (y/n): ")
        if response.lower() != 'y':
            print_info("Installation cancelled.")
            sys.exit(0)
    
    # Step 1: Check Python
    python_cmd = check_python()
    
    # Step 2: Check pip
    pip_cmd = check_pip(python_cmd)
    
    # Step 3: Get project files
    project_dir = get_project_files()
    
    # Step 4: Install project
    install_project(python_cmd, pip_cmd, project_dir)
    
    print("\n" + "="*60)
    print(f"{Colors.GREEN}Installation Complete!{Colors.RESET}")
    print("="*60)
    
    print_success("You can now use the 'sis' command to run the Software Install Script.")
    print_info("For more information, run: sis --help")
    print_info("To start the interactive TUI, run: sis tui")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
