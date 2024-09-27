@Echo off&setlocal,EnableDelayedExpansion

REM License
REM 本项目受 Apache License Version 2.0 约束

REM 检查是否以管理员权限运行
net session >nul 2>&1
if %errorlevel% neq 0 (
    cls
    title   初始化失败，需要管理员权限......
    echo:
    echo:
    echo:
    echo:
    echo:       ______________________________________________________________
    echo:
    echo:             初始化失败！
    echo:
    echo:             错误: 需要管理员权限！
    echo:             解决方案：请右键单击此脚本并选择 "以管理员身份运行"
    echo:             __________________________________________________  
    echo:
    echo:             无法继续执行，请按任意键退出。
    echo:
    echo:       ______________________________________________________________
    echo:
    pause > nul
    taskkill /f /im cmd.exe 
    exit /b )

:Choice
cls
title   Software Install Script
echo:
echo:
echo:
echo:
echo:       ______________________________________________________________
echo:
echo:             切换 Winget 列表源
echo:
echo:             本脚本会有以下行为:
echo:             1.更换 Winget 列表源为中国科学技术大学镜像源
echo:             2.激活 Winget 代理配置
echo:
echo:             __________________________________________________      
echo:
echo:             [Y] 同意 
echo:             [N] 拒绝
echo:             [R] 重置列表源
echo:
echo:       ______________________________________________________________
echo:
set /p Choice=请输入(Y/N/R)以继续:
IF /i "!Choice!"=="Y" Goto :Next
IF /i "!Choice!"=="R" Goto :Rollback
IF /i "!Choice!"=="N" Goto :End
Echo 请输入Y/N/R，请按任意键返回。
Pause>Nul&Goto :Choice

REM 同意执行块
:Next
echo 正在将 Winget 列表源切换到中国科学技术大学镜像源
winget source remove winget
winget source add winget https://mirrors.ustc.edu.cn/winget-source

echo 正在激活 Winget 代理配置
winget settings --enable ProxyCommandLineOptions
taskkill /f /im cmd.exe
exit /b

REM 重置执行块
:Rollback
echo 重置 Winget 列表源
winget source reset --force
taskkill /f /im cmd.exe
exit /b

REM 终止执行块
:End
ECHO 用户取消安装，正在退出。
taskkill /f /im cmd.exe
exit /b
