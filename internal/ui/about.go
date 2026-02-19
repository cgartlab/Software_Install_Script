package ui

import (
	"fmt"
	"os"
	"strings"

	tea "github.com/charmbracelet/bubbletea"
	"swiftinstall/internal/appinfo"
)

// GetAboutText 返回关于信息
func GetAboutText() string {
	return fmt.Sprintf("%s\n%s: %s\n%s: %s\nGitHub: %s\n%s",
		TitleStyle.Render("关于 SwiftInstall"),
		"作者", appinfo.Author,
		"联系方式", appinfo.Contact,
		appinfo.GitHubURL,
		HelpStyle.Render(appinfo.Copyright),
	)
}

// AboutModel 关于页面模型
type AboutModel struct {
	width    int
	height   int
	quitting bool
}

// NewAboutModel 创建关于页面模型
func NewAboutModel() AboutModel {
	return AboutModel{}
}

// Init 初始化
func (m AboutModel) Init() tea.Cmd {
	return nil
}

// Update 更新
func (m AboutModel) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.WindowSizeMsg:
		m.width = msg.Width
		m.height = msg.Height
		return m, nil

	case tea.KeyMsg:
		// 任意键退出
		m.quitting = true
		return m, tea.Quit
	}
	return m, nil
}

// View 视图
func (m AboutModel) View() string {
	var b strings.Builder

	b.WriteString(GetLogo())
	b.WriteString("\n\n")
	b.WriteString(GetAboutText())
	b.WriteString("\n\n")
	b.WriteString(HelpStyle.Render("Press any key to go back"))

	return b.String()
}

// RunAbout 显示关于页面
func RunAbout() {
	// 使用 TUI 模式显示关于页面
	p := tea.NewProgram(NewAboutModel(), tea.WithAltScreen())
	if _, err := p.Run(); err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
}

// ShowAboutSimple 简单显示关于信息（用于命令行模式）
func ShowAboutSimple() {
	fmt.Println(GetLogo())
	fmt.Println()
	fmt.Println(GetAboutText())
	fmt.Println()
	fmt.Println(HelpStyle.Render("Author: "+appinfo.Author+" | "+appinfo.Copyright))
}
