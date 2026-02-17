# Software Install Script

<div align="center">
  <strong>常用软件批量安装脚本</strong>
  <br><br>
  基于 Winget (Windows) 和 Homebrew (macOS)
</div>

---

## 介绍

这是我自用的一个 Windows 和 macOS 的软件批量安装脚本。
分别基于 winget 和 homebrew 包管理器。

---

## Windows 使用方法

1. 将压缩包解压到同一个文件夹内
2. 运行 `switch_winget_to_USTCsource.bat` 文件，将源切换为国内源（可选）
3. 双击 `software_install.bat` 文件即可

脚本会自动搜寻、下载，并安装列表文件中的软件。

---

## macOS 使用方法

1. 将压缩包解压到同一个文件夹内
2. 打开终端，将 `install_packages.sh` 文件拖入终端对话框中，回车即可

---

## 软件列表

### Windows

可根据自己的需求，在终端中使用命令 `winget search 关键词` 来搜索安装包，将 ID 添加到 `software_list.txt` 文件中。

### macOS

可根据自己的需求，在终端中使用命令 `brew search 关键词` 来搜索安装包，将软件名添加到 `packages.txt` 文件中。

---

## 项目文件说明

### Windows 文件夹

| 文件 | 说明 |
|------|------|
| `switch_winget_to_USTCsource.bat` | 切换为国内安装源 |
| `software_list.txt` | 软件安装列表 |
| `software_install.bat` | 安装执行脚本 |

### macOS 文件夹

| 文件 | 说明 |
|------|------|
| `packages.txt` | 软件安装列表 |
| `install_packages.sh` | 安装执行脚本 |

---

## 在线访问

- **GitHub 仓库**：[https://github.com/cgartlab/Software_Install_Script](https://github.com/cgartlab/Software_Install_Script)

---

## 许可证

[MIT License](LICENSE)
