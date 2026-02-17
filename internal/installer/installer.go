package installer

import (
	"bufio"
	"fmt"
	"os/exec"
	"runtime"
	"strings"
	"sync"
)

// InstallStatus 安装状态
type InstallStatus string

const (
	StatusPending     InstallStatus = "pending"
	StatusInstalling  InstallStatus = "installing"
	StatusSuccess     InstallStatus = "success"
	StatusFailed      InstallStatus = "failed"
	StatusSkipped     InstallStatus = "skipped"
	StatusDownloading InstallStatus = "downloading"
)

// PackageInfo 包信息
type PackageInfo struct {
	Name        string
	ID          string
	Version     string
	Description string
	Publisher   string
	Installed   bool
}

// InstallResult 安装结果
type InstallResult struct {
	Package PackageInfo
	Status  InstallStatus
	Error   error
	Output  string
}

// Installer 安装器接口
type Installer interface {
	Install(packageID string) (*InstallResult, error)
	Uninstall(packageID string) (*InstallResult, error)
	Search(query string) ([]PackageInfo, error)
	IsInstalled(packageID string) (bool, error)
	GetInstalled() ([]PackageInfo, error)
	Update() error
}

// BaseInstaller 基础安装器
type BaseInstaller struct {
	mu sync.RWMutex
}

// WindowsInstaller Windows 安装器
type WindowsInstaller struct {
	BaseInstaller
}

// NewInstaller 创建安装器
func NewInstaller() Installer {
	switch runtime.GOOS {
	case "windows":
		return &WindowsInstaller{}
	case "darwin":
		return &MacOSInstaller{}
	default:
		return nil
	}
}

// Install 安装软件
func (w *WindowsInstaller) Install(packageID string) (*InstallResult, error) {
	// 检查是否已安装
	installed, err := w.IsInstalled(packageID)
	if err == nil && installed {
		return &InstallResult{
			Package: PackageInfo{ID: packageID},
			Status:  StatusSkipped,
			Output:  "Already installed",
		}, nil
	}

	cmd := exec.Command("winget", "install", "--id", packageID, "--silent", "--accept-source-agreements", "--accept-package-agreements")
	output, err := cmd.CombinedOutput()

	result := &InstallResult{
		Package: PackageInfo{ID: packageID},
		Output:  string(output),
	}

	if err != nil {
		result.Status = StatusFailed
		result.Error = err
		// 检查是否因为已安装而失败
		if strings.Contains(string(output), "already installed") {
			result.Status = StatusSkipped
			result.Error = nil
		}
	} else {
		result.Status = StatusSuccess
	}

	return result, nil
}

// Uninstall 卸载软件
func (w *WindowsInstaller) Uninstall(packageID string) (*InstallResult, error) {
	cmd := exec.Command("winget", "uninstall", "--id", packageID, "--silent")
	output, err := cmd.CombinedOutput()

	result := &InstallResult{
		Package: PackageInfo{ID: packageID},
		Output:  string(output),
	}

	if err != nil {
		result.Status = StatusFailed
		result.Error = err
		if strings.Contains(string(output), "not installed") {
			result.Status = StatusSkipped
			result.Error = nil
		}
	} else {
		result.Status = StatusSuccess
	}

	return result, nil
}

// Search 搜索软件
func (w *WindowsInstaller) Search(query string) ([]PackageInfo, error) {
	cmd := exec.Command("winget", "search", query)
	output, err := cmd.Output()
	if err != nil {
		return nil, err
	}

	return parseWingetSearch(string(output)), nil
}

// IsInstalled 检查是否已安装
func (w *WindowsInstaller) IsInstalled(packageID string) (bool, error) {
	cmd := exec.Command("winget", "list", "--id", packageID)
	output, err := cmd.Output()
	if err != nil {
		return false, nil
	}
	return strings.Contains(string(output), packageID), nil
}

// GetInstalled 获取已安装软件列表
func (w *WindowsInstaller) GetInstalled() ([]PackageInfo, error) {
	cmd := exec.Command("winget", "list")
	output, err := cmd.Output()
	if err != nil {
		return nil, err
	}

	return parseWingetList(string(output)), nil
}

// Update 更新包管理器
func (w *WindowsInstaller) Update() error {
	cmd := exec.Command("winget", "source", "update")
	return cmd.Run()
}

// parseWingetSearch 解析 winget 搜索结果
func parseWingetSearch(output string) []PackageInfo {
	var packages []PackageInfo
	lines := strings.Split(output, "\n")
	
	// 找到标题行和分隔行
	dataStart := -1
	for i, line := range lines {
		if strings.Contains(line, "Name") && strings.Contains(line, "Id") {
			dataStart = i + 2 // 跳过标题行和分隔行
			break
		}
	}
	
	if dataStart == -1 || dataStart >= len(lines) {
		return packages
	}
	
	// 解析数据行
	for i := dataStart; i < len(lines); i++ {
		line := strings.TrimSpace(lines[i])
		if line == "" {
			continue
		}
		
		// 解析行数据 - winget 输出格式: Name Id Version [Source/Tag]
		// 使用更智能的解析方式
		pkg := parseWingetLine(line)
		if pkg.ID != "" {
			packages = append(packages, pkg)
		}
	}
	
	return packages
}

// parseWingetLine 解析单行 winget 输出
func parseWingetLine(line string) PackageInfo {
	// winget 输出格式示例:
	// Git Git.Git 2.47.0 winget
	// 或
	// GitHub Desktop GitHub.GitHubDesktop 3.5.4 Tag: git winget
	
	fields := strings.Fields(line)
	if len(fields) < 2 {
		return PackageInfo{}
	}
	
	// 最后一列通常是 source (winget 或 msstore)
	// 倒数第二列通常是版本号
	// 第二列是 ID
	// 第一列是名称
	
	pkg := PackageInfo{}
	
	// 简单启发式解析
	if len(fields) >= 4 {
		// 假设最后一个是 source，倒数第二是版本
		pkg.Name = fields[0]
		pkg.ID = fields[1]
		pkg.Version = fields[len(fields)-2]
	} else if len(fields) == 3 {
		pkg.Name = fields[0]
		pkg.ID = fields[1]
		pkg.Version = fields[2]
	} else if len(fields) == 2 {
		pkg.Name = fields[0]
		pkg.ID = fields[1]
	}
	
	return pkg
}

// parseWingetList 解析 winget 列表
func parseWingetList(output string) []PackageInfo {
	var packages []PackageInfo
	scanner := bufio.NewScanner(strings.NewReader(output))
	
	// 跳过标题行
	for scanner.Scan() {
		line := scanner.Text()
		if strings.Contains(line, "Name") && strings.Contains(line, "Id") {
			break
		}
	}

	// 解析结果
	for scanner.Scan() {
		line := scanner.Text()
		if line == "" {
			continue
		}

		fields := strings.Fields(line)
		if len(fields) >= 2 {
			pkg := PackageInfo{
				Name:      fields[0],
				ID:        fields[1],
				Installed: true,
			}
			packages = append(packages, pkg)
		}
	}

	return packages
}

// MacOSInstaller macOS 安装器
type MacOSInstaller struct {
	BaseInstaller
}

// Install 安装软件
func (m *MacOSInstaller) Install(packageName string) (*InstallResult, error) {
	// 检查是否已安装
	installed, err := m.IsInstalled(packageName)
	if err == nil && installed {
		return &InstallResult{
			Package: PackageInfo{Name: packageName},
			Status:  StatusSkipped,
			Output:  "Already installed",
		}, nil
	}

	cmd := exec.Command("brew", "install", packageName)
	output, err := cmd.CombinedOutput()

	result := &InstallResult{
		Package: PackageInfo{Name: packageName},
		Output:  string(output),
	}

	if err != nil {
		result.Status = StatusFailed
		result.Error = err
		if strings.Contains(string(output), "already installed") {
			result.Status = StatusSkipped
			result.Error = nil
		}
	} else {
		result.Status = StatusSuccess
	}

	return result, nil
}

// Uninstall 卸载软件
func (m *MacOSInstaller) Uninstall(packageName string) (*InstallResult, error) {
	cmd := exec.Command("brew", "uninstall", packageName)
	output, err := cmd.CombinedOutput()

	result := &InstallResult{
		Package: PackageInfo{Name: packageName},
		Output:  string(output),
	}

	if err != nil {
		result.Status = StatusFailed
		result.Error = err
	} else {
		result.Status = StatusSuccess
	}

	return result, nil
}

// Search 搜索软件
func (m *MacOSInstaller) Search(query string) ([]PackageInfo, error) {
	cmd := exec.Command("brew", "search", "--desc", query)
	output, err := cmd.Output()
	if err != nil {
		return nil, err
	}

	return parseBrewSearch(string(output)), nil
}

// IsInstalled 检查是否已安装
func (m *MacOSInstaller) IsInstalled(packageName string) (bool, error) {
	cmd := exec.Command("brew", "list", "--versions", packageName)
	err := cmd.Run()
	return err == nil, nil
}

// GetInstalled 获取已安装软件列表
func (m *MacOSInstaller) GetInstalled() ([]PackageInfo, error) {
	cmd := exec.Command("brew", "list", "--versions")
	output, err := cmd.Output()
	if err != nil {
		return nil, err
	}

	return parseBrewList(string(output)), nil
}

// Update 更新包管理器
func (m *MacOSInstaller) Update() error {
	cmd := exec.Command("brew", "update")
	return cmd.Run()
}

// parseBrewSearch 解析 brew 搜索结果
func parseBrewSearch(output string) []PackageInfo {
	var packages []PackageInfo
	scanner := bufio.NewScanner(strings.NewReader(output))

	for scanner.Scan() {
		line := scanner.Text()
		if line == "" || strings.HasPrefix(line, "==>") {
			continue
		}

		// 解析格式: package-name (Description)
		if idx := strings.Index(line, "("); idx > 0 {
			name := strings.TrimSpace(line[:idx])
			desc := strings.Trim(line[idx:], "()")
			packages = append(packages, PackageInfo{
				Name:        name,
				Description: desc,
			})
		} else {
			packages = append(packages, PackageInfo{
				Name: strings.TrimSpace(line),
			})
		}
	}

	return packages
}

// parseBrewList 解析 brew 列表
func parseBrewList(output string) []PackageInfo {
	var packages []PackageInfo
	scanner := bufio.NewScanner(strings.NewReader(output))

	for scanner.Scan() {
		line := scanner.Text()
		fields := strings.Fields(line)
		if len(fields) >= 1 {
			pkg := PackageInfo{
				Name:      fields[0],
				Version:   "",
				Installed: true,
			}
			if len(fields) >= 2 {
				pkg.Version = fields[1]
			}
			packages = append(packages, pkg)
		}
	}

	return packages
}

// BatchInstall 批量安装
func BatchInstall(packages []string, parallel bool, callback func(result *InstallResult)) ([]*InstallResult, error) {
	installer := NewInstaller()
	if installer == nil {
		return nil, fmt.Errorf("unsupported platform: %s", runtime.GOOS)
	}

	var results []*InstallResult
	var mu sync.Mutex

	if parallel {
		var wg sync.WaitGroup
		semaphore := make(chan struct{}, 4) // 限制并发数

		for _, pkg := range packages {
			wg.Add(1)
			semaphore <- struct{}{}

			go func(packageID string) {
				defer wg.Done()
				defer func() { <-semaphore }()

				result, err := installer.Install(packageID)
				if err != nil && result == nil {
					result = &InstallResult{
						Package: PackageInfo{ID: packageID},
						Status:  StatusFailed,
						Error:   err,
					}
				}

				mu.Lock()
				results = append(results, result)
				mu.Unlock()

				if callback != nil {
					callback(result)
				}
			}(pkg)
		}

		wg.Wait()
	} else {
		for _, pkg := range packages {
			result, err := installer.Install(pkg)
			if err != nil && result == nil {
				result = &InstallResult{
					Package: PackageInfo{ID: pkg},
					Status:  StatusFailed,
					Error:   err,
				}
			}

			results = append(results, result)

			if callback != nil {
				callback(result)
			}
		}
	}

	return results, nil
}

// CheckPackageManager 检查包管理器是否可用
func CheckPackageManager() (string, bool) {
	switch runtime.GOOS {
	case "windows":
		cmd := exec.Command("winget", "--version")
		err := cmd.Run()
		if err == nil {
			return "winget", true
		}
		return "winget", false
	case "darwin":
		cmd := exec.Command("brew", "--version")
		err := cmd.Run()
		if err == nil {
			return "homebrew", true
		}
		return "homebrew", false
	default:
		return "", false
	}
}
