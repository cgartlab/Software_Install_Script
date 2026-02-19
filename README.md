# SwiftInstall

<p align="center">
  <b>⚡ 快速、简单、可靠的跨平台软件安装工具</b>
</p>

<p align="center">
  <a href="https://github.com/cgartlab/SwiftInstall/releases">
    <img src="https://img.shields.io/github/v/release/cgartlab/SwiftInstall?style=flat-square&color=blue" alt="Release">
  </a>
  <a href="https://goreportcard.com/report/github.com/cgartlab/SwiftInstall">
    <img src="https://goreportcard.com/badge/github.com/cgartlab/SwiftInstall?style=flat-square" alt="Go Report Card">
  </a>
  <a href="https://github.com/cgartlab/SwiftInstall/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-CC%20BY--NC%204.0-green?style=flat-square" alt="License">
  </a>
</p>

---

## 🌟 特性

- 🎨 **精美的 TUI 界面** - 基于 [Bubble Tea](https://github.com/charmbracelet/bubbletea) 的现代化终端交互体验
- 🚀 **极速安装** - 支持并行安装，大幅提升软件部署效率
- 🔍 **智能搜索** - 内置软件包搜索，快速找到所需软件
- ⚙️ **配置管理** - 交互式配置文件管理，轻松增删软件
- 🧙 **安装向导** - 引导式软件安装体验，新手友好
- 🌐 **多语言支持** - 支持中文和英文界面
- 🔄 **启动自动更新检查** - 首次可选择是否启用自动更新检查
- 🩺 **环境预检** - 安装与搜索前自动检查包管理器与关键依赖
- 📦 **跨平台** - 支持 Windows (Winget)、macOS (Homebrew) 和 Linux
- 💾 **单二进制文件** - 无需依赖，单文件即可运行

## 📦 安装

### 一键安装（推荐）

#### Windows (PowerShell)

```powershell
# 一键安装最新版本
iex (irm https://cgartlab.com/SwiftInstall/install.ps1)

# 安装指定版本
iex (irm https://cgartlab.com/SwiftInstall/install.ps1) -Version "1.0.0"
```

#### Linux / macOS (Bash)

```bash
# 使用 curl 一键安装
curl -fsSL https://cgartlab.com/SwiftInstall/install.sh | bash

# 使用 wget 一键安装
wget -qO- https://cgartlab.com/SwiftInstall/install.sh | bash
```


### 环境一键准备（新）

安装 `sis` 后，执行以下单条命令即可自动完成环境检测、依赖准备与验证：

```bash
sis setup --auto-install-deps
```

可选：

- `--dry-run`：仅预览操作，不执行系统命令。
- `--auto-install-deps=false`：只做检测与验证，不自动安装依赖。

### 手动安装

从 [GitHub Releases](https://github.com/cgartlab/SwiftInstall/releases) 下载对应平台的二进制文件，解压后添加到系统 PATH。

### 从源码构建

**要求：**
- Go 1.21 或更高版本

```bash
# 克隆仓库
git clone https://github.com/cgartlab/SwiftInstall.git
cd SwiftInstall

# 构建
go build -o sis main.go

# 安装
go install
```

## 🚀 快速开始

### 命令行模式

```bash
# 安装配置中的所有软件
sis install

# 安装指定软件
sis install Git.Git Microsoft.VisualStudioCode

# 搜索软件（带查询参数）
sis search vscode

# 搜索软件（交互模式）
sis search

# 列出已配置的软件
sis list

# 检查系统状态
sis status

# 显示版本
sis version
```

### 交互式模式

直接运行 `sis` 命令启动交互式菜单：

```bash
sis
```

使用 **↑/↓ 箭头键** 导航，**Enter** 选择，**q** 退出。

## 📖 使用指南

### 配置文件

配置文件位于：
- **Windows:** `%USERPROFILE%\.si\config.yaml`
- **Linux/macOS:** `~/.si/config.yaml`

示例配置：

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

### 可用命令

| 命令 | 描述 |
|------|------|
| `sis` | 启动交互式主菜单 |
| `sis install [package...]` | 安装软件（无参数时从配置安装） |
| `sis uninstall [package...]` | 卸载软件（无参数时从配置卸载） |
| `sis uninstall-all` | 一键卸载配置中的全部软件 |
| `sis search [query]` | 搜索软件（无参数时进入交互搜索） |
| `sis list` | 列出已配置软件 |
| `sis config` | 配置管理 |
| `sis edit-list` | 用默认编辑器自由编辑安装列表 |
| `sis status` | 系统状态 |
| `sis version` | 版本信息 |
| `sis wizard` | 安装向导 |
| `sis clean` | 清理缓存 |
| `sis about` | 作者与项目信息 |
| `sis help` | 完整帮助文档（含参数、快捷键、示例） |
| `sis setup` | 环境一键准备 |


### 帮助文档与快捷键

#### 获取帮助

- 输入 `sis help` 查看完整帮助文档（功能模块、参数、快捷键、示例）
- 输入 `sis <命令> help` 或 `sis <命令> --help` 查看该命令简要说明
- 输入 `sis <命令> -h` 查看该命令简要说明

#### 交互式主菜单快捷键

| 快捷键 | 功能 |
|--------|------|
| `↑/↓` | 上下导航 |
| `Enter` | 确认进入选中项 |
| `i` | 快速安装 |
| `s` | 快速搜索 |
| `c` | 配置管理 |
| `a` | 关于作者（显示后可按任意键返回） |
| `q` | 退出程序 |

#### 安装界面快捷键

| 快捷键 | 功能 |
|--------|------|
| `a` | 显示关于信息（安装完成后） |
| `Enter` | 完成安装并退出 |
| `Esc` | 完成安装并退出 |
| `q` | 取消安装并退出 |

#### 搜索界面快捷键

| 快捷键 | 功能 |
|--------|------|
| `Enter` | 执行搜索 / 添加选中软件到配置 |
| `/` | 重新搜索 |
| `Esc` | 返回搜索输入框 |
| `q` | 退出搜索 |

#### 配置管理快捷键

| 快捷键 | 功能 |
|--------|------|
| `a` | 添加软件 |
| `Enter` / `e` | 编辑选中软件 |
| `d` / `r` | 删除选中软件 |
| `Tab` | 切换输入框（添加/编辑模式） |
| `q` | 返回主菜单 |

#### 关于页面快捷键

| 快捷键 | 功能 |
|--------|------|
| `任意键` | 返回主菜单 |

### 环境预检

首次运行安装或搜索命令时，会自动执行环境预检：
- 检测包管理器（Winget/Homebrew/ apt/dnf/pacman 等）
- 检查必要的系统命令
- 提供环境修复建议

### 自动更新检查

首次启动时会询问是否启用自动更新检查。可随时修改配置：
```bash
# 在配置文件中设置
auto_update_check: true  # 或 false
```

## 🖼️ 界面预览

### 主菜单

```
⚡ SwiftInstall ⚡

主菜单

> ⚡ 安装软件
  🗑️ 卸载软件
  🔍 搜索软件
  ⚙️ 配置管理
  📊 系统状态
  🧹 清理缓存
  🚪 退出

导航：↑/上 • ↓/下 • Enter 选择 • i 安装 • s 搜索 • c 配置 • a 关于 • q 退出
```

### 安装进度

```
软件安装

████████████████████░░░░░  75%

安装进度

Name                 ID                           Status
Git                  Git.Git                      ✓ 成功
Visual Studio Code   Microsoft.VisualStudioCode   ✓ 成功
7-Zip                7zip.7zip                    ◉ 安装中

✓ 已完成：2  ✗ 失败：0  ⊘ 跳过：1

Exit: Enter/Esc | About: a | Quit: q
```

### 搜索界面

```
搜索软件

> vscode

搜索结果：3

Name                     ID                              Publisher
Visual Studio Code       Microsoft.VisualStudioCode      Microsoft
VSCode Insiders          Microsoft.VisualStudioCode...   Microsoft
VSCodium                 VSCodium.VSCodium               VSCodium

Add: Enter | Refine: / | Back: Esc | Quit: q
```

### 关于页面

```
███████╗██╗    ██╗██╗███████╗████████╗
██╔════╝██║    ██║██║██╔════╝╚══██╔══╝
███████╗██║ █╗ ██║██║█████╗     ██║
╚════██║██║███╗██║██║██╔══╝     ██║
███████║╚███╔███╔╝██║██║        ██║
╚══════╝ ╚══╝╚══╝ ╚═╝╚═╝        ╚═╝

关于 SwiftInstall
作者：CGArtLab
联系方式：https://cgartlab.com
GitHub: https://github.com/cgartlab/SwiftInstall
© 2026 CGArtLab. All rights reserved.

Press any key to go back
```

## 🏗️ 技术栈

- **Go 1.21+** - 编程语言
- **[Bubble Tea](https://github.com/charmbracelet/bubbletea)** - TUI 框架
- **[Lipgloss](https://github.com/charmbracelet/lipgloss)** - 样式库
- **[Cobra](https://github.com/spf13/cobra)** - CLI 框架
- **[Viper](https://github.com/spf13/viper)** - 配置管理
- **[YAML](https://yaml.org/)** - 配置文件格式

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📝 许可证

本项目采用 [CC BY-NC 4.0](LICENSE) 许可证。

## 🙏 致谢

- [Bubble Tea](https://github.com/charmbracelet/bubbletea) - 强大的 TUI 框架
- [Lipgloss](https://github.com/charmbracelet/lipgloss) - 优雅的样式库
- [Mole](https://github.com/tw93/Mole) - 界面风格参考

---

<p align="center">
  Made with ❤️ by <a href="https://cgartlab.com">CGArtLab</a>
</p>
