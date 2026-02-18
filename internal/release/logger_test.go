package release

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestReleaseLoggerLevelFiltering(t *testing.T) {
	tmp := t.TempDir()
	cfg := LoggingConfig{Level: "warn", OutputPath: filepath.Join(tmp, "release.log"), MaxSize: 10, MaxBackups: 2, MaxAge: 7, Compress: false}
	l, err := NewReleaseLogger(cfg, "r1")
	if err != nil {
		t.Fatalf("NewReleaseLogger: %v", err)
	}
	defer l.Close()

	l.Debug("debug", nil)
	l.Info("info", nil)
	l.Warn("warn", map[string]string{"k": "v"})
	entries := l.GetEntries()
	if len(entries) != 1 {
		t.Fatalf("expected 1 entry, got %d", len(entries))
	}
	if entries[0].Level != LogLevelWarn {
		t.Fatalf("expected warn level, got %v", entries[0].Level)
	}
}

func TestReleaseLoggerRotationAndArchive(t *testing.T) {
	tmp := t.TempDir()
	logPath := filepath.Join(tmp, "release.log")
	cfg := LoggingConfig{Level: "debug", OutputPath: logPath, MaxSize: 1, MaxBackups: 2, MaxAge: 7, Compress: true}
	l, err := NewReleaseLogger(cfg, "r2")
	if err != nil {
		t.Fatalf("NewReleaseLogger: %v", err)
	}
	defer l.Close()

	for i := 0; i < 5000; i++ {
		l.Info(strings.Repeat("x", 400), map[string]int{"i": i})
	}

	files, err := os.ReadDir(tmp)
	if err != nil {
		t.Fatalf("ReadDir: %v", err)
	}

	hasArchive := false
	for _, f := range files {
		if strings.HasPrefix(f.Name(), "release.log.") && strings.HasSuffix(f.Name(), ".gz") {
			hasArchive = true
		}
	}
	if !hasArchive {
		t.Fatalf("expected at least one compressed archive, files=%v", fileNames(files))
	}
}

func fileNames(entries []os.DirEntry) []string {
	names := make([]string, 0, len(entries))
	for _, e := range entries {
		names = append(names, e.Name())
	}
	return names
}
