#!/bin/bash

# 切换 Homebrew 源为中国源
echo "Switching Homebrew source to China..."
brew update-reset
echo 'export HOMEBREW_BREW_GIT_REMOTE="https://mirrors.ustc.edu.cn/brew.git"' >> ~/.bash_profile
echo 'export HOMEBREW_CORE_GIT_REMOTE="https://mirrors.ustc.edu.cn/homebrew-core.git"' >> ~/.bash_profile
source ~/.bash_profile
echo "Homebrew source switched to China."

# 定义软件列表文件路径
software_list="packages.txt"

# 检查软件列表文件是否存在
if [ ! -f "$software_list" ]; then
    echo "Software list file $software_list not found!"
    exit 1
fi

# 逐行读取软件列表文件并安装软件
while IFS= read -r package; do
    echo "Checking if $package is installed..."
    if brew list --versions "$package" > /dev/null; then
        echo "$package is already installed. Skipping."
    else
        echo "Installing $package..."
        brew install "$package"
    fi
done < "$software_list"

echo "All software installation completed."
