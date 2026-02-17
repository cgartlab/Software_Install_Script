package config

import (
	"fmt"
	"log"
	"os"
	"path/filepath"
	"runtime"
	"sync"

	"github.com/spf13/viper"
	"gopkg.in/yaml.v3"
)

var (
	instance *Config
	once     sync.Once
)

// Software 表示一个软件包
type Software struct {
	Name     string `json:"name" yaml:"name"`
	ID       string `json:"id" yaml:"id"`
	Package  string `json:"package" yaml:"package"`
	Category string `json:"category" yaml:"category"`
	Version  string `json:"version,omitempty" yaml:"version,omitempty"`
	Source   string `json:"source,omitempty" yaml:"source,omitempty"`
}

// Config 配置结构
type Config struct {
	viper       *viper.Viper
	configFile  string
	software    []Software
	mu          sync.RWMutex
}

// Init 初始化配置
func Init() {
	once.Do(func() {
		instance = &Config{
			viper: viper.New(),
		}
		instance.load()
	})
}

// Get 获取配置实例
func Get() *Config {
	if instance == nil {
		Init()
	}
	return instance
}

// SetConfigFile 设置配置文件路径
func SetConfigFile(file string) {
	if instance != nil {
		instance.configFile = file
	}
}

// GetString 获取字符串配置
func GetString(key string) string {
	if instance == nil {
		return ""
	}
	return instance.viper.GetString(key)
}

// Set 设置配置值
func Set(key string, value interface{}) {
	if instance != nil {
		instance.viper.Set(key, value)
	}
}

// Save 保存配置
func Save() error {
	if instance == nil {
		return fmt.Errorf("config not initialized")
	}
	return instance.save()
}

// load 加载配置
func (c *Config) load() {
	// 设置默认配置
	c.setDefaults()

	// 确定配置文件路径
	if c.configFile == "" {
		c.configFile = c.getDefaultConfigPath()
	}

	// 确保配置目录存在
	configDir := filepath.Dir(c.configFile)
	if err := os.MkdirAll(configDir, 0755); err != nil {
		log.Printf("Warning: failed to create config directory: %v", err)
	}

	// 检查配置文件是否存在
	if _, err := os.Stat(c.configFile); os.IsNotExist(err) {
		// 创建默认配置
		c.createDefaultConfig()
	} else {
		// 加载现有配置
		c.loadFromFile()
	}
}

// setDefaults 设置默认值
func (c *Config) setDefaults() {
	c.viper.SetDefault("language", "zh")
	c.viper.SetDefault("theme", "dark")
	c.viper.SetDefault("parallel_install", true)
	c.viper.SetDefault("max_workers", 4)
	c.viper.SetDefault("auto_update_check", true)
	c.viper.SetDefault("confirm_before_install", true)
}

// getDefaultConfigPath 获取默认配置文件路径
func (c *Config) getDefaultConfigPath() string {
	homeDir, _ := os.UserHomeDir()
	return filepath.Join(homeDir, ".si", "config.yaml")
}

// createDefaultConfig 创建默认配置
func (c *Config) createDefaultConfig() {
	c.software = c.getDefaultSoftware()
	if err := c.save(); err != nil {
		log.Printf("Warning: failed to save default config: %v", err)
	}
}

// getDefaultSoftware 获取默认软件列表
func (c *Config) getDefaultSoftware() []Software {
	if runtime.GOOS == "windows" {
		return []Software{
			{Name: "Git", ID: "Git.Git", Category: "Development"},
			{Name: "Visual Studio Code", ID: "Microsoft.VisualStudioCode", Category: "Development"},
			{Name: "7-Zip", ID: "7zip.7zip", Category: "Utilities"},
			{Name: "Google Chrome", ID: "Google.Chrome", Category: "Browsers"},
		}
	} else if runtime.GOOS == "darwin" {
		return []Software{
			{Name: "Git", Package: "git", Category: "Development"},
			{Name: "Visual Studio Code", Package: "visual-studio-code", Category: "Development"},
			{Name: "Google Chrome", Package: "google-chrome", Category: "Browsers"},
		}
	}
	return []Software{}
}

// loadFromFile 从文件加载配置
func (c *Config) loadFromFile() {
	data, err := os.ReadFile(c.configFile)
	if err != nil {
		c.software = c.getDefaultSoftware()
		return
	}

	var config struct {
		Software []Software `yaml:"software"`
	}

	if err := yaml.Unmarshal(data, &config); err != nil {
		c.software = c.getDefaultSoftware()
		return
	}

	c.software = config.Software
}

// save 保存配置到文件
func (c *Config) save() error {
	c.mu.Lock()
	defer c.mu.Unlock()

	config := struct {
		Software []Software `yaml:"software"`
	}{
		Software: c.software,
	}

	data, err := yaml.Marshal(config)
	if err != nil {
		return err
	}

	return os.WriteFile(c.configFile, data, 0644)
}

// GetSoftwareList 获取软件列表
func (c *Config) GetSoftwareList() []Software {
	c.mu.RLock()
	defer c.mu.RUnlock()

	result := make([]Software, len(c.software))
	copy(result, c.software)
	return result
}

// AddSoftware 添加软件
func (c *Config) AddSoftware(s Software) {
	c.mu.Lock()
	defer c.mu.Unlock()

	c.software = append(c.software, s)
}

// RemoveSoftware 移除软件
func (c *Config) RemoveSoftware(index int) bool {
	c.mu.Lock()
	defer c.mu.Unlock()

	if index < 0 || index >= len(c.software) {
		return false
	}

	c.software = append(c.software[:index], c.software[index+1:]...)
	return true
}

// UpdateSoftware 更新软件
func (c *Config) UpdateSoftware(index int, s Software) bool {
	c.mu.Lock()
	defer c.mu.Unlock()

	if index < 0 || index >= len(c.software) {
		return false
	}

	c.software[index] = s
	return true
}

// ClearSoftware 清空软件列表
func (c *Config) ClearSoftware() {
	c.mu.Lock()
	defer c.mu.Unlock()

	c.software = []Software{}
}

// ImportFromFile 从文件导入配置
func (c *Config) ImportFromFile(path string) error {
	data, err := os.ReadFile(path)
	if err != nil {
		return err
	}

	var imported struct {
		Software []Software `yaml:"software" json:"software"`
	}

	if err := yaml.Unmarshal(data, &imported); err != nil {
		// 尝试 JSON 格式
		if err := yaml.Unmarshal(data, &imported); err != nil {
			return err
		}
	}

	c.mu.Lock()
	c.software = imported.Software
	c.mu.Unlock()

	return c.save()
}

// ExportToFile 导出配置到文件
func (c *Config) ExportToFile(path string) error {
	c.mu.RLock()
	defer c.mu.RUnlock()

	config := struct {
		Software []Software `yaml:"software" json:"software"`
	}{
		Software: c.software,
	}

	data, err := yaml.Marshal(config)
	if err != nil {
		return err
	}

	return os.WriteFile(path, data, 0644)
}
