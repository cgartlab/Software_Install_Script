@echo off

REM License
REM 本项目受 Apache License Version 2.0 约束

title 更换 Winget 列表源

ECHO.
ECHO 请注意，安装脚本会进行以下操作：申请管理员权限，切换 Winget 列表源。
ECHO 若同意，请按任意键继续......
pause > nul

REM 提权命令
%1 mshta vbscript:CreateObject("Shell.Application").ShellExecute("cmd.exe","/c %~s0 ::","","runas",1)(window.close)&&exit
cd /d "%~dp0"

REM 更换列表源 为 中科大源
winget source remove winget
winget source add winget https://mirrors.ustc.edu.cn/winget-source


ECHO 切换结束，请按任意键退出。
pause > nul
exit
