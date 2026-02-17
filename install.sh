#!/bin/bash

# SwiftInstall 一键安装脚本 (Linux/macOS)
# 使用方法: curl -fsSL https://cgartlab.com/SwiftInstall/install.sh | bash

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 变量
VERSION="${VERSION:-latest}"
INSTALL_DIR="${INSTALL_DIR:-$HOME/.local/bin}"
ADD_TO_PATH="${ADD_TO_PATH:-true}"

# 打印彩色输出
print_color() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# 显示 Logo
show_logo() {
    cat << 'EOF'
███████╗██╗    ██╗██╗███████╗████████╗    ██╗███╗   ██╗███████╗████████╗ █████╗ ██╗     ██╗     
██╔════╝██║    ██║██║██╔════╝╚══██╔══╝    ██║████╗  ██║██╔════╝╚══██╔══╝██╔══██╗██║     ██║     
███████╗██║ █╗ ██║██║█████╗     ██║       ██║██╔██╗ ██║███████╗   ██║   ███████║██║     ██║     
╚════██║██║███╗██║██║██╔══╝     ██║       ██║██║╚██╗██║╚════██║   ██║   ██╔══██║██║     ██║     
███████║╚███╔███╔╝██║██║        ██║       ██║██║ ╚████║███████║   ██║   ██║  ██║███████╗███████╗
╚══════╝ ╚══╝╚══╝ ╚═╝╚═╝        ╚═╝       ╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝
EOF
}

# 检测操作系统
detect_os() {
    local os
    case "$(uname -s)" in
        Linux*)     os=linux;;
        Darwin*)    os=darwin;;
        CYGWIN*|MINGW*|MSYS*) os=windows;;
        *)          os=unknown;;
    esac
    echo "$os"
}

# 检测架构
detect_arch() {
    local arch
    case "$(uname -m)" in
        x86_64|amd64)   arch=amd64;;
        arm64|aarch64)  arch=arm64;;
        armv7l)         arch=arm;;
        i386|i686)      arch=386;;
        *)              arch=amd64;;
    esac
    echo "$arch"
}

# 下载文件
download_file() {
    local url=$1
    local output=$2
    
    print_color "$YELLOW" "Downloading from $url..."
    
    if command -v curl &> /dev/null; then
        curl -fsSL "$url" -o "$output"
    elif command -v wget &> /dev/null; then
        wget -q "$url" -O "$output"
    else
        print_color "$RED" "Error: curl or wget is required"
        exit 1
    fi
    
    print_color "$GREEN" "Download completed!"
}

# 添加到 PATH
add_to_path() {
    local dir=$1
    
    if [[ ":$PATH:" != *":$dir:"* ]]; then
        # 检测 shell
        local shell_rc
        case "$(basename "$SHELL")" in
            bash)   shell_rc="$HOME/.bashrc";;
            zsh)    shell_rc="$HOME/.zshrc";;
            fish)   shell_rc="$HOME/.config/fish/config.fish";;
            *)      shell_rc="$HOME/.profile";;
        esac
        
        echo "export PATH=\"$dir:\$PATH\"" >> "$shell_rc"
        print_color "$GREEN" "Added to PATH in $shell_rc"
        print_color "$YELLOW" "Please run: source $shell_rc"
    else
        print_color "$GREEN" "Already in PATH: $dir"
    fi
}

# 主安装流程
main() {
    show_logo
    
    print_color "$CYAN" "\nStarting SwiftInstall installation..."
    print_color "$BLUE" "Version: $VERSION"
    print_color "$BLUE" "Install Directory: $INSTALL_DIR"
    echo ""
    
    # 检测系统
    local os=$(detect_os)
    local arch=$(detect_arch)
    
    if [ "$os" = "unknown" ]; then
        print_color "$RED" "Unsupported operating system"
        exit 1
    fi
    
    print_color "$BLUE" "Detected: $os/$arch"
    
    # 创建安装目录
    if [ ! -d "$INSTALL_DIR" ]; then
        mkdir -p "$INSTALL_DIR"
        print_color "$GREEN" "Created directory: $INSTALL_DIR"
    fi
    
    # 构建下载 URL
    local base_url="https://cgartlab.com/SwiftInstall"
    local download_url
    local output_file
    
    if [ "$os" = "windows" ]; then
        download_url="$base_url/releases/latest/sis-windows-$arch.exe"
        output_file="$INSTALL_DIR/sis.exe"
    else
        download_url="$base_url/releases/latest/sis-$os-$arch"
        output_file="$INSTALL_DIR/sis"
    fi
    
    # 下载文件
    download_file "$download_url" "$output_file"
    
    # 设置可执行权限 (Linux/macOS)
    if [ "$os" != "windows" ]; then
        chmod +x "$output_file"
    fi
    
    # 验证安装
    if [ -f "$output_file" ]; then
        local file_size=$(du -h "$output_file" | cut -f1)
        print_color "$BLUE" "File size: $file_size"
        
        print_color "$YELLOW" "\nVerifying installation..."
        if "$output_file" version &> /dev/null; then
            print_color "$GREEN" "Installation successful!"
            "$output_file" version
        else
            print_color "$YELLOW" "Warning: Could not verify installation"
        fi
    else
        print_color "$RED" "Installation failed: File not found"
        exit 1
    fi
    
    # 添加到 PATH
    if [ "$ADD_TO_PATH" = "true" ]; then
        print_color "$YELLOW" "\nAdding to PATH..."
        add_to_path "$INSTALL_DIR"
    fi
    
    # 完成
    echo ""
    print_color "$GREEN" "========================================"
    print_color "$GREEN" "Installation Complete!"
    print_color "$GREEN" "========================================"
    echo ""
    print_color "$WHITE" "Usage:"
    print_color "$BLUE" "  sis install    - Install packages"
    print_color "$BLUE" "  sis list       - List packages"
    print_color "$BLUE" "  sis search     - Search packages"
    print_color "$BLUE" "  sis --help     - Show help"
    echo ""
    print_color "$BLUE" "For more information: https://cgartlab.com/SwiftInstall"
}

# 运行安装
main
