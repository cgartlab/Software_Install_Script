# SwiftInstall 开发笔记

## 项目结构

```
SwiftInstall/
├── main.go                     # 程序入口
├── cmd/
│   ├── root.go                 # Cobra 根命令和子命令定义
│   └── release/                # 发布工具
│       └── main.go
├── internal/
│   ├── appinfo/                # 应用信息（作者、联系方式等）
│   │   └── appinfo.go
│   ├── config/                 # 配置管理
│   │   └── config.go
│   ├── i18n/                   # 国际化
│   │   └── i18n.go
│   ├── installer/              # 安装器实现
│   │   ├── installer.go        # 安装器接口和实现
│   │   ├── preflight.go        # 环境预检
│   │   ├── bootstrap.go        # 引导程序
│   │   ├── linux.go            # Linux 支持
│   │   └── command.go
│   └── ui/                     # TUI 界面
│       ├── menu.go             # 主菜单
│       ├── install.go          # 安装界面
│       ├── search.go           # 搜索界面
│       ├── config.go           # 配置管理界面
│       ├── about.go            # 关于页面
│       ├── styles.go           # 样式定义
│       └── logo.go             # Logo 定义
├── docs/                       # 文档
│   ├── QUICKSTART.md           # 快速入门
│   ├── COMMAND_REFERENCE.md    # 命令参考
│   ├── AUTO_RELEASE_GUIDE.md   # 自动发布指南
│   └── AUTO_RELEASE_LOGIC.md   # 自动发布逻辑
├── bin/                        # 编译输出
├── release/                    # 发布包
└── *.md                        # 项目文档
```

## 技术栈

### 核心依赖

| 库 | 用途 | 版本 |
|----|------|------|
| `github.com/spf13/cobra` | CLI 框架 | v1.8.0 |
| `github.com/spf13/viper` | 配置管理 | v1.18.2 |
| `github.com/charmbracelet/bubbletea` | TUI 框架 | v0.25.0 |
| `github.com/charmbracelet/bubbles` | TUI 组件 | v0.18.0 |
| `github.com/charmbracelet/lipgloss` | 样式库 | v0.10.0 |
| `gopkg.in/yaml.v3` | YAML 解析 | v3.0.1 |

### Go 版本要求

- Go 1.21+

## 构建命令

```bash
# 当前平台
go build -o sis main.go

# 所有平台
make build-all

# 仅 Windows
make build-windows

# 仅 Linux
make build-linux

# 仅 macOS
make build-darwin

# 创建发布包
make release
```

## 命令注册

所有命令在 `cmd/root.go` 的 `init()` 函数中注册：

```go
func init() {
    cobra.OnInitialize(initConfig)
    
    rootCmd.AddCommand(versionCmd)
    rootCmd.AddCommand(installCmd)
    rootCmd.AddCommand(uninstallCmd)
    rootCmd.AddCommand(searchCmd)
    rootCmd.AddCommand(listCmd)
    rootCmd.AddCommand(configCmd)
    rootCmd.AddCommand(wizardCmd)
    rootCmd.AddCommand(batchCmd)
    rootCmd.AddCommand(exportCmd)
    rootCmd.AddCommand(updateCmd)
    rootCmd.AddCommand(cleanCmd)
    rootCmd.AddCommand(statusCmd)
    rootCmd.AddCommand(aboutCmd)
    rootCmd.AddCommand(helpDocCmd)
    rootCmd.AddCommand(uninstallAllCmd)
    rootCmd.AddCommand(editListCmd)
    rootCmd.AddCommand(setupCmd)
}
```

## TUI 架构

### 模型（Model）

每个界面都是一个 TUI 模型，实现 `tea.Model` 接口：

```go
type Model interface {
    Init() Cmd
    Update(Msg) (Model, Cmd)
    View() string
}
```

### 消息循环

```
用户输入 → Update() → 更新状态 → View() → 渲染
          ↓
       返回 Cmd → 执行副作用 → 返回 Msg → Update()
```

### 样式系统

样式在 `ui/styles.go` 中统一定义：

```go
var (
    TitleStyle = lipgloss.NewStyle().
                Foreground(lipgloss.Color(ColorPrimary)).
                Bold(true)
    
    SuccessStyle = lipgloss.NewStyle().
                  Foreground(lipgloss.Color(ColorAccent)).
                  Bold(true)
    
    ErrorStyle = lipgloss.NewStyle().
                Foreground(lipgloss.Color(ColorError)).
                Bold(true)
)
```

## 配置管理

### 配置结构

```go
type Config struct {
    viper      *viper.Viper
    configFile string
    software   []Software
    mu         sync.RWMutex
}

type Software struct {
    Name     string
    ID       string
    Package  string
    Category string
    Version  string
    Source   string
}
```

### 配置流程

```
Init() → load() → setDefaults() → loadFromFile()
                      ↓
                  createDefaultConfig()
```

## 安装器接口

```go
type Installer interface {
    Install(packageID string) (*InstallResult, error)
    Uninstall(packageID string) (*InstallResult, error)
    Search(query string) ([]PackageInfo, error)
    IsInstalled(packageID string) (bool, error)
    GetInstalled() ([]PackageInfo, error)
    Update() error
}
```

### 实现

- `WindowsInstaller` - Winget
- `MacOSInstaller` - Homebrew
- `LinuxInstaller` - apt/dnf/pacman

## 国际化

### 支持的语言

- 中文 (zh)
- 英文 (en)

### 使用方式

```go
import "swiftinstall/internal/i18n"

text := i18n.T("key_name")
```

### 翻译文件

翻译在 `internal/i18n/i18n.go` 中定义：

```go
translations = map[string]map[string]string{
    "zh": {
        "app_name": "SwiftInstall",
        // ...
    },
    "en": {
        "app_name": "SwiftInstall",
        // ...
    },
}
```

## 并发控制

### 安装并发

```go
semaphore := make(chan struct{}, 4)  // 最多 4 个并发
for _, pkg := range packages {
    go func() {
        semaphore <- struct{}{}
        defer func() { <-semaphore }()
        // 安装逻辑
    }()
}
```

### Mutex 保护

```go
type InstallModel struct {
    mu sync.Mutex
    // ...
}

func (m *InstallModel) update() {
    m.mu.Lock()
    defer m.mu.Unlock()
    // 更新共享数据
}
```

## 错误处理

### 错误模式

```go
// 验证错误
if err := validatePackageID(packageID); err != nil {
    return &InstallResult{Status: StatusFailed, Error: err}
}

// 平台不支持
inst := installer.NewInstaller()
if inst == nil {
    return fmt.Errorf("unsupported platform")
}

// Panic 恢复
defer func() {
    if r := recover(); r != nil {
        result = &InstallResult{
            Status: StatusFailed,
            Error:  fmt.Errorf("panic: %v", r),
        }
    }
}()
```

## 测试

### 运行测试

```bash
# 所有测试
go test ./...

# 带覆盖率
go test -cover ./...

# 特定包
go test ./internal/installer/
```

### 测试文件

- `internal/installer/installer_test.go`
- `internal/config/config_test.go`
- `internal/i18n/i18n_test.go`
- `cmd/root_test.go`

## 发布流程

### 手动发布

1. 更新 `CHANGELOG.md`
2. 提交更改
3. 创建 Git 标签
4. 运行 `make release`
5. 上传到 GitHub Releases

### 自动化发布

参考 `docs/AUTO_RELEASE_GUIDE.md`

## 常见问题

### Q: 如何添加新命令？

```go
// 1. 在 cmd/root.go 中定义命令
var newCmd = &cobra.Command{
    Use:   "newcmd",
    Short: "新命令简述",
    Run: func(cmd *cobra.Command, args []string) {
        runNewCmd()
    },
}

// 2. 在 init() 中注册
func init() {
    rootCmd.AddCommand(newCmd)
}

// 3. 实现执行函数
func runNewCmd() {
    // 实现逻辑
}
```

### Q: 如何添加新的 TUI 界面？

```go
// 1. 创建模型
type MyModel struct {
    // 状态字段
}

// 2. 实现 tea.Model 接口
func (m MyModel) Init() tea.Cmd { ... }
func (m MyModel) Update(msg tea.Msg) (tea.Model, tea.Cmd) { ... }
func (m MyModel) View() string { ... }

// 3. 创建运行函数
func RunMyUI() {
    p := tea.NewProgram(NewMyModel(), tea.WithAltScreen())
    p.Run()
}
```

### Q: 如何添加新的翻译？

```go
// 在 internal/i18n/i18n.go 中添加
translations = map[string]map[string]string{
    "zh": {
        "new_key": "新翻译",
    },
    "en": {
        "new_key": "New translation",
    },
}

// 使用
text := i18n.T("new_key")
```

## 代码风格

### 命名约定

- 包名：小写，无下划线
- 导出标识：大写字母开头
- 私有标识：小写字母开头
- 接口：-er 后缀（Installer, Runner）

### 注释规范

```go
// Installer 安装器接口
type Installer interface {
    // Install 安装软件
    Install(packageID string) (*InstallResult, error)
}
```

### 错误消息

- 小写字母开头
- 不使用句号结尾
- 不包含换行
- 不使用 "error" 前缀

## 性能优化

### 已实施的优化

1. 正则表达式缓存
2. 并发安装（信号量控制）
3. Mutex 保护共享数据
4. Panic 恢复机制

### 待优化项

1.  winget 输出解析优化
2.  配置加载缓存
3.  TUI 渲染优化

## 参考资源

- [Bubble Tea 文档](https://github.com/charmbracelet/bubbletea)
- [Cobra 文档](https://github.com/spf13/cobra)
- [Viper 文档](https://github.com/spf13/viper)
- [Lipgloss 文档](https://github.com/charmbracelet/lipgloss)
