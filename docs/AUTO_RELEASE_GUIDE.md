# 自动化版本发布系统使用指南

## 快速开始

### 1. 安装

```bash
# 克隆仓库
git clone https://github.com/your-org/swiftinstall.git
cd swiftinstall

# 构建发布工具
go build -o release-tool ./cmd/release
```

### 2. 配置

创建配置文件 `release-config.json`:

```json
{
  "versioning": {
    "strategy": "semantic",
    "prereleaseEnabled": false
  },
  "autoRelease": {
    "enabled": true,
    "triggerBranches": ["main"],
    "requireApproval": true,
    "approvalThreshold": 0.8,
    "maxAutoBumpLevel": "minor"
  },
  "build": {
    "platforms": [
      {"goos": "windows", "goarch": "amd64", "suffix": ".exe"},
      {"goos": "linux", "goarch": "amd64", "suffix": ""},
      {"goos": "darwin", "goarch": "amd64", "suffix": ""}
    ]
  },
  "test": {
    "enabled": true,
    "minCoverage": 0.8
  },
  "deploy": {
    "enabled": true,
    "rollbackStrategy": "automatic"
  }
}
```

### 3. 运行

```bash
# 干运行模式（预览）
./release-tool -project myapp -dry-run

# 执行实际发布
./release-tool -project myapp

# 指定配置文件
./release-tool -project myapp -config /path/to/config.json

# JSON输出格式
./release-tool -project myapp -output json
```

## 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-config` | 配置文件路径 | `release-config.json` |
| `-project` | 项目名称 | 必填 |
| `-tag` | 当前版本标签 | 自动检测 |
| `-dry-run` | 干运行模式 | `false` |
| `-skip-tests` | 跳过测试 | `false` |
| `-skip-deploy` | 跳过部署 | `false` |
| `-verbose` | 详细输出 | `false` |
| `-output` | 输出格式 (text/json) | `text` |

## 提交消息规范

系统使用语义化提交消息来判断版本类型：

### 功能新增 (Minor版本)

```
feat: 添加用户认证功能
feat(auth): 实现OAuth2登录
feat(api): 新增用户管理API
```

### Bug修复 (Patch版本)

```
fix: 修复登录验证错误
fix(auth): 修复token过期问题
fix(api): 修复参数验证逻辑
```

### 破坏性变更 (Major版本)

```
feat!: 重构API接口结构
feat(api)!: 移除废弃的端点

BREAKING CHANGE: API v1已废弃，请迁移到v2
```

### 其他类型

```
docs: 更新API文档
style: 格式化代码
refactor: 重构用户服务
perf: 优化数据库查询
test: 添加单元测试
chore: 更新依赖版本
```

## 版本判定规则

### 自动判定

| 提交类型 | 版本变更 | 示例 |
|---------|---------|------|
| `feat!` 或 `BREAKING CHANGE` | Major | 1.0.0 → 2.0.0 |
| `feat` | Minor | 1.0.0 → 1.1.0 |
| `fix` | Patch | 1.0.0 → 1.0.1 |
| 其他 | Patch | 1.0.0 → 1.0.1 |

### 手动覆盖

在提交消息中添加版本标记：

```
feat: 新功能 [version:major]
fix: 修复bug [version:minor]
chore: 更新配置 [version:patch]
```

## GitHub Actions集成

### 自动发布工作流

在 `.github/workflows/auto-release.yml` 中配置：

```yaml
name: Auto Release

on:
  push:
    branches: [main]

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - uses: actions/setup-go@v5
        with:
          go-version: '1.21'
      
      - name: Build release tool
        run: go build -o release-tool ./cmd/release
      
      - name: Run release
        run: ./release-tool -project ${{ github.event.repository.name }}
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### 手动触发

```yaml
on:
  workflow_dispatch:
    inputs:
      dry_run:
        description: 'Dry run mode'
        required: false
        default: 'false'
```

## 配置详解

### 版本控制配置

```json
{
  "versioning": {
    "strategy": "semantic",
    "prereleaseEnabled": true,
    "prereleaseIdentifier": "rc",
    "branchPatterns": {
      "main": "release",
      "develop": "prerelease",
      "feature/*": "none"
    }
  }
}
```

### 自动发布配置

```json
{
  "autoRelease": {
    "enabled": true,
    "triggerBranches": ["main"],
    "requireApproval": true,
    "approvalThreshold": 0.8,
    "maxAutoBumpLevel": "minor",
    "quietPeriodHours": 2,
    "minCommitsThreshold": 1
  }
}
```

### 构建配置

```json
{
  "build": {
    "platforms": [
      {"goos": "windows", "goarch": "amd64", "suffix": ".exe"},
      {"goos": "linux", "goarch": "amd64", "suffix": ""},
      {"goos": "darwin", "goarch": "arm64", "suffix": ""}
    ],
    "artifactNaming": "{{.Name}}-{{.Version}}-{{.GOOS}}-{{.GOARCH}}{{.Suffix}}",
    "buildTimeout": 30,
    "cacheEnabled": true
  }
}
```

### 测试配置

```json
{
  "test": {
    "enabled": true,
    "minCoverage": 0.8,
    "timeout": 10,
    "testSuites": ["./..."],
    "parallel": true,
    "requiredTests": ["unit"]
  }
}
```

### 部署配置

```json
{
  "deploy": {
    "enabled": true,
    "rollbackStrategy": "automatic",
    "healthCheckPath": "/health",
    "healthCheckTimeout": 30,
    "environments": [
      {
        "name": "staging",
        "type": "testing",
        "autoDeploy": true,
        "deployStrategy": "rolling"
      },
      {
        "name": "production",
        "type": "production",
        "autoDeploy": false,
        "deployStrategy": "blue-green"
      }
    ]
  }
}
```

## 日志与监控

### 日志配置

```json
{
  "logging": {
    "level": "info",
    "outputPath": "./logs/release.log",
    "maxSize": 100,
    "maxBackups": 3,
    "maxAge": 7,
    "compress": true
  }
}
```

### 日志级别

- `debug`: 详细调试信息
- `info`: 常规操作信息
- `warn`: 警告信息
- `error`: 错误信息

### 日志示例

```
[2024-01-18 10:30:00] [INFO] [ANALYSIS] [Release:release-123] Starting change analysis
[2024-01-18 10:30:01] [INFO] [VERSION_DECISION] [Release:release-123] Version decision: 1.0.0 → 1.1.0
[2024-01-18 10:30:05] [INFO] [BUILD] [Release:release-123] Build completed for platform windows/amd64
[2024-01-18 10:30:10] [INFO] [TEST] [Release:release-123] Test suite passed with 85% coverage
[2024-01-18 10:30:15] [INFO] [DEPLOY] [Release:release-123] Deployment successful to staging
```

## 异常处理

### 常见错误

| 错误代码 | 说明 | 处理方式 |
|---------|------|---------|
| VERSION_PARSE_ERROR | 版本解析失败 | 检查版本格式 |
| BUILD_FAILED | 构建失败 | 查看构建日志 |
| TEST_FAILED | 测试失败 | 检查测试用例 |
| DEPLOY_FAILED | 部署失败 | 自动回滚 |
| HEALTH_CHECK_FAILED | 健康检查失败 | 自动回滚 |

### 回滚机制

当部署失败或健康检查失败时，系统会自动执行回滚：

1. 识别当前部署的版本
2. 获取上一个稳定版本
3. 执行回滚部署
4. 验证回滚后的健康状态
5. 通知相关人员

## 最佳实践

### 1. 提交消息规范

- 使用语义化提交消息
- 清晰描述变更内容
- 标注破坏性变更

### 2. 分支策略

- `main`: 生产环境，自动发布
- `develop`: 开发环境，预发布
- `feature/*`: 功能分支，不触发发布
- `hotfix/*`: 紧急修复，需要审批

### 3. 版本管理

- 主版本更新需要审批
- 次版本更新可自动发布
- 修订版本更新可自动发布

### 4. 测试要求

- 保持测试覆盖率 ≥ 80%
- 关键测试必须通过
- 性能测试达标

### 5. 部署策略

- 生产环境使用蓝绿部署
- 测试环境使用滚动部署
- 主版本更新使用金丝雀发布

## 故障排查

### 构建失败

```bash
# 检查Go版本
go version

# 检查依赖
go mod tidy

# 本地构建测试
go build -v ./...
```

### 测试失败

```bash
# 运行详细测试
go test -v ./...

# 检查覆盖率
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out
```

### 部署失败

1. 检查部署日志
2. 验证环境配置
3. 检查健康检查端点
4. 查看回滚状态

## 高级用法

### 自定义版本规则

```go
engine.AddCustomRule(release.VersionRule{
    Name: "security_update",
    Condition: func(r release.ChangeAnalysisResult) bool {
        return r.ContainsSecurityFix
    },
    VersionBump: release.ChangeTypePatch,
    Priority: 90,
})
```

### 自定义部署策略

```go
deployManager.RegisterStrategy("custom", func(ctx context.Context, env EnvironmentConfig) error {
    // 自定义部署逻辑
    return nil
})
```

### Webhook通知

```json
{
  "notifications": {
    "enabled": true,
    "webhooks": [
      "https://hooks.example.com/release"
    ]
  }
}
```

## API参考

### Go API

```go
// 创建发布管道
pipeline, err := release.NewReleasePipeline("config.json", "myapp")

// 执行发布
result, err := pipeline.Execute(ctx, commits, fileChanges, "v1.0.0")

// 获取结果
fmt.Printf("New version: %s\n", result.NewVersion)
fmt.Printf("Success: %v\n", result.Success)
```

### 配置管理

```go
configManager := release.NewConfigManager("config.json")
configManager.Load()

// 修改配置
config := configManager.GetConfig()
config.AutoRelease.RequireApproval = false
configManager.Save()
```

---

**文档版本**: v1.0  
**最后更新**: 2024年
