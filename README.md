# SwiftInstall

<p align="center">
  <img src="https://raw.githubusercontent.com/yourusername/swiftinstall/main/assets/logo.png" alt="SwiftInstall Logo" width="200">
</p>

<p align="center">
  <b>⚡ 快速、简单、可靠的跨平台软件安装工具</b>
</p>

<p align="center">
  <a href="https://github.com/yourusername/swiftinstall/releases">
    <img src="https://img.shields.io/github/v/release/yourusername/swiftinstall?style=flat-square&color=blue" alt="Release">
  </a>
  <a href="https://goreportcard.com/report/github.com/yourusername/swiftinstall">
    <img src="https://goreportcard.com/badge/github.com/yourusername/swiftinstall?style=flat-square" alt="Go Report Card">
  </a>
  <a href="https://github.com/yourusername/swiftinstall/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/yourusername/swiftinstall?style=flat-square&color=green" alt="License">
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

### 手动安装

从 [GitHub Releases](https://github.com/yourusername/swiftinstall/releases) 下载对应平台的二进制文件，解压后添加到系统 PATH。

### 从源码构建

**要求：**
- Go 1.21 或更高版本

```bash
# 克隆仓库
git clone https://github.com/yourusername/swiftinstall.git
cd swiftinstall

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

# 搜索软件
sis search vscode

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
| `sis install [package...]` | 安装软件 |
| `sis uninstall [package...]` | 卸载软件 |
| `sis search <query>` | 搜索软件 |
| `sis list` | 列出已配置软件 |
| `sis config` | 配置管理 |
| `sis status` | 系统状态 |
| `sis version` | 版本信息 |
| `sis wizard` | 安装向导 |
| `sis clean` | 清理缓存 |

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

导航: ↑/k 上 • ↓/j 下 • Enter 选择 • q 退出
```

### 安装进度

```
软件安装

████████████████████░░░░░  75%

安装中...

Name                 ID                           Status
Git                  Git.Git                      ✓ 成功
Visual Studio Code   Microsoft.VisualStudioCode   ✓ 成功
7-Zip                7zip.7zip                    ◉ 安装中
```

## 🏗️ 技术栈

- **Go 1.21+** - 编程语言
- **[Bubble Tea](https://github.com/charmbracelet/bubbletea)** - TUI 框架
- **[Lipgloss](https://github.com/charmbracelet/lipgloss)** - 样式库
- **[Cobra](https://github.com/spf13/cobra)** - CLI 框架
- **[Viper](https://github.com/spf13/viper)** - 配置管理

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📝 许可证

本项目采用 [MIT](LICENSE) 许可证。

## 🙏 致谢

- [Bubble Tea](https://github.com/charmbracelet/bubbletea) - 强大的 TUI 框架
- [Lipgloss](https://github.com/charmbracelet/lipgloss) - 优雅的样式库
- [Mole](https://github.com/tw93/Mole) - 界面风格参考

---

<p align="center">
  Made with ❤️ by <a href="https://cgartlab.com">CGArtLab</a>
</p>
