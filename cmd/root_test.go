package cmd

import (
	"bytes"
	"testing"
)

func TestRootCommandHasCoreSubcommandsAndFlags(t *testing.T) {
	cmd := rootCmd
	expectedSubcommands := []string{"install", "uninstall", "search", "list", "config", "wizard", "batch", "export", "update", "clean", "status", "about", "help", "uninstall-all", "edit-list", "setup"}

	for _, name := range expectedSubcommands {
		if c, _, err := cmd.Find([]string{name}); err != nil || c == nil || c.Name() != name {
			t.Fatalf("missing subcommand %q", name)
		}
	}

	if cmd.PersistentFlags().Lookup("config") == nil {
		t.Fatal("missing --config persistent flag")
	}
	if cmd.PersistentFlags().Lookup("lang") == nil {
		t.Fatal("missing --lang persistent flag")
	}

	if setupCmd.Flags().Lookup("auto-install-deps") == nil {
		t.Fatal("missing --auto-install-deps")
	}
	if setupCmd.Flags().Lookup("dry-run") == nil {
		t.Fatal("missing --dry-run")
	}
}

func TestHelpCommandOutput(t *testing.T) {
	buf := &bytes.Buffer{}
	rootCmd.SetOut(buf)
	rootCmd.SetErr(buf)
	rootCmd.SetArgs([]string{"help"})
	if err := Execute(); err != nil {
		t.Fatalf("execute help: %v", err)
	}
}
