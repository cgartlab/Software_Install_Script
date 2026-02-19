# 视觉化进度条组件文档

## 概述

`VisualProgress` 是一个专为安装类功能设计的视觉化进度条组件，解决用户无法感知安装进度的问题。

## 核心特性

### 1. 假进度机制
- 进度条按固定速率自动增长（默认每秒 2%）
- 无需等待真实安装进度，让用户立即看到"有进度在推进"
- 可配置的增长速率

### 2. 真实状态匹配
- 当真实安装完成时，进度条立即跳至 100%
- 最终状态与实际安装结果强匹配
- 避免"假进度"超过真实进度

### 3. 错误处理
- 安装失败时进度条停止增长
- 保持当前视觉进度，显示错误状态
- 不会继续增长误导用户

### 4. 真实进度优先
- 当真实完成度超过假进度时，采用真实进度
- 确保进度条始终反映最佳可用信息

## 使用方法

### 基本使用

```go
// 创建配置
config := DefaultVisualProgressConfig()
config.TotalTasks = 5  // 总任务数
config.FakeRate = 0.02  // 每秒 2% 假进度

// 创建进度条
vp := NewVisualProgress(config)

// 在 TUI 中使用
model := tea.NewProgram(vp)
```

### 配置参数

```go
type VisualProgressConfig struct {
    FakeRate        float64 // 假进度增长速率（每秒百分比）
    MinProgress     float64 // 最小进度（起始进度）
    MaxFakeProgress float64 // 最大假进度（真实完成前上限）
    TotalTasks      int     // 总任务数
}
```

### 默认配置

```go
func DefaultVisualProgressConfig() VisualProgressConfig {
    return VisualProgressConfig{
        FakeRate:        0.02, // 每秒 2%
        MinProgress:     0.05, // 最小 5%
        MaxFakeProgress: 0.85, // 最大 85%
        TotalTasks:      1,
    }
}
```

## API 参考

### 创建与初始化

```go
// 创建进度条
vp := NewVisualProgress(config)

// 初始化（返回 TUI 命令）
cmd := vp.Init()
```

### 进度报告

```go
// 报告一个任务完成
vp.ReportComplete()

// 报告错误
vp.ReportError()

// 获取当前进度百分比
percent := vp.GetPercent()
```

### 状态查询

```go
// 是否真实完成
if vp.IsComplete() {
    // 所有任务已完成
}

// 是否有错误
if vp.HasError() {
    // 安装过程中出现错误
}
```

### 视图渲染

```go
// 渲染进度条
view := vp.View()

// 设置宽度
vp.SetWidth(50)
```

### 重置

```go
// 重置进度条到初始状态
vp.Reset()
```

## 集成示例

### 在安装界面中使用

```go
type InstallModel struct {
    visualProgress *VisualProgress
    packages       []config.Software
    results        []*installer.InstallResult
}

func NewInstallModel(packages []config.Software) InstallModel {
    config := DefaultVisualProgressConfig()
    config.TotalTasks = len(packages)
    
    return InstallModel{
        visualProgress: NewVisualProgress(config),
        packages:       packages,
        results:        make([]*installer.InstallResult, len(packages)),
    }
}

func (m *InstallModel) Init() tea.Cmd {
    return tea.Batch(
        m.visualProgress.Init(),
        m.runInstall(),
    )
}

func (m *InstallModel) installPackage(index int) {
    result := installPackage(m.packages[index])
    m.results[index] = result
    
    // 报告完成状态
    if result.Status == installer.StatusSuccess {
        m.visualProgress.ReportComplete()
    } else {
        m.visualProgress.ReportError()
    }
}

func (m *InstallModel) View() string {
    var b strings.Builder
    b.WriteString("安装进度:\n")
    b.WriteString(m.visualProgress.View())
    return b.String()
}
```

## 最佳实践

### 1. 选择合适的假进度速率

- **快速安装**（< 10 秒）：`FakeRate = 0.05`（每秒 5%）
- **普通安装**（10-60 秒）：`FakeRate = 0.02`（每秒 2%）
- **慢速安装**（> 60 秒）：`FakeRate = 0.01`（每秒 1%）

### 2. 设置合理的最大假进度

```go
// 如果安装通常很快，设置较低的最大假进度
config.MaxFakeProgress = 0.70  // 70%

// 如果安装通常很慢，设置较高的最大假进度
config.MaxFakeProgress = 0.90  // 90%
```

### 3. 多任务并行安装

```go
// 对于并行安装，进度基于完成的任务数
config.TotalTasks = len(packages)

// 每个任务完成后报告
for i, pkg := range packages {
    go func(index int) {
        result := install(pkg)
        m.results[index] = result
        m.visualProgress.ReportComplete()
    }(i)
}
```

## 测试

```bash
# 运行单元测试
go test -v ./internal/ui -run TestVisualProgress

# 测试用例包括：
# - TestVisualProgress_Basic: 基本功能测试
# - TestVisualProgress_FakeProgress: 假进度增长测试
# - TestVisualProgress_Error: 错误处理测试
# - TestVisualProgress_Reset: 重置功能测试
# - TestVisualProgress_RealBeatsFake: 真实进度优先测试
```

## 视觉效果

```
初始状态 (5%):
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   5%

假进度增长 (45%):
██████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░   45%

真实完成 (100%):
███████████████████████████████████████████████  100%
```

## 注意事项

1. **线程安全**: 组件内部使用互斥锁，可安全地在 goroutine 中调用
2. **内存管理**: 组件轻量级，无额外内存开销
3. **TUI 集成**: 完美集成 Bubble Tea 框架，支持实时更新
4. **可配置性**: 所有参数均可配置，适应不同场景

## 故障排除

### 进度条不增长

检查是否调用了 `Init()` 返回的命令：
```go
func (m *InstallModel) Init() tea.Cmd {
    return m.visualProgress.Init()  // 必须返回这个命令
}
```

### 进度条超过 100%

确保在真实完成时调用 `ReportComplete()`：
```go
if allTasksCompleted {
    m.visualProgress.ReportComplete()  // 这会设置进度为 100%
}
```

### 错误后进度条继续增长

错误时调用 `ReportError()`：
```go
if installFailed {
    m.visualProgress.ReportError()  // 这会停止假进度增长
}
```
