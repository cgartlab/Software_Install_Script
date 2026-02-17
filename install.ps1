# SwiftInstall 一键安装脚本
# 使用方法: iex (irm https://cgartlab.com/SwiftInstall/install.ps1)

param(
    [string]$Version = "latest",
    [string]$InstallDir = "$env:LOCALAPPDATA\SwiftInstall",
    [switch]$AddToPath = $true
)

$ErrorActionPreference = "Stop"

# 颜色输出函数
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

# Logo
function Show-Logo {
    Write-ColorOutput @"
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ███████╗██╗    ██╗██╗████████╗██╗  ██╗██╗███╗   ██╗███████╗████████╗       ║
║   ██╔════╝██║    ██║██║╚══██╔══╝██║  ██║██║████╗  ██║██╔════╝╚══██╔══╝       ║
║   ███████╗██║ █╗ ██║██║   ██║   ███████║██║██╔██╗ ██║█████╗     ██║          ║
║   ╚════██║██║███╗██║██║   ██║   ██╔══██║██║██║╚██╗██║██╔══╝     ██║          ║
║   ███████║╚███╔███╔╝██║   ██║   ██║  ██║██║██║ ╚████║███████╗   ██║          ║
║   ╚══════╝ ╚══╝╚══╝ ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝          ║
║                                                                              ║
║   ██╗███╗   ██╗███████╗████████╗███████╗███╗   ███╗                          ║
║   ██║████╗  ██║██╔════╝╚══██╔══╝██╔════╝████╗ ████║                          ║
║   ██║██╔██╗ ██║█████╗     ██║   █████╗  ██╔████╔██║                          ║
║   ██║██║╚██╗██║██╔══╝     ██║   ██╔══╝  ██║╚██╔╝██║                          ║
║   ██║██║ ╚████║███████║   ██║   ███████╗██║ ╚═╝ ██║                          ║
║   ╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚══════╝╚═╝     ╚═╝                          ║
║                                                                              ║
║              ⚡  Fast • Simple • Reliable • Cross-Platform  ⚡                ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"@ -Color Cyan
}

# 检测系统架构
function Get-Architecture {
    $arch = $env:PROCESSOR_ARCHITECTURE
    switch ($arch) {
        "AMD64" { return "amd64" }
        "ARM64" { return "arm64" }
        default { return "amd64" }
    }
}

# 下载文件
function Download-File {
    param(
        [string]$Url,
        [string]$OutputPath
    )
    
    Write-ColorOutput "Downloading from $Url..." -Color Yellow
    
    try {
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri $Url -OutFile $OutputPath -UseBasicParsing
        $ProgressPreference = 'Continue'
        Write-ColorOutput "Download completed!" -Color Green
    }
    catch {
        Write-ColorOutput "Download failed: $_" -Color Red
        exit 1
    }
}

# 添加到 PATH
function Add-ToPath {
    param([string]$Directory)
    
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($currentPath -notlike "*$Directory*") {
        [Environment]::SetEnvironmentVariable("Path", "$currentPath;$Directory", "User")
        Write-ColorOutput "Added to PATH: $Directory" -Color Green
        Write-ColorOutput "Please restart your terminal to use 'sis' command" -Color Yellow
    }
    else {
        Write-ColorOutput "Already in PATH: $Directory" -Color Green
    }
}

# 主安装流程
function Install-SwiftInstall {
    Show-Logo
    
    Write-ColorOutput "`nStarting SwiftInstall installation..." -Color Cyan
    Write-ColorOutput "Version: $Version" -Color Gray
    Write-ColorOutput "Install Directory: $InstallDir" -Color Gray
    Write-ColorOutput "`n"
    
    # 创建安装目录
    if (!(Test-Path $InstallDir)) {
        New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
        Write-ColorOutput "Created directory: $InstallDir" -Color Green
    }
    
    # 检测架构
    $arch = Get-Architecture
    Write-ColorOutput "Detected architecture: $arch" -Color Gray
    
    # 构建下载 URL
    $baseUrl = "https://cgartlab.com/SwiftInstall"
    if ($Version -eq "latest") {
        $downloadUrl = "$baseUrl/releases/latest/sis-windows-$arch.exe"
    }
    else {
        $downloadUrl = "$baseUrl/releases/download/$Version/sis-windows-$arch.exe"
    }
    
    # 下载文件
    $outputFile = "$InstallDir\sis.exe"
    Download-File -Url $downloadUrl -OutputPath $outputFile
    
    # 验证下载
    if (Test-Path $outputFile) {
        $fileSize = (Get-Item $outputFile).Length
        Write-ColorOutput "File size: $([math]::Round($fileSize/1MB, 2)) MB" -Color Gray
        
        # 测试运行
        Write-ColorOutput "`nVerifying installation..." -Color Yellow
        try {
            $version = & $outputFile version 2>&1
            Write-ColorOutput "Installation successful!" -Color Green
            Write-ColorOutput "`n$version" -Color Cyan
        }
        catch {
            Write-ColorOutput "Warning: Could not verify installation" -Color Yellow
        }
    }
    else {
        Write-ColorOutput "Installation failed: File not found" -Color Red
        exit 1
    }
    
    # 添加到 PATH
    if ($AddToPath) {
        Write-ColorOutput "`nAdding to PATH..." -Color Yellow
        Add-ToPath -Directory $InstallDir
    }
    
    # 完成
    Write-ColorOutput "`n========================================" -Color Green
    Write-ColorOutput "Installation Complete!" -Color Green
    Write-ColorOutput "========================================" -Color Green
    Write-ColorOutput "`nUsage:" -Color White
    Write-ColorOutput "  sis install    - Install packages" -Color Gray
    Write-ColorOutput "  sis list       - List packages" -Color Gray
    Write-ColorOutput "  sis search     - Search packages" -Color Gray
    Write-ColorOutput "  sis --help     - Show help" -Color Gray
    Write-ColorOutput "`nFor more information: https://cgartlab.com/SwiftInstall" -Color Gray
}

# 运行安装
Install-SwiftInstall
