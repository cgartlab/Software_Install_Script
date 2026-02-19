package ui

import (
	"math"
	"sync"
	"time"

	"github.com/charmbracelet/bubbles/progress"
	tea "github.com/charmbracelet/bubbletea"
)

// VisualProgressConfig 视觉进度条配置
type VisualProgressConfig struct {
	// 假进度增长速率（每秒增长的百分比，0.01 = 1%）
	FakeRate float64
	// 最小进度（至少显示的进度）
	MinProgress float64
	// 最大假进度（真实完成前最多显示到多少）
	MaxFakeProgress float64
	// 总任务数
	TotalTasks int
}

// DefaultVisualProgressConfig 默认配置
func DefaultVisualProgressConfig() VisualProgressConfig {
	return VisualProgressConfig{
		FakeRate:        0.02, // 每秒 2% 假进度
		MinProgress:     0.05, // 最小显示 5%
		MaxFakeProgress: 0.85, // 真实完成前最多显示到 85%
		TotalTasks:      1,
	}
}

// VisualProgress 视觉进度条组件
type VisualProgress struct {
	progress   progress.Model
	config     VisualProgressConfig
	current    float64 // 当前视觉进度
	realDone   int     // 真实完成的任务数
	total      int     // 总任务数
	isComplete bool    // 是否真实完成
	hasError   bool    // 是否有错误
	startTime  time.Time
	mu         sync.RWMutex
}

// NewVisualProgress 创建视觉进度条
func NewVisualProgress(config VisualProgressConfig) *VisualProgress {
	p := progress.New(progress.WithDefaultGradient())
	p.Width = 50

	vp := &VisualProgress{
		progress:   p,
		config:     config,
		total:      config.TotalTasks,
		current:    config.MinProgress,
		startTime:  time.Now(),
		isComplete: false,
		hasError:   false,
	}

	return vp
}

// Init 初始化
func (vp *VisualProgress) Init() tea.Cmd {
	return tickVisualCmd()
}

// tickVisualMsg 视觉进度更新消息
type tickVisualMsg struct{}

// tickVisualCmd 视觉进度定时命令
func tickVisualCmd() tea.Cmd {
	return tea.Tick(time.Millisecond*100, func(t time.Time) tea.Msg {
		return tickVisualMsg{}
	})
}

// Update 更新进度条
func (vp *VisualProgress) Update(msg tea.Msg) (tea.Cmd, bool) {
	vp.mu.Lock()
	defer vp.mu.Unlock()

	switch msg.(type) {
	case tickVisualMsg:
		if vp.isComplete {
			// 已完成，不再更新
			return nil, false
		}

		if vp.hasError {
			// 有错误，停止增长
			return nil, false
		}

		// 计算假进度
		elapsed := time.Since(vp.startTime).Seconds()
		fakeProgress := vp.config.MinProgress + (elapsed * vp.config.FakeRate)

		// 限制最大假进度
		if fakeProgress > vp.config.MaxFakeProgress {
			fakeProgress = vp.config.MaxFakeProgress
		}

		// 基于真实完成度的最小进度
		realProgress := float64(vp.realDone) / float64(vp.total)

		// 取假进度和真实进度的较大值
		vp.current = math.Max(fakeProgress, realProgress)

		// 确保不超过最大值
		if vp.current > vp.config.MaxFakeProgress {
			vp.current = vp.config.MaxFakeProgress
		}

		vp.progress.SetPercent(vp.current)
		return tickVisualCmd(), false

	case progress.FrameMsg:
		newModel, cmd := vp.progress.Update(msg)
		vp.progress = newModel.(progress.Model)
		return cmd, false
	}

	return nil, false
}

// UpdateManual 手动更新进度（用于测试或非 TUI 环境）
func (vp *VisualProgress) UpdateManual() {
	vp.mu.Lock()
	defer vp.mu.Unlock()

	if vp.isComplete || vp.hasError {
		return
	}

	// 计算假进度
	elapsed := time.Since(vp.startTime).Seconds()
	fakeProgress := vp.config.MinProgress + (elapsed * vp.config.FakeRate)

	// 限制最大假进度
	if fakeProgress > vp.config.MaxFakeProgress {
		fakeProgress = vp.config.MaxFakeProgress
	}

	// 基于真实完成度的最小进度
	realProgress := float64(vp.realDone) / float64(vp.total)

	// 取假进度和真实进度的较大值
	vp.current = math.Max(fakeProgress, realProgress)

	// 确保不超过最大值
	if vp.current > vp.config.MaxFakeProgress {
		vp.current = vp.config.MaxFakeProgress
	}

	vp.progress.SetPercent(vp.current)
}

// ReportComplete 报告一个任务真实完成
func (vp *VisualProgress) ReportComplete() {
	vp.mu.Lock()
	defer vp.mu.Unlock()

	vp.realDone++

	// 如果所有任务都完成了，立即跳到 100%
	if vp.realDone >= vp.total {
		vp.isComplete = true
		vp.current = 1.0
		vp.progress.SetPercent(1.0)
	} else {
		// 否则更新进度至少为真实完成度
		realProgress := float64(vp.realDone) / float64(vp.total)
		if vp.current < realProgress {
			vp.current = realProgress
			vp.progress.SetPercent(realProgress)
		}
	}
}

// ReportError 报告错误
func (vp *VisualProgress) ReportError() {
	vp.mu.Lock()
	defer vp.mu.Unlock()

	vp.hasError = true
	// 错误时不停止进度条，但标记状态
}

// GetPercent 获取当前进度百分比
func (vp *VisualProgress) GetPercent() float64 {
	vp.mu.RLock()
	defer vp.mu.RUnlock()
	return vp.current
}

// IsComplete 是否真实完成
func (vp *VisualProgress) IsComplete() bool {
	vp.mu.RLock()
	defer vp.mu.RUnlock()
	return vp.isComplete
}

// HasError 是否有错误
func (vp *VisualProgress) HasError() bool {
	vp.mu.RLock()
	defer vp.mu.RUnlock()
	return vp.hasError
}

// View 渲染进度条视图
func (vp *VisualProgress) View() string {
	vp.mu.RLock()
	defer vp.mu.RUnlock()
	return vp.progress.View()
}

// SetWidth 设置进度条宽度
func (vp *VisualProgress) SetWidth(width int) {
	vp.mu.Lock()
	defer vp.mu.Unlock()
	vp.progress.Width = width
}

// Reset 重置进度条
func (vp *VisualProgress) Reset() {
	vp.mu.Lock()
	defer vp.mu.Unlock()

	vp.current = vp.config.MinProgress
	vp.realDone = 0
	vp.isComplete = false
	vp.hasError = false
	vp.startTime = time.Now()
	vp.progress.SetPercent(vp.config.MinProgress)
}
