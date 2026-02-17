# Setup sis alias for PowerShell
$sisPath = "C:\Users\cgart\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\Scripts\sis.exe"

# Create PowerShell profile if it doesn't exist
if (!(Test-Path -Path $PROFILE)) {
    New-Item -ItemType File -Path $PROFILE -Force
}

# Add alias to profile
$aliasLine = "Set-Alias -Name sis -Value '$sisPath'"
$profileContent = Get-Content $PROFILE -Raw -ErrorAction SilentlyContinue

if ($profileContent -notlike "*Set-Alias -Name sis*") {
    Add-Content -Path $PROFILE -Value "`n# SwiftInstall alias`n$aliasLine`n"
    Write-Host "Added sis alias to PowerShell profile." -ForegroundColor Green
    Write-Host "Please restart PowerShell to use the 'sis' command." -ForegroundColor Yellow
} else {
    Write-Host "sis alias already exists in PowerShell profile." -ForegroundColor Cyan
}

# Create alias for current session
Set-Alias -Name sis -Value $sisPath
Write-Host "sis alias is now available in this session." -ForegroundColor Green