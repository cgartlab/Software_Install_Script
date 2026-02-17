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

- **批量安装** - 一键安装多个软件
- **跨平台** - 支持 Windows (Winget) 和 macOS (Homebrew)
- **智能搜索** - 内置软件搜索功能
- **安装队列** - 可视化队列管理
- **自动检测** - 自动识别系统和包管理器
- **多语言** - 支持中英文界面

---

## 🚀 快速开始

```bash
# 在线安装
curl -fsSL https://raw.githubusercontent.com/cgartlab/Software_Install_Script/main/install.py | python3

# 或手动安装
git clone https://github.com/cgartlab/Software_Install_Script.git
cd Software_Install_Script
pip install -r requirements.txt
python3 -m sis.main tui
```

---

## 📖 使用说明

### 启动 TUI 界面

```bash
python3 -m sis.main tui
```

### 主菜单功能

| 选项 | 功能 |
|------|------|
| 1 | 安装软件 - 批量安装配置列表中的软件 |
| 2 | 配置软件列表 - 添加/删除软件 |
| 3 | 搜索软件 - 搜索并添加到安装队列 |
| 4 | 设置 - 程序设置 |
| 5 | 退出 |

### CLI 命令

```bash
python3 -m sis.main version    # 显示版本
python3 -m sis.main install    # 直接安装
python3 -m sis.main config     # 配置管理
```

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

## ❓ 常见问题

**Q: 如何查找软件 ID？**

Windows: `winget search 软件名`

macOS: `brew search 软件名`

**Q: 安装失败怎么办？**

1. 检查网络连接
2. 确认包管理器可用
3. 尝试管理员权限运行

---

## 📄 许可证

[MIT License](LICENSE)

---

<p align="center">
  <sub>Made with ❤️ | Fast • Simple • Reliable</sub>
</p>
