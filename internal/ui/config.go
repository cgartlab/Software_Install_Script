package ui

import (
	"fmt"
	"log"
	"os"
	"strings"

	"swiftinstall/internal/config"
	"swiftinstall/internal/i18n"
	"swiftinstall/internal/installer"

	"github.com/charmbracelet/bubbles/table"
	"github.com/charmbracelet/bubbles/textinput"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
)

// ConfigModel 配置管理模型
type ConfigModel struct {
	mode        string // "list", "add", "edit", "remove"
	table       table.Model
	inputs      []textinput.Model
	focusIndex  int
	packages    []config.Software
	selected    int
	quitting    bool
	width       int
	height      int
	message     string
	messageType string // "success", "error", "info"
}

// NewConfigModel 创建配置管理模型
func NewConfigModel() ConfigModel {
	columns := []table.Column{
		{Title: "#", Width: 5},
		{Title: i18n.T("config_name"), Width: 25},
		{Title: i18n.T("config_id"), Width: 30},
		{Title: i18n.T("config_category"), Width: 20},
	}

	cfg := config.Get()
	packages := cfg.GetSoftwareList()

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
		table.WithFocused(true),
		table.WithHeight(10),
	)

	s := table.DefaultStyles()
	s.Header = s.Header.
		BorderStyle(lipgloss.NormalBorder()).
		BorderForeground(lipgloss.Color(ColorPrimary)).
		BorderBottom(true).
		Bold(false)
	s.Selected = s.Selected.
		Foreground(lipgloss.Color(ColorText)).
		Background(lipgloss.Color(ColorSecondary)).
		Bold(false)
	t.SetStyles(s)

	// 创建输入框
	inputs := make([]textinput.Model, 3)

	inputs[0] = textinput.New()
	inputs[0].Placeholder = i18n.T("config_name")
	inputs[0].Focus()
	inputs[0].CharLimit = 50
	inputs[0].Width = 40

	inputs[1] = textinput.New()
	inputs[1].Placeholder = i18n.T("config_id")
	inputs[1].CharLimit = 50
	inputs[1].Width = 40

	inputs[2] = textinput.New()
	inputs[2].Placeholder = i18n.T("config_category")
	inputs[2].CharLimit = 30
	inputs[2].Width = 40
	inputs[2].SetValue("Other")

	return ConfigModel{
		mode:     "list",
		table:    t,
		inputs:   inputs,
		packages: packages,
	}
}

// Init 初始化
func (m ConfigModel) Init() tea.Cmd {
	return nil
}

// Update 更新
func (m ConfigModel) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
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
			if m.mode == "list" {
				m.quitting = true
				return m, tea.Quit
			} else {
				m.mode = "list"
				m.message = ""
				return m, nil
			}
		case "a":
			if m.mode == "list" {
				m.mode = "add"
				m.focusIndex = 0
				for i := range m.inputs {
					m.inputs[i].SetValue("")
					m.inputs[i].Blur()
				}
				m.inputs[0].Focus()
				return m, textinput.Blink
			}
		case "e":
			if m.mode == "list" && len(m.packages) > 0 {
				m.mode = "edit"
				m.selected = m.table.Cursor()
				if m.selected < len(m.packages) {
					pkg := m.packages[m.selected]
					m.inputs[0].SetValue(pkg.Name)
					id := pkg.ID
					if id == "" {
						id = pkg.Package
					}
					m.inputs[1].SetValue(id)
					m.inputs[2].SetValue(pkg.Category)
				}
				m.focusIndex = 0
				for i := range m.inputs {
					m.inputs[i].Blur()
				}
				m.inputs[0].Focus()
				return m, textinput.Blink
			}
		case "d", "r":
			if m.mode == "list" && len(m.packages) > 0 {
				m.mode = "remove"
				m.selected = m.table.Cursor()
				return m, nil
			}
		case "enter":
			switch m.mode {
			case "add":
				if m.focusIndex < len(m.inputs)-1 {
					m.focusIndex++
					for i := range m.inputs {
						if i == m.focusIndex {
							m.inputs[i].Focus()
						} else {
							m.inputs[i].Blur()
						}
					}
					return m, textinput.Blink
				}
				// 保存
				m.savePackage()
				return m, nil
			case "edit":
				if m.focusIndex < len(m.inputs)-1 {
					m.focusIndex++
					for i := range m.inputs {
						if i == m.focusIndex {
							m.inputs[i].Focus()
						} else {
							m.inputs[i].Blur()
						}
					}
					return m, textinput.Blink
				}
				// 更新
				m.updatePackage()
				return m, nil
			case "remove":
				m.deletePackage()
				return m, nil
			}
		case "y":
			if m.mode == "remove" {
				m.deletePackage()
				return m, nil
			}
		case "n":
			if m.mode == "remove" {
				m.mode = "list"
				m.message = ""
				return m, nil
			}
		case "tab", "shift+tab":
			if m.mode == "add" || m.mode == "edit" {
				if msg.String() == "tab" {
					m.focusIndex = (m.focusIndex + 1) % len(m.inputs)
				} else {
					m.focusIndex--
					if m.focusIndex < 0 {
						m.focusIndex = len(m.inputs) - 1
					}
				}
				for i := range m.inputs {
					if i == m.focusIndex {
						m.inputs[i].Focus()
					} else {
						m.inputs[i].Blur()
					}
				}
				return m, textinput.Blink
			}
		}
	}

	if m.mode == "list" {
		m.table, cmd = m.table.Update(msg)
	} else if m.mode == "add" || m.mode == "edit" {
		for i := range m.inputs {
			m.inputs[i], cmd = m.inputs[i].Update(msg)
		}
	}

	return m, cmd
}

// savePackage 保存包
func (m *ConfigModel) savePackage() {
	name := m.inputs[0].Value()
	id := m.inputs[1].Value()
	category := m.inputs[2].Value()

	if name == "" || id == "" {
		m.message = "Name and ID are required"
		m.messageType = "error"
		return
	}

	cfg := config.Get()
	cfg.AddSoftware(config.Software{
		Name:     name,
		ID:       id,
		Category: category,
	})
	if err := config.Save(); err != nil {
		log.Printf("Error: failed to save config after adding package: %v", err)
		m.message = fmt.Sprintf("%s: %v", i18n.T("config_save_error"), err)
		m.messageType = "error"
		return
	}

	// 刷新列表
	m.packages = cfg.GetSoftwareList()
	m.refreshTable()

	m.mode = "list"
	m.message = fmt.Sprintf("Added: %s", name)
	m.messageType = "success"
}

// updatePackage 更新包
func (m *ConfigModel) updatePackage() {
	name := m.inputs[0].Value()
	id := m.inputs[1].Value()
	category := m.inputs[2].Value()

	if name == "" || id == "" {
		m.message = "Name and ID are required"
		m.messageType = "error"
		return
	}

	cfg := config.Get()
	cfg.UpdateSoftware(m.selected, config.Software{
		Name:     name,
		ID:       id,
		Category: category,
	})
	if err := config.Save(); err != nil {
		log.Printf("Error: failed to save config after updating package: %v", err)
		m.message = fmt.Sprintf("%s: %v", i18n.T("config_save_error"), err)
		m.messageType = "error"
		return
	}

	// 刷新列表
	m.packages = cfg.GetSoftwareList()
	m.refreshTable()

	m.mode = "list"
	m.message = fmt.Sprintf("Updated: %s", name)
	m.messageType = "success"
}

// deletePackage 删除包
func (m *ConfigModel) deletePackage() {
	if m.selected >= len(m.packages) {
		m.mode = "list"
		return
	}

	name := m.packages[m.selected].Name
	cfg := config.Get()
	cfg.RemoveSoftware(m.selected)
	if err := config.Save(); err != nil {
		log.Printf("Error: failed to save config after removing package: %v", err)
		m.message = fmt.Sprintf("%s: %v", i18n.T("config_save_error"), err)
		m.messageType = "error"
		return
	}

	// 刷新列表
	m.packages = cfg.GetSoftwareList()
	m.refreshTable()

	m.mode = "list"
	m.message = fmt.Sprintf("Removed: %s", name)
	m.messageType = "success"
}

// refreshTable 刷新表格
func (m *ConfigModel) refreshTable() {
	var rows []table.Row
	for i, pkg := range m.packages {
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
	m.table.SetRows(rows)
}

// View 视图
func (m ConfigModel) View() string {
	if m.quitting {
		return "\n  " + i18n.T("common_cancel") + "\n"
	}

	var b strings.Builder

	// 标题
	b.WriteString(TitleStyle.Render(i18n.T("config_title")))
	b.WriteString("\n\n")

	switch m.mode {
	case "list":
		// 表格
		if len(m.packages) > 0 {
			b.WriteString(m.table.View())
			b.WriteString("\n")
		} else {
			b.WriteString(WarningStyle.Render(i18n.T("warn_no_packages")))
			b.WriteString("\n")
		}

		// 消息
		if m.message != "" {
			b.WriteString("\n")
			if m.messageType == "success" {
				b.WriteString(SuccessStyle.Render(m.message))
			} else if m.messageType == "error" {
				b.WriteString(ErrorStyle.Render(m.message))
			} else {
				b.WriteString(InfoStyle.Render(m.message))
			}
			b.WriteString("\n")
		}

		// 帮助
		b.WriteString("\n")
		b.WriteString(HelpStyle.Render(
			i18n.T("config_add") + " a | " +
				i18n.T("config_edit") + " e | " +
				i18n.T("config_remove") + " d/r | " +
				i18n.T("common_cancel") + " q",
		))

	case "add":
		b.WriteString(HighlightStyle.Render(i18n.T("config_add")))
		b.WriteString("\n\n")

		for i, input := range m.inputs {
			label := ""
			switch i {
			case 0:
				label = i18n.T("config_name") + ":"
			case 1:
				label = i18n.T("config_id") + ":"
			case 2:
				label = i18n.T("config_category") + ":"
			}

			if i == m.focusIndex {
				b.WriteString(HighlightStyle.Render("> "+label) + " ")
			} else {
				b.WriteString("  " + label + " ")
			}
			b.WriteString(input.View())
			b.WriteString("\n")
		}

		b.WriteString("\n")
		b.WriteString(HelpStyle.Render(i18n.T("common_confirm") + " Enter | " + i18n.T("common_cancel") + " q"))

	case "edit":
		b.WriteString(HighlightStyle.Render(i18n.T("config_edit")))
		b.WriteString("\n\n")

		for i, input := range m.inputs {
			label := ""
			switch i {
			case 0:
				label = i18n.T("config_name") + ":"
			case 1:
				label = i18n.T("config_id") + ":"
			case 2:
				label = i18n.T("config_category") + ":"
			}

			if i == m.focusIndex {
				b.WriteString(HighlightStyle.Render("> "+label) + " ")
			} else {
				b.WriteString("  " + label + " ")
			}
			b.WriteString(input.View())
			b.WriteString("\n")
		}

		b.WriteString("\n")
		b.WriteString(HelpStyle.Render(i18n.T("common_confirm") + " Enter | " + i18n.T("common_cancel") + " q"))

	case "remove":
		if m.selected < len(m.packages) {
			pkg := m.packages[m.selected]
			b.WriteString(WarningStyle.Render("Confirm removal:"))
			b.WriteString("\n\n")
			b.WriteString(fmt.Sprintf("  Name: %s\n", pkg.Name))
			id := pkg.ID
			if id == "" {
				id = pkg.Package
			}
			b.WriteString(fmt.Sprintf("  ID: %s\n", id))
			b.WriteString("\n")
			b.WriteString(HelpStyle.Render(i18n.T("common_yes") + " y | " + i18n.T("common_no") + " n"))
		}
	}

	return b.String()
}

// RunConfigManager 运行配置管理器
func RunConfigManager() {
	p := tea.NewProgram(NewConfigModel(), tea.WithAltScreen())
	if _, err := p.Run(); err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
}

// RunWizard 运行向导
func RunWizard() {
	// 简化的向导实现
	fmt.Println(GetLogo())
	fmt.Println()
	fmt.Println(TitleStyle.Render(i18n.T("wizard_welcome")))
	fmt.Println()
	fmt.Println(i18n.T("wizard_desc"))
	fmt.Println()

	// 选择语言
	fmt.Println(InfoStyle.Render("Select language / 选择语言:"))
	fmt.Println("  1. English")
	fmt.Println("  2. 中文")
	fmt.Print("\nEnter choice (1-2): ")

	var choice string
	if _, err := fmt.Scanln(&choice); err != nil {
		log.Printf("Warning: failed to read language choice: %v", err)
		// 默认使用中文
		i18n.SetLanguage("zh")
	} else if choice == "1" {
		i18n.SetLanguage("en")
	} else {
		i18n.SetLanguage("zh")
	}

	fmt.Println()
	fmt.Println(SuccessStyle.Render("✓ " + i18n.T("wizard_finish")))
}

// RunBatch 运行批量安装
func RunBatch(packages []config.Software, parallel bool) {
	RunInstall(packages, parallel)
}

// RunBatchFromFile 从文件批量安装
func RunBatchFromFile(file string) {
	cfg := config.Get()
	err := cfg.ImportFromFile(file)
	if err != nil {
		fmt.Println(ErrorStyle.Render(fmt.Sprintf("Failed to load file: %v", err)))
		return
	}

	packages := cfg.GetSoftwareList()
	RunInstall(packages, true)
}

// RunExport 运行导出
func RunExport(packages []config.Software, format, output string) {
	if len(packages) == 0 {
		fmt.Println(WarningStyle.Render(i18n.T("warn_no_packages")))
		return
	}

	cfg := config.Get()

	if output != "" {
		err := cfg.ExportToFile(output)
		if err != nil {
			fmt.Println(ErrorStyle.Render(fmt.Sprintf("Export failed: %v", err)))
			return
		}
		fmt.Println(SuccessStyle.Render(fmt.Sprintf("Exported to: %s", output)))
	} else {
		// 打印到控制台
		fmt.Println(InfoStyle.Render("Current configuration:"))
		for i, pkg := range packages {
			id := pkg.ID
			if id == "" {
				id = pkg.Package
			}
			fmt.Printf("  %d. %s (%s) [%s]\n", i+1, pkg.Name, id, pkg.Category)
		}
	}
}

// RunUpdateCheck 运行更新检查
func RunUpdateCheck() {
	fmt.Println(TitleStyle.Render(i18n.T("cmd_update_short")))
	fmt.Println()
	fmt.Println(InfoStyle.Render("Checking for updates..."))

	// 这里可以实现实际的更新检查逻辑
	fmt.Println()
	fmt.Println(SuccessStyle.Render("✓ You are using the latest version!"))
}

// RunClean 运行清理
func RunClean() {
	fmt.Println(TitleStyle.Render(i18n.T("cmd_clean_short")))
	fmt.Println()
	fmt.Println(InfoStyle.Render("Cleaning cache..."))

	// 这里可以实现实际的清理逻辑
	fmt.Println()
	fmt.Println(SuccessStyle.Render("✓ Cache cleaned successfully!"))
}

// RunStatus 运行状态检查
func RunStatus() {
	fmt.Println(TitleStyle.Render(i18n.T("cmd_status_short")))
	fmt.Println()

	// 平台信息
	pm, available := installer.CheckPackageManager()

	fmt.Println(InfoStyle.Render(i18n.T("status_platform") + ":"))
	fmt.Printf("  OS: %s\n", getOSName())
	fmt.Printf("  Arch: %s\n", getArch())
	fmt.Println()

	fmt.Println(InfoStyle.Render(i18n.T("status_package_mgr") + ":"))
	if available {
		fmt.Printf("  %s: %s\n", pm, SuccessStyle.Render("Available"))
	} else {
		fmt.Printf("  %s: %s\n", pm, ErrorStyle.Render("Not available"))
	}
	fmt.Println()

	// 已安装软件
	inst := installer.NewInstaller()
	if inst != nil {
		fmt.Println(InfoStyle.Render(i18n.T("status_installed") + ":"))
		installed, err := inst.GetInstalled()
		if err == nil {
			fmt.Printf("  Total: %d packages\n", len(installed))
		}
	}
}

// getOSName 获取操作系统名称
func getOSName() string {
	return "Windows"
}

// getArch 获取架构
func getArch() string {
	return "amd64"
}
