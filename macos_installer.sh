#!/bin/bash

# 跨平台软件安装解决方案 - macOS版本
APP_NAME="SwiftInstall"
APP_VERSION="1.0.0"

echo "$APP_NAME v$APP_VERSION"
echo "跨平台软件安装解决方案"

echo
echo "1. 检测操作系统平台"
echo "检测到平台: macOS"

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未检测到Python 3。请先安装Python 3.7或更高版本。"
    echo "您可以使用Homebrew安装: brew install python"
    read -p "按Enter键退出..."
    exit 1
fi

# 检查pip是否安装
if ! command -v pip3 &> /dev/null; then
    echo "错误: 未检测到pip3。请确保Python安装时包含了pip。"
    read -p "按Enter键退出..."
    exit 1
fi

# 检查curl是否安装
if ! command -v curl &> /dev/null; then
    echo "警告: 未检测到curl，区域检测可能无法正常工作。"
    echo "您可以使用Homebrew安装: brew install curl"
fi

echo
echo "2. 启动主安装脚本"
echo "正在启动跨平台安装程序..."

# 确保脚本有执行权限
chmod +x installer.py

# 运行主安装脚本
python3 installer.py

read -p "按Enter键退出..."
