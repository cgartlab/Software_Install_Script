# SwiftInstall

<p align="center">
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
</p>

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

---

## 🚀 快速开始

```bash
# 克隆仓库
git clone https://github.com/cgartlab/Software_Install_Script.git
cd Software_Install_Script

# 安装依赖
pip install -r requirements.txt

# 启动图形化向导
python -m sis.main wizard
```

---

## 📖 使用说明

### CLI 命令

```bash
# 启动图形化安装向导（推荐）
python -m sis.main wizard

# 系统环境检查
python -m sis.main check

# 批量安装（并行模式）
python -m sis.main batch --parallel

# 批量安装（顺序模式）
python -m sis.main batch --sequential

# 从配置文件安装
python -m sis.main batch -c config.json

# 启动 TUI 界面
python -m sis.main tui

# 配置软件列表
python -m sis.main config

# 导出自动化脚本
python -m sis.main export --format powershell -o install.ps1
python -m sis.main export --format bash -o install.sh
python -m sis.main export --format python -o install.py
python -m sis.main export --format json -o config.json

# 刷新环境变量（无需重启终端）
python -m sis.main refresh

# 查看安装日志
python -m sis.main logs

# 切换语言
python -m sis.main lang zh    # 中文
python -m sis.main lang en    # English

# 显示版本
python -m sis.main version
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

**macOS**
- macOS 10.15+
- Homebrew

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
├── Windows/               # Windows 批处理脚本
├── macOS/                 # macOS Shell 脚本
├── requirements.txt       # Python 依赖
└── setup.py              # 安装配置
```

---

## ❓ 常见问题

**Q: 如何查找软件 ID？**

Windows: `winget search 软件名`

macOS: `brew search 软件名`

**Q: 安装失败怎么办？**

1. 运行 `python -m sis.main check` 检查系统环境
2. 检查网络连接
3. 确认包管理器可用
4. 尝试管理员权限运行
5. 查看 `~/.sis/logs/` 目录下的日志文件

**Q: 环境变量更新后需要重启终端吗？**

不需要。运行 `python -m sis.main refresh` 即可热刷新环境变量。

**Q: 如何在沙盒环境中使用？**

程序会自动检测沙盒环境并提供相应的解决方案建议。部分功能可能受限。

---

## 📄 许可证

[MIT License](LICENSE)

---

<p align="center">
  <sub>Made with ❤️ | Fast • Simple • Reliable</sub>
</p>
