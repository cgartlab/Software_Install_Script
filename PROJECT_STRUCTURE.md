# SwiftInstall Go 重构版 - 项目结构说明

## 📁 项目结构

```
swiftinstall/
├── main.go                          # 程序入口
├── go.mod                           # Go 模块定义
├── Makefile                         # 构建脚本
├── README.md                        # 项目说明
├── PROJECT_STRUCTURE.md             # 本文档
│
├── cmd/                             # 命令行接口层
│   └── root.go                      # Cobra 根命令定义，包含所有子命令
│
└── internal/                        # 内部包
    ├── config/                      # 配置管理
    │   └── config.go               # 配置文件读写、软件列表管理
    │
    ├── i18n/                        # 国际化
    │   └── i18n.go                 # 多语言翻译支持（中/英）
    │
    ├── installer/                   # 安装器核心
    │   └── installer.go            # Windows/macOS 安装器实现
    │
    └── ui/                          # TUI 界面层
        ├── styles.go               # Lipgloss 样式定义
        ├── logo.go                 # Logo ASCII 艺术
        ├── menu.go                 # 主菜单界面
        ├── install.go              # 安装/卸载界面
        ├── search.go               # 搜索界面
        └── config.go               # 配置管理界面
```

## 📦 包说明

### cmd/root.go
- 使用 Cobra 框架定义 CLI 命令结构
- 包含所有子命令：install, uninstall, search, list, config, wizard, batch, export, update, clean, status
- 处理全局标志：--config, --lang
- 初始化配置和语言设置

### internal/config/config.go
- 使用 Viper 进行配置管理
- YAML 格式的配置文件存储在 `~/.si/config.yaml`
- 支持软件列表的增删改查
- 支持配置导入导出

### internal/i18n/i18n.go
- 内置中英文翻译
- 支持运行时语言切换
- 使用 `T(key)` 函数获取翻译文本

### internal/installer/installer.go
- 定义 Installer 接口
- WindowsInstaller：使用 winget 命令
- MacOSInstaller：使用 brew 命令
- 支持批量安装（并行/串行）
- 支持搜索、检查安装状态

### internal/ui/*.go
- 使用 Bubble Tea TUI 框架
- 基于 Elm 架构（Model-Update-View）
- Lipgloss 用于样式美化

#### styles.go
- 定义颜色常量（Indigo 主题）
- 定义各种 UI 组件样式
- 状态图标和样式映射

#### logo.go
- ASCII Logo 艺术
- 多种尺寸：full, compact, minimal

#### menu.go
- 主菜单界面
- 使用 bubbles/list 组件
- 支持键盘导航

#### install.go
- 安装进度界面
- 实时进度条
- 安装状态表格
- 支持并行安装

#### search.go
- 软件搜索界面
- 文本输入框
- 搜索结果表格
- 支持添加到配置

#### config.go
- 配置管理界面
- 列表/添加/编辑/删除 模式
- 表单输入验证

## 🎨 界面风格（参考 Mole）

### 颜色主题
- Primary: #6366f1 (Indigo)
- Accent: #10b981 (Emerald/Success)
- Warning: #f59e0b (Amber)
- Error: #ef4444 (Red)
- Info: #3b82f6 (Blue)

### 交互设计
- 方向键导航
- Enter 确认
- q 退出
- 清晰的视觉反馈

## 🚀 构建说明

### 环境要求
- Go 1.21+
- Windows: winget
- macOS: Homebrew

### 构建命令
```bash
# 安装依赖
go mod download

# 构建当前平台
go build -o bin/si main.go

# 使用 Makefile
make build
make build-all
```

### 运行
```bash
# 交互式模式
./si

# 命令行模式
./si install
./si search vscode
./si config
```

## 📝 与原 Python 版本的对比

| 特性 | Python 版 | Go 版 |
|------|----------|-------|
| 界面框架 | Rich + questionary | Bubble Tea |
| CLI 框架 | Click | Cobra |
| 配置管理 | PyYAML | Viper |
| 性能 | 解释执行 | 编译执行 |
| 单文件大小 | 依赖较多 | 单二进制文件 |
| 交互体验 | 良好 | 更流畅 |
| 跨平台构建 | 复杂 | 简单 (交叉编译) |

## 🔧 扩展建议

1. **添加更多平台支持**
   - Linux (apt, yum, pacman)
   - 通用包管理器 (snap, flatpak)

2. **增强功能**
   - 软件版本管理
   - 安装脚本自定义
   - 批量导入导出
   - 安装历史记录

3. **UI 改进**
   - 更多主题
   - 自定义颜色
   - 鼠标支持

4. **网络功能**
   - 远程配置同步
   - 软件仓库管理
   - 更新通知

## 📄 许可证

MIT License
