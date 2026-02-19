package db

import (
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"strings"
	"time"
)

// Syncer 数据库同步器
type Syncer struct {
	db       *Database
	progress func(current, total int, message string)
}

// SyncProgress 同步进度回调
type SyncProgress func(current, total int, message string)

// NewSyncer 创建同步器
func NewSyncer(db *Database) *Syncer {
	return &Syncer{
		db: db,
	}
}

// SetProgressCallback 设置进度回调
func (s *Syncer) SetProgressCallback(cb SyncProgress) {
	s.progress = cb
}

// Sync 执行同步
func (s *Syncer) Sync() error {
	if s.db == nil {
		return fmt.Errorf("database not initialized")
	}

	s.report(0, 0, "Starting database sync...")

	// 清空现有数据
	s.report(0, 0, "Clearing existing data...")
	if err := s.db.ClearPackages(); err != nil {
		return fmt.Errorf("failed to clear packages: %w", err)
	}

	// 从 winget 导出所有包数据
	s.report(0, 0, "Exporting packages from winget...")
	packages, err := s.exportFromWinget()
	if err != nil {
		// 如果 export 不可用，尝试使用 fallback 方案
		s.report(0, 0, "Winget export failed, using fallback method...")
		packages, err = s.fallbackExport()
		if err != nil {
			return fmt.Errorf("failed to export from winget: %w", err)
		}
	}

	total := len(packages)
	if total == 0 {
		return fmt.Errorf("no packages exported from winget")
	}

	s.report(0, total, fmt.Sprintf("Importing %d packages...", total))

	// 批量导入数据库（每 1000 条提交一次）
	batchSize := 1000
	for i := 0; i < len(packages); i += batchSize {
		end := i + batchSize
		if end > len(packages) {
			end = len(packages)
		}

		batch := packages[i:end]
		if err := s.db.SavePackages(batch); err != nil {
			return fmt.Errorf("failed to save batch: %w", err)
		}

		s.report(end, total, fmt.Sprintf("Imported %d/%d packages...", end, total))
	}

	// 更新元数据
	if err := s.db.UpdateMetadata("last_sync", time.Now().Format(time.RFC3339)); err != nil {
		return fmt.Errorf("failed to update metadata: %w", err)
	}

	s.report(total, total, "Sync completed!")
	return nil
}

// exportFromWinget 从 winget 导出数据（JSON 格式）
func (s *Syncer) exportFromWinget() ([]Package, error) {
	// 使用 winget export 导出 JSON 格式到临时文件
	tmpFile := os.TempDir() + string(os.PathSeparator) + "winget-export.json"
	cmd := exec.Command("winget", "export", "-o", tmpFile)
	output, err := cmd.CombinedOutput()
	if err != nil {
		return nil, fmt.Errorf("winget export failed: %w, output: %s", err, string(output))
	}

	// 读取文件
	data, err := os.ReadFile(tmpFile)
	if err != nil {
		return nil, err
	}

	// 清理临时文件
	os.Remove(tmpFile)

	return parseWingetExport(data)
}

// fallbackExport 降级方案：使用常见字母搜索获取常用包
func (s *Syncer) fallbackExport() ([]Package, error) {
	// 常见搜索关键词，用于获取常用软件
	commonSearches := []string{
		"a", "b", "c", "d", "e", "f", "g", "h", "i", "j",
		"k", "l", "m", "n", "o", "p", "q", "r", "s", "t",
		"u", "v", "w", "x", "y", "z",
	}

	var allPackages []Package
	seen := make(map[string]bool)

	for i, query := range commonSearches {
		s.report(i*100, len(commonSearches)*100, fmt.Sprintf("Searching: %s...", query))

		cmd := exec.Command("winget", "search", query)
		output, err := cmd.Output()
		if err != nil {
			continue
		}

		packages := parseWingetSearchOutput(string(output))
		for _, pkg := range packages {
			if !seen[pkg.ID] {
				seen[pkg.ID] = true
				allPackages = append(allPackages, pkg)
			}
		}
	}

	return allPackages, nil
}

// WingetExportRoot winget export 的 JSON 根结构
type WingetExportRoot struct {
	Sources []WingetExportSource `json:"Sources"`
}

// WingetExportSource winget export 的源结构
type WingetExportSource struct {
	Packages []WingetExportPackage `json:"Packages"`
}

// WingetExportPackage winget export 的 JSON 结构
type WingetExportPackage struct {
	PackageIdentifier string `json:"PackageIdentifier"`
	PackageName       string `json:"PackageName"`
	PackageVersion    string `json:"PackageVersion,omitempty"`
	Publisher         string `json:"Publisher,omitempty"`
}

// parseWingetExport 解析 winget export 输出（JSON 格式）
func parseWingetExport(data []byte) ([]Package, error) {
	var packages []Package

	// 首先尝试解析为完整 JSON 结构
	var root WingetExportRoot
	if err := json.Unmarshal(data, &root); err == nil {
		// 完整 JSON 格式
		for _, source := range root.Sources {
			for _, pkg := range source.Packages {
				if pkg.PackageIdentifier != "" {
					packages = append(packages, Package{
						ID:        pkg.PackageIdentifier,
						Name:      pkg.PackageName,
						Publisher: pkg.Publisher,
						Version:   pkg.PackageVersion,
						Source:    "winget",
					})
				}
			}
		}
		return packages, nil
	}

	// 如果不是完整 JSON，尝试 JSON Lines 格式（每行一个 JSON 对象）
	lines := strings.Split(string(data), "\n")
	for _, line := range lines {
		line = strings.TrimSpace(line)
		if line == "" {
			continue
		}

		var pkg WingetExportPackage
		if err := json.Unmarshal([]byte(line), &pkg); err != nil {
			continue
		}

		if pkg.PackageIdentifier != "" {
			packages = append(packages, Package{
				ID:        pkg.PackageIdentifier,
				Name:      pkg.PackageName,
				Publisher: pkg.Publisher,
				Version:   pkg.PackageVersion,
				Source:    "winget",
			})
		}
	}

	return packages, nil
}

// parseWingetSearchOutput 解析 winget search 输出
func parseWingetSearchOutput(output string) []Package {
	var packages []Package
	lines := strings.Split(output, "\n")

	// 找到数据开始位置
	dataStart := -1
	for i, line := range lines {
		if strings.Contains(line, "Name") && strings.Contains(line, "Id") {
			if i+2 < len(lines) {
				dataStart = i + 2
				break
			}
		}
	}

	if dataStart == -1 {
		return packages
	}

	// 解析数据行
	for i := dataStart; i < len(lines); i++ {
		line := strings.TrimSpace(lines[i])
		if line == "" || strings.HasPrefix(line, "<") || strings.HasPrefix(line, "-") {
			continue
		}

		pkg := parseWingetLine(line)
		if pkg.ID != "" {
			packages = append(packages, pkg)
		}
	}

	return packages
}

// parseWingetLine 解析 winget 输出行
func parseWingetLine(line string) Package {
	pkg := Package{Source: "winget"}

	// winget 输出格式：Name    Id    Version    Source
	// 使用多个空格分割
	fields := strings.Fields(line)
	if len(fields) < 2 {
		return pkg
	}

	// 简单解析：第一个是 Name，倒数第二个是 Id，最后一个是 Version
	pkg.Name = fields[0]
	if len(fields) >= 3 {
		pkg.ID = fields[len(fields)-2]
		pkg.Version = fields[len(fields)-1]
	} else if len(fields) == 2 {
		pkg.ID = fields[1]
	}

	return pkg
}

// report 报告进度
func (s *Syncer) report(current, total int, message string) {
	if s.progress != nil {
		s.progress(current, total, message)
	}
}
