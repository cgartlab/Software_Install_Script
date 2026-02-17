package cmd

import (
	"fmt"
	"log"
	"os"
	"runtime"

	"github.com/charmbracelet/lipgloss"
	"github.com/spf13/cobra"
	"swiftinstall/internal/config"
	"swiftinstall/internal/i18n"
	"swiftinstall/internal/ui"
)

var (
	version   = "dev"
	commit    = "unknown"
	date      = "unknown"
	cfgFile   string
	language  string
)

var rootCmd = &cobra.Command{
	Use:   "sis",
	Short: i18n.T("app_short_desc"),
	Long:  ui.GetLogo() + "\n\n" + i18n.T("app_long_desc"),
	Run: func(cmd *cobra.Command, args []string) {
		// 如果没有子命令，显示帮助信息并启动交互式菜单
		fmt.Println(ui.GetCompactLogo())
		fmt.Println()
		fmt.Println(ui.InfoStyle.Render("Usage: sis <command> [flags]"))
		fmt.Println()
		fmt.Println(ui.HelpStyle.Render("Commands:"))
		fmt.Println(ui.HelpStyle.Render("  install     Install software packages"))
		fmt.Println(ui.HelpStyle.Render("  uninstall   Uninstall software packages"))
		fmt.Println(ui.HelpStyle.Render("  search      Search for software packages"))
		fmt.Println(ui.HelpStyle.Render("  list        List configured packages"))
		fmt.Println(ui.HelpStyle.Render("  config      Manage configuration"))
		fmt.Println(ui.HelpStyle.Render("  status      Show system status"))
		fmt.Println()
		fmt.Println(ui.HelpStyle.Render("Run 'sis --help' for more information"))
		fmt.Println()
		
		// 询问是否启动交互式菜单
		fmt.Print(ui.InfoStyle.Render("Launch interactive menu? [Y/n]: "))
		var response string
		if _, err := fmt.Scanln(&response); err != nil {
			// 输入错误时默认启动交互式菜单
			log.Printf("Warning: failed to read user input: %v", err)
			fmt.Println()
			fmt.Println(ui.InfoStyle.Render("Input reading failed. Launching interactive menu automatically..."))
			fmt.Println()
			runInteractiveTUI()
			return
		}
		if response == "" || response == "y" || response == "Y" {
			runInteractiveTUI()
		}
	},
}

func Execute() error {
	return rootCmd.Execute()
}

func init() {
	cobra.OnInitialize(initConfig)

	rootCmd.PersistentFlags().StringVar(&cfgFile, "config", "", i18n.T("flag_config"))
	rootCmd.PersistentFlags().StringVarP(&language, "lang", "l", "", i18n.T("flag_language"))

	// 添加子命令
	rootCmd.AddCommand(versionCmd)
	rootCmd.AddCommand(installCmd)
	rootCmd.AddCommand(uninstallCmd)
	rootCmd.AddCommand(searchCmd)
	rootCmd.AddCommand(listCmd)
	rootCmd.AddCommand(configCmd)
	rootCmd.AddCommand(wizardCmd)
	rootCmd.AddCommand(batchCmd)
	rootCmd.AddCommand(exportCmd)
	rootCmd.AddCommand(updateCmd)
	rootCmd.AddCommand(cleanCmd)
	rootCmd.AddCommand(statusCmd)
}

func initConfig() {
	// 初始化配置
	if cfgFile != "" {
		config.SetConfigFile(cfgFile)
	}
	config.Init()

	// 设置语言
	if language != "" {
		i18n.SetLanguage(language)
	} else if lang := config.GetString("language"); lang != "" {
		i18n.SetLanguage(lang)
	}
}

var versionCmd = &cobra.Command{
	Use:   "version",
	Short: i18n.T("cmd_version_short"),
	Run: func(cmd *cobra.Command, args []string) {
		style := lipgloss.NewStyle().
			Foreground(lipgloss.Color(ui.ColorPrimary)).
			Bold(true)

		fmt.Println(ui.GetLogo())
		fmt.Println()
		fmt.Println(style.Render(fmt.Sprintf("Version: %s", version)))
		fmt.Println(style.Render(fmt.Sprintf("Commit:  %s", commit)))
		fmt.Println(style.Render(fmt.Sprintf("Date:    %s", date)))
		fmt.Println(style.Render(fmt.Sprintf("Go:      %s", runtime.Version())))
		fmt.Println(style.Render(fmt.Sprintf("OS/Arch: %s/%s", runtime.GOOS, runtime.GOARCH)))
	},
}

var installCmd = &cobra.Command{
	Use:   "install [package...]",
	Short: i18n.T("cmd_install_short"),
	Long:  i18n.T("cmd_install_long"),
	Run: func(cmd *cobra.Command, args []string) {
		if len(args) == 0 {
			// 从配置文件安装
			runInstallFromConfig()
		} else {
			// 安装指定包
			runInstallPackages(args)
		}
	},
}

var uninstallCmd = &cobra.Command{
	Use:   "uninstall [package...]",
	Short: i18n.T("cmd_uninstall_short"),
	Long:  i18n.T("cmd_uninstall_long"),
	Run: func(cmd *cobra.Command, args []string) {
		if len(args) == 0 {
			runUninstallFromConfig()
		} else {
			runUninstallPackages(args)
		}
	},
}

var searchCmd = &cobra.Command{
	Use:   "search <query>",
	Short: i18n.T("cmd_search_short"),
	Long:  i18n.T("cmd_search_long"),
	Args:  cobra.ExactArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		runSearch(args[0])
	},
}

var listCmd = &cobra.Command{
	Use:   "list",
	Short: i18n.T("cmd_list_short"),
	Long:  i18n.T("cmd_list_long"),
	Run: func(cmd *cobra.Command, args []string) {
		runList()
	},
}

var configCmd = &cobra.Command{
	Use:   "config",
	Short: i18n.T("cmd_config_short"),
	Long:  i18n.T("cmd_config_long"),
	Run: func(cmd *cobra.Command, args []string) {
		runConfig()
	},
}

var wizardCmd = &cobra.Command{
	Use:   "wizard",
	Short: i18n.T("cmd_wizard_short"),
	Long:  i18n.T("cmd_wizard_long"),
	Run: func(cmd *cobra.Command, args []string) {
		runWizard()
	},
}

var batchCmd = &cobra.Command{
	Use:   "batch [file]",
	Short: i18n.T("cmd_batch_short"),
	Long:  i18n.T("cmd_batch_long"),
	Run: func(cmd *cobra.Command, args []string) {
		if len(args) > 0 {
			runBatchFromFile(args[0])
		} else {
			runBatchFromConfig()
		}
	},
}

var exportCmd = &cobra.Command{
	Use:   "export",
	Short: i18n.T("cmd_export_short"),
	Long:  i18n.T("cmd_export_long"),
	Run: func(cmd *cobra.Command, args []string) {
		format, _ := cmd.Flags().GetString("format")
		output, _ := cmd.Flags().GetString("output")
		runExport(format, output)
	},
}

var updateCmd = &cobra.Command{
	Use:   "update",
	Short: i18n.T("cmd_update_short"),
	Long:  i18n.T("cmd_update_long"),
	Run: func(cmd *cobra.Command, args []string) {
		runUpdate()
	},
}

var cleanCmd = &cobra.Command{
	Use:   "clean",
	Short: i18n.T("cmd_clean_short"),
	Long:  i18n.T("cmd_clean_long"),
	Run: func(cmd *cobra.Command, args []string) {
		runClean()
	},
}

var statusCmd = &cobra.Command{
	Use:   "status",
	Short: i18n.T("cmd_status_short"),
	Long:  i18n.T("cmd_status_long"),
	Run: func(cmd *cobra.Command, args []string) {
		runStatus()
	},
}

func init() {
	exportCmd.Flags().StringP("format", "f", "json", i18n.T("flag_export_format"))
	exportCmd.Flags().StringP("output", "o", "", i18n.T("flag_export_output"))
	batchCmd.Flags().BoolP("parallel", "p", true, i18n.T("flag_parallel"))
}

func runInteractiveTUI() {
	// 启动交互式 TUI
	ui.RunMainMenu()
}

func runInstallFromConfig() {
	cfg := config.Get()
	packages := cfg.GetSoftwareList()
	if len(packages) == 0 {
		fmt.Println(ui.WarningStyle.Render(i18n.T("warn_no_packages")))
		os.Exit(1)
	}
	ui.RunInstall(packages, false)
}

func runInstallPackages(packages []string) {
	ui.RunInstallByName(packages, false)
}

func runUninstallFromConfig() {
	cfg := config.Get()
	packages := cfg.GetSoftwareList()
	if len(packages) == 0 {
		fmt.Println(ui.WarningStyle.Render(i18n.T("warn_no_packages")))
		os.Exit(1)
	}
	ui.RunUninstall(packages)
}

func runUninstallPackages(packages []string) {
	ui.RunUninstallByName(packages)
}

func runSearch(query string) {
	ui.RunSearch(query)
}

func runList() {
	cfg := config.Get()
	packages := cfg.GetSoftwareList()
	ui.ShowPackageList(packages)
}

func runConfig() {
	ui.RunConfigManager()
}

func runWizard() {
	ui.RunWizard()
}

func runBatchFromFile(file string) {
	ui.RunBatchFromFile(file)
}

func runBatchFromConfig() {
	cfg := config.Get()
	packages := cfg.GetSoftwareList()
	ui.RunBatch(packages, true)
}

func runExport(format, output string) {
	cfg := config.Get()
	packages := cfg.GetSoftwareList()
	ui.RunExport(packages, format, output)
}

func runUpdate() {
	ui.RunUpdateCheck()
}

func runClean() {
	ui.RunClean()
}

func runStatus() {
	ui.RunStatus()
}
