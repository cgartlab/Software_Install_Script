# 常用软件安装脚本

## 介绍

这是我自用的一个常用软件批量安装脚本，基于 winget 包管理器。
其中 switch_winget_to_USTCsource.bat 文件用于切换为国内安装源。
software_list.txt 文件为软件安装列表。
software_install.bat 文件为安装执行脚本。

## 软件安装列表

可根据自己的需求，在终端中使用命令 'winget search 关键词' 来搜索安装包，将ID添加到软件安装列表中。
列表中包含

```console
9PKTQ5699M62
MSPCManager
Git.Git
Python.Python
Microsoft.VisualStudioCode
Tencent.WeixinDevTools
7zip.7zip
Figma.Figma
Krita.Krita
BlenderFoundation.Blender
Unity.UnityHub
Telegram.TelegramDesktop
Tencent.WeChat
Tencent.TIM
voidtools.Everything
ByteDance.JianyingPro
Daum.PotPlayer
xanderfrangos.twinkletray
Notion.Notion
Obsidian.Obsidian
Yuanli.uTools
QL-Win.QuickLook
nomic.gpt4all
Valve.Steam
```
## 使用方式

将压缩包解压到同一个文件夹内
运行 switch_winget_to_USTCsource.bat 文件，将源切换为国内源。
若有更适合你的源可以更换内部链接。

双击 software_install.bat 文件即可。
脚本会自动搜寻，下载，并安装列表文件中的软件。

Enjoy it！
