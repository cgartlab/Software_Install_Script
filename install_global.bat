@echo off
REM SwiftInstall Global Installation Script
REM This script adds 'sis' command to the system PATH

setlocal EnableDelayedExpansion

echo.
echo ============================================
echo   SwiftInstall Global Installation
echo ============================================
echo.

REM Check for admin privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Running without administrator privileges.
    echo [INFO] Will install to user PATH only.
    echo.
)

REM Get the script directory
set "INSTALL_DIR=%~dp0"
set "INSTALL_DIR=%INSTALL_DIR:~0,-1%"

echo [INFO] Installation directory: %INSTALL_DIR%
echo.

REM Create the sis.bat wrapper script content
set "SIS_BAT=%INSTALL_DIR%\sis.bat"

if exist "%SIS_BAT%" (
    echo [OK] sis.bat already exists
) else (
    echo [INFO] Creating sis.bat...
    (
        echo @echo off
        echo REM SwiftInstall CLI Entry Point
        echo cd /d "%INSTALL_DIR%"
        echo python -m sis.main %%*
    ) > "%SIS_BAT%"
    echo [OK] sis.bat created
)

echo.
echo [INFO] Adding to PATH...
echo.

REM Get current user PATH
for /f "tokens=2*" %%a in ('reg query "HKCU\Environment" /v PATH 2^>nul') do set "USER_PATH=%%b"

REM Check if already in PATH
echo %USER_PATH% | findstr /i /c:"%INSTALL_DIR%" >nul
if %errorlevel% equ 0 (
    echo [OK] Already in user PATH
) else (
    echo [INFO] Adding to user PATH...
    
    REM Add to user PATH
    if defined USER_PATH (
        setx PATH "%USER_PATH%;%INSTALL_DIR%" >nul
    ) else (
        setx PATH "%INSTALL_DIR%" >nul
    )
    
    echo [OK] Added to user PATH
    echo.
    echo [IMPORTANT] Please restart your terminal or run:
    echo   refreshenv
    echo   or open a new PowerShell/CMD window
)

echo.
echo ============================================
echo   Installation Complete!
echo ============================================
echo.
echo You can now use 'sis' command from anywhere:
echo.
echo   sis --help      Show help
echo   sis wizard      Launch guided wizard
echo   sis check       Check system environment
echo   sis tui         Launch TUI interface
echo.
echo NOTE: If 'sis' command is not recognized,
echo       please restart your terminal.
echo.

pause
endlocal
