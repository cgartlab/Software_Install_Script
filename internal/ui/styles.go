package ui

import (
	"github.com/charmbracelet/lipgloss"
)

// 颜色常量
const (
	ColorPrimary       = "#c7894e" // Muted orange
	ColorPrimaryBright = "#d9a56f"
	ColorSecondary     = "#2f3338" // Muted slate
	ColorAccent        = "#6da874" // Muted green
	ColorWarning       = "#c99b67" // Warm orange
	ColorError         = "#ef4444" // Red
	ColorInfo          = "#7f9ab5" // Muted blue
	ColorMuted         = "#6b7280" // Gray
	ColorText          = "#f8fafc" // White
	ColorBackground    = "#1e293b" // Dark slate
)

// 样式定义
var (
	// 基础样式
	BaseStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color(ColorText))

	// 标题样式
	TitleStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color(ColorPrimary)).
			Bold(true).
			Padding(0, 1)

	// 副标题样式
	SubtitleStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color(ColorMuted)).
			Italic(true)

	// 成功样式
	SuccessStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color(ColorAccent)).
			Bold(true)

	// 警告样式
	WarningStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color(ColorWarning)).
			Bold(true)

	// 错误样式
	ErrorStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color(ColorError)).
			Bold(true)

	// 信息样式
	InfoStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color(ColorInfo))

	// 高亮样式
	HighlightStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color(ColorPrimaryBright)).
			Bold(true)

	// 菜单样式
	MenuStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color(ColorText)).
			Padding(0, 1)

	MenuDescriptionStyle = lipgloss.NewStyle().
				Foreground(lipgloss.Color(ColorMuted)).
				PaddingLeft(4)

	MenuSelectedStyle = lipgloss.NewStyle().
				Foreground(lipgloss.Color(ColorPrimaryBright)).
				Bold(true).
				Padding(0, 1)

	// 盒子样式
	BoxStyle = lipgloss.NewStyle().
			Border(lipgloss.RoundedBorder()).
			BorderForeground(lipgloss.Color(ColorPrimary)).
			Padding(1, 2)

	BoxActiveStyle = lipgloss.NewStyle().
			Border(lipgloss.RoundedBorder()).
			BorderForeground(lipgloss.Color(ColorAccent)).
			Padding(1, 2)

	// 状态样式
	StatusSuccess = lipgloss.NewStyle().
			Foreground(lipgloss.Color(ColorAccent))

	StatusFailed = lipgloss.NewStyle().
			Foreground(lipgloss.Color(ColorError))

	StatusPending = lipgloss.NewStyle().
			Foreground(lipgloss.Color(ColorMuted))

	StatusInstalling = lipgloss.NewStyle().
				Foreground(lipgloss.Color(ColorInfo))

	// 进度条样式
	ProgressBarStyle = lipgloss.NewStyle().
				Foreground(lipgloss.Color(ColorPrimary))

	ProgressCompleteStyle = lipgloss.NewStyle().
				Foreground(lipgloss.Color(ColorAccent))

	// 表格样式
	TableHeaderStyle = lipgloss.NewStyle().
				Foreground(lipgloss.Color(ColorPrimaryBright)).
				Bold(true)

	TableCellStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color(ColorText))

	// 输入样式
	InputStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color(ColorText)).
			Border(lipgloss.NormalBorder()).
			BorderForeground(lipgloss.Color(ColorPrimary))

	// 帮助样式
	HelpStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color(ColorMuted))

	// Logo 样式
	LogoStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color(ColorPrimary)).
			Bold(true)

	// 分隔线样式
	DividerStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color(ColorMuted))
)

// GetStatusStyle 根据状态获取样式
func GetStatusStyle(status string) lipgloss.Style {
	switch status {
	case "success", "completed", "installed":
		return StatusSuccess
	case "failed", "error":
		return StatusFailed
	case "pending", "waiting":
		return StatusPending
	case "installing", "running", "downloading":
		return StatusInstalling
	default:
		return StatusPending
	}
}

// GetStatusIcon 根据状态获取图标
func GetStatusIcon(status string) string {
	switch status {
	case "success", "completed", "installed":
		return "✓"
	case "failed", "error":
		return "✗"
	case "pending", "waiting":
		return "○"
	case "installing", "running":
		return "◉"
	case "downloading":
		return "↓"
	case "skipped":
		return "⊘"
	default:
		return "○"
	}
}
