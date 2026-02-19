# SwiftInstall 快速入门指南

## 1. 简介

SwiftInstall (简称 `sis`) 是一个跨平台的软件安装管理工具，支持 Windows (Winget)、macOS (Homebrew) 和 Linux (apt/dnf/pacman)。

### 主要功能

- 🎨 精美的 TUI 交互界面
- 🔍 软件包搜索
- ⚙️ 配置文件管理
- 🚀 批量并行安装
- 🌐 多语言支持（中文/英文）

## 2. 安装

### Windows (PowerShell)

```powershell
# 一键安装最新版本
iex (irm https://cgartlab.com/SwiftInstall/install.ps1)
```

### Linux / macOS (Bash)

```bash
# 使用 curl 一键安装
curl -fsSL https://cgartlab.com/SwiftInstall/install.sh | bash
```

### 手动安装

1. 从 [GitHub Releases](https://github.com/cgartlab/SwiftInstall/releases) 下载对应平台的二进制文件
2. 解压后添加到系统 PATH

### 从源码构建

```bash
git clone https://github.com/cgartlab/SwiftInstall.git
cd SwiftInstall
go build -o sis main.go
go install
```

## 3. 快速开始

### 3.1 启动交互式菜单

```bash
sis
```

使用方向键导航，Enter 选择，q 退出。

### 3.2 命令行模式

```bash
# 安装配置中的所有软件
sis install

# 安装指定软件
sis install Git.Git Microsoft.VisualStudioCode

# 搜索软件
sis search vscode

# 列出已配置的软件
sis list

# 查看系统状态
sis status

# 查看帮助
sis help
```

## 4. 配置文件

### 配置文件位置

- **Windows:** `%USERPROFILE%\.si\config.yaml`
- **Linux/macOS:** `~/.si/config.yaml`

### 示例配置

```yaml
language: zh
theme: dark
parallel_install: true
auto_update_check: true
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

### 编辑配置

```bash
# 使用交互式配置管理器
sis config

# 使用默认编辑器直接编辑
sis edit-list
```

## 5. 快捷键说明

### 主菜单

| 快捷键 | 功能 |
|--------|------|
| `↑/↓` | 上下导航 |
| `Enter` | 确认选择 |
| `i` | 快速安装 |
| `s` | 快速搜索 |
| `c` | 配置管理 |
| `a` | 关于作者 |
| `q` | 退出 |

### 搜索界面

| 快捷键 | 功能 |
|--------|------|
| `Enter` | 搜索 / 添加选中软件 |
| `/` | 重新搜索 |
| `Esc` | 返回输入框 |
| `q` | 退出 |

### 安装界面

| 快捷键 | 功能 |
|--------|------|
| `a` | 显示关于（安装完成后） |
| `Enter` / `Esc` | 完成并退出 |
| `q` | 取消并退出 |

### 配置管理

| 快捷键 | 功能 |
|--------|------|
| `a` | 添加软件 |
| `Enter` / `e` | 编辑软件 |
| `d` / `r` | 删除软件 |
| `Tab` | 切换输入框 |
| `q` | 返回 |

## 6. 常用场景

### 场景 1: 首次使用

```bash
# 1. 安装 sis
# 2. 运行 sis 启动交互菜单
# 3. 选择"配置管理"添加要安装的软件
# 4. 选择"安装软件"开始安装
```

### 场景 2: 快速安装常用软件

```bash
# 直接指定包名安装
sis install Git.Git Microsoft.VisualStudioCode Google.Chrome
```

### 场景 3: 搜索并安装软件

```bash
# 1. 搜索软件
sis search vscode

# 2. 按 Enter 添加到配置

# 3. 安装配置中的软件
sis install
```

### 场景 4: 批量部署环境

```bash
# 1. 准备配置文件 config.yaml
software:
  - name: Git
    id: Git.Git
    category: Development
  - name: Node.js
    id: OpenJS.NodeJS
    category: Development
  - name: VS Code
    id: Microsoft.VisualStudioCode
    category: Development

# 2. 执行安装
sis install
```

### 场景 5: 环境预检

```bash
# 自动检测包管理器和依赖
sis setup --auto-install-deps

# 仅检测，不自动安装
sis setup --dry-run
```

## 7. 故障排除

### 问题 1: 找不到包管理器

**症状:** 运行安装命令时提示 "package manager is not available"

**解决方案:**
- Windows: 确保 Winget 已安装（Windows 10 1709+）
- macOS: 安装 Homebrew `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
- Linux: 确保 apt/dnf/pacman 可用

### 问题 2: 安装失败

**症状:** 软件安装失败

**解决方案:**
1. 检查网络连接
2. 确认包 ID 正确
3. 查看错误信息
4. 尝试手动安装包验证

### 问题 3: 配置文件无法保存

**症状:** 配置修改后无法保存

**解决方案:**
1. 检查配置文件权限
2. 确保配置目录存在
3. 检查磁盘空间

## 8. 获取帮助

```bash
# 完整帮助文档
sis help

# 命令特定帮助
sis install --help
sis search --help

# 版本信息
sis version

# 关于信息
sis about
```

## 9. 下一步

- 查看 [README.md](README.md) 了解更多功能
- 查看 [CHANGELOG.md](CHANGELOG.md) 了解最新版本
- 在 [GitHub](https://github.com/cgartlab/SwiftInstall) 上提交 Issue 或 PR

---

**祝你使用愉快！** 🎉
