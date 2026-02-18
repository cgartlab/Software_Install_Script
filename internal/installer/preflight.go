package installer

import (
	"fmt"
	"os/exec"
	"runtime"
)

// EnvironmentReport 环境检查结果
type EnvironmentReport struct {
	Platform       string
	PackageManager string
	Ready          bool
	Details        []string
}

// CheckEnvironment 检查运行环境是否满足一次安装要求
func CheckEnvironment() EnvironmentReport {
	report := EnvironmentReport{Platform: runtime.GOOS, Ready: true}
	pm, ok := CheckPackageManager()
	report.PackageManager = pm
	if !ok {
		report.Ready = false
		report.Details = append(report.Details, "package manager is not available")
		return report
	}
	report.Details = append(report.Details, fmt.Sprintf("package manager detected: %s", pm))

	checks := requiredCommandsForPlatform(runtime.GOOS, pm)
	for _, name := range checks {
		if _, err := exec.LookPath(name); err != nil {
			report.Ready = false
			report.Details = append(report.Details, fmt.Sprintf("missing command: %s", name))
		}
	}
	if report.Ready {
		report.Details = append(report.Details, "environment preflight passed")
	}
	return report
}

func requiredCommandsForPlatform(goos, pm string) []string {
	switch goos {
	case "windows":
		return []string{"winget"}
	case "darwin":
		return []string{"brew"}
	case "linux":
		switch pm {
		case "apt":
			return []string{"apt", "apt-cache", "dpkg"}
		case "dnf":
			return []string{"dnf", "rpm"}
		case "pacman":
			return []string{"pacman"}
		case "zypper":
			return []string{"zypper", "rpm"}
		}
	}
	return nil
}
