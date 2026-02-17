# SwiftInstall Global Installation Script (PowerShell)
# This script adds 'sis' command to the system PATH

param(
    [switch]$Uninstall
)

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  SwiftInstall Global Installation" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$InstallDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Write-Host "[INFO] Installation directory: $InstallDir" -ForegroundColor Gray

if ($Uninstall) {
    Write-Host ""
    Write-Host "[INFO] Uninstalling..." -ForegroundColor Yellow
    
    $userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    $newPath = ($userPath -split ';' | Where-Object { $_ -ne $InstallDir }) -join ';'
    [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
    
    Write-Host "[OK] Removed from user PATH" -ForegroundColor Green
    Write-Host ""
    Write-Host "Please restart your terminal for changes to take effect." -ForegroundColor Yellow
    exit 0
}

# Create sis.bat if it doesn't exist
$sisBatPath = Join-Path $InstallDir "sis.bat"

$sisBatContent = @"
@echo off
REM SwiftInstall CLI Entry Point
cd /d "$InstallDir"
python -m sis.main %*
"@

if (Test-Path $sisBatPath) {
    Write-Host "[OK] sis.bat already exists" -ForegroundColor Green
} else {
    Write-Host "[INFO] Creating sis.bat..." -ForegroundColor Gray
    Set-Content -Path $sisBatPath -Value $sisBatContent -Encoding ASCII
    Write-Host "[OK] sis.bat created" -ForegroundColor Green
}

# Create sis.ps1 for PowerShell users
$sisPs1Path = Join-Path $InstallDir "sis.ps1"

$sisPs1Content = @"
# SwiftInstall CLI Entry Point (PowerShell)
Set-Location "$InstallDir"
python -m sis.main @args
"@

if (Test-Path $sisPs1Path) {
    Write-Host "[OK] sis.ps1 already exists" -ForegroundColor Green
} else {
    Write-Host "[INFO] Creating sis.ps1..." -ForegroundColor Gray
    Set-Content -Path $sisPs1Path -Value $sisPs1Content -Encoding UTF8
    Write-Host "[OK] sis.ps1 created" -ForegroundColor Green
}

Write-Host ""
Write-Host "[INFO] Adding to PATH..." -ForegroundColor Gray

# Get current user PATH
$userPath = [Environment]::GetEnvironmentVariable("PATH", "User")

# Check if already in PATH
if ($userPath -split ';' | Where-Object { $_ -eq $InstallDir }) {
    Write-Host "[OK] Already in user PATH" -ForegroundColor Green
} else {
    Write-Host "[INFO] Adding to user PATH..." -ForegroundColor Gray
    
    # Add to user PATH
    if ($userPath) {
        $newPath = "$userPath;$InstallDir"
    } else {
        $newPath = $InstallDir
    }
    
    [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
    
    # Also update current session
    $env:PATH = "$env:PATH;$InstallDir"
    
    Write-Host "[OK] Added to user PATH" -ForegroundColor Green
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  Installation Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "You can now use 'sis' command from anywhere:" -ForegroundColor White
Write-Host ""
Write-Host "  sis --help      Show help" -ForegroundColor Cyan
Write-Host "  sis wizard      Launch guided wizard" -ForegroundColor Cyan
Write-Host "  sis check       Check system environment" -ForegroundColor Cyan
Write-Host "  sis tui         Launch TUI interface" -ForegroundColor Cyan
Write-Host ""
Write-Host "NOTE: If 'sis' command is not recognized," -ForegroundColor Yellow
Write-Host "      please restart your terminal or run:" -ForegroundColor Yellow
Write-Host "      `$env:PATH = [Environment]::GetEnvironmentVariable('PATH', 'User')" -ForegroundColor Yellow
Write-Host ""
