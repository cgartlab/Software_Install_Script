package i18n

import (
	"sync"
	"testing"
)

func TestTranslation(t *testing.T) {
	tests := []struct {
		key    string
		wantZh string
		wantEn string
	}{
		{"app_name", "SwiftInstall", "SwiftInstall"},
		{"app_short_desc", "快速、简单、可靠的跨平台软件安装工具", "Fast, simple, reliable cross-platform software installer"},
		{"menu_install", "安装软件", "Install Software"},
		{"common_success", "成功", "Success"},
		{"common_failed", "失败", "Failed"},
	}

	for _, tt := range tests {
		t.Run("Chinese_"+tt.key, func(t *testing.T) {
			SetLanguage("zh")
			got := T(tt.key)
			if got != tt.wantZh {
				t.Errorf("T(%q) with zh = %q, want %q", tt.key, got, tt.wantZh)
			}
		})

		t.Run("English_"+tt.key, func(t *testing.T) {
			SetLanguage("en")
			got := T(tt.key)
			if got != tt.wantEn {
				t.Errorf("T(%q) with en = %q, want %q", tt.key, got, tt.wantEn)
			}
		})
	}
}

func TestLanguageSwitch(t *testing.T) {
	SetLanguage("zh")
	if GetLanguage() != "zh" {
		t.Errorf("Initial language = %q, want %q", GetLanguage(), "zh")
	}

	SetLanguage("en")
	if GetLanguage() != "en" {
		t.Errorf("After SetLanguage(en): language = %q, want %q", GetLanguage(), "en")
	}

	got := T("menu_install")
	want := "Install Software"
	if got != want {
		t.Errorf("T(menu_install) after switch = %q, want %q", got, want)
	}

	SetLanguage("zh")
	if GetLanguage() != "zh" {
		t.Errorf("After SetLanguage(zh): language = %q, want %q", GetLanguage(), "zh")
	}

	got = T("menu_install")
	want = "安装软件"
	if got != want {
		t.Errorf("T(menu_install) after switch back = %q, want %q", got, want)
	}
}

func TestInvalidLanguage(t *testing.T) {
	SetLanguage("zh")
	currentLang := GetLanguage()

	SetLanguage("invalid")

	if GetLanguage() != currentLang {
		t.Errorf("SetLanguage(invalid) changed language from %q to %q", currentLang, GetLanguage())
	}
}

func TestCompleteness(t *testing.T) {
	zhTranslations := translations["zh"]
	enTranslations := translations["en"]

	zhKeys := make(map[string]bool)
	enKeys := make(map[string]bool)

	for key := range zhTranslations {
		zhKeys[key] = true
	}

	for key := range enTranslations {
		enKeys[key] = true
	}

	missingInZh := []string{}
	for key := range enKeys {
		if !zhKeys[key] {
			missingInZh = append(missingInZh, key)
		}
	}

	missingInEn := []string{}
	for key := range zhKeys {
		if !enKeys[key] {
			missingInEn = append(missingInEn, key)
		}
	}

	if len(missingInZh) > 0 {
		t.Logf("Warning: Keys missing in Chinese translation: %v", missingInZh)
	}

	if len(missingInEn) > 0 {
		t.Logf("Warning: Keys missing in English translation: %v", missingInEn)
	}

	t.Logf("Total translations: zh=%d, en=%d", len(zhTranslations), len(enTranslations))
}

func TestFallback(t *testing.T) {
	SetLanguage("zh")
	got := T("nonexistent_key")
	if got != "nonexistent_key" {
		t.Errorf("T(nonexistent_key) = %q, want %q", got, "nonexistent_key")
	}

	SetLanguage("en")
	got = T("nonexistent_key")
	if got != "nonexistent_key" {
		t.Errorf("T(nonexistent_key) in en = %q, want %q", got, "nonexistent_key")
	}
}

func TestConcurrentTranslation(t *testing.T) {
	var wg sync.WaitGroup

	for i := 0; i < 100; i++ {
		wg.Add(2)

		go func() {
			defer wg.Done()
			SetLanguage("zh")
			_ = T("menu_install")
		}()

		go func() {
			defer wg.Done()
			SetLanguage("en")
			_ = T("menu_install")
		}()
	}

	wg.Wait()
}

func TestAllKeysExist(t *testing.T) {
	requiredKeys := []string{
		"app_name",
		"app_short_desc",
		"menu_title",
		"menu_install",
		"menu_uninstall",
		"menu_search",
		"menu_config",
		"menu_exit",
		"common_success",
		"common_failed",
		"common_cancel",
		"common_confirm",
		"install_title",
		"install_progress",
		"config_title",
		"status_title",
	}

	for _, key := range requiredKeys {
		t.Run("zh_"+key, func(t *testing.T) {
			SetLanguage("zh")
			got := T(key)
			if got == key {
				t.Errorf("Missing Chinese translation for key: %s", key)
			}
		})

		t.Run("en_"+key, func(t *testing.T) {
			SetLanguage("en")
			got := T(key)
			if got == key {
				t.Errorf("Missing English translation for key: %s", key)
			}
		})
	}
}
