# Software Install Script - Online Installer (PowerShell)
# This script provides a one-line installation from the custom domain

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Software Install Script - Online Installer" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[INFO] This script will install the Software Install Script (SIS) tool." -ForegroundColor Gray
Write-Host "[INFO] It will:" -ForegroundColor Gray
Write-Host "  1. Download the latest version from https://cgartlab.com/Software_Install_Script/" -ForegroundColor Gray
Write-Host "  2. Install dependencies" -ForegroundColor Gray
Write-Host "  3. Add to system PATH" -ForegroundColor Gray
Write-Host ""

# Check if Python is installed
Write-Host "[INFO] Checking Python installation..." -ForegroundColor Gray
$pythonCmd = $null
if (Get-Command "python3" -ErrorAction SilentlyContinue) {
    $pythonCmd = "python3"
} elseif (Get-Command "python" -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
} else {
    Write-Host "[ERROR] Python is not installed. Please install Python 3.7 or higher first." -ForegroundColor Red
    exit 1
}

$versionOutput = & $pythonCmd --version 2>&1
Write-Host "[OK] $versionOutput" -ForegroundColor Green

# Check if git is available
Write-Host "[INFO] Checking git installation..." -ForegroundColor Gray
if (-not (Get-Command "git" -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] git is not installed. Please install git first." -ForegroundColor Red
    exit 1
}
Write-Host "[OK] git is installed" -ForegroundColor Green

# Clone the repository
$tempDir = Join-Path $env:TEMP "Software_Install_Script_$(Get-Date -Format 'yyyyMMddHHmmss')"
Write-Host "[INFO] Cloning repository from GitHub..." -ForegroundColor Gray

try {
    if (Test-Path $tempDir) {
        Remove-Item -Path $tempDir -Recurse -Force
    }
    
    git clone "https://github.com/cgartlab/Software_Install_Script.git" $tempDir
    if ($LASTEXITCODE -ne 0) {
        throw "git clone failed"
    }
    
    Write-Host "[OK] Repository cloned successfully" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to clone repository: $_" -ForegroundColor Red
    exit 1
}

# Run the global installer
Write-Host "[INFO] Running global installer..." -ForegroundColor Gray
Set-Location $tempDir

try {
    & $pythonCmd -m pip install -e .
    if ($LASTEXITCODE -ne 0) {
        throw "pip install failed"
    }
    
    & .\install_global.ps1
    if ($LASTEXITCODE -ne 0) {
        throw "global install failed"
    }
    
    Write-Host "[OK] Installation completed successfully!" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Installation failed: $_" -ForegroundColor Red
    exit 1
}

# Cleanup
Write-Host "[INFO] Cleaning up..." -ForegroundColor Gray
Set-Location $env:TEMP
try {
    Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue
} catch {
    Write-Host "[WARNING] Could not cleanup temporary directory" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  Installation Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "You can now use the 'sis' command!" -ForegroundColor White
Write-Host ""
Write-Host "  sis --help      Show help" -ForegroundColor Cyan
Write-Host "  sis wizard      Launch guided wizard" -ForegroundColor Cyan
Write-Host "  sis check       Check system environment" -ForegroundColor Cyan
Write-Host "  sis tui         Launch TUI interface" -ForegroundColor Cyan
Write-Host ""
Write-Host "NOTE: If 'sis' command is not recognized," -ForegroundColor Yellow
Write-Host "      please restart your terminal." -ForegroundColor Yellow
Write-Host ""
