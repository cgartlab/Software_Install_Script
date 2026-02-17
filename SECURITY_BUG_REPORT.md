# SwiftInstall 安全漏洞与功能缺陷检测报告

## 检测概述

**检测日期**: 2026-02-17  
**检测方法**: 仅使用软件自带的官方命令进行检测  
**检测环境**: Windows 10, Python 3.12.10

---

## 一、检测命令与结果

| 命令 | 执行结果 | 状态 |
|------|----------|------|
| `python installer.py` | 成功运行，DeprecationWarning | ⚠️ 有警告 |
| `sis.bat --help` | 正常显示帮助信息 | ✅ 正常 |
| `sis.bat check` | **崩溃 - UnicodeDecodeError** | ❌ 失败 |
| `sis.bat version` | 正常显示版本 | ✅ 正常 |
| `sis.bat logs` | 正常 | ✅ 正常 |
| `sis.bat config` | 正常运行 | ✅ 正常 |
| `sis.bat wizard` | **崩溃 - AttributeError** | ❌ 失败 |
| `sis.bat lang en` | 正常 | ✅ 正常 |
| `sis.bat update` | 正常 | ✅ 正常 |
| `sis.bat refresh` | 正常 | ✅ 正常 |
| `sis.bat tui` | 交互问题 | ⚠️ 异常 |
| `sis.bat install` | 正常运行 | ✅ 正常 |
| `windows_installer.bat` | 编码乱码问题 | ⚠️ 异常 |

---

## 二、发现的漏洞与问题

### 2.1 关键漏洞 (Critical)

#### 🔴 漏洞1: 向导模式崩溃 - AttributeError

| 项目 | 内容 |
|------|------|
| **命令** | `sis.bat wizard` |
| **错误类型** | AttributeError |
| **错误信息** | `'SandboxInfo' object has no attribute 'detect'` |
| **触发位置** | `sis/guided_ui.py:317` |
| **根本原因** | 代码错误：`get_sandbox_detector().detect().detect()` 错误地调用了`detect()`方法两次 |

**错误代码片段**:
```python
# 第317行 - 错误代码
is_restricted, sandbox_info = get_sandbox_detector().detect(), get_sandbox_detector().detect().detect()
#                                                    ↑ 多余的 .detect()
```

**堆栈跟踪**:
```
AttributeError: 'SandboxInfo' object has no attribute 'detect'
  File "sis/guided_ui.py", line 317, in _check_sandbox
    is_restricted, sandbox_info = get_sandbox_detector().detect(), get_sandbox_detector().detect().detect()
```

**影响**: 
- 用户无法使用向导模式进行安装
- 程序直接崩溃退出
- 这是**阻塞性Bug**，导致核心功能完全不可用

---

### 2.2 高危漏洞 (High)

#### 🟠 漏洞2: Unicode编码处理导致程序崩溃

| 项目 | 内容 |
|------|------|
| **命令** | `sis.bat check`, `sis.bat wizard` |
| **错误类型** | UnicodeDecodeError |
| **错误信息** | `'gbk' codec can't decode byte 0x90 in position 7: illegal multibyte sequence` |
| **触发位置** | `subprocess` 线程读取输出时 |
| **根本原因** | Windows控制台默认使用GBK编码，程序输出UTF-8内容时解码失败 |

**错误堆栈**:
```
UnicodeDecodeError: 'gbk' codec can't decode byte 0x90 in position 7
  File "subprocess.py", line 1599, in _readerthread
    buffer.append(fh.read())
```

**触发条件**:
- 在Windows中文版系统上运行
- subprocess执行命令输出包含非ASCII字符
- 线程异步读取输出时编码不匹配

**影响**:
- `check` 命令检测过程中程序崩溃
- `wizard` 命令在环境分析阶段崩溃
- 用户无法完成系统检测

---

### 2.3 中危漏洞 (Medium)

#### 🟡 漏洞3: Python API弃用警告

| 项目 | 内容 |
|------|------|
| **命令** | `python installer.py` |
| **警告类型** | DeprecationWarning |
| **警告信息** | `'locale.getdefaultlocale' is deprecated and slated for removal in Python 3.15` |
| **触发位置** | `installer.py:99` |
| **根本原因** | 使用了即将在Python 3.15中移除的API |

**代码片段**:
```python
# installer.py:99
system_lang = locale.getdefaultlocale()[0]  # 弃用的API
```

**影响**:
- 当前版本可运行但有警告
- 未来Python版本升级后将无法使用

---

#### 🟡 漏洞4: Windows批处理文件编码问题

| 项目 | 内容 |
|------|------|
| **命令** | `windows_installer.bat` |
| **问题** | 中文输出显示乱码 |
| **症状** | `'�到平台:' is not recognized as an internal or external command` |
| **根本原因** | `chcp 65001` 编码设置未在所有命令执行前生效 |

**影响**:
- 批处理文件中的中文显示为乱码
- 可能导致用户误解输出信息

---

### 2.4 低危漏洞 (Low)

#### 🟢 问题5: TUI交互模式问题

| 项目 | 内容 |
|------|------|
| **命令** | `sis.bat tui` |
| **问题** | 管道输入处理不当 |
| **症状** | 程序异常终止 |

---

## 三、漏洞验证过程

### 测试1: installer.py (基础安装器)
```
执行: python installer.py
结果: ⚠️ DeprecationWarning
位置: installer.py:99
```

### 测试2: sis.bat check (系统检测)
```
执行: sis.bat check
结果: ❌ UnicodeDecodeError 崩溃
```

### 测试3: sis.bat wizard (安装向导)
```
执行: sis.bat wizard
结果: ❌ AttributeError 崩溃
```

### 测试4: sis.bat version (版本查看)
```
执行: sis.bat version
结果: ✅ 正常
```

### 测试5: sis.bat config (配置管理)
```
执行: sis.bat config
结果: ✅ 正常
```

### 测试6: sis.bat update (更新检查)
```
执行: sis.bat update
结果: ✅ 正常
```

---

## 四、修复建议优先级

| 优先级 | 问题 | 修复建议 |
|--------|------|----------|
| **P0** | guided_ui.py:317 AttributeError | 修正代码为 `get_sandbox_detector().detect()` |
| **P1** | UnicodeDecodeError | 为所有subprocess调用添加编码参数 `encoding='utf-8'` |
| **P2** | locale.getdefaultlocale弃用 | 替换为 `locale.getlocale()` 或手动检测 |
| **P3** | 批处理编码问题 | 确保 `chcp 65001` 在所有echo之前执行 |

---

## 五、总结

本次安全检测使用**软件自带的官方命令**进行，发现以下问题：

1. **关键漏洞**: 1个 (wizard命令崩溃)
2. **高危漏洞**: 1个 (Unicode编码导致崩溃)
3. **中危问题**: 2个 (API弃用、编码问题)
4. **低危问题**: 1个 (TUI交互)

**核心问题**: 
- `wizard` 命令完全不可用（关键Bug）
- `check` 命令在特定条件下崩溃

建议优先修复这些阻塞性问题以恢复软件核心功能的可用性。

---

*检测完成 - 2026-02-17*
