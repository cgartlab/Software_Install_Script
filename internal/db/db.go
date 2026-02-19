package db

import (
	"database/sql"
	"fmt"
	"os"
	"path/filepath"
	"sync"
	"time"

	_ "modernc.org/sqlite"
	"swiftinstall/internal/config"
)

// Package 表示软件包信息
type Package struct {
	ID        string    `json:"id"`
	Name      string    `json:"name"`
	Publisher string    `json:"publisher"`
	Version   string    `json:"version"`
	Source    string    `json:"source"`
	CreatedAt time.Time `json:"-"`
}

// Database 数据库结构
type Database struct {
	db   *sql.DB
	path string
	mu   sync.RWMutex
}

var (
	instance *Database
	once     sync.Once
)

// GetDB 获取数据库实例（单例）
func GetDB() (*Database, error) {
	var err error
	once.Do(func() {
		instance, err = NewDatabase()
	})
	return instance, err
}

// NewDatabase 创建新的数据库实例
func NewDatabase() (*Database, error) {
	dbPath := getDBPath()

	// 确保目录存在
	dir := filepath.Dir(dbPath)
	if err := os.MkdirAll(dir, 0755); err != nil {
		return nil, fmt.Errorf("failed to create database directory: %w", err)
	}

	db, err := sql.Open("sqlite", dbPath)
	if err != nil {
		return nil, fmt.Errorf("failed to open database: %w", err)
	}

	d := &Database{
		db:   db,
		path: dbPath,
	}

	if err := d.init(); err != nil {
		db.Close()
		return nil, err
	}

	return d, nil
}

// getDBPath 获取数据库文件路径
func getDBPath() string {
	// 使用配置目录存储数据库
	return filepath.Join(config.GetConfigDir(), "packages.db")
}

// init 初始化数据库表
func (d *Database) init() error {
	d.mu.Lock()
	defer d.mu.Unlock()

	schema := `
	CREATE TABLE IF NOT EXISTS packages (
		id TEXT PRIMARY KEY,
		name TEXT NOT NULL,
		publisher TEXT,
		version TEXT,
		source TEXT DEFAULT 'winget',
		created_at DATETIME DEFAULT CURRENT_TIMESTAMP
	);
	
	CREATE INDEX IF NOT EXISTS idx_name ON packages(name);
	CREATE INDEX IF NOT EXISTS idx_publisher ON packages(publisher);
	
	CREATE TABLE IF NOT EXISTS metadata (
		key TEXT PRIMARY KEY,
		value TEXT,
		updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
	);
	`

	_, err := d.db.Exec(schema)
	return err
}

// Close 关闭数据库
func (d *Database) Close() error {
	if d.db != nil {
		return d.db.Close()
	}
	return nil
}

// Search 搜索软件包
func (d *Database) Search(query string, limit int) ([]Package, error) {
	d.mu.RLock()
	defer d.mu.RUnlock()

	if limit <= 0 {
		limit = 50
	}

	// 支持模糊搜索
	searchQuery := "%" + query + "%"
	sqlStr := `
		SELECT id, name, publisher, version, source, created_at
		FROM packages
		WHERE name LIKE ? OR id LIKE ? OR publisher LIKE ?
		ORDER BY 
			CASE WHEN name LIKE ? THEN 0 ELSE 1 END,
			CASE WHEN id LIKE ? THEN 0 ELSE 1 END,
			name
		LIMIT ?
	`

	rows, err := d.db.Query(sqlStr, searchQuery, searchQuery, searchQuery, searchQuery, searchQuery, limit)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var packages []Package
	for rows.Next() {
		var pkg Package
		var createdAtStr string
		err := rows.Scan(&pkg.ID, &pkg.Name, &pkg.Publisher, &pkg.Version, &pkg.Source, &createdAtStr)
		if err != nil {
			return nil, err
		}
		if createdAtStr != "" {
			pkg.CreatedAt, _ = time.Parse(time.RFC3339, createdAtStr)
		}
		packages = append(packages, pkg)
	}

	return packages, rows.Err()
}

// GetPackage 获取单个软件包
func (d *Database) GetPackage(id string) (*Package, error) {
	d.mu.RLock()
	defer d.mu.RUnlock()

	var pkg Package
	var createdAtStr string
	err := d.db.QueryRow(
		"SELECT id, name, publisher, version, source, created_at FROM packages WHERE id = ?",
		id,
	).Scan(&pkg.ID, &pkg.Name, &pkg.Publisher, &pkg.Version, &pkg.Source, &createdAtStr)

	if err == sql.ErrNoRows {
		return nil, nil
	}
	if err != nil {
		return nil, err
	}

	if createdAtStr != "" {
		pkg.CreatedAt, _ = time.Parse(time.RFC3339, createdAtStr)
	}
	return &pkg, nil
}

// SavePackages 批量保存软件包
func (d *Database) SavePackages(packages []Package) error {
	d.mu.Lock()
	defer d.mu.Unlock()

	tx, err := d.db.Begin()
	if err != nil {
		return err
	}
	defer func() {
		if err := tx.Rollback(); err != nil && err != sql.ErrTxDone {
			// 忽略 Rollback 错误（可能是事务已提交）
		}
	}()

	stmt, err := tx.Prepare(`
		INSERT OR REPLACE INTO packages (id, name, publisher, version, source, created_at)
		VALUES (?, ?, ?, ?, ?, ?)
	`)
	if err != nil {
		return err
	}
	defer stmt.Close()

	for _, pkg := range packages {
		_, err := stmt.Exec(pkg.ID, pkg.Name, pkg.Publisher, pkg.Version, pkg.Source, time.Now())
		if err != nil {
			return err
		}
	}

	return tx.Commit()
}

// ClearPackages 清空软件包表
func (d *Database) ClearPackages() error {
	d.mu.Lock()
	defer d.mu.Unlock()

	_, err := d.db.Exec("DELETE FROM packages")
	return err
}

// GetStats 获取数据库统计信息
func (d *Database) GetStats() (map[string]interface{}, error) {
	d.mu.RLock()
	defer d.mu.RUnlock()

	stats := make(map[string]interface{})

	// 包总数
	var count int
	err := d.db.QueryRow("SELECT COUNT(*) FROM packages").Scan(&count)
	if err != nil {
		return nil, err
	}
	stats["total_packages"] = count

	// 最后更新时间
	var lastUpdate, lastUpdateTimeStr string
	err = d.db.QueryRow(
		"SELECT value, updated_at FROM metadata WHERE key = 'last_sync'",
	).Scan(&lastUpdate, &lastUpdateTimeStr)
	if err == nil {
		if lastUpdate != "" {
			stats["last_sync"] = lastUpdate
		}
		if lastUpdateTimeStr != "" {
			t, _ := time.Parse(time.RFC3339, lastUpdateTimeStr)
			stats["last_sync_time"] = t
		}
	}

	// 数据库文件大小
	if info, err := os.Stat(d.path); err == nil {
		stats["db_size_bytes"] = info.Size()
		stats["db_size_mb"] = float64(info.Size()) / 1024 / 1024
	}

	return stats, nil
}

// UpdateMetadata 更新元数据
func (d *Database) UpdateMetadata(key, value string) error {
	d.mu.Lock()
	defer d.mu.Unlock()

	_, err := d.db.Exec(`
		INSERT OR REPLACE INTO metadata (key, value, updated_at)
		VALUES (?, ?, ?)
	`, key, value, time.Now())
	return err
}

// GetMetadata 获取元数据
func (d *Database) GetMetadata(key string) (string, error) {
	d.mu.RLock()
	defer d.mu.RUnlock()

	var value sql.NullString
	err := d.db.QueryRow(
		"SELECT value FROM metadata WHERE key = ?", key,
	).Scan(&value)

	if err == sql.ErrNoRows {
		return "", nil
	}
	if err != nil {
		return "", err
	}

	if value.Valid {
		return value.String, nil
	}
	return "", nil
}

// GetPath 获取数据库文件路径
func (d *Database) GetPath() string {
	return d.path
}
