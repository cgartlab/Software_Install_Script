package db

import (
	"time"
)

// AutoSyncConfig 自动同步配置
type AutoSyncConfig struct {
	Enabled     bool          `json:"enabled" yaml:"enabled"`
	IntervalDays int          `json:"interval_days" yaml:"interval_days"`
	LastSync    time.Time     `json:"last_sync,omitempty" yaml:"last_sync,omitempty"`
}

// ShouldAutoSync 检查是否应该自动同步
func ShouldAutoSync() bool {
	database, err := GetDB()
	if err != nil {
		return false
	}
	defer database.Close()

	// 获取最后同步时间
	lastSyncStr, err := database.GetMetadata("last_sync")
	if err != nil || lastSyncStr == "" {
		return true // 从未同步过，需要同步
	}

	lastSync, err := time.Parse(time.RFC3339, lastSyncStr)
	if err != nil {
		return true
	}

	// 检查是否超过 7 天
	return time.Since(lastSync) > 7*24*time.Hour
}

// GetLastSyncTime 获取最后同步时间
func GetLastSyncTime() (time.Time, error) {
	database, err := GetDB()
	if err != nil {
		return time.Time{}, err
	}
	defer database.Close()

	lastSyncStr, err := database.GetMetadata("last_sync")
	if err != nil || lastSyncStr == "" {
		return time.Time{}, nil
	}

	return time.Parse(time.RFC3339, lastSyncStr)
}

// GetDatabaseInfo 获取数据库信息
func GetDatabaseInfo() (map[string]interface{}, error) {
	database, err := GetDB()
	if err != nil {
		return nil, err
	}
	defer database.Close()

	return database.GetStats()
}

// QuickSync 快速同步（仅在需要时）
func QuickSync() error {
	if !ShouldAutoSync() {
		return nil
	}

	database, err := GetDB()
	if err != nil {
		return err
	}
	defer database.Close()

	syncer := NewSyncer(database)
	return syncer.Sync()
}
