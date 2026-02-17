# SwiftInstall

<p align="center">
  <strong>跨平台软件批量安装工具</strong><br>
  <a href="./README.zh.md">简体中文</a> | <a href="./README.md">English</a>
</p>

---

## 概述

SwiftInstall 是一款支持 Windows 和 macOS 的现代化批量软件安装 CLI 工具，具备向导式安装、环境检测和并行处理功能。

## 功能特性

| 功能 | 描述 |
|------|------|
| 🎨 向导安装 | 交互式 TUI，支持双语 |
| 🔍 环境检测 | 自动检测系统环境 |
| 🚀 批量安装 | 4 线程并行安装 |
| ⚙️ 热刷新 | 无需重启刷新环境变量 |
| 📝 脚本导出 | 导出 PowerShell/Bash/Python 脚本 |
| 🛡️ 沙盒检测 | 自动检测沙盒环境 |

## 快速开始

| 平台 | 命令 |
|------|------|
| Windows | `irm https://cgartlab.com/Software_Install_Script/install.py \| python3` |
| macOS | `curl -fsSL https://cgartlab.com/Software_Install_Script/install.py \| python3` |

## 使用方法

| 命令 | 功能 |
|------|------|
| `sis wizard` | 启动向导 |
| `sis check` | 检查环境 |
| `sis batch` | 批量安装 |
| `sis refresh` | 刷新环境 |
| `sis export` | 导出脚本 |
| `sis --help` | 显示帮助 |

## 项目结构

```
Software_Install_Script/
├── docs/           # 文档
├── scripts/        # 安装脚本
│   ├── windows/
│   └── macos/
├── sis/            # 主 Python 包
├── assets/         # 静态资源
├── tests/          # 测试文件
├── install.py      # 在线安装器
└── setup.py        # 包配置
```

## 系统要求

| 平台 | 要求 |
|------|------|
| Windows | Windows 10/11, PowerShell 5.1+, Python 3.7+, Winget |
| macOS | macOS 10.15+, 终端, Python 3.7+, Homebrew |

## 文档

- [完整文档](./README_CLI.md)
- [问题反馈](https://github.com/cgartlab/Software_Install_Script/issues)

## 许可证

[MIT License](LICENSE-2.0)

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/cgartlab">cgartlab</a> · © 2026 SwiftInstall
</p>
