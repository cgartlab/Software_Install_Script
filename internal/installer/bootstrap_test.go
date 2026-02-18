package installer

import "testing"

func TestInstallationPlan(t *testing.T) {
	tests := []struct {
		goos    string
		pm      string
		wantErr bool
	}{
		{"windows", "winget", false},
		{"darwin", "brew", false},
		{"linux", "apt", false},
		{"linux", "", true},
		{"plan9", "", true},
	}

	for _, tt := range tests {
		_, err := installationPlan(tt.goos, tt.pm)
		if (err != nil) != tt.wantErr {
			t.Fatalf("installationPlan(%s,%s) err=%v wantErr=%v", tt.goos, tt.pm, err, tt.wantErr)
		}
	}
}

func TestActionableCommands(t *testing.T) {
	cmds := actionableCommands("linux", "apt")
	if len(cmds) == 0 || cmds[0][0] != "sudo" {
		t.Fatalf("unexpected commands: %v", cmds)
	}
}
