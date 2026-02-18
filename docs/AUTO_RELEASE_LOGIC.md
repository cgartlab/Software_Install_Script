# 自动发布逻辑判断机制技术文档

## 1. 概述

本文档详细描述了自动化版本发布系统的逻辑判断机制，包括触发条件判断标准、分支处理逻辑、异常处理规则、状态转换机制以及关键决策点判定依据。

## 2. 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    自动发布系统架构                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ Git事件监听   │───>│ 变更分析器   │───>│ 版本判定引擎 │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                    │          │
│         v                   v                    v          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ 配置管理器   │    │ 日志系统     │    │ 错误处理器   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                    │          │
│         v                   v                    v          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ 构建管理器   │    │ 测试管理器   │    │ 部署管理器   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 3. 自动发布触发条件判断标准

### 3.1 基础触发条件

```go
type TriggerCondition struct {
    Branch           string
    MinCommits       int
    QuietPeriodHours int
    RequiredChecks   []string
    ExcludedPaths    []string
}

func ShouldTriggerRelease(condition TriggerCondition, event GitEvent) bool {
    if !contains(condition.Branch, event.Branch) {
        return false
    }
    
    if event.CommitCount < condition.MinCommits {
        return false
    }
    
    if !hasPassedAllChecks(condition.RequiredChecks) {
        return false
    }
    
    if time.Since(event.LastCommit) < time.Duration(condition.QuietPeriodHours)*time.Hour {
        return false
    }
    
    return true
}
```

### 3.2 触发条件矩阵

| 条件类型 | 检查项 | 通过标准 | 失败处理 |
|---------|--------|---------|---------|
| 分支检查 | 当前分支是否在触发分支列表中 | 精确匹配或通配符匹配 | 跳过发布 |
| 提交数量 | 自上次发布以来的提交数 | ≥ minCommitsThreshold | 等待更多提交 |
| CI状态 | 所有CI检查是否通过 | 100%通过 | 阻止发布 |
| 静默期 | 距离最后一次提交的时间 | ≥ quietPeriodHours | 延迟发布 |
| 代码质量 | 代码扫描结果 | 无高危问题 | 阻止发布 |

### 3.3 触发条件伪代码

```
FUNCTION evaluate_trigger_conditions(event, config):
    # 1. 检查分支
    IF event.branch NOT IN config.trigger_branches:
        RETURN {triggered: false, reason: "branch_not_configured"}
    
    # 2. 检查提交数量
    commits_since_release = get_commits_since_last_release()
    IF commits_since_release.length < config.min_commits_threshold:
        RETURN {triggered: false, reason: "insufficient_commits"}
    
    # 3. 检查CI状态
    FOR check IN config.required_checks:
        IF check.status != "success":
            RETURN {triggered: false, reason: "ci_check_failed", check: check.name}
    
    # 4. 检查静默期
    time_since_last_commit = now() - event.last_commit_time
    IF time_since_last_commit < config.quiet_period:
        RETURN {triggered: false, reason: "quiet_period_active"}
    
    # 5. 检查代码质量
    quality_result = run_code_quality_check()
    IF quality_result.has_critical_issues:
        RETURN {triggered: false, reason: "quality_gate_failed"}
    
    RETURN {triggered: true, reason: "all_conditions_met"}
END FUNCTION
```

## 4. 分支处理逻辑

### 4.1 分支策略映射

```go
type BranchStrategy struct {
    Pattern          string
    VersionStrategy  string
    AutoRelease      bool
    RequireApproval  bool
    TargetEnvironments []string
}

var DefaultBranchStrategies = []BranchStrategy{
    {
        Pattern:          "main",
        VersionStrategy:  "release",
        AutoRelease:      true,
        RequireApproval:  false,
        TargetEnvironments: []string{"staging", "production"},
    },
    {
        Pattern:          "develop",
        VersionStrategy:  "prerelease",
        AutoRelease:      true,
        RequireApproval:  false,
        TargetEnvironments: []string{"staging"},
    },
    {
        Pattern:          "feature/*",
        VersionStrategy:  "none",
        AutoRelease:      false,
        RequireApproval:  true,
        TargetEnvironments: []string{},
    },
    {
        Pattern:          "hotfix/*",
        VersionStrategy:  "patch",
        AutoRelease:      true,
        RequireApproval:  true,
        TargetEnvironments: []string{"staging", "production"},
    },
}
```

### 4.2 分支处理流程图

```
                    ┌─────────────────┐
                    │  接收Git事件    │
                    └────────┬────────┘
                             │
                             v
                    ┌─────────────────┐
                    │  识别分支类型   │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              v              v              v
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │   main   │  │ develop  │  │ feature  │
        └────┬─────┘  └────┬─────┘  └────┬─────┘
             │              │              │
             v              v              v
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │ 正式发布 │  │ 预发布   │  │ 不发布   │
        └────┬─────┘  └────┬─────┘  └──────────┘
             │              │
             v              v
        ┌──────────┐  ┌──────────┐
        │ 自动部署 │  │ 自动部署 │
        │ staging  │  │ staging  │
        │ + prod   │  └──────────┘
        └──────────┘
```

### 4.3 分支处理伪代码

```
FUNCTION process_branch(branch_name, config):
    # 匹配分支策略
    matched_strategy = NULL
    FOR strategy IN config.branch_strategies:
        IF match_pattern(strategy.pattern, branch_name):
            matched_strategy = strategy
            BREAK
    
    IF matched_strategy == NULL:
        RETURN {action: "skip", reason: "no_matching_strategy"}
    
    # 根据策略决定版本类型
    version_type = determine_version_type(
        matched_strategy.version_strategy,
        get_commits_since_last_release()
    )
    
    # 检查是否需要审批
    IF matched_strategy.require_approval:
        approval_result = request_approval(branch_name, version_type)
        IF NOT approval_result.approved:
            RETURN {action: "skip", reason: "approval_rejected"}
    
    # 执行发布
    IF matched_strategy.auto_release:
        RETURN {
            action: "release",
            version_type: version_type,
            environments: matched_strategy.target_environments
        }
    ELSE:
        RETURN {action: "manual_trigger_required"}
END FUNCTION
```

## 5. 异常情况识别与处理规则

### 5.1 异常类型定义

```go
type ExceptionType int

const (
    ExceptionBuildFailed ExceptionType = iota
    ExceptionTestFailed
    ExceptionDeployFailed
    ExceptionHealthCheckFailed
    ExceptionRollbackFailed
    ExceptionConfigInvalid
    ExceptionGitOperationFailed
    ExceptionNetworkError
    ExceptionTimeout
)

type Exception struct {
    Type        ExceptionType
    Code        string
    Message     string
    Recoverable bool
    Context     map[string]interface{}
    Timestamp   time.Time
}
```

### 5.2 异常处理策略矩阵

| 异常类型 | 恢复策略 | 重试次数 | 回滚操作 | 通知级别 |
|---------|---------|---------|---------|---------|
| 构建失败 | 中止发布 | 0 | 无 | ERROR |
| 测试失败 | 中止发布 | 0 | 无 | ERROR |
| 部署失败 | 自动回滚 | 1 | 执行回滚 | CRITICAL |
| 健康检查失败 | 自动回滚 | 3 | 执行回滚 | CRITICAL |
| 回滚失败 | 人工介入 | 0 | 无 | FATAL |
| 配置无效 | 中止发布 | 0 | 无 | ERROR |
| Git操作失败 | 重试 | 3 | 无 | WARN |
| 网络错误 | 重试 | 5 | 无 | WARN |
| 超时 | 重试 | 2 | 视情况而定 | ERROR |

### 5.3 异常处理流程

```
FUNCTION handle_exception(exception, context):
    # 记录异常
    log_exception(exception, context)
    
    # 判断是否可恢复
    IF NOT exception.recoverable:
        # 不可恢复异常处理
        IF exception.type IN [ExceptionDeployFailed, ExceptionHealthCheckFailed]:
            rollback_result = execute_rollback(context)
            IF NOT rollback_result.success:
                trigger_manual_intervention(exception)
        
        notify_stakeholders(exception, "CRITICAL")
        RETURN {status: "failed", action: "abort"}
    
    # 可恢复异常处理
    retry_count = 0
    max_retries = get_max_retries(exception.type)
    
    WHILE retry_count < max_retries:
        retry_count++
        
        # 等待退避时间
        wait_time = calculate_backoff(retry_count)
        sleep(wait_time)
        
        # 重试操作
        retry_result = retry_operation(exception, context)
        
        IF retry_result.success:
            log_recovery(exception, retry_count)
            RETURN {status: "recovered", retries: retry_count}
    
    # 重试耗尽
    notify_stakeholders(exception, "ERROR")
    RETURN {status: "failed", action: "max_retries_exceeded"}
END FUNCTION
```

### 5.4 异常识别规则

```go
func IdentifyException(err error, stage ReleaseStage) *Exception {
    switch {
    case isBuildError(err):
        return &Exception{
            Type:        ExceptionBuildFailed,
            Code:        "BUILD_001",
            Message:     "Build process failed",
            Recoverable: false,
        }
    
    case isTestError(err):
        return &Exception{
            Type:        ExceptionTestFailed,
            Code:        "TEST_001",
            Message:     "Test suite failed",
            Recoverable: false,
        }
    
    case isDeployError(err):
        return &Exception{
            Type:        ExceptionDeployFailed,
            Code:        "DEPLOY_001",
            Message:     "Deployment failed",
            Recoverable: true,
        }
    
    case isHealthCheckError(err):
        return &Exception{
            Type:        ExceptionHealthCheckFailed,
            Code:        "HEALTH_001",
            Message:     "Health check failed",
            Recoverable: true,
        }
    
    case isTimeoutError(err):
        return &Exception{
            Type:        ExceptionTimeout,
            Code:        "TIMEOUT_001",
            Message:     "Operation timed out",
            Recoverable: true,
        }
    
    default:
        return &Exception{
            Type:        ExceptionGitOperationFailed,
            Code:        "UNKNOWN_001",
            Message:     err.Error(),
            Recoverable: false,
        }
    }
}
```

## 6. 发布流程状态转换机制

### 6.1 状态定义

```go
type ReleaseState int

const (
    StateIdle ReleaseState = iota          // 空闲状态
    StateAnalyzing                         // 分析变更中
    StateVersionDeciding                   // 版本决策中
    StateBuilding                          // 构建中
    StateTesting                           // 测试中
    StateDeploying                         // 部署中
    StateCompleted                         // 已完成
    StateFailed                            // 已失败
    StateRolledBack                        // 已回滚
)
```

### 6.2 状态转换图

```
                    ┌─────────┐
                    │  Idle   │
                    └────┬────┘
                         │ trigger
                         v
                  ┌─────────────┐
                  │  Analyzing  │
                  └──────┬──────┘
                         │ analysis_complete
                         v
               ┌──────────────────┐
               │ VersionDeciding  │
               └────────┬─────────┘
                        │ version_decided
                        v
                  ┌──────────┐
                  │ Building │◄──────┐
                  └────┬─────┘       │
                       │ build_complete    retry
                       v                  │
                  ┌──────────┐            │
                  │ Testing  ├────────────┘
                  └────┬─────┘
                       │ test_complete
                       v
                 ┌───────────┐
                 │ Deploying │◄──────┐
                 └─────┬─────┘       │
                       │ deploy_complete    rollback
                       v                       │
        ┌──────────────────────────────┐      │
        │         Completed            │      │
        └──────────────────────────────┘      │
                                                │
        ┌──────────────────────────────┐      │
        │           Failed             ├──────┘
        └──────────────┬───────────────┘
                       │ rollback_initiated
                       v
        ┌──────────────────────────────┐
        │         RolledBack           │
        └──────────────────────────────┘
```

### 6.3 状态转换规则

```go
type StateTransition struct {
    From      ReleaseState
    To        ReleaseState
    Event     string
    Condition func(*ReleaseContext) bool
    Action    func(*ReleaseContext) error
}

var ValidTransitions = []StateTransition{
    {
        From:  StateIdle,
        To:    StateAnalyzing,
        Event: "trigger",
        Condition: func(ctx *ReleaseContext) bool {
            return ctx.HasNewCommits()
        },
    },
    {
        From:  StateAnalyzing,
        To:    StateVersionDeciding,
        Event: "analysis_complete",
        Condition: func(ctx *ReleaseContext) bool {
            return ctx.AnalysisResult != nil
        },
    },
    {
        From:  StateVersionDeciding,
        To:    StateBuilding,
        Event: "version_decided",
        Condition: func(ctx *ReleaseContext) bool {
            return ctx.VersionDecision.ChangeType != ChangeTypeNone
        },
    },
    {
        From:  StateBuilding,
        To:    StateTesting,
        Event: "build_complete",
        Condition: func(ctx *ReleaseContext) bool {
            return ctx.BuildResults.AllSuccessful()
        },
    },
    {
        From:  StateBuilding,
        To:    StateFailed,
        Event: "build_failed",
        Condition: func(ctx *ReleaseContext) bool {
            return ctx.BuildResults.HasFailures()
        },
    },
    {
        From:  StateTesting,
        To:    StateDeploying,
        Event: "test_complete",
        Condition: func(ctx *ReleaseContext) bool {
            return ctx.TestResults.AllPassed()
        },
    },
    {
        From:  StateTesting,
        To:    StateFailed,
        Event: "test_failed",
        Condition: func(ctx *ReleaseContext) bool {
            return ctx.TestResults.HasFailures()
        },
    },
    {
        From:  StateDeploying,
        To:    StateCompleted,
        Event: "deploy_complete",
        Condition: func(ctx *ReleaseContext) bool {
            return ctx.DeployResults.AllSuccessful()
        },
    },
    {
        From:  StateDeploying,
        To:    StateRolledBack,
        Event: "rollback_complete",
        Condition: func(ctx *ReleaseContext) bool {
            return ctx.RollbackResult.Success
        },
    },
    {
        From:  StateFailed,
        To:    StateRolledBack,
        Event: "rollback_initiated",
        Condition: func(ctx *ReleaseContext) bool {
            return ctx.Config.RollbackStrategy == "automatic"
        },
    },
}
```

### 6.4 状态机实现

```go
type StateMachine struct {
    currentState ReleaseState
    transitions  []StateTransition
    context      *ReleaseContext
}

func (sm *StateMachine) Transition(event string) error {
    for _, t := range sm.transitions {
        if t.From == sm.currentState && t.Event == event {
            if t.Condition != nil && !t.Condition(sm.context) {
                return fmt.Errorf("transition condition not met")
            }
            
            oldState := sm.currentState
            sm.currentState = t.To
            
            if t.Action != nil {
                if err := t.Action(sm.context); err != nil {
                    sm.currentState = oldState
                    return err
                }
            }
            
            return nil
        }
    }
    
    return fmt.Errorf("invalid transition from %s on event %s", sm.currentState, event)
}
```

## 7. 关键决策点判定依据

### 7.1 版本类型决策

```go
type VersionDecisionRule struct {
    Name        string
    Priority    int
    Condition   func(ChangeAnalysisResult) bool
    VersionType ChangeType
}

var VersionDecisionRules = []VersionDecisionRule{
    {
        Name:     "breaking_change",
        Priority: 100,
        Condition: func(r ChangeAnalysisResult) bool {
            return r.BreakingChanges > 0
        },
        VersionType: ChangeTypeMajor,
    },
    {
        Name:     "new_features",
        Priority: 80,
        Condition: func(r ChangeAnalysisResult) bool {
            return r.NewFeatures > 0
        },
        VersionType: ChangeTypeMinor,
    },
    {
        Name:     "bug_fixes",
        Priority: 60,
        Condition: func(r ChangeAnalysisResult) bool {
            return r.BugFixes > 0 && r.NewFeatures == 0
        },
        VersionType: ChangeTypePatch,
    },
    {
        Name:     "large_changes",
        Priority: 50,
        Condition: func(r ChangeAnalysisResult) bool {
            return r.FilesModified > 20 || r.LinesAdded > 1000
        },
        VersionType: ChangeTypeMinor,
    },
    {
        Name:     "minor_changes",
        Priority: 40,
        Condition: func(r ChangeAnalysisResult) bool {
            return r.OtherChanges > 0
        },
        VersionType: ChangeTypePatch,
    },
}
```

### 7.2 版本决策流程

```
FUNCTION decide_version_type(analysis_result):
    # 按优先级排序规则
    sorted_rules = sort_by_priority(VersionDecisionRules)
    
    # 遍历规则找到匹配项
    FOR rule IN sorted_rules:
        IF rule.condition(analysis_result):
            RETURN {
                type: rule.version_type,
                rule: rule.name,
                confidence: calculate_confidence(analysis_result)
            }
    
    # 无匹配规则
    RETURN {
        type: ChangeTypeNone,
        rule: "no_changes",
        confidence: 1.0
    }
END FUNCTION
```

### 7.3 审批决策

```go
func NeedsApproval(decision VersionDecision, config AutoReleaseConfig) bool {
    // 主版本更新需要审批
    if decision.ChangeType == ChangeTypeMajor {
        return true
    }
    
    // 包含破坏性变更需要审批
    if decision.AnalysisResult.BreakingChanges > 0 {
        return true
    }
    
    // 大规模变更需要审批
    if decision.AnalysisResult.FilesModified > 50 ||
       decision.AnalysisResult.LinesAdded > 2000 {
        return true
    }
    
    // 置信度低于阈值需要审批
    if decision.Confidence < config.ApprovalThreshold {
        return true
    }
    
    // 超过自动发布最大级别需要审批
    if decision.ChangeType.String() > config.MaxAutoBumpLevel {
        return true
    }
    
    return false
}
```

### 7.4 部署策略决策

```go
func DetermineDeployStrategy(env EnvironmentConfig, decision VersionDecision) DeployStrategy {
    // 生产环境使用蓝绿部署
    if env.Type == "production" {
        return StrategyBlueGreen
    }
    
    // 主版本更新使用金丝雀部署
    if decision.ChangeType == ChangeTypeMajor {
        return StrategyCanary
    }
    
    // 默认使用滚动部署
    return StrategyRolling
}
```

### 7.5 回滚决策

```go
func ShouldRollback(err error, config DeployConfig) bool {
    // 部署失败
    if isDeployError(err) {
        return config.RollbackStrategy == "automatic"
    }
    
    // 健康检查失败
    if isHealthCheckError(err) {
        return true
    }
    
    // 关键服务不可用
    if isCriticalServiceDown(err) {
        return true
    }
    
    return false
}
```

## 8. 配置参数说明

### 8.1 核心配置参数

| 参数名 | 类型 | 默认值 | 说明 |
|-------|------|-------|------|
| autoRelease.enabled | bool | true | 是否启用自动发布 |
| autoRelease.triggerBranches | []string | ["main"] | 触发发布的分支列表 |
| autoRelease.requireApproval | bool | true | 是否需要审批 |
| autoRelease.approvalThreshold | float | 0.8 | 审批置信度阈值 |
| autoRelease.maxAutoBumpLevel | string | "minor" | 自动发布的最大版本级别 |
| autoRelease.quietPeriodHours | int | 2 | 静默期（小时） |
| autoRelease.minCommitsThreshold | int | 1 | 最小提交数量阈值 |

### 8.2 版本控制配置

| 参数名 | 类型 | 默认值 | 说明 |
|-------|------|-------|------|
| versioning.strategy | string | "semantic" | 版本控制策略 |
| versioning.prereleaseEnabled | bool | false | 是否启用预发布 |
| versioning.prereleaseIdentifier | string | "rc" | 预发布标识符 |
| versioning.branchPatterns | map | {} | 分支模式映射 |

## 9. 日志与监控

### 9.1 日志级别

- **DEBUG**: 详细的调试信息
- **INFO**: 常规操作信息
- **WARN**: 警告信息
- **ERROR**: 错误信息
- **FATAL**: 致命错误

### 9.2 关键日志点

```go
// 发布开始
logger.Info("Release pipeline started", map[string]interface{}{
    "releaseId": releaseID,
    "branch": branch,
    "commits": len(commits),
})

// 版本决策
logger.Info("Version decision made", map[string]interface{}{
    "currentVersion": currentVersion,
    "newVersion": newVersion,
    "changeType": changeType,
    "confidence": confidence,
})

// 构建完成
logger.Info("Build completed", map[string]interface{}{
    "platform": platform,
    "duration": duration,
    "artifactSize": size,
})

// 部署完成
logger.Info("Deployment completed", map[string]interface{}{
    "environment": env,
    "version": version,
    "healthCheck": healthy,
})

// 异常发生
logger.Error("Exception occurred", err, map[string]interface{}{
    "type": exceptionType,
    "stage": stage,
    "recoverable": recoverable,
})
```

## 10. 最佳实践建议

### 10.1 版本发布策略

1. **主版本更新**: 需要人工审批，使用蓝绿部署
2. **次版本更新**: 可自动发布，使用滚动部署
3. **修订版本更新**: 可自动发布，使用滚动部署

### 10.2 异常处理建议

1. **构建失败**: 立即中止，通知开发团队
2. **测试失败**: 立即中止，通知开发团队
3. **部署失败**: 自动回滚，通知运维团队
4. **健康检查失败**: 自动回滚，通知运维团队

### 10.3 监控告警

1. 发布成功率监控
2. 平均发布时长监控
3. 回滚率监控
4. 异常类型分布监控

---

**文档版本**: v1.0  
**最后更新**: 2024年  
**维护者**: 自动发布系统团队
