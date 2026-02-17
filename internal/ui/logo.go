package ui

import (
	"github.com/charmbracelet/lipgloss"
)

// Logo ASCII 艺术
const (
	logoFull = `
███████╗██╗    ██╗██╗███████╗████████╗    ██╗███╗   ██╗███████╗████████╗ █████╗ ██╗     ██╗     
██╔════╝██║    ██║██║██╔════╝╚══██╔══╝    ██║████╗  ██║██╔════╝╚══██╔══╝██╔══██╗██║     ██║     
███████╗██║ █╗ ██║██║█████╗     ██║       ██║██╔██╗ ██║███████╗   ██║   ███████║██║     ██║     
╚════██║██║███╗██║██║██╔══╝     ██║       ██║██║╚██╗██║╚════██║   ██║   ██╔══██║██║     ██║     
███████║╚███╔███╔╝██║██║        ██║       ██║██║ ╚████║███████║   ██║   ██║  ██║███████╗███████╗
╚══════╝ ╚══╝╚══╝ ╚═╝╚═╝        ╚═╝       ╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝`

	logoCompact = `
███████╗██╗    ██╗██╗███████╗████████╗    ██╗███╗   ██╗███████╗████████╗ █████╗ ██╗     ██╗     
██╔════╝██║    ██║██║██╔════╝╚══██╔══╝    ██║████╗  ██║██╔════╝╚══██╔══╝██╔══██╗██║     ██║     
███████╗██║ █╗ ██║██║█████╗     ██║       ██║██╔██╗ ██║███████╗   ██║   ███████║██║     ██║     
╚════██║██║███╗██║██║██╔══╝     ██║       ██║██║╚██╗██║╚════██║   ██║   ██╔══██║██║     ██║     
███████║╚███╔███╔╝██║██║        ██║       ██║██║ ╚████║███████║   ██║   ██║  ██║███████╗███████╗
╚══════╝ ╚══╝╚══╝ ╚═╝╚═╝        ╚═╝       ╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝
`
	logoMinimal = `⚡ SwiftInstall ⚡`
)

// GetLogo 获取 Logo
func GetLogo() string {
	return LogoStyle.Render(logoFull)
}

// GetCompactLogo 获取紧凑版 Logo
func GetCompactLogo() string {
	return LogoStyle.Render(logoCompact)
}

// GetMinimalLogo 获取最小版 Logo
func GetMinimalLogo() string {
	return lipgloss.NewStyle().
		Foreground(lipgloss.Color(ColorPrimaryBright)).
		Bold(true).
		Render(logoMinimal)
}

// GetLogoWithVersion 获取带版本的 Logo
func GetLogoWithVersion(version string) string {
	logo := GetLogo()
	versionStr := lipgloss.NewStyle().
		Foreground(lipgloss.Color(ColorMuted)).
		Render("Version: " + version)
	return logo + "\n" + versionStr
}

// GetWelcomeMessage 获取欢迎消息
func GetWelcomeMessage() string {
	welcome := `
欢迎使用 SwiftInstall！

这是一个跨平台软件安装工具，支持：
  • Windows (Winget)
  • macOS (Homebrew)

使用方向键导航，Enter 键选择，q 键退出。
`
	return BoxStyle.Render(welcome)
}
