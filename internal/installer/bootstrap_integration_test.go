package installer

import "testing"

type fakeRunner struct {
	calls int
}

func (f *fakeRunner) Run(name string, args ...string) error {
	f.calls++
	return nil
}

func TestRunOneCommandSetupDryRun(t *testing.T) {
	r := &fakeRunner{}
	res, err := RunOneCommandSetup(SetupOptions{AutoInstallDeps: true, DryRun: true}, r)
	if err != nil {
		// environment may already be ready; dry-run should still not fail
		t.Fatalf("RunOneCommandSetup dry-run error: %v", err)
	}
	if res == nil {
		t.Fatal("expected non-nil result")
	}
	if r.calls != 0 {
		t.Fatalf("dry-run should not execute commands, calls=%d", r.calls)
	}
}
