package ui

import (
	"fmt"
	"os"
	"strings"

	"github.com/charmbracelet/bubbles/table"
	"github.com/charmbracelet/bubbles/textinput"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
	"swiftinstall/internal/config"
	"swiftinstall/internal/i18n"
	"swiftinstall/internal/installer"
)

// SearchModel 搜索模型
type SearchModel struct {
	input       textinput.Model
	results     []installer.PackageInfo
	table       table.Model
	query       string
	searching   bool
	quitting    bool
	width       int
	height      int
	selected    []installer.PackageInfo
	message     string
	messageType string
}

// NewSearchModel 创建搜索模型
func NewSearchModel(initialQuery string) SearchModel {
	ti := textinput.New()
	ti.Placeholder = i18n.T("search_placeholder")
	ti.Focus()
	ti.CharLimit = 100
	ti.Width = 50
	ti.SetValue(initialQuery)

	columns := []table.Column{
		{Title: i18n.T("config_name"), Width: 25},
		{Title: i18n.T("config_id"), Width: 30},
		{Title: "Publisher", Width: 15},
	}

	t := table.New(
		table.WithColumns(columns),
		table.WithHeight(10),
	)

	s := table.DefaultStyles()
	s.Header = s.Header.
		BorderStyle(lipgloss.NormalBorder()).
		BorderForeground(lipgloss.Color(ColorPrimary)).
		BorderBottom(true).
		Bold(false)
	s.Selected = s.Selected.
		Foreground(lipgloss.Color(ColorPrimaryBright)).
		Bold(true)
	t.SetStyles(s)

	return SearchModel{
		input:    ti,
		query:    initialQuery,
		table:    t,
		results:  []installer.PackageInfo{},
		selected: []installer.PackageInfo{},
	}
}

// Init 初始化
func (m SearchModel) Init() tea.Cmd {
	if m.query != "" {
		return m.search(m.query)
	}
	return textinput.Blink
}

// search 搜索命令
func (m SearchModel) search(query string) tea.Cmd {
	return func() tea.Msg {
		inst := installer.NewInstaller()
		if inst == nil {
			return searchResultMsg{err: fmt.Errorf("unsupported platform")}
		}

		results, err := inst.Search(query)
		return searchResultMsg{results: results, err: err}
	}
}

// searchResultMsg 搜索结果消息
type searchResultMsg struct {
	results []installer.PackageInfo
	err     error
}

// Update 更新
func (m SearchModel) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	var cmd tea.Cmd

	switch msg := msg.(type) {
	case tea.WindowSizeMsg:
		m.width = msg.Width
		m.height = msg.Height
		m.table.SetWidth(msg.Width)
		return m, nil

	case tea.KeyMsg:
		switch msg.String() {
		case "q", "ctrl+c":
			m.quitting = true
			return m, tea.Quit
		case "enter":
			if m.searching {
				// 选择当前项
				if len(m.results) > 0 {
					selectedRow := m.table.Cursor()
					if selectedRow < len(m.results) {
						pkg := m.results[selectedRow]
						// 添加到配置
						cfg := config.Get()
						cfg.AddSoftware(config.Software{
							Name:     pkg.Name,
							ID:       pkg.ID,
							Category: "Other",
						})
						if err := config.Save(); err != nil {
							m.message = fmt.Sprintf("%s: %v", i18n.T("config_save_error"), err)
							m.messageType = "error"
							return m, nil
						}
						m.selected = append(m.selected, pkg)
						m.message = i18n.T("search_added_hint")
						m.messageType = "success"
					}
				}
			} else {
				// 开始搜索
				m.query = m.input.Value()
				if m.query != "" {
					m.searching = true
					m.message = ""
					return m, m.search(m.query)
				}
			}
		case "esc":
			if m.searching {
				m.searching = false
				m.input.Focus()
				return m, textinput.Blink
			}
		case "/":
			if m.searching {
				m.searching = false
				m.input.Focus()
				return m, textinput.Blink
			}
		}

	case searchResultMsg:
		m.searching = false
		if msg.err != nil {
			m.results = []installer.PackageInfo{}
			m.message = fmt.Sprintf("%s: %v", i18n.T("common_error"), msg.err)
			m.messageType = "error"
		} else {
			m.message = ""
			m.messageType = ""
			m.results = msg.results
			// 更新表格
			var rows []table.Row
			for _, pkg := range m.results {
				id := pkg.ID
				if id == "" {
					id = pkg.Name
				}
				rows = append(rows, table.Row{
					pkg.Name,
					id,
					pkg.Publisher,
				})
			}
			m.table.SetRows(rows)
		}
		return m, nil
	}

	if !m.searching {
		m.input, cmd = m.input.Update(msg)
	} else {
		m.table, cmd = m.table.Update(msg)
	}

	return m, cmd
}

// View 视图
func (m SearchModel) View() string {
	if m.quitting {
		return "\n  " + i18n.T("common_cancel") + "\n"
	}

	var b strings.Builder

	// 标题
	b.WriteString(TitleStyle.Render(i18n.T("search_title")))
	b.WriteString("\n\n")

	// 输入框
	b.WriteString(m.input.View())
	b.WriteString("\n\n")

	// 搜索结果
	if len(m.results) > 0 {
		b.WriteString(InfoStyle.Render(fmt.Sprintf("%s: %d", i18n.T("search_results"), len(m.results))))
		b.WriteString("\n")
		b.WriteString(m.table.View())
		b.WriteString("\n")
		b.WriteString(HelpStyle.Render("Add: Enter | Refine: / | Back: Esc | Quit: q"))
	} else if m.query != "" && !m.searching {
		b.WriteString(WarningStyle.Render(i18n.T("search_no_results")))
		b.WriteString("\n")
		b.WriteString(HelpStyle.Render("Refine: / | Quit: q"))
	} else {
		b.WriteString(HelpStyle.Render("Enter to search | Quit: q"))
	}

	if m.message != "" {
		b.WriteString("\n")
		if m.messageType == "error" {
			b.WriteString(ErrorStyle.Render(m.message))
		} else {
			b.WriteString(SuccessStyle.Render(m.message))
		}
		b.WriteString("\n")
	}

	// 已选择
	if len(m.selected) > 0 {
		b.WriteString("\n")
		b.WriteString(SuccessStyle.Render(fmt.Sprintf("✓ %s: %d", i18n.T("search_added_count"), len(m.selected))))
	}

	return b.String()
}

// RunSearch 运行搜索
func RunSearch(query string) {
	if !isInteractiveTerminal() {
		if err := runSearchPlainText(query); err != nil {
			fmt.Println(ErrorStyle.Render(err.Error()))
			os.Exit(1)
		}
		return
	}

	p := tea.NewProgram(NewSearchModel(query), tea.WithAltScreen())
	if _, err := p.Run(); err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
}

func runSearchPlainText(query string) error {
	if strings.TrimSpace(query) == "" {
		return fmt.Errorf("search command requires a query in non-interactive mode")
	}

	inst := installer.NewInstaller()
	if inst == nil {
		return fmt.Errorf("unsupported platform")
	}

	results, err := inst.Search(query)
	if err != nil {
		return fmt.Errorf("search failed: %w", err)
	}

	if len(results) == 0 {
		fmt.Println(WarningStyle.Render(i18n.T("search_no_results")))
		return nil
	}

	fmt.Println(TitleStyle.Render(i18n.T("search_title")))
	fmt.Printf("%-4s %-36s %s\n", "#", i18n.T("config_name"), i18n.T("config_id"))
	for i, pkg := range results {
		name := pkg.Name
		if name == "" {
			name = pkg.ID
		}
		fmt.Printf("%-4d %-36s %s\n", i+1, name, pkg.ID)
	}
	return nil
}

// ShowPackageList 显示包列表
func ShowPackageList(packages []config.Software) {
	if len(packages) == 0 {
		fmt.Println(WarningStyle.Render(i18n.T("warn_no_packages")))
		return
	}

	columns := []table.Column{
		{Title: "#", Width: 5},
		{Title: i18n.T("config_name"), Width: 25},
		{Title: i18n.T("config_id"), Width: 30},
		{Title: i18n.T("config_category"), Width: 20},
	}

	var rows []table.Row
	for i, pkg := range packages {
		id := pkg.ID
		if id == "" {
			id = pkg.Package
		}
		rows = append(rows, table.Row{
			fmt.Sprintf("%d", i+1),
			pkg.Name,
			id,
			pkg.Category,
		})
	}

	t := table.New(
		table.WithColumns(columns),
		table.WithRows(rows),
		table.WithHeight(len(packages)+2),
	)

	s := table.DefaultStyles()
	s.Header = s.Header.
		BorderStyle(lipgloss.NormalBorder()).
		BorderForeground(lipgloss.Color(ColorPrimary)).
		BorderBottom(true).
		Bold(true)
	t.SetStyles(s)

	fmt.Println(TitleStyle.Render(i18n.T("cmd_list_short")))
	fmt.Println()
	fmt.Println(t.View())
	fmt.Println()
	fmt.Println(HelpStyle.Render(fmt.Sprintf("Total: %d packages", len(packages))))
}
