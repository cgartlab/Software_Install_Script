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
import time
from pathlib import Path

# ANSI color codes for better output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    DIM = '\033[2m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

# Decorative elements
class Decorations:
    BOX_TOP = "╔" + "═" * 58 + "╗"
    BOX_BOTTOM = "╚" + "═" * 58 + "╝"
    BOX_MIDDLE = "║" + " " * 58 + "║"
    LINE_SINGLE = "─" * 60
    LINE_DOUBLE = "═" * 60
    BULLET = "•"
    ARROW = "➜"
    CHECK = "✓"
    CROSS = "✗"
    WARNING = "⚠"
    INFO = "ℹ"
    SPARKLE = "✨"
    ROCKET = "🚀"
    PACKAGE = "📦"
    GEAR = "⚙"
    BOLD = ""

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
            MAGENTA = ''
            WHITE = ''
            DIM = ''
            BOLD = ''
            RESET = ''

# SwiftInstall ASCII Art Logo
LOGO = f"""
{Colors.CYAN}   _____       _      __      _       _           _   {Colors.RESET}
{Colors.CYAN}  / ____|     | |    / _|    | |     | |         | |  {Colors.RESET}
{Colors.CYAN} | (___  _   _| |__ | |_ __ _| | __ _| |__   __ _| |_ {Colors.RESET}
{Colors.CYAN}  \\___ \\| | | | '_ \\|  _/ _` | |/ _` | '_ \\ / _` | __|{Colors.RESET}
{Colors.CYAN}  ____) | |_| | |_) | || (_| | | (_| | |_) | (_| | |_ {Colors.RESET}
{Colors.CYAN} |_____/ \\__,_|_.__/|_| \\__,_|_|\\__,_|_.__/ \\__,_|\\__|{Colors.RESET}
{Colors.DIM}                                                      {Colors.RESET}
{Colors.DIM}       Fast • Simple • Reliable • Cross-Platform      {Colors.RESET}
"""

# Print functions with colors and decorations
def print_logo():
    """Print the SwiftInstall logo"""
    print(LOGO)

def print_box_top():
    """Print top border of box"""
    print(f"{Colors.CYAN}{Decorations.BOX_TOP}{Colors.RESET}")

def print_box_bottom():
    """Print bottom border of box"""
    print(f"{Colors.CYAN}{Decorations.BOX_BOTTOM}{Colors.RESET}")

def print_box_middle(text="", align="center"):
    """Print middle line of box with text"""
    if not text:
        print(f"{Colors.CYAN}{Decorations.BOX_MIDDLE}{Colors.RESET}")
    else:
        if align == "center":
            padding = (58 - len(text)) // 2
            line = " " * padding + text + " " * (58 - padding - len(text))
        elif align == "left":
            line = " " + text + " " * (57 - len(text))
        else:  # right
            line = " " * (57 - len(text)) + text + " "
        print(f"{Colors.CYAN}║{Colors.RESET}{line}{Colors.CYAN}║{Colors.RESET}")

def print_info(msg):
    print(f"{Colors.BLUE}{Decorations.BOLD}[{Decorations.INFO} INFO]{Colors.RESET}{Colors.BLUE} {msg}{Colors.RESET}")

def print_success(msg):
    print(f"{Colors.GREEN}{Decorations.BOLD}[{Decorations.CHECK} SUCCESS]{Colors.RESET}{Colors.GREEN} {msg}{Colors.RESET}")

def print_warning(msg):
    print(f"{Colors.YELLOW}{Decorations.BOLD}[{Decorations.WARNING} WARNING]{Colors.RESET}{Colors.YELLOW} {msg}{Colors.RESET}")

def print_error(msg):
    print(f"{Colors.RED}{Decorations.BOLD}[{Decorations.CROSS} ERROR]{Colors.RESET}{Colors.RED} {msg}{Colors.RESET}")

def print_header(msg):
    """Print a decorative header"""
    print(f"\n{Colors.CYAN}{Decorations.LINE_DOUBLE}{Colors.RESET}")
    print(f"{Colors.CYAN}{Decorations.BOLD}  {Decorations.ROCKET} {msg}{Colors.RESET}")
    print(f"{Colors.CYAN}{Decorations.LINE_DOUBLE}{Colors.RESET}")

def print_step(step_num, total_steps, msg):
    """Print a step indicator"""
    progress = f"[{step_num}/{total_steps}]"
    print(f"\n{Colors.CYAN}{Decorations.BOLD}{progress}{Colors.RESET} {Colors.WHITE}{msg}{Colors.RESET}")
    print(f"{Colors.DIM}{Decorations.LINE_SINGLE}{Colors.RESET}")

def print_progress_bar(percent, width=40):
    """Print a progress bar"""
    filled = int(width * percent / 100)
    empty = width - filled
    bar = f"{Colors.GREEN}{'█' * filled}{Colors.DIM}{'░' * empty}{Colors.RESET}"
    print(f"  {bar} {Colors.BOLD}{percent}%{Colors.RESET}")

def print_menu_item(number, text, description=""):
    """Print a menu item"""
    if description:
        print(f"  {Colors.CYAN}{Decorations.BULLET}{Colors.RESET} [{Colors.BOLD}{number}{Colors.RESET}] {text}")
        print(f"      {Colors.DIM}{description}{Colors.RESET}")
    else:
        print(f"  {Colors.CYAN}{Decorations.BULLET}{Colors.RESET} [{Colors.BOLD}{number}{Colors.RESET}] {text}")

def print_divider():
    """Print a divider line"""
    print(f"{Colors.DIM}{Decorations.LINE_SINGLE}{Colors.RESET}")

def print_boxed_title(title):
    """Print a title in a decorative box"""
    print_box_top()
    print_box_middle("")
    print_box_middle(title)
    print_box_middle("")
    print_box_bottom()

# Check if Python is installed and meets version requirements
def check_python():
    print_step(1, 4, "Checking Python Installation")
    
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
        print_progress_bar(100)
        return python_cmd
        
    except Exception as e:
        print_error(f"Failed to check Python version: {e}")
        sys.exit(1)

# Check if pip is available
def check_pip(python_cmd):
    print_step(2, 4, "Checking pip Installation")
    
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
                print_progress_bar(100)
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
    print_step(3, 4, "Getting Project Files")
    
    # Check if we're already in the project directory
    if os.path.exists('setup.py') and os.path.exists('sis'):
        print_info("Already in the project directory. Using existing files.")
        print_progress_bar(100)
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
            print_progress_bar(100)
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
        print_progress_bar(100)
        return os.path.abspath(target_dir)
        
    except Exception as e:
        print_error(f"Failed to download or extract zip file: {e}")
        print_error("Could not get project files. Please manually clone or download the repository.")
        sys.exit(1)

# Install the project and its dependencies
def install_project(python_cmd, pip_cmd, project_dir):
    print_step(4, 4, "Installing Project and Dependencies")
    
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
        print_progress_bar(100)
        
    except Exception as e:
        print_error(f"Installation failed: {e}")
        sys.exit(1)

def print_welcome_screen():
    """Print the welcome screen"""
    print("\n" + Decorations.LINE_DOUBLE)
    print_logo()
    print(Decorations.LINE_DOUBLE + "\n")
    
    print_box_top()
    print_box_middle("")
    print_box_middle(f"{Decorations.SPARKLE}  Welcome to SwiftInstall Online Installer  {Decorations.SPARKLE}")
    print_box_middle("")
    print_box_middle("This script will install SwiftInstall and its dependencies.", "left")
    print_box_middle("")
    print_box_bottom()
    
    print(f"\n{Colors.BOLD}Installation Steps:{Colors.RESET}")
    print_menu_item(1, "Check Python", "Verify Python 3.7+ is installed")
    print_menu_item(2, "Check pip", "Verify pip is available")
    print_menu_item(3, "Get Project Files", "Clone or download from GitHub")
    print_menu_item(4, "Install Dependencies", "Install required packages")
    print()

def print_completion_screen():
    """Print the completion screen"""
    print("\n" + Decorations.LINE_DOUBLE)
    print(f"{Colors.GREEN}{Decorations.BOLD}")
    print_boxed_title(f"{Decorations.CHECK} Installation Complete! {Decorations.CHECK}")
    print(f"{Colors.RESET}")
    
    print_success("SwiftInstall has been successfully installed!")
    print()
    
    print(f"{Colors.CYAN}{Decorations.BOLD}Next Steps:{Colors.RESET}")
    print(f"  {Decorations.ARROW} Run {Colors.BOLD}sis --help{Colors.RESET} to see available commands")
    print(f"  {Decorations.ARROW} Run {Colors.BOLD}sis wizard{Colors.RESET} to start the interactive installer")
    print(f"  {Decorations.ARROW} Run {Colors.BOLD}sis check{Colors.RESET} to verify your environment")
    print()
    
    print(f"{Colors.DIM}{Decorations.LINE_SINGLE}{Colors.RESET}")
    print(f"{Colors.DIM}Thank you for installing SwiftInstall!{Colors.RESET}")
    print(f"{Colors.DIM}{Decorations.LINE_SINGLE}{Colors.RESET}\n")

def main():
    print_welcome_screen()
    
    # Interactive prompt
    if sys.stdin.isatty():
        response = input(f"{Colors.BOLD}Do you want to continue? (y/n): {Colors.RESET}")
        if response.lower() != 'y':
            print_info("Installation cancelled.")
            sys.exit(0)
    
    print()
    
    # Step 1: Check Python
    python_cmd = check_python()
    
    # Step 2: Check pip
    pip_cmd = check_pip(python_cmd)
    
    # Step 3: Get project files
    project_dir = get_project_files()
    
    # Step 4: Install project
    install_project(python_cmd, pip_cmd, project_dir)
    
    # Print completion screen
    print_completion_screen()

if __name__ == "__main__":
    main()
