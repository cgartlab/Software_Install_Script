package ui

import (
	"testing"
	"time"
)

// TestVisualProgress_Basic 测试基本功能
func TestVisualProgress_Basic(t *testing.T) {
	config := DefaultVisualProgressConfig()
	config.TotalTasks = 3
	vp := NewVisualProgress(config)

	// 初始状态
	if vp.GetPercent() != config.MinProgress {
		t.Errorf("初始进度应为 %.2f, 得到 %.2f", config.MinProgress, vp.GetPercent())
	}

	if vp.IsComplete() {
		t.Error("初始状态不应为完成")
	}

	// 报告一个任务完成
	vp.ReportComplete()
	if vp.GetPercent() < 0.33 {
		t.Errorf("完成 1 个任务后进度应至少为 0.33, 得到 %.2f", vp.GetPercent())
	}

	// 报告第二个任务完成
	vp.ReportComplete()
	if vp.GetPercent() < 0.66 {
		t.Errorf("完成 2 个任务后进度应至少为 0.66, 得到 %.2f", vp.GetPercent())
	}

	// 报告最后一个任务完成
	vp.ReportComplete()
	if !vp.IsComplete() {
		t.Error("所有任务完成后应该标记为完成")
	}
	if vp.GetPercent() != 1.0 {
		t.Errorf("完成后进度应为 1.0, 得到 %.2f", vp.GetPercent())
	}
}

// TestVisualProgress_FakeProgress 测试假进度增长
func TestVisualProgress_FakeProgress(t *testing.T) {
	config := VisualProgressConfig{
		FakeRate:        0.1, // 每秒 10%
		MinProgress:     0.05,
		MaxFakeProgress: 0.85,
		TotalTasks:      10,
	}
	vp := NewVisualProgress(config)

	// 等待 2 秒，假进度应该增长
	time.Sleep(2 * time.Second)
	vp.UpdateManual() // 手动更新

	percent := vp.GetPercent()
	expectedMin := 0.05 + (2.0 * 0.1) // 0.25
	if percent < expectedMin {
		t.Errorf("2 秒后进度应至少为 %.2f, 得到 %.2f", expectedMin, percent)
	}

	// 不应该超过最大假进度
	if percent > config.MaxFakeProgress {
		t.Errorf("进度不应超过最大假进度 %.2f, 得到 %.2f", config.MaxFakeProgress, percent)
	}
}

// TestVisualProgress_Error 测试错误处理
func TestVisualProgress_Error(t *testing.T) {
	config := DefaultVisualProgressConfig()
	vp := NewVisualProgress(config)

	// 报告错误
	vp.ReportError()

	if !vp.HasError() {
		t.Error("应该标记为有错误")
	}
}

// TestVisualProgress_Reset 测试重置功能
func TestVisualProgress_Reset(t *testing.T) {
	config := DefaultVisualProgressConfig()
	config.TotalTasks = 2
	vp := NewVisualProgress(config)

	// 完成一个任务
	vp.ReportComplete()

	// 重置
	vp.Reset()

	if vp.GetPercent() != config.MinProgress {
		t.Errorf("重置后进度应为 %.2f, 得到 %.2f", config.MinProgress, vp.GetPercent())
	}

	if vp.IsComplete() {
		t.Error("重置后不应为完成状态")
	}

	if vp.HasError() {
		t.Error("重置后不应有错误状态")
	}

	// 进度应该重新开始增长
	time.Sleep(500 * time.Millisecond)
	vp.UpdateManual() // 手动更新
	if vp.GetPercent() <= config.MinProgress {
		t.Error("重置后进度应该重新增长")
	}
}

// TestVisualProgress_RealBeatsFake 测试真实进度优先于假进度
func TestVisualProgress_RealBeatsFake(t *testing.T) {
	config := VisualProgressConfig{
		FakeRate:        0.01, // 每秒 1% 慢速
		MinProgress:     0.05,
		MaxFakeProgress: 0.85,
		TotalTasks:      5,
	}
	vp := NewVisualProgress(config)

	// 等待 1 秒，假进度应该只增长到约 0.06
	time.Sleep(1 * time.Second)
	fakePercent := vp.GetPercent()

	// 突然完成 3 个任务（60%）
	vp.ReportComplete()
	vp.ReportComplete()
	vp.ReportComplete()

	realPercent := vp.GetPercent()
	if realPercent < 0.6 {
		t.Errorf("真实完成 3 个任务后进度应至少为 0.6, 得到 %.2f", realPercent)
	}

	if realPercent <= fakePercent {
		t.Errorf("真实进度 (%.2f) 应该大于假进度 (%.2f)", realPercent, fakePercent)
	}
}
