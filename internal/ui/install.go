package ui

import (
	"fmt"
	"os"
	"strings"
	"sync"
	"time"

	"github.com/charmbracelet/bubbles/progress"
	"github.com/charmbracelet/bubbles/table"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
	"swiftinstall/internal/config"
	"swiftinstall/internal/i18n"
	"swiftinstall/internal/installer"
)

// InstallModel 安装界面模型
type InstallModel struct {
	packages []config.Software
	results  []*installer.InstallResult
	progress progress.Model
	table    table.Model
	status   string
	quitting bool
	done     bool
	parallel bool
	width    int
	height   int
	mu       sync.Mutex
}

// tickMsg 定时消息
type tickMsg struct{}

// NewInstallModel 创建安装模型
func NewInstallModel(packages []config.Software, parallel bool) InstallModel {
	p := progress.New(progress.WithDefaultGradient())
	p.Width = 50

	columns := []table.Column{
		{Title: i18n.T("config_name"), Width: 20},
		{Title: i18n.T("config_id"), Width: 30},
		{Title: i18n.T("common_status"), Width: 15},
	}

	var rows []table.Row
	for _, pkg := range packages {
		id := pkg.ID
		if id == "" {
			id = pkg.Package
		}
		rows = append(rows, table.Row{
			pkg.Name,
			id,
			i18n.T("common_pending"),
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

	return InstallModel{
		packages: packages,
		results:  make([]*installer.InstallResult, len(packages)),
		progress: p,
		table:    t,
		parallel: parallel,
		status:   i18n.T("install_progress"),
	}
}

// Init 初始化
func (m InstallModel) Init() tea.Cmd {
	return tea.Batch(
		tickCmd(),
		m.runInstall(),
	)
}

// tickCmd 定时命令
func tickCmd() tea.Cmd {
	return tea.Tick(time.Millisecond*100, func(t time.Time) tea.Msg {
		return tickMsg{}
	})
}

// runInstall 运行安装
func (m InstallModel) runInstall() tea.Cmd {
	return func() tea.Msg {
		var wg sync.WaitGroup
		
		if m.parallel {
			semaphore := make(chan struct{}, 4)
			for i := range m.packages {
				wg.Add(1)
				semaphore <- struct{}{}
				go func(index int) {
					defer wg.Done()
					defer func() { <-semaphore }()
					m.installPackage(index)
				}(i)
			}
		} else {
			for i := range m.packages {
				wg.Add(1)
				go func(index int) {
					defer wg.Done()
					m.installPackage(index)
				}(i)
			}
		}
		
		wg.Wait()
		return installDoneMsg{}
	}
}

// installPackage 安装单个包
func (m *InstallModel) installPackage(index int) {
	inst := installer.NewInstaller()
	if inst == nil {
		m.mu.Lock()
		m.results[index] = &installer.InstallResult{
			Status: installer.StatusFailed,
			Error:  fmt.Errorf("unsupported platform"),
		}
		m.mu.Unlock()
		return
	}

	pkg := m.packages[index]
	packageID := pkg.ID
	if packageID == "" {
		packageID = pkg.Package
	}

	result, _ := inst.Install(packageID)

	m.mu.Lock()
	m.results[index] = result

	status := string(result.Status)
	if result.Status == installer.StatusSuccess {
		status = SuccessStyle.Render(i18n.T("common_success"))
	} else if result.Status == installer.StatusFailed {
		status = ErrorStyle.Render(i18n.T("common_failed"))
	} else if result.Status == installer.StatusSkipped {
		status = WarningStyle.Render(i18n.T("install_skipped"))
	}

	rows := m.table.Rows()
	rows[index][2] = status
	m.table.SetRows(rows)
	m.mu.Unlock()
}

// installDoneMsg 安装完成消息
type installDoneMsg struct{}

// Update 更新
func (m InstallModel) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
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
			if m.done {
				return m, tea.Quit
			}
		}

	case tickMsg:
		// 计算进度
		completed := 0
		for _, r := range m.results {
			if r != nil {
				completed++
			}
		}
		
		if completed < len(m.packages) {
			percent := float64(completed) / float64(len(m.packages))
			m.progress.SetPercent(percent)
			return m, tickCmd()
		}

	case installDoneMsg:
		m.done = true
		m.progress.SetPercent(1.0)
		m.status = i18n.T("common_done")
		return m, nil

	case progress.FrameMsg:
		progressModel, cmd := m.progress.Update(msg)
		m.progress = progressModel.(progress.Model)
		return m, cmd
	}

	var cmd tea.Cmd
	m.table, cmd = m.table.Update(msg)
	return m, cmd
}

// View 视图
func (m InstallModel) View() string {
	if m.quitting {
		return "\n  " + i18n.T("common_cancel") + "\n"
	}

	var b strings.Builder

	// 标题
	b.WriteString(TitleStyle.Render(i18n.T("install_title")))
	b.WriteString("\n\n")

	// 进度条
	b.WriteString(m.progress.View())
	b.WriteString("\n\n")

	// 状态
	b.WriteString(InfoStyle.Render(m.status))
	b.WriteString("\n\n")

	// 表格
	b.WriteString(m.table.View())
	b.WriteString("\n")

	// 统计
	if m.done {
		success, failed, skipped := 0, 0, 0
		for _, r := range m.results {
			if r != nil {
				switch r.Status {
				case installer.StatusSuccess:
					success++
				case installer.StatusFailed:
					failed++
				case installer.StatusSkipped:
					skipped++
				}
			}
		}

		b.WriteString("\n")
		b.WriteString(SuccessStyle.Render(fmt.Sprintf("✓ %s: %d", i18n.T("install_completed"), success)))
		b.WriteString("  ")
		if failed > 0 {
			b.WriteString(ErrorStyle.Render(fmt.Sprintf("✗ %s: %d", i18n.T("install_failed"), failed)))
			b.WriteString("  ")
		}
		if skipped > 0 {
			b.WriteString(WarningStyle.Render(fmt.Sprintf("⊘ %s: %d", i18n.T("install_skipped"), skipped)))
		}
		b.WriteString("\n\n")
		b.WriteString(HelpStyle.Render(i18n.T("common_confirm") + " Enter | " + i18n.T("common_cancel") + " q"))
	} else {
		b.WriteString("\n")
		b.WriteString(HelpStyle.Render(i18n.T("common_cancel") + " q"))
	}

	return b.String()
}

// RunInstall 运行安装界面
func RunInstall(packages []config.Software, parallel bool) {
	if len(packages) == 0 {
		fmt.Println(WarningStyle.Render(i18n.T("warn_no_packages")))
		return
	}

	p := tea.NewProgram(NewInstallModel(packages, parallel), tea.WithAltScreen())
	if _, err := p.Run(); err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
}

// RunInstallByName 按名称安装
func RunInstallByName(packageNames []string, parallel bool) {
	packages := make([]config.Software, len(packageNames))
	for i, name := range packageNames {
		packages[i] = config.Software{
			Name: name,
			ID:   name,
		}
	}
	RunInstall(packages, parallel)
}

// RunUninstall 运行卸载界面
func RunUninstall(packages []config.Software) {
	// 简化版本，直接卸载
	inst := installer.NewInstaller()
	if inst == nil {
		fmt.Println(ErrorStyle.Render("Unsupported platform"))
		return
	}

	fmt.Println(TitleStyle.Render(i18n.T("menu_uninstall")))
	fmt.Println()

	for _, pkg := range packages {
		packageID := pkg.ID
		if packageID == "" {
			packageID = pkg.Package
		}

		fmt.Printf("Uninstalling %s... ", pkg.Name)
		result, err := inst.Uninstall(packageID)
		if err != nil || result.Status == installer.StatusFailed {
			fmt.Println(ErrorStyle.Render("✗ Failed"))
		} else if result.Status == installer.StatusSkipped {
			fmt.Println(WarningStyle.Render("⊘ Not installed"))
		} else {
			fmt.Println(SuccessStyle.Render("✓ Success"))
		}
	}
}

// RunUninstallByName 按名称卸载
func RunUninstallByName(packageNames []string) {
	packages := make([]config.Software, len(packageNames))
	for i, name := range packageNames {
		packages[i] = config.Software{
			Name: name,
			ID:   name,
		}
	}
	RunUninstall(packages)
}
