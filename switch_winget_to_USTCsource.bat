@echo off
:: BatchGotAdmin (Run as Admin code starts)
REM --> Check for permissions
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"

REM --> If error flag set, we do not have admin.
if '%errorlevel%' NEQ '0' (
    echo Requesting administrative privileges...
    goto UACPrompt
) else ( goto gotAdmin )

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    set params = %*:"="
    echo UAC.ShellExecute "cmd.exe", "/c ""%~s0"" %params%", "", "runas", 1 >> "%temp%\getadmin.vbs"

    "%temp%\getadmin.vbs"
    del "%temp%\getadmin.vbs"
    exit /B

:gotAdmin
    pushd "%CD%"
    CD /D "%~dp0"
:: BatchGotAdmin (Run as Admin code ends)

REM 设置 Winget 安装源为 USTC 镜像源
echo Setting Winget source to USTC mirror...
winget source add USTC https://mirrors.ustc.edu.cn/winget-source

REM 检查连接是否成功
echo Checking connection to USTC mirror...
ping -n 1 mirrors.ustc.edu.cn | findstr /i "Reply" > nul
if errorlevel 1 (
    echo Unable to connect to USTC mirror. Resetting to default source...
    winget source reset
    echo Winget source reset to default.
) else (
    echo Connection to USTC mirror successful.
)

pause
