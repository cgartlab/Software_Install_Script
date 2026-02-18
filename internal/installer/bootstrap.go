package installer

import (
	"fmt"
	"runtime"
)

type CommandRunner interface {
	Run(name string, args ...string) error
}

type SetupOptions struct {
	AutoInstallDeps bool
	DryRun          bool
}

type SetupResult struct {
	Platform          string
	PackageManager    string
	EnvironmentReady  bool
	DependencyActions []string
	Verification      []string
}

type RealCommandRunner struct{}

func (r RealCommandRunner) Run(name string, args ...string) error {
	cmd := buildCommand(name, args...)
	return cmd.Run()
}

func RunOneCommandSetup(opts SetupOptions, runner CommandRunner) (*SetupResult, error) {
	if runner == nil {
		runner = RealCommandRunner{}
	}

	report := CheckEnvironment()
	result := &SetupResult{
		Platform:         runtime.GOOS,
		PackageManager:   report.PackageManager,
		EnvironmentReady: report.Ready,
	}

	if report.Ready {
		result.Verification = append(result.Verification, "environment preflight passed")
		return result, nil
	}

	if !opts.AutoInstallDeps {
		return result, fmt.Errorf("environment is not ready: %v", report.Details)
	}

	actions, err := installationPlan(runtime.GOOS, report.PackageManager)
	if err != nil {
		return result, err
	}
	result.DependencyActions = append(result.DependencyActions, actions...)

	for _, action := range actions {
		result.Verification = append(result.Verification, "planned: "+action)
	}

	if opts.DryRun {
		return result, nil
	}

	for _, cmd := range actionableCommands(runtime.GOOS, report.PackageManager) {
		if err := runner.Run(cmd[0], cmd[1:]...); err != nil {
			return result, fmt.Errorf("failed to run %s: %w", cmd[0], err)
		}
	}

	post := CheckEnvironment()
	result.EnvironmentReady = post.Ready
	result.PackageManager = post.PackageManager
	result.Verification = append(result.Verification, post.Details...)
	if !post.Ready {
		return result, fmt.Errorf("environment still not ready after setup")
	}
	return result, nil
}

func installationPlan(goos, pm string) ([]string, error) {
	switch goos {
	case "windows":
		return []string{"ensure winget sources are up to date"}, nil
	case "darwin":
		return []string{"install Homebrew if missing", "refresh brew metadata"}, nil
	case "linux":
		switch pm {
		case "apt":
			return []string{"apt update"}, nil
		case "dnf":
			return []string{"dnf check-update"}, nil
		case "pacman":
			return []string{"pacman -Sy"}, nil
		case "zypper":
			return []string{"zypper refresh"}, nil
		default:
			return nil, fmt.Errorf("unsupported linux package manager")
		}
	default:
		return nil, fmt.Errorf("unsupported platform: %s", goos)
	}
}

func actionableCommands(goos, pm string) [][]string {
	switch goos {
	case "windows":
		return [][]string{{"winget", "source", "update"}}
	case "darwin":
		return [][]string{{"brew", "update"}}
	case "linux":
		switch pm {
		case "apt":
			return [][]string{{"sudo", "apt", "update"}}
		case "dnf":
			return [][]string{{"sudo", "dnf", "check-update"}}
		case "pacman":
			return [][]string{{"sudo", "pacman", "-Sy"}}
		case "zypper":
			return [][]string{{"sudo", "zypper", "refresh"}}
		}
	}
	return nil
}
