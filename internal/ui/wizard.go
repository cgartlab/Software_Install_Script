package ui

import (
	"fmt"
	"io"
	"log"
	"os"
	"runtime"

	"github.com/charmbracelet/bubbles/list"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
	"swiftinstall/internal/config"
	"swiftinstall/internal/i18n"
)

// GetCurrentPlatform 获取当前平台
func GetCurrentPlatform() string {
	return runtime.GOOS
}

// GetPackageManagerForPlatform 为指定平台获取包管理器
func GetPackageManagerForPlatform(platform string) string {
	switch platform {
	case "windows":
		return "winget"
	case "darwin":
		return "brew"
	case "linux":
		return "apt/yum/dnf"
	default:
		return "unknown"
	}
}

// WizardItem 向导项
type WizardItem struct {
	Title       string
	Description string
	Value       interface{}
}

func (i WizardItem) FilterValue() string { return i.Title }

// WizardStepType 向导步骤类型
type WizardStepType int

const (
	WizardStepWelcome WizardStepType = iota
	WizardStepLanguage
	WizardStepPlatform
	WizardStepPackageManager
	WizardStepSoftwareSelection
	WizardStepReview
	WizardStepInstall
	WizardStepComplete
)

// WizardModel 向导模型
type WizardModel struct {
	step         WizardStepType
	list         list.Model
	quitting     bool
	width        int
	height       int
	selectedLang string
	softwareList []config.Software
	installSteps []string
	currentStep  int
	totalSteps   int
}

// NewWizard 创建新向导
func NewWizard() WizardModel {
	m := WizardModel{
		step:        WizardStepWelcome,
		softwareList: make([]config.Software, 0),
		installSteps: make([]string, 0),
		currentStep:  1,
		totalSteps:   8,
	}
	
	// 初始化列表
	items := []list.Item{
		WizardItem{Title: "Git", Description: "Version control system", Value: "Git.Git"},
		WizardItem{Title: "VS Code", Description: "Popular code editor", Value: "Microsoft.VisualStudioCode"},
		WizardItem{Title: "Node.js", Description: "JavaScript runtime", Value: "OpenJS.NodeJS"},
		WizardItem{Title: "Python", Description: "Python programming language", Value: "Python.Python"},
		WizardItem{Title: "Docker", Description: "Container platform", Value: "Docker.DockerDesktop"},
		WizardItem{Title: "Postman", Description: "API development tool", Value: "Postman.Postman"},
		WizardItem{Title: "Google Chrome", Description: "Web browser", Value: "Google.Chrome"},
		WizardItem{Title: "Visual Studio", Description: "IDE for .NET development", Value: "Microsoft.VisualStudio.2022.Community"},
	}
	
	l := list.New(items, wizardItemDelegate{}, 0, 0)
	l.Title = i18n.T("wizard_software_selection")
	l.SetShowStatusBar(false)
	l.SetFilteringEnabled(true)
	l.Styles.Title = TitleStyle
	
	m.list = l
	return m
}

// Init 初始化
func (m WizardModel) Init() tea.Cmd {
	return nil
}

// Update 更新
func (m WizardModel) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.WindowSizeMsg:
		m.width = msg.Width
		m.height = msg.Height
		if m.list.IsFiltered() {
			m.list.SetHeight(m.height - 20) // 额外空间用于过滤器输入
		} else {
			m.list.SetHeight(m.height - 10)
		}
		m.list.SetWidth(m.width - 4)
		return m, nil

	case tea.KeyMsg:
		switch msg.Type {
		case tea.KeyEnter:
			return m.handleEnter()
		case tea.KeyEsc:
			if m.step != WizardStepWelcome && m.step != WizardStepComplete {
				m.step = WizardStepWelcome
				return m, nil
			}
		case tea.KeyCtrlC:
			m.quitting = true
			return m, tea.Quit
		}
		
		// 处理快捷键
		switch msg.String() {
		case "n", "N":
			// 下一步
			return m.nextStep()
		case "b", "B":
			// 上一步
			return m.prevStep()
		case "q", "Q":
			m.quitting = true
			return m, tea.Quit
		}
	}

	var cmd tea.Cmd
	if m.isSoftwareSelectionStep() {
		m.list, cmd = m.list.Update(msg)
		return m, cmd
	}

	return m, nil
}

// handleEnter 处理回车键
func (m WizardModel) handleEnter() (WizardModel, tea.Cmd) {
	switch m.step {
	case WizardStepWelcome:
		m.step = WizardStepLanguage
	case WizardStepLanguage:
		// 语言选择通常有子选项，这里简化处理
		m.step = WizardStepPlatform
	case WizardStepPlatform:
		m.step = WizardStepPackageManager
	case WizardStepPackageManager:
		m.step = WizardStepSoftwareSelection
	case WizardStepSoftwareSelection:
		// 获取选中的软件
		if selectedItem := m.list.SelectedItem(); selectedItem != nil {
			// 切换到下一个步骤而不是继续选择
			m.step = WizardStepReview
		}
	case WizardStepReview:
		m.step = WizardStepInstall
	case WizardStepInstall:
		m.step = WizardStepComplete
	case WizardStepComplete:
		m.quitting = true
		return m, tea.Quit
	}
	
	return m, nil
}

// nextStep 下一步
func (m WizardModel) nextStep() (WizardModel, tea.Cmd) {
	nextStep := m.step + 1
	if nextStep <= WizardStepComplete {
		m.step = nextStep
	}
	return m, nil
}

// prevStep 上一步
func (m WizardModel) prevStep() (WizardModel, tea.Cmd) {
	prevStep := m.step - 1
	if prevStep >= WizardStepWelcome {
		m.step = prevStep
	}
	return m, nil
}

// isSoftwareSelectionStep 是否是软件选择步骤
func (m WizardModel) isSoftwareSelectionStep() bool {
	return m.step == WizardStepSoftwareSelection
}

// View 视图
func (m WizardModel) View() string {
	if m.quitting {
		return "\n  " + i18n.T("wizard_goodbye") + "\n"
	}

	var content string
	
	// 显示进度条
	progress := fmt.Sprintf("%s: %d/%d", i18n.T("wizard_progress"), m.currentStep, m.totalSteps)
	content += SubtitleStyle.Render(progress) + "\n\n"

	switch m.step {
	case WizardStepWelcome:
		content += m.renderWelcomeStep()
	case WizardStepLanguage:
		content += m.renderLanguageStep()
	case WizardStepPlatform:
		content += m.renderPlatformStep()
	case WizardStepPackageManager:
		content += m.renderPackageManagerStep()
	case WizardStepSoftwareSelection:
		content += m.renderSoftwareSelectionStep()
	case WizardStepReview:
		content += m.renderReviewStep()
	case WizardStepInstall:
		content += m.renderInstallStep()
	case WizardStepComplete:
		content += m.renderCompleteStep()
	}

	// 添加导航帮助
	helpText := fmt.Sprintf("%s: n(next) • b(back) • q(quit) • enter(select)",
		i18n.T("common_navigation"))
	help := HelpStyle.Render(helpText)

	return lipgloss.JoinVertical(
		lipgloss.Left,
		GetLogo(),
		"",
		TitleStyle.Render(i18n.T("wizard_title")),
		"",
		content,
		"",
		help,
	)
}

// renderWelcomeStep 渲染欢迎步骤
func (m WizardModel) renderWelcomeStep() string {
	content := TitleStyle.Render(i18n.T("wizard_welcome")) + "\n\n"
	content += i18n.T("wizard_desc") + "\n\n"
	content += InfoStyle.Render(i18n.T("wizard_follow_guide"))
	return content
}

// renderLanguageStep 渲染语言选择步骤
func (m WizardModel) renderLanguageStep() string {
	content := TitleStyle.Render(i18n.T("wizard_language")) + "\n\n"
	content += i18n.T("wizard_select_language") + "\n\n"
	content += "  1. English\n"
	content += "  2. 中文\n\n"
	content += InfoStyle.Render(i18n.T("wizard_press_enter_continue"))
	return content
}

// renderPlatformStep 渲染平台选择步骤
func (m WizardModel) renderPlatformStep() string {
	content := TitleStyle.Render(i18n.T("wizard_platform")) + "\n\n"
	content += i18n.T("wizard_detected_platform") + ": " + GetCurrentPlatform() + "\n\n"
	content += i18n.T("wizard_platform_info") + "\n\n"
	content += InfoStyle.Render(i18n.T("wizard_press_enter_continue"))
	return content
}

// renderPackageManagerStep 渲染包管理器选择步骤
func (m WizardModel) renderPackageManagerStep() string {
	content := TitleStyle.Render(i18n.T("wizard_package_manager")) + "\n\n"
	pm := GetPackageManagerForPlatform(GetCurrentPlatform())
	content += i18n.T("wizard_detected_package_manager") + ": " + pm + "\n\n"
	content += i18n.T("wizard_package_manager_info") + "\n\n"
	content += InfoStyle.Render(i18n.T("wizard_press_enter_continue"))
	return content
}

// renderSoftwareSelectionStep 渲染软件选择步骤
func (m WizardModel) renderSoftwareSelectionStep() string {
	content := i18n.T("wizard_select_software") + "\n\n"
	content += m.list.View() + "\n\n"
	content += InfoStyle.Render(i18n.T("wizard_use_arrows_select"))
	return content
}

// renderReviewStep 渲染审核步骤
func (m WizardModel) renderReviewStep() string {
	content := TitleStyle.Render(i18n.T("wizard_review")) + "\n\n"
	content += i18n.T("wizard_selected_software") + ":\n"
	for _, software := range m.softwareList {
		content += "  - " + software.Name + " (" + software.Package + ")\n"
	}
	content += "\n" + InfoStyle.Render(i18n.T("wizard_press_enter_install"))
	return content
}

// renderInstallStep 渲染安装步骤
func (m WizardModel) renderInstallStep() string {
	content := TitleStyle.Render(i18n.T("wizard_installing")) + "\n\n"
	content += i18n.T("wizard_installing_desc") + "\n\n"
	
	// 显示安装进度
	if len(m.installSteps) > 0 {
		for _, step := range m.installSteps {
			content += "  ✓ " + step + "\n"
		}
	} else {
		content += InfoStyle.Render(i18n.T("wizard_please_wait"))
	}
	
	return content
}

// renderCompleteStep 渲染完成步骤
func (m WizardModel) renderCompleteStep() string {
	content := TitleStyle.Render(i18n.T("wizard_complete")) + "\n\n"
	content += SuccessStyle.Render(i18n.T("wizard_successfully_installed")) + "\n\n"
	content += i18n.T("wizard_next_steps") + ":\n"
	content += "  - " + i18n.T("wizard_check_installed_software") + "\n"
	content += "  - " + i18n.T("wizard_run_sis_command") + "\n\n"
	content += InfoStyle.Render(i18n.T("wizard_thank_you"))
	return content
}

// wizardItemDelegate 软件项委托
type wizardItemDelegate struct{}

func (d wizardItemDelegate) Height() int                             { return 2 }
func (d wizardItemDelegate) Spacing() int                            { return 1 }
func (d wizardItemDelegate) Update(_ tea.Msg, _ *list.Model) tea.Cmd { return nil }
func (d wizardItemDelegate) Render(w io.Writer, m list.Model, index int, listItem list.Item) {
	item, ok := listItem.(WizardItem)
	if !ok {
		return
	}

	title := item.Title
	desc := item.Description

	if index == m.Index() {
		title = MenuSelectedStyle.Render("> " + title)
		desc = MenuSelectedStyle.UnsetBold().Foreground(lipgloss.Color(ColorMuted)).Render("  " + desc)
	} else {
		title = MenuStyle.Render("  " + title)
		desc = MenuDescriptionStyle.Render(desc)
	}

	fmt.Fprint(w, lipgloss.JoinVertical(lipgloss.Left, title, desc))
}

// RunNewWizard 运行新向导
func RunNewWizard() {
	p := tea.NewProgram(NewWizard(), tea.WithAltScreen())
	if _, err := p.Run(); err != nil {
		log.Printf("Error running wizard: %v", err)
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
}