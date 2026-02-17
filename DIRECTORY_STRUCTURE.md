# Directory Structure | 目录结构说明

This document explains the organization and purpose of each directory in the SwiftInstall project.

本文档说明 SwiftInstall 项目中各目录的组织结构和用途。

---

## Root Directory | 根目录

```
Software_Install_Script/
```

### Core Files | 核心文件

| File | Description | 描述 |
|------|-------------|------|
| `README.md` | Main documentation (English/Chinese) | 主文档（中英文） |
| `README.zh.md` | Chinese documentation | 中文文档 |
| `README_CLI.md` | CLI detailed documentation | CLI 详细文档 |
| `LICENSE-2.0` | MIT License file | MIT 许可证文件 |
| `setup.py` | Python package setup | Python 包配置 |
| `requirements.txt` | Python dependencies | Python 依赖项 |
| `index.html` | Project website | 项目官网页面 |

### Installation Files | 安装文件

| File | Description | 描述 |
|------|-------------|------|
| `install.py` | Online installer (cross-platform) | 在线安装器（跨平台） |
| `install_global.bat` | Windows global installer | Windows 全局安装脚本 |
| `install_global.ps1` | Windows PowerShell installer | Windows PowerShell 安装脚本 |
| `macos_installer.sh` | macOS shell installer | macOS Shell 安装脚本 |
| `windows_installer.bat` | Windows batch installer | Windows 批处理安装脚本 |
| `online_install.ps1` | Windows online installer | Windows 在线安装脚本 |
| `sis.bat` | Windows shortcut | Windows 快捷方式 |
| `sis.ps1` | PowerShell shortcut | PowerShell 快捷方式 |

---

## 📁 docs/ - Documentation | 文档

Contains project documentation and guides.

存放项目文档和指南。

**Contents | 内容：**
- User guides | 用户指南
- API documentation | API 文档
- Troubleshooting guides | 故障排除指南

---

## 📁 scripts/ - Installation Scripts | 安装脚本

Platform-specific installation scripts.

平台特定的安装脚本。

### 📁 scripts/windows/ - Windows Scripts | Windows 脚本

| File | Description | 描述 |
|------|-------------|------|
| `software_install.bat` | Main installation script | 主安装脚本 |
| `software_install_proxy.bat` | Installation with proxy support | 带代理支持的安装脚本 |
| `software_list.txt` | Software package list | 软件包列表 |
| `switch_winget_to_USTCsource.bat` | Switch to USTC mirror | 切换到中科大镜像源 |

### 📁 scripts/macos/ - macOS Scripts | macOS 脚本

| File | Description | 描述 |
|------|-------------|------|
| `install_packages.sh` | Main installation script | 主安装脚本 |
| `packages.txt` | Software package list | 软件包列表 |

---

## 📁 sis/ - Main Package | 主程序包

Core Python package containing all application logic.

核心 Python 包，包含所有应用程序逻辑。

### Core Modules | 核心模块

| File | Description | 描述 |
|------|-------------|------|
| `__init__.py` | Package initialization | 包初始化 |
| `main.py` | Entry point & CLI | 入口点和命令行接口 |
| `installer.py` | Core installation logic | 核心安装逻辑 |
| `ui.py` | UI components & styling | UI 组件和样式 |
| `guided_ui.py` | Interactive TUI wizard | 交互式 TUI 向导 |
| `i18n.py` | Internationalization | 国际化支持 |

### Environment Modules | 环境模块

| File | Description | 描述 |
|------|-------------|------|
| `env_check.py` | Environment detection | 环境检测 |
| `env_manager.py` | Environment management | 环境管理 |
| `sandbox_handler.py` | Sandbox detection | 沙盒检测 |

### Utility Modules | 工具模块

| File | Description | 描述 |
|------|-------------|------|
| `batch_installer.py` | Batch installation | 批量安装 |
| `config.py` | Configuration management | 配置管理 |
| `error_handler.py` | Error handling | 错误处理 |
| `logo.py` | ASCII art & branding | ASCII 艺术和品牌 |
| `themes.py` | Color themes | 颜色主题 |
| `update_checker.py` | Update checking | 更新检查 |

---

## 📁 tests/ - Test Files | 测试文件

Contains unit tests and integration tests.

存放单元测试和集成测试。

**Contents | 内容：**
- Unit tests | 单元测试
- Integration tests | 集成测试
- Test fixtures | 测试夹具

---

## 📁 assets/ - Static Assets | 静态资源

Static files for the project.

项目的静态文件。

**Contents | 内容：**
- Images | 图片
- Icons | 图标
- Fonts | 字体
- Other static resources | 其他静态资源

---

## 📁 .github/ - GitHub Configuration | GitHub 配置

GitHub-specific files and workflows.

GitHub 特定的文件和工作流。

**Contents | 内容：**
- `workflows/` - GitHub Actions CI/CD
- `FUNDING.yml` - Sponsorship configuration

---

## Legacy Directories | 旧版目录

The following directories are maintained for backward compatibility:

以下目录为保持向后兼容性而保留：

### 📁 Windows/ (Legacy) | Windows/（旧版）

Original Windows scripts location.

原始 Windows 脚本位置。

> ⚠️ **Note**: New scripts should be placed in `scripts/windows/`
> 
> ⚠️ **注意**: 新脚本应放在 `scripts/windows/` 中

### 📁 macOS/ (Legacy) | macOS/（旧版）

Original macOS scripts location.

原始 macOS 脚本位置。

> ⚠️ **Note**: New scripts should be placed in `scripts/macos/`
> 
> ⚠️ **注意**: 新脚本应放在 `scripts/macos/` 中

---

## File Naming Conventions | 文件命名规范

### Scripts | 脚本

- Use lowercase with underscores | 使用小写和下划线
- Be descriptive | 描述性命名
- Include platform suffix when needed | 需要时包含平台后缀

Examples | 示例：
- `software_install.bat` ✓
- `SoftwareInstall.bat` ✗
- `macos_installer.sh` ✓

### Python Modules | Python 模块

- Use lowercase with underscores | 使用小写和下划线
- Follow PEP 8 naming conventions | 遵循 PEP 8 命名规范

Examples | 示例：
- `batch_installer.py` ✓
- `BatchInstaller.py` ✗
- `error_handler.py` ✓

---

## Contributing | 贡献

When adding new files, please follow this directory structure:

添加新文件时，请遵循此目录结构：

1. **Documentation** → `docs/`
2. **Scripts** → `scripts/<platform>/`
3. **Tests** → `tests/`
4. **Assets** → `assets/`
5. **Core code** → `sis/`

---

<p align="center">
  <sub>Last updated | 最后更新: 2026-02-17</sub>
</p>
