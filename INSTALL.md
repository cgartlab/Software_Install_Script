# SwiftInstall 安装指南

## 🚀 一键安装（最简单的方式）

### Windows

在 PowerShell 中运行以下命令：

```powershell
# 一键安装最新版本
iex (irm https://cgartlab.com/SwiftInstall/install.ps1)

# 安装指定版本
iex (irm https://cgartlab.com/SwiftInstall/install.ps1) -Version "1.0.0"

# 自定义安装目录
iex (irm https://cgartlab.com/SwiftInstall/install.ps1) -InstallDir "C:\Tools"

# 不添加到 PATH
iex (irm https://cgartlab.com/SwiftInstall/install.ps1) -AddToPath:$false
```

### Linux / macOS

在终端中运行以下命令：

```bash
# 使用 curl 一键安装
curl -fsSL https://cgartlab.com/SwiftInstall/install.sh | bash

# 使用 wget 一键安装
wget -qO- https://cgartlab.com/SwiftInstall/install.sh | bash

# 安装指定版本
curl -fsSL https://cgartlab.com/SwiftInstall/install.sh | VERSION="1.0.0" bash

# 自定义安装目录
curl -fsSL https://cgartlab.com/SwiftInstall/install.sh | INSTALL_DIR="/usr/local/bin" bash
```

## 📦 手动安装

### 下载预编译二进制文件

1. 访问 [GitHub Releases](https://github.com/yourusername/swiftinstall/releases)
2. 下载对应平台的二进制文件
3. 解压并将 `sis` (或 `sis.exe`) 移动到系统 PATH 中

### 支持的系统

| 平台 | 架构 | 文件名 |
|------|------|--------|
| Windows | amd64 | `sis-windows-amd64.exe` |
| Windows | arm64 | `sis-windows-arm64.exe` |
| Linux | amd64 | `sis-linux-amd64` |
| Linux | arm64 | `sis-linux-arm64` |
| macOS | amd64 | `sis-darwin-amd64` |
| macOS | arm64 | `sis-darwin-arm64` |

### 从源码构建

**要求：**
- Go 1.21 或更高版本
- Git

**步骤：**

```bash
# 克隆仓库
git clone https://github.com/yourusername/swiftinstall.git
cd swiftinstall

# 安装依赖
go mod download

# 构建
go build -o sis main.go

# 安装到系统 (可选)
go install
```

## ⚙️ 配置

安装完成后，配置文件会自动创建在：

- **Windows:** `%USERPROFILE%\.si\config.yaml`
- **Linux/macOS:** `~/.si/config.yaml`

### 配置文件示例

```yaml
software:
  - name: Git
    id: Git.Git
    category: Development
  - name: Visual Studio Code
    id: Microsoft.VisualStudioCode
    category: Development
  - name: 7-Zip
    id: 7zip.7zip
    category: Utilities
```

## 🎯 快速开始

安装完成后，打开新的终端窗口并运行：

```bash
# 查看版本
sis version

# 列出已配置的软件
sis list

# 安装所有配置的软件
sis install

# 搜索软件
sis search vscode

# 启动交互式菜单
sis
```

## 🔧 卸载

### Windows

```powershell
# 删除安装目录
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\SwiftInstall"

# 从 PATH 中移除 (手动编辑环境变量)
```

### Linux / macOS

```bash
# 删除安装目录
rm -rf ~/.local/bin/sis
rm -rf ~/.si

# 从 PATH 配置中移除 (编辑 ~/.bashrc, ~/.zshrc 或 ~/.profile)
```

## ❓ 常见问题

### Q: 安装脚本提示权限不足？

**Windows:** 以管理员身份运行 PowerShell

**Linux/macOS:** 使用 `sudo` 或将安装目录改为用户目录：
```bash
curl -fsSL https://cgartlab.com/SwiftInstall/install.sh | INSTALL_DIR="$HOME/.local/bin" bash
```

### Q: 安装后无法找到 `sis` 命令？

安装后需要重新打开终端，或手动刷新 PATH：

```bash
# Linux/macOS
source ~/.bashrc  # 或 ~/.zshrc

# Windows
# 重新打开 PowerShell 窗口
```

### Q: 如何更新到最新版本？

重新运行一键安装命令即可更新。

## 📞 获取帮助

- 项目主页: https://cgartlab.com/SwiftInstall
- GitHub Issues: https://github.com/yourusername/swiftinstall/issues
- 文档: https://cgartlab.com/SwiftInstall/docs
