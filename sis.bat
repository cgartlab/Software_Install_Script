@echo off
REM SwiftInstall CLI Entry Point
REM This script enables global access to the 'sis' command

setlocal

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"

REM Run the sis module
python -m sis.main %*

endlocal
