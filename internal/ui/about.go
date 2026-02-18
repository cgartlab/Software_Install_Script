package ui

import (
	"fmt"

	"swiftinstall/internal/appinfo"
	"swiftinstall/internal/i18n"
)

// GetAboutText 返回关于信息
func GetAboutText() string {
	return fmt.Sprintf("%s\n%s: %s\n%s: %s\nGitHub: %s\n%s",
		TitleStyle.Render(i18n.T("about_title")),
		i18n.T("about_author"), appinfo.Author,
		i18n.T("about_contact"), appinfo.Contact,
		appinfo.GitHubURL,
		HelpStyle.Render(appinfo.Copyright),
	)
}

// RunAbout 显示关于页面
func RunAbout() {
	fmt.Println(GetLogo())
	fmt.Println()
	fmt.Println(GetAboutText())
}
