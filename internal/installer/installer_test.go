package installer

import (
	"runtime"
	"strings"
	"testing"
)

func TestValidatePackageID(t *testing.T) {
	tests := []struct {
		name      string
		packageID string
		wantErr   bool
	}{
		{"Valid Windows Package ID", "Git.Git", false},
		{"Valid Package ID with Publisher", "Microsoft.VisualStudioCode", false},
		{"Empty Package ID", "", true},
		{"Package ID with spaces", "Some Package", true},
		{"Valid Homebrew package", "git", false},
		{"Package ID too long", strings.Repeat("a", 129), true},
		{"Package ID with invalid chars", "test@package", true},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := validatePackageID(tt.packageID)
			if (err != nil) != tt.wantErr {
				t.Errorf("validatePackageID(%q) error = %v, wantErr %v", tt.packageID, err, tt.wantErr)
			}
		})
	}
}

func TestParseWingetLine(t *testing.T) {
	tests := []struct {
		name    string
		line    string
		wantID  string
		wantVer string
	}{
		{"Standard winget output", "Git Git.Git 2.47.0 winget", "Git.Git", "2.47.0"},
		{"Package with space in name", "GitHub Desktop GitHub.GitHubDesktop 3.5.4 winget", "GitHub.GitHubDesktop", "3.5.4"},
		{"Two field output", "Python Python.Python.3.12", "Python.Python.3.12", ""},
		{"Empty line", "", "", ""},
		{"Single field", "Git.Git", "Git.Git", ""},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := parseWingetLine(tt.line)
			if got.ID != tt.wantID {
				t.Errorf("parseWingetLine(%q).ID = %q, want %q", tt.line, got.ID, tt.wantID)
			}
			if got.Version != tt.wantVer {
				t.Errorf("parseWingetLine(%q).Version = %q, want %q", tt.line, got.Version, tt.wantVer)
			}
		})
	}
}

func TestCheckPackageManager(t *testing.T) {
	name, available := CheckPackageManager()

	switch runtime.GOOS {
	case "windows":
		if name != "winget" {
			t.Errorf("CheckPackageManager() name = %q, want %q", name, "winget")
		}
		t.Logf("Windows: winget available = %v", available)
	case "darwin":
		if name != "homebrew" {
			t.Errorf("CheckPackageManager() name = %q, want %q", name, "homebrew")
		}
		t.Logf("macOS: homebrew available = %v", available)
	case "linux":
		if name == "" {
			t.Errorf("CheckPackageManager() name is empty on linux")
		}
		t.Logf("Linux: %s available = %v", name, available)
	default:
		if name != "" {
			t.Errorf("CheckPackageManager() name = %q on unsupported OS, want empty", name)
		}
	}
}

func TestInstallStatus(t *testing.T) {
	statuses := []InstallStatus{
		StatusPending,
		StatusInstalling,
		StatusSuccess,
		StatusFailed,
		StatusSkipped,
		StatusDownloading,
	}

	expected := []string{
		"pending",
		"installing",
		"success",
		"failed",
		"skipped",
		"downloading",
	}

	for i, status := range statuses {
		if string(status) != expected[i] {
			t.Errorf("InstallStatus[%d] = %q, want %q", i, status, expected[i])
		}
	}
}

func TestNewInstaller(t *testing.T) {
	inst := NewInstaller()

	switch runtime.GOOS {
	case "windows":
		if inst == nil {
			t.Error("NewInstaller() returned nil on Windows")
		}
	case "darwin":
		if inst == nil {
			t.Error("NewInstaller() returned nil on macOS")
		}
	case "linux":
		if inst == nil {
			t.Error("NewInstaller() returned nil on Linux")
		}
	default:
		if inst != nil {
			t.Errorf("NewInstaller() returned non-nil on unsupported OS %s", runtime.GOOS)
		}
	}
}
