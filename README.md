# SwiftInstall

<div align="center">
  <br>
  <code>
    ╭────────────────────────────────────────────╮
    │     ⚡  ╭──────────╮  ⚡                   │
    │        │  📦📦📦  │                        │
    │     ═══╡  📦📦📦  ╞═══                    │
    │        │  📦📦📦  │                        │
    │     ⚡  ╰──────────╯  ⚡                   │
    │                                            │
    │        SwiftInstall                        │
    │        Fast • Simple • Reliable            │
    ╰────────────────────────────────────────────╯
  </code>
  <br><br>
  <strong>跨平台软件批量安装工具</strong>
  <br>
  基于 Winget (Windows) 和 Homebrew (macOS)
</div>

---

## ✨ 功能特性

- **批量安装** - 一键安装多个软件，支持并行安装
- **跨平台** - 支持 Windows (Winget) 和 macOS (Homebrew)
- **智能搜索** - 内置软件搜索功能
- **安装队列** - 可视化队列管理
- **自动检测** - 自动识别系统和包管理器
- **多语言** - 支持中英文界面
- **环境检测** - 安装前自动检测系统兼容性
- **沙盒识别** - 自动识别沙盒/虚拟机环境
- **热刷新** - 环境变量更新无需重启终端
- **自动化脚本** - 支持导出 PowerShell/Bash/Python 脚本
- **详细日志** - 完整的安装日志记录
- **全局命令** - 安装后可在任意目录使用 `sis` 命令

---

## 🚀 快速开始

### 在线安装（推荐）

```powershell
# PowerShell 在线安装（推荐使用自定义域名）
ipmo install -Name Microsoft.PowerShell.Utility -Force -Confirm:$false
try {
    # 尝试使用自定义域名（推荐）
    $scriptUrl = "https://cgartlab.com/Software_Install_Script/online_install.ps1"
    $script = Invoke-RestMethod -Uri $scriptUrl -ErrorAction Stop
    Write-Output "✅ 成功从自定义域名获取安装脚本"
} catch {
    # 备用：使用 GitHub raw URL
    $scriptUrl = "https://raw.githubusercontent.com/cgartlab/Software_Install_Script/main/online_install.ps1"
    $script = Invoke-RestMethod -Uri $scriptUrl -ErrorAction Stop
    Write-Output "✅ 成功从 GitHub 获取安装脚本"
}

# 执行安装脚本
Write-Output "🚀 开始安装 SwiftInstall..."
eval $script
```

### 本地安装

```bash
# 克隆仓库
git clone https://github.com/cgartlab/Software_Install_Script.git
cd Software_Install_Script

# 安装依赖
pip install -r requirements.txt

# 安装全局命令（可选，安装后可在任意目录使用 'sis' 命令）
powershell -ExecutionPolicy Bypass -File install_global.ps1

# 启动图形化向导
sis wizard
# 或
python -m sis.main wizard
```

---

## 🌐 在线访问

项目提供了现代化的在线访问页面：

- **官方网站**：[https://cgartlab.com/Software_Install_Script/](https://cgartlab.com/Software_Install_Script/)
- **GitHub 仓库**：[https://github.com/cgartlab/Software_Install_Script](https://github.com/cgartlab/Software_Install_Script)

---

## 📖 使用说明

### 全局命令安装

安装后，`sis` 命令可以在任意目录下使用：

```powershell
# Windows - 运行安装脚本
powershell -ExecutionPolicy Bypass -File install_global.ps1

# 或使用批处理脚本
install_global.bat

# 安装后重启终端，即可全局使用
sis --help
sis wizard
sis check
```

> **注意**：安装后需要重启终端或运行 `$env:PATH = [Environment]::GetEnvironmentVariable('PATH', 'User')` 刷新环境变量。

### CLI 命令

```bash
# 启动图形化安装向导（推荐）
sis wizard

# 系统环境检查
sis check

# 批量安装（并行模式）
sis batch --parallel

# 批量安装（顺序模式）
sis batch --sequential

# 从配置文件安装
sis batch -c config.json

# 启动 TUI 界面
sis tui

# 配置软件列表
sis config

# 导出自动化脚本
sis export --format powershell -o install.ps1
sis export --format bash -o install.sh
sis export --format python -o install.py
sis export --format json -o config.json

# 刷新环境变量（无需重启终端）
sis refresh

# 查看安装日志
sis logs

# 切换语言
sis lang zh    # 中文
sis lang en    # English

# 显示版本
sis version
```

### 主菜单功能（TUI 模式）

| 选项 | 功能 |
|------|------|
| 1 | 安装软件 - 批量安装配置列表中的软件 |
| 2 | 配置软件列表 - 添加/删除软件 |
| 3 | 搜索软件 - 搜索并添加到安装队列 |
| 4 | 设置 - 程序设置 |
| 5 | 退出 |

---

## 💻 系统要求

**Windows**
- Windows 10 (1809+) / Windows 11
- Windows Package Manager (Winget)
- PowerShell 7+（推荐）
- Python 3.8+

**macOS**
- macOS 10.15+
- Homebrew
- Python 3.8+

---

## ⚙️ 配置文件

配置文件位置：`~/.sis/config.yaml`

```yaml
software:
  - name: Visual Studio Code
    id: Microsoft.VisualStudioCode
    category: Development
  - name: Google Chrome
    package: google-chrome
    category: Browsers
```

---

## 📁 项目结构

```
Software_Install_Script/
├── sis/                    # 主程序模块
│   ├── main.py            # CLI 入口
│   ├── installer.py       # 安装器
│   ├── config.py          # 配置管理
│   ├── env_check.py       # 环境检测
│   ├── env_manager.py     # 环境变量管理
│   ├── error_handler.py   # 错误处理
│   ├── batch_installer.py # 批量安装
│   ├── sandbox_handler.py # 沙盒处理
│   ├── guided_ui.py       # 图形向导
│   ├── i18n.py            # 国际化
│   └── ui.py              # UI 组件
├── online_install.ps1     # 在线安装脚本
├── install_global.ps1     # 全局安装脚本
├── install_global.bat     # 全局安装批处理脚本
├── install.py             # 安装入口脚本
├── index.html             # GitHub Pages 主页
├── requirements.txt       # Python 依赖
└── README.md              # 项目文档
```

---

## ❓ 常见问题

### 如何查找软件 ID？

- **Windows**: `winget search 软件名`
- **macOS**: `brew search 软件名`

### 安装失败怎么办？

1. 运行 `sis check` 检查系统环境
2. 检查网络连接
3. 确认包管理器可用
4. 尝试管理员权限运行
5. 查看 `~/.sis/logs/` 目录下的日志文件

### 环境变量更新后需要重启终端吗？

不需要。运行 `sis refresh` 即可热刷新环境变量。

### 如何在沙盒环境中使用？

程序会自动检测沙盒环境并提供相应的解决方案建议。部分功能可能受限。

### 在线安装时遇到 404 错误怎么办？

1. 检查网络连接
2. 尝试使用备用安装方法
3. 确保 GitHub 访问正常
4. 尝试直接下载并运行安装脚本

---

## 🔧 故障排除

### 网络问题

- 确保网络连接正常
- 检查防火墙设置
- 尝试使用 VPN 或代理

### 权限问题

- 以管理员权限运行终端
- 确保用户有足够的权限修改系统设置

### 包管理器问题

- **Windows**: 运行 `winget --version` 检查 Winget 是否正常
- **macOS**: 运行 `brew doctor` 检查 Homebrew 是否正常

### Python 问题

- 确保 Python 3.8+ 已安装
- 检查 `pip` 是否可用
- 尝试升级 pip: `python -m pip install --upgrade pip`

---

## 📄 许可证

[MIT License](LICENSE)

---

<div align="center">
  <sub>Made with ❤️ | Fast • Simple • Reliable</sub>
</div>