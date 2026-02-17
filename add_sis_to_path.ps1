# Add Python Scripts directory to PATH for sis command
$scriptsPath = "C:\Users\cgart\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\Scripts"

# Get current user PATH
$currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")

# Check if already in PATH
if ($currentPath -notlike "*$scriptsPath*") {
    # Add to PATH
    $newPath = $currentPath + ";" + $scriptsPath
    [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
    Write-Host "Added sis to PATH. Please restart your terminal." -ForegroundColor Green
} else {
    Write-Host "sis is already in PATH." -ForegroundColor Yellow
}

# Also add for current session
$env:PATH += ";" + $scriptsPath
Write-Host "You can now use 'sis' command in this session." -ForegroundColor Cyan