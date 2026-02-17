@echo off
chcp 65001 > nul

:: 跨平台软件安装解决方案 - Windows版本
set "APP_NAME=SwiftInstall"
set "APP_VERSION=1.0.0"

echo %APP_NAME% v%APP_VERSION%
echo 跨平台软件安装解决方案

echo.
echo 1. 检测操作系统平台
echo 检测到平台: Windows

:: 检查Python是否安装
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未检测到Python。请先安装Python 3.7或更高版本。
    echo 您可以从 https://www.python.org/downloads/ 下载并安装Python。
    pause
    exit /b 1
)

:: 检查pip是否安装
pip --version > nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未检测到pip。请确保Python安装时包含了pip。
    pause
    exit /b 1
)

:: 检查curl是否安装
curl --version > nul 2>&1
if %errorlevel% neq 0 (
    echo 警告: 未检测到curl，区域检测可能无法正常工作。
)

echo.
echo 2. 启动主安装脚本
echo 正在启动跨平台安装程序...
python installer.py

pause
