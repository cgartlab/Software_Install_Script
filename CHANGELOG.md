# Changelog

All notable changes to SwiftInstall will be documented in this file.

## [Unreleased]

### Fixed
- 修复 `InstallModel` 并发安全问题，添加 `sync.Mutex` 保护共享数据
- 合并 `cmd/root.go` 中的重复 `init()` 函数
- 修复 `config.save()` 方法，保存所有配置项（language, theme, parallel_install 等）
- 修复 `getOSName()` 和 `getArch()` 使用 `runtime.GOOS` 和 `runtime.GOARCH` 动态获取系统信息
- 修复 Makefile 中 ldflags 包路径错误
- 添加 `validatePackageID()` 函数验证包ID格式，防止潜在命令注入
- 改进 `parseWingetLine()` 函数，使用正则表达式更好地解析含空格的软件名
- 修复 `IsInstalled()` 方法错误返回值，正确返回错误信息
- 修复 `Install()` 方法中 `IsInstalled` 错误被忽略的问题
- 修复 `BatchInstall()` 并发安装时缺少 panic 恢复机制
- 修复 `install.go` 中非并行模式实际仍是并发执行的问题
- 修复 `ShowSpinner()` goroutine 缺少 panic 恢复机制
- 修复 `installPackage()` 中 `Install` 错误被忽略的问题
- 添加数组越界检查防止 table 更新崩溃

### Added
- 添加 `internal/installer/installer_test.go` 测试文件
  - TestValidatePackageID: 包ID验证测试
  - TestParseWingetLine: winget输出解析测试
  - TestCheckPackageManager: 包管理器检测测试
- 添加 `internal/config/config_test.go` 测试文件
  - TestConfigInit: 配置初始化测试
  - TestConfigSave: 配置保存测试
  - TestConfigPersistence: 配置持久化测试
  - TestConcurrentAccess: 并发访问测试
- 添加 `internal/i18n/i18n_test.go` 测试文件
  - TestTranslation: 翻译功能测试
  - TestLanguageSwitch: 语言切换测试
  - TestCompleteness: 翻译完整性测试
- 添加包级正则表达式缓存，优化性能

### Changed
- 优化并发安装时的线程安全性
- 改进 winget 输出解析的健壮性
- 统一错误处理模式，添加日志记录
- 改进并发安装的 semaphore 获取方式，避免主 goroutine 阻塞

## [0.1.2] - 2024-01-01

### Added
- 初始版本发布
- 支持 Windows (Winget) 和 macOS (Homebrew)
- 交互式 TUI 界面
- 多语言支持（中文/英文）
- 批量安装功能
- 配置文件管理
