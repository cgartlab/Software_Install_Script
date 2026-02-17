package ui

import (
	"fmt"
	"io"
	"os"

	"github.com/charmbracelet/bubbles/list"
	"github.com/charmbracelet/bubbles/spinner"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
	"swiftinstall/internal/config"
	"swiftinstall/internal/i18n"
)

// MenuItem 菜单项
type MenuItem struct {
	Title       string
	Description string
	Icon        string
	Action      func()
}

func (i MenuItem) FilterValue() string { return i.Title }

// MainMenuModel 主菜单模型
type MainMenuModel struct {
	list     list.Model
	quitting bool
	width    int
	height   int
}

// NewMainMenu 创建主菜单
func NewMainMenu() MainMenuModel {
	items := []list.Item{
		MenuItem{
			Title:       i18n.T("menu_install"),
			Description: i18n.T("cmd_install_long"),
			Icon:        "⚡",
			Action:      func() { RunInstall(config.Get().GetSoftwareList(), false) },
		},
		MenuItem{
			Title:       i18n.T("menu_uninstall"),
			Description: i18n.T("cmd_uninstall_long"),
			Icon:        "🗑️",
			Action:      func() { RunUninstall(config.Get().GetSoftwareList()) },
		},
		MenuItem{
			Title:       i18n.T("menu_search"),
			Description: i18n.T("cmd_search_long"),
			Icon:        "🔍",
			Action:      func() { RunSearch("") },
		},
		MenuItem{
			Title:       i18n.T("menu_config"),
			Description: i18n.T("cmd_config_long"),
			Icon:        "⚙️",
			Action:      func() { RunConfigManager() },
		},
		MenuItem{
			Title:       i18n.T("menu_wizard"),
			Description: i18n.T("cmd_wizard_long"),
			Icon:        "🧙",
			Action:      func() { RunWizard() },
		},
		MenuItem{
			Title:       i18n.T("menu_status"),
			Description: i18n.T("cmd_status_long"),
			Icon:        "📊",
			Action:      func() { RunStatus() },
		},
		MenuItem{
			Title:       i18n.T("menu_clean"),
			Description: i18n.T("cmd_clean_long"),
			Icon:        "🧹",
			Action:      func() { RunClean() },
		},
		MenuItem{
			Title:       i18n.T("menu_update"),
			Description: i18n.T("cmd_update_long"),
			Icon:        "🔄",
			Action:      func() { RunUpdateCheck() },
		},
		MenuItem{
			Title:       i18n.T("menu_exit"),
			Description: "Exit the application",
			Icon:        "🚪",
			Action:      func() { os.Exit(0) },
		},
	}

	l := list.New(items, menuItemDelegate{}, 60, 20)
	l.Title = i18n.T("menu_title")
	l.SetShowStatusBar(false)
	l.SetFilteringEnabled(false)
	l.Styles.Title = TitleStyle
	l.Styles.PaginationStyle = HelpStyle
	l.Styles.HelpStyle = HelpStyle

	return MainMenuModel{list: l}
}

// Init 初始化
func (m MainMenuModel) Init() tea.Cmd {
	return nil
}

// Update 更新
func (m MainMenuModel) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
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
		case "enter":
			if item, ok := m.list.SelectedItem().(MenuItem); ok {
				item.Action()
			}
		}
	}

	var cmd tea.Cmd
	m.list, cmd = m.list.Update(msg)
	return m, cmd
}

// View 视图
func (m MainMenuModel) View() string {
	if m.quitting {
		return "\n  " + i18n.T("menu_exit") + "\n"
	}

	logo := GetCompactLogo()
	menu := m.list.View()
	
	// 构建帮助信息
	helpText := fmt.Sprintf("%s: ↑/k %s • ↓/j %s • Enter %s • q %s",
		i18n.T("common_navigation"),
		i18n.T("common_up"),
		i18n.T("common_down"),
		i18n.T("common_select"),
		i18n.T("common_quit"),
	)
	help := HelpStyle.Render(helpText)
	
	// 添加命令提示
	tip := SubtitleStyle.Render(fmt.Sprintf("%s: sis install, sis search, sis list...", i18n.T("common_tip")))

	return lipgloss.JoinVertical(
		lipgloss.Center,
		logo,
		"",
		TitleStyle.Render(i18n.T("menu_title")),
		"",
		menu,
		"",
		help,
		"",
		tip,
	)
}

// menuItemDelegate 菜单项委托
type menuItemDelegate struct{}

func (d menuItemDelegate) Height() int                             { return 2 }
func (d menuItemDelegate) Spacing() int                            { return 1 }
func (d menuItemDelegate) Update(_ tea.Msg, _ *list.Model) tea.Cmd { return nil }
func (d menuItemDelegate) Render(w io.Writer, m list.Model, index int, listItem list.Item) {
	item, ok := listItem.(MenuItem)
	if !ok {
		return
	}

	str := fmt.Sprintf("%s %s\n    %s", item.Icon, item.Title, item.Description)

	fn := MenuStyle.Render
	if index == m.Index() {
		fn = func(s ...string) string {
			return MenuSelectedStyle.Render("> " + s[0])
		}
	}

	fmt.Fprint(w, fn(str))
}

// RunMainMenu 运行主菜单
func RunMainMenu() {
	p := tea.NewProgram(NewMainMenu(), tea.WithAltScreen())
	if _, err := p.Run(); err != nil {
		fmt.Printf("Error: %v", err)
		os.Exit(1)
	}
}

// SpinnerModel 加载动画模型
type SpinnerModel struct {
	spinner  spinner.Model
	message  string
	quitting bool
}

// NewSpinner 创建加载动画
func NewSpinner(message string) SpinnerModel {
	s := spinner.New()
	s.Spinner = spinner.Dot
	s.Style = lipgloss.NewStyle().Foreground(lipgloss.Color(ColorPrimary))
	return SpinnerModel{spinner: s, message: message}
}

// Init 初始化
func (m SpinnerModel) Init() tea.Cmd {
	return m.spinner.Tick
}

// Update 更新
func (m SpinnerModel) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		if msg.String() == "q" || msg.String() == "ctrl+c" {
			m.quitting = true
			return m, tea.Quit
		}
	default:
		var cmd tea.Cmd
		m.spinner, cmd = m.spinner.Update(msg)
		return m, cmd
	}
	return m, nil
}

// View 视图
func (m SpinnerModel) View() string {
	if m.quitting {
		return ""
	}
	return lipgloss.JoinHorizontal(
		lipgloss.Center,
		m.spinner.View(),
		" ",
		m.message,
	)
}

// ShowSpinner 显示加载动画
func ShowSpinner(message string, action func()) {
	p := tea.NewProgram(NewSpinner(message))
	go func() {
		action()
		p.Quit()
	}()
	if _, err := p.Run(); err != nil {
		fmt.Printf("Error: %v\n", err)
	}
}
