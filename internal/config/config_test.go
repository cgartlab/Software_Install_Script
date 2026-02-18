package config

import (
	"os"
	"path/filepath"
	"runtime"
	"sync"
	"testing"

	"gopkg.in/yaml.v3"
)

func resetConfig() {
	instance = nil
	once = sync.Once{}
}

func TestConfigInit(t *testing.T) {
	resetConfig()

	Init()

	if instance == nil {
		t.Fatal("ConfigInit() did not initialize instance")
	}

	cfg := Get()
	if cfg == nil {
		t.Fatal("Get() returned nil after Init()")
	}
}

func TestConfigSingleton(t *testing.T) {
	resetConfig()

	Init()
	cfg1 := Get()

	Init()
	cfg2 := Get()

	if cfg1 != cfg2 {
		t.Error("Get() returned different instances")
	}
}

func TestConfigSave(t *testing.T) {
	tmpDir, err := os.MkdirTemp("", "config_test")
	if err != nil {
		t.Fatalf("Failed to create temp dir: %v", err)
	}
	defer os.RemoveAll(tmpDir)

	resetConfig()
	Init()

	configPath := filepath.Join(tmpDir, "config.yaml")
	SetConfigFile(configPath)

	cfg := Get()
	cfg.AddSoftware(Software{
		Name:     "TestApp",
		ID:       "Test.Publisher.TestApp",
		Category: "Test",
	})

	err = Save()
	if err != nil {
		t.Fatalf("Save() failed: %v", err)
	}

	if _, err := os.Stat(configPath); os.IsNotExist(err) {
		t.Error("Save() did not create config file")
	}
}

func TestConfigPersistence(t *testing.T) {
	tmpDir, err := os.MkdirTemp("", "config_persistence_test")
	if err != nil {
		t.Fatalf("Failed to create temp dir: %v", err)
	}
	defer os.RemoveAll(tmpDir)

	configPath := filepath.Join(tmpDir, "config.yaml")

	resetConfig()
	Init()
	SetConfigFile(configPath)

	cfg := Get()
	cfg.AddSoftware(Software{
		Name:     "PersistentApp",
		ID:       "Test.PersistentApp",
		Category: "Test",
	})

	if err := Save(); err != nil {
		t.Fatalf("First save failed: %v", err)
	}

	data, err := os.ReadFile(configPath)
	if err != nil {
		t.Fatalf("Failed to read config file: %v", err)
	}

	var loaded struct {
		Software []Software `yaml:"software"`
	}
	if err := yaml.Unmarshal(data, &loaded); err != nil {
		t.Fatalf("Failed to unmarshal config: %v", err)
	}

	found := false
	for _, s := range loaded.Software {
		if s.ID == "Test.PersistentApp" {
			found = true
			break
		}
	}

	if !found {
		t.Error("ConfigPersistence: saved software not found in config file")
	}
}

func TestGetSoftwareList(t *testing.T) {
	resetConfig()
	Init()

	cfg := Get()
	cfg.ClearSoftware()

	cfg.AddSoftware(Software{Name: "App1", ID: "App1.ID"})
	cfg.AddSoftware(Software{Name: "App2", ID: "App2.ID"})

	list := cfg.GetSoftwareList()

	if len(list) != 2 {
		t.Errorf("GetSoftwareList() returned %d items, want 2", len(list))
	}
}

func TestAddRemoveSoftware(t *testing.T) {
	resetConfig()
	Init()

	cfg := Get()
	cfg.ClearSoftware()

	cfg.AddSoftware(Software{Name: "TestApp", ID: "Test.ID"})
	list := cfg.GetSoftwareList()
	if len(list) != 1 {
		t.Errorf("After AddSoftware: len = %d, want 1", len(list))
	}

	removed := cfg.RemoveSoftware(0)
	if !removed {
		t.Error("RemoveSoftware(0) returned false")
	}

	list = cfg.GetSoftwareList()
	if len(list) != 0 {
		t.Errorf("After RemoveSoftware: len = %d, want 0", len(list))
	}

	removed = cfg.RemoveSoftware(100)
	if removed {
		t.Error("RemoveSoftware(100) should return false for invalid index")
	}
}

func TestUpdateSoftware(t *testing.T) {
	resetConfig()
	Init()

	cfg := Get()
	cfg.ClearSoftware()
	cfg.AddSoftware(Software{Name: "OldName", ID: "Old.ID"})

	updated := cfg.UpdateSoftware(0, Software{Name: "NewName", ID: "New.ID"})
	if !updated {
		t.Error("UpdateSoftware(0) returned false")
	}

	list := cfg.GetSoftwareList()
	if list[0].Name != "NewName" {
		t.Errorf("UpdateSoftware: Name = %q, want %q", list[0].Name, "NewName")
	}

	updated = cfg.UpdateSoftware(100, Software{})
	if updated {
		t.Error("UpdateSoftware(100) should return false for invalid index")
	}
}

func TestDefaultSoftware(t *testing.T) {
	resetConfig()
	Init()

	cfg := Get()
	list := cfg.GetSoftwareList()

	if len(list) == 0 {
		t.Log("Warning: default software list is empty")
	}

	if runtime.GOOS == "windows" {
		hasGit := false
		for _, s := range list {
			if s.ID == "Git.Git" {
				hasGit = true
				break
			}
		}
		if !hasGit {
			t.Log("Note: Git not in default Windows software list")
		}
	}
}

func TestConcurrentAccess(t *testing.T) {
	resetConfig()
	Init()

	cfg := Get()
	cfg.ClearSoftware()

	done := make(chan bool)
	for i := 0; i < 10; i++ {
		go func(idx int) {
			cfg.AddSoftware(Software{
				Name: "ConcurrentApp",
				ID:   "Concurrent.ID",
			})
			done <- true
		}(i)
	}

	for i := 0; i < 10; i++ {
		<-done
	}

	for i := 0; i < 10; i++ {
		go func() {
			_ = cfg.GetSoftwareList()
			done <- true
		}()
	}

	for i := 0; i < 10; i++ {
		<-done
	}
}
