package installer

import (
	"fmt"
	"os/exec"
	"strings"
)

// LinuxInstaller Linux 安装器
type LinuxInstaller struct {
	BaseInstaller
	manager string
}

// NewLinuxInstaller 创建 Linux 安装器
func NewLinuxInstaller() Installer {
	pm, ok := detectLinuxPackageManager()
	if !ok {
		return nil
	}
	return &LinuxInstaller{manager: pm}
}

func detectLinuxPackageManager() (string, bool) {
	candidates := []string{"apt", "dnf", "pacman", "zypper"}
	for _, cmd := range candidates {
		if _, err := exec.LookPath(cmd); err == nil {
			return cmd, true
		}
	}
	return "", false
}

func (l *LinuxInstaller) Install(packageID string) (*InstallResult, error) {
	if packageID == "" {
		return &InstallResult{Package: PackageInfo{ID: packageID}, Status: StatusFailed, Error: fmt.Errorf("empty package ID")}, fmt.Errorf("empty package ID")
	}

	installed, _ := l.IsInstalled(packageID)
	if installed {
		return &InstallResult{Package: PackageInfo{ID: packageID}, Status: StatusSkipped, Output: "Already installed"}, nil
	}

	cmd := l.commandForInstall(packageID)
	output, err := cmd.CombinedOutput()
	res := &InstallResult{Package: PackageInfo{ID: packageID}, Output: string(output)}
	if err != nil {
		res.Status = StatusFailed
		res.Error = err
		if strings.Contains(strings.ToLower(string(output)), "already") {
			res.Status = StatusSkipped
			res.Error = nil
		}
		return res, err
	}
	res.Status = StatusSuccess
	return res, nil
}

func (l *LinuxInstaller) Uninstall(packageID string) (*InstallResult, error) {
	cmd := l.commandForUninstall(packageID)
	output, err := cmd.CombinedOutput()
	res := &InstallResult{Package: PackageInfo{ID: packageID}, Output: string(output)}
	if err != nil {
		res.Status = StatusFailed
		res.Error = err
		if strings.Contains(strings.ToLower(string(output)), "not installed") || strings.Contains(strings.ToLower(string(output)), "not found") {
			res.Status = StatusSkipped
			res.Error = nil
		}
		return res, err
	}
	res.Status = StatusSuccess
	return res, nil
}

func (l *LinuxInstaller) Search(query string) ([]PackageInfo, error) {
	cmd := l.commandForSearch(query)
	output, err := cmd.Output()
	if err != nil {
		return nil, err
	}
	return parseLinuxSearch(l.manager, string(output)), nil
}

func (l *LinuxInstaller) IsInstalled(packageID string) (bool, error) {
	cmd := l.commandForIsInstalled(packageID)
	err := cmd.Run()
	return err == nil, nil
}

func (l *LinuxInstaller) GetInstalled() ([]PackageInfo, error) {
	cmd := l.commandForListInstalled()
	output, err := cmd.Output()
	if err != nil {
		return nil, err
	}
	return parseLinuxInstalled(l.manager, string(output)), nil
}

func (l *LinuxInstaller) Update() error {
	cmd := l.commandForUpdate()
	return cmd.Run()
}

func (l *LinuxInstaller) commandForInstall(pkg string) *exec.Cmd {
	switch l.manager {
	case "apt":
		return exec.Command("sudo", "apt", "install", "-y", pkg)
	case "dnf":
		return exec.Command("sudo", "dnf", "install", "-y", pkg)
	case "pacman":
		return exec.Command("sudo", "pacman", "-S", "--noconfirm", pkg)
	case "zypper":
		return exec.Command("sudo", "zypper", "--non-interactive", "install", pkg)
	default:
		return exec.Command("false")
	}
}

func (l *LinuxInstaller) commandForUninstall(pkg string) *exec.Cmd {
	switch l.manager {
	case "apt":
		return exec.Command("sudo", "apt", "remove", "-y", pkg)
	case "dnf":
		return exec.Command("sudo", "dnf", "remove", "-y", pkg)
	case "pacman":
		return exec.Command("sudo", "pacman", "-R", "--noconfirm", pkg)
	case "zypper":
		return exec.Command("sudo", "zypper", "--non-interactive", "remove", pkg)
	default:
		return exec.Command("false")
	}
}

func (l *LinuxInstaller) commandForSearch(query string) *exec.Cmd {
	switch l.manager {
	case "apt":
		return exec.Command("apt-cache", "search", query)
	case "dnf":
		return exec.Command("dnf", "search", query)
	case "pacman":
		return exec.Command("pacman", "-Ss", query)
	case "zypper":
		return exec.Command("zypper", "search", query)
	default:
		return exec.Command("false")
	}
}

func (l *LinuxInstaller) commandForIsInstalled(pkg string) *exec.Cmd {
	switch l.manager {
	case "apt":
		return exec.Command("dpkg", "-s", pkg)
	case "dnf":
		return exec.Command("rpm", "-q", pkg)
	case "pacman":
		return exec.Command("pacman", "-Q", pkg)
	case "zypper":
		return exec.Command("rpm", "-q", pkg)
	default:
		return exec.Command("false")
	}
}

func (l *LinuxInstaller) commandForListInstalled() *exec.Cmd {
	switch l.manager {
	case "apt":
		return exec.Command("apt", "list", "--installed")
	case "dnf":
		return exec.Command("dnf", "list", "installed")
	case "pacman":
		return exec.Command("pacman", "-Q")
	case "zypper":
		return exec.Command("zypper", "search", "--installed-only")
	default:
		return exec.Command("false")
	}
}

func (l *LinuxInstaller) commandForUpdate() *exec.Cmd {
	switch l.manager {
	case "apt":
		return exec.Command("sudo", "apt", "update")
	case "dnf":
		return exec.Command("sudo", "dnf", "check-update")
	case "pacman":
		return exec.Command("sudo", "pacman", "-Sy")
	case "zypper":
		return exec.Command("sudo", "zypper", "refresh")
	default:
		return exec.Command("false")
	}
}

func parseLinuxSearch(manager, output string) []PackageInfo {
	var packages []PackageInfo
	lines := strings.Split(output, "\n")
	for _, line := range lines {
		line = strings.TrimSpace(line)
		if line == "" {
			continue
		}
		switch manager {
		case "apt":
			parts := strings.SplitN(line, " - ", 2)
			name := strings.TrimSpace(parts[0])
			desc := ""
			if len(parts) == 2 {
				desc = strings.TrimSpace(parts[1])
			}
			if name != "" {
				packages = append(packages, PackageInfo{Name: name, ID: name, Description: desc})
			}
		case "pacman":
			if strings.Contains(line, "/") {
				fields := strings.Fields(line)
				if len(fields) >= 1 {
					name := fields[0]
					if idx := strings.Index(name, "/"); idx >= 0 {
						name = name[idx+1:]
					}
					packages = append(packages, PackageInfo{Name: name, ID: name})
				}
			}
		default:
			fields := strings.Fields(line)
			if len(fields) > 0 {
				name := fields[0]
				packages = append(packages, PackageInfo{Name: name, ID: name})
			}
		}
		if len(packages) >= 100 {
			break
		}
	}
	return packages
}

func parseLinuxInstalled(_ string, output string) []PackageInfo {
	var packages []PackageInfo
	lines := strings.Split(output, "\n")
	for _, line := range lines {
		fields := strings.Fields(strings.TrimSpace(line))
		if len(fields) == 0 {
			continue
		}
		name := fields[0]
		if idx := strings.Index(name, "/"); idx >= 0 {
			name = name[:idx]
		}
		if name == "Listing..." || name == "Installed" {
			continue
		}
		packages = append(packages, PackageInfo{Name: name, ID: name, Installed: true})
		if len(packages) >= 2000 {
			break
		}
	}
	return packages
}
