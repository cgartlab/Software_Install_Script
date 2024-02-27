# 常用软件安装脚本

## 介绍

这是我自用的一个 Windows 和 macOS 的软件批量安装脚本。
分别基于 winget 和 homebrew 包管理器。

其中 Windows 文件夹内
`switch_winget_to_USTCsource.bat` 文件用于切换为国内安装源。
`software_list.txt` 文件为软件安装列表。
`software_install.bat` 文件为安装执行脚本。

macOS 文件夹内
`packages.txt` 文件为软件安装列表。
`install_packages.sh` 文件为安装执行脚本。

## Windows 软件安装列表

可根据自己的需求，在终端中使用命令 `winget search 关键词` 来搜索安装包，将ID添加到软件安装列表中。

## macOS 软件安装列表

可根据自己的需求，在终端中使用命令 `brew search 关键词` 来搜索安装包，将软件名添加到列表文件中。

## 使用方式

### Windows

将压缩包解压到同一个文件夹内
运行 `switch_winget_to_USTCsource.bat` 文件，将源切换为国内源。
若有更适合你的源可以更换内部链接。

双击 `software_install.bat` 文件即可。
脚本会自动搜寻，下载，并安装列表文件中的软件。

### macOS

将压缩包解压到同一个文件夹内
打开终端，将 `install_packages.sh` 文件拖入终端对话框中，回车。

Enjoy it！
