package ui

import (
	"fmt"
	"io"
	"os"

	"github.com/charmbracelet/bubbles/list"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
	"swiftinstall/internal/appinfo"
)

// CommandItem 命令菜单项
type CommandItem struct {
	Name        string
	Description string
	Icon        string
	IsHighlight bool // 是否高亮（推荐选项）
	Action      func()
}

func (i CommandItem) FilterValue() string { return i.Name }

// CommandMenuModel 命令菜单模型
type CommandMenuModel struct {
	list     list.Model
	quitting bool
	width    int
	height   int
}

// NewCommandMenu 创建命令菜单
func NewCommandMenu() CommandMenuModel {
	items := []list.Item{
		CommandItem{
			Name:        "interactive",
			Description: "Enter interactive mode - 进入交互模式",
			Icon:        "✨",
			IsHighlight: true,
			Action: func() {
				RunMainMenu()
			},
		},
		CommandItem{
			Name:        "install",
			Description: "Install software packages - 安装软件",
			Icon:        "⚡",
			Action: func() {
				runCommand("install")
			},
		},
		CommandItem{
			Name:        "search",
			Description: "Search for software - 搜索软件",
			Icon:        "🔍",
			Action: func() {
				RunSearch("")
			},
		},
		CommandItem{
			Name:        "list",
			Description: "List configured packages - 列出已配置软件",
			Icon:        "📋",
			Action: func() {
				runCommand("list")
			},
		},
		CommandItem{
			Name:        "config",
			Description: "Manage configuration - 配置管理",
			Icon:        "⚙️",
			Action: func() {
				RunConfigManager()
			},
		},
		CommandItem{
			Name:        "status",
			Description: "Show system status - 系统状态",
			Icon:        "📊",
			Action: func() {
				RunStatus()
			},
		},
		CommandItem{
			Name:        "db",
			Description: "Database management - 数据库管理",
			Icon:        "🗄️",
			Action: func() {
				runCommand("db")
			},
		},
		CommandItem{
			Name:        "help",
			Description: "Show help document - 显示帮助文档",
			Icon:        "❓",
			Action: func() {
				// 显示帮助信息
				fmt.Println(GetCompactLogo())
				fmt.Println()
				fmt.Println(TitleStyle.Render("SwiftInstall Help"))
				fmt.Println()
				fmt.Println(InfoStyle.Render("Commands:"))
				fmt.Println("  sis install [package...]   Install software")
				fmt.Println("  sis search [query]         Search software")
				fmt.Println("  sis list                   List configured packages")
				fmt.Println("  sis config                 Configuration manager")
				fmt.Println("  sis status                 System status")
				fmt.Println("  sis db                     Database management")
				fmt.Println("  sis version                Version info")
				fmt.Println("  sis help                   Full help document")
				fmt.Println()
				fmt.Println(HelpStyle.Render("© 2026 CGArtLab. All rights reserved."))
			},
		},
		CommandItem{
			Name:        "exit",
			Description: "Exit the program - 退出程序",
			Icon:        "🚪",
			Action: func() {
				os.Exit(0)
			},
		},
	}

	l := list.New(items, commandItemDelegate{}, 60, 20)
	l.Title = "Command Menu - 命令菜单"
	l.SetShowStatusBar(false)
	l.SetFilteringEnabled(false)
	l.Styles.Title = TitleStyle
	l.Styles.PaginationStyle = HelpStyle
	l.Styles.HelpStyle = HelpStyle

	return CommandMenuModel{list: l}
}

// runCommand 运行命令（通过 exec 重新调用 sis）
func runCommand(cmd string) {
	// 显示提示
	fmt.Println()
	fmt.Println(InfoStyle.Render(fmt.Sprintf("Run: sis %s [args...]", cmd)))
	fmt.Println()
}

// Init 初始化
func (m CommandMenuModel) Init() tea.Cmd {
	return nil
}

// Update 更新
func (m CommandMenuModel) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.WindowSizeMsg:
		m.width = msg.Width
		m.height = msg.Height
		m.list.SetWidth(msg.Width)
		return m, nil

	case tea.KeyMsg:
		switch msg.String() {
		case "q", "ctrl+c":
			m.quitting = true
			return m, tea.Quit
		case "up":
			m.list.CursorUp()
			return m, nil
		case "down":
			m.list.CursorDown()
			return m, nil
		case "enter":
			if item, ok := m.list.SelectedItem().(CommandItem); ok {
				// 对于 interactive 选项，设置标志并退出
				if item.Name == "interactive" {
					m.quitting = true
					return m, tea.Quit
				}
				// 其他命令，显示提示并退出
				m.quitting = true
				return m, tea.Quit
			}
		case "i":
			// 快捷键 i 直接进入交互模式
			m.quitting = true
			return m, tea.Quit
		}
	}

	var cmd tea.Cmd
	m.list, cmd = m.list.Update(msg)
	return m, cmd
}

// View 视图
func (m CommandMenuModel) View() string {
	if m.quitting {
		return "\n"
	}

	logo := GetCompactLogo()
	menu := m.list.View()

	helpText := "↑/↓ Navigate • Enter Select • i Interactive • q Quit"
	help := HelpStyle.Render(helpText)

	meta := SubtitleStyle.Render(fmt.Sprintf("Author: %s", appinfo.Author))
	copy := HelpStyle.Render(appinfo.Copyright)

	return lipgloss.JoinVertical(
		lipgloss.Left,
		logo,
		"",
		menu,
		"",
		help,
		"",
		meta,
		copy,
	)
}

// commandItemDelegate 命令项委托
type commandItemDelegate struct{}

func (d commandItemDelegate) Height() int  { return 3 }
func (d commandItemDelegate) Spacing() int { return 1 }
func (d commandItemDelegate) Update(_ tea.Msg, _ *list.Model) tea.Cmd {
	return nil
}

func (d commandItemDelegate) Render(w io.Writer, m list.Model, index int, listItem list.Item) {
	item, ok := listItem.(CommandItem)
	if !ok {
		return
	}

	title := fmt.Sprintf("%s %s", item.Icon, item.Name)
	desc := item.Description

	if item.IsHighlight {
		// 高亮样式（推荐选项）
		highlightStyle := lipgloss.NewStyle().
			Foreground(lipgloss.Color("#ffd700")). // 金色
			Bold(true)
		title = highlightStyle.Render("✨ " + item.Name + " [RECOMMENDED]")
		desc = highlightStyle.UnsetBold().
			Foreground(lipgloss.Color("#ffa500")). // 橙色
			Render("  " + desc)
	} else if index == m.Index() {
		// 选中样式
		title = MenuSelectedStyle.Render("> " + title)
		desc = MenuSelectedStyle.UnsetBold().Foreground(lipgloss.Color(ColorMuted)).Render("  " + desc)
	} else {
		// 普通样式
		title = MenuStyle.Render("  " + title)
		desc = MenuDescriptionStyle.Render(desc)
	}

	fmt.Fprint(w, lipgloss.JoinVertical(lipgloss.Left, title, desc))
}

// RunCommandMenu 运行命令菜单
func RunCommandMenu() {
	p := tea.NewProgram(NewCommandMenu(), tea.WithAltScreen())
	model, err := p.Run()
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}

	// 检查是否选择了 interactive 选项
	if m, ok := model.(CommandMenuModel); ok {
		if item, ok := m.list.SelectedItem().(CommandItem); ok {
			if item.Name == "interactive" {
				// 进入交互模式
				RunMainMenu()
			}
		}
	}
}
