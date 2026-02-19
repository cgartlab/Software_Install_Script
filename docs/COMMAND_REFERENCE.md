# SwiftInstall 命令参考手册

## 命令总览

| 命令 | 简述 | 交互模式 |
|------|------|----------|
| `sis` | 启动交互菜单 | 是 |
| `sis install` | 安装软件 | 是 |
| `sis uninstall` | 卸载软件 | 否 |
| `sis uninstall-all` | 一键卸载全部 | 否 |
| `sis search` | 搜索软件 | 是 |
| `sis list` | 列出配置 | 否 |
| `sis config` | 配置管理 | 是 |
| `sis edit-list` | 编辑列表 | 否 |
| `sis status` | 系统状态 | 否 |
| `sis version` | 版本信息 | 否 |
| `sis about` | 关于作者 | 是 |
| `sis help` | 帮助文档 | 否 |
| `sis setup` | 环境准备 | 否 |
| `sis clean` | 清理缓存 | 否 |
| `sis update` | 检查更新 | 否 |
| `sis wizard` | 安装向导 | 是 |

---

## 详细命令说明

### `sis` (无参数)

启动交互式主菜单。

```bash
sis
```

**快捷键:**
- `↑/↓`: 导航
- `Enter`: 选择
- `i`: 快速安装
- `s`: 快速搜索
- `c`: 配置管理
- `a`: 关于作者
- `q`: 退出

---

### `sis install [package...]`

安装软件包。

```bash
# 从配置文件安装所有软件
sis install

# 安装指定的软件包
sis install Git.Git Microsoft.VisualStudioCode

# 查看帮助
sis install --help
```

**参数:**
- `[package...]`: 可选，软件包 ID 列表。不提供时从配置文件读取。

**交互:**
- 显示安装进度条
- 显示每个软件包的安装状态
- 支持并行安装（默认 4 个并发）

**快捷键:**
- `a`: 显示关于信息（安装完成后）
- `Enter/Esc`: 完成并退出
- `q`: 取消并退出

---

### `sis uninstall [package...]`

卸载软件包。

```bash
# 卸载配置中的所有软件
sis uninstall

# 卸载指定的软件包
sis uninstall Git.Git Microsoft.VisualStudioCode
```

**参数:**
- `[package...]`: 可选，软件包 ID 列表。不提供时从配置文件读取。

---

### `sis uninstall-all`

一键卸载配置中的全部软件。

```bash
sis uninstall-all
```

**注意:** 此命令会卸载所有配置的软件，请谨慎使用。

---

### `sis search [query]`

搜索软件包。

```bash
# 交互式搜索
sis search

# 直接搜索
sis search vscode

# 查看帮助
sis search --help
```

**参数:**
- `[query]`: 可选，搜索关键词。不提供时进入交互搜索界面。

**交互:**
- 输入搜索关键词
- 显示搜索结果列表
- 按 Enter 添加到配置

**快捷键:**
- `Enter`: 执行搜索 / 添加选中软件
- `/`: 重新搜索
- `Esc`: 返回输入框
- `q`: 退出

---

### `sis list`

列出配置文件中已配置的软件。

```bash
sis list
```

**输出:**
- 序号
- 软件名称
- 软件 ID/包名
- 分类

---

### `sis config`

交互式配置管理器。

```bash
sis config
```

**功能:**
- 添加软件
- 编辑软件
- 删除软件
- 浏览配置列表

**快捷键:**
- `a`: 添加软件
- `Enter/e`: 编辑选中软件
- `d/r`: 删除选中软件
- `Tab`: 切换输入框
- `q`: 返回

---

### `sis edit-list`

使用系统默认编辑器直接编辑配置文件。

```bash
sis edit-list
```

**说明:**
- Windows: 使用记事本或配置的编辑器
- Linux/macOS: 使用 `$EDITOR` 环境变量指定的编辑器

---

### `sis status`

显示系统状态信息。

```bash
sis status
```

**输出:**
- 操作系统信息
- 系统架构
- 包管理器状态
- 已安装软件数量

---

### `sis version`

显示版本和构建信息。

```bash
sis version
```

**输出:**
- 版本号
- Git 提交哈希
- 构建日期
- Go 版本
- 操作系统/架构

---

### `sis about`

显示作者和项目信息。

```bash
sis about
```

**交互:**
- 全屏显示关于信息
- 按任意键返回

---

### `sis help`

显示完整的帮助文档。

```bash
sis help

# 或查看特定命令的帮助
sis install help
sis search --help
```

**内容:**
- 所有可用命令
- 命令参数说明
- 快捷键列表
- 使用示例

---

### `sis setup`

环境一键准备。

```bash
# 自动检测并安装依赖
sis setup --auto-install-deps

# 仅预览，不执行
sis setup --dry-run

# 只检测，不自动安装
sis setup --auto-install-deps=false
```

**参数:**
- `--auto-install-deps`: 是否自动安装依赖（默认 true）
- `--dry-run`: 仅预览操作（默认 false）

**功能:**
- 检测包管理器
- 检查必要命令
- 自动安装依赖
- 验证环境状态

---

### `sis clean`

清理安装缓存和临时文件。

```bash
sis clean
```

---

### `sis update`

检查 SwiftInstall 更新。

```bash
sis update
```

---

### `sis wizard`

启动安装向导。

```bash
sis wizard
```

**功能:**
- 引导式软件安装
- 语言选择
- 常用软件推荐

---

## 全局参数

以下参数可用于所有命令：

| 参数 | 简述 | 示例 |
|------|------|------|
| `--config` | 指定配置文件路径 | `sis --config /path/to/config.yaml` |
| `--lang` / `-l` | 设置语言 | `sis -l en` |
| `--help` / `-h` | 显示帮助 | `sis install --help` |

---

## 配置文件说明

### 文件位置

- **Windows:** `%USERPROFILE%\.si\config.yaml`
- **Linux/macOS:** `~/.si/config.yaml`

### 配置项

```yaml
# 语言设置 (zh/en)
language: zh

# 主题 (dark/light)
theme: dark

# 并行安装
parallel_install: true

# 最大并发数
max_workers: 4

# 自动更新检查
auto_update_check: true

# 安装前确认
confirm_before_install: true

# 软件列表
software:
  - name: Git
    id: Git.Git
    category: Development
  - name: VS Code
    id: Microsoft.VisualStudioCode
    category: Development
```

### 软件包字段

| 字段 | 必填 | 说明 |
|------|------|------|
| `name` | 是 | 软件显示名称 |
| `id` | 是 | 包管理器 ID (Winget/Homebrew) |
| `package` | 否 | 备用包名 |
| `category` | 否 | 分类标签 |
| `version` | 否 | 指定版本 |
| `source` | 否 | 指定来源 |

---

## 退出代码

| 代码 | 含义 |
|------|------|
| `0` | 成功 |
| `1` | 一般错误 |
| `2` | 配置文件错误 |
| `3` | 环境检查失败 |

---

## 示例

### 示例 1: 完整安装流程

```bash
# 1. 启动交互菜单
sis

# 2. 选择"配置管理"，添加软件
# 3. 选择"安装软件"，开始安装
```

### 示例 2: 命令行快速安装

```bash
sis install Git.Git Microsoft.VisualStudioCode Google.Chrome
```

### 示例 3: 搜索并安装

```bash
# 搜索
sis search python

# 选择后添加到配置，然后安装
sis install
```

### 示例 4: 环境检查

```bash
# 完整环境准备
sis setup --auto-install-deps

# 仅检查
sis status
```

### 示例 5: 配置管理

```bash
# 查看配置
sis list

# 编辑配置
sis config

# 直接编辑文件
sis edit-list
```

---

## 另请参阅

- [README.md](../README.md) - 项目概述
- [QUICKSTART.md](QUICKSTART.md) - 快速入门
- [CHANGELOG.md](../CHANGELOG.md) - 版本历史
