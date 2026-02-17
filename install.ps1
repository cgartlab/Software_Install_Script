# SwiftInstall 一键安装脚本
# 使用方法: iex (irm https://cgartlab.com/SwiftInstall/install.ps1)

param(
    [string]$Version = "latest",
    [string]$InstallDir = "$env:LOCALAPPDATA\SwiftInstall",
    [switch]$AddToPath = $true,
    [switch]$SkipMirrorTest,
    [string]$Mirror = ""
)

$ErrorActionPreference = "Stop"

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
███████╗██╗    ██╗██╗███████╗████████╗    ██╗███╗   ██╗███████╗████████╗ █████╗ ██╗     ██╗     
██╔════╝██║    ██║██║██╔════╝╚══██╔══╝    ██║████╗  ██║██╔════╝╚══██╔══╝██╔══██╗██║     ██║     
███████╗██║ █╗ ██║██║█████╗     ██║       ██║██╔██╗ ██║███████╗   ██║   ███████║██║     ██║     
╚════██║██║███╗██║██║██╔══╝     ██║       ██║██║╚██╗██║╚════██║   ██║   ██╔══██║██║     ██║     
███████║╚███╔███╔╝██║██║        ██║       ██║██║ ╚████║███████║   ██║   ██║  ██║███████╗███████╗
╚══════╝ ╚══╝╚══╝ ╚═╝╚═╝        ╚═╝       ╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝
"@ -Color Cyan
}

function Get-Architecture {
    $arch = $env:PROCESSOR_ARCHITECTURE
    switch ($arch) {
        "AMD64" { return "amd64" }
        "ARM64" { return "arm64" }
        default { return "amd64" }
    }
}

function Download-File {
    param(
        [string]$Url,
        [string]$OutputPath
    )
    
    Write-ColorOutput "Downloading from $Url..." -Color Yellow
    
    $webClient = New-Object System.Net.WebClient
    
    $global:DownloadCompleted = $false
    $global:DownloadProgress = 0
    $script:downloadStartTime = $null
    
    $progressAction = {
        if ($null -eq $script:downloadStartTime) {
            $script:downloadStartTime = Get-Date
        }
        
        $elapsed = (Get-Date) - $script:downloadStartTime
        $elapsedSeconds = $elapsed.TotalSeconds
        
        if ($elapsedSeconds -gt 0 -and $EventArgs.BytesReceived -gt 0) {
            $speed = $EventArgs.BytesReceived / $elapsedSeconds
            $speedMB = $speed / 1MB
            
            $barWidth = 30
            $progress = [math]::Min($EventArgs.ProgressPercentage, 100)
            $filled = [math]::Floor($barWidth * $progress / 100)
            $empty = $barWidth - $filled
            
            $progressBar = "[" + ("=" * $filled) + (" " * $empty) + "]"
            
            $receivedMB = [math]::Round($EventArgs.BytesReceived / 1MB, 2)
            $totalMB = if ($EventArgs.TotalBytesToReceive -gt 0) { [math]::Round($EventArgs.TotalBytesToReceive / 1MB, 2) } else { "?" }
            
            $eta = if ($speed -gt 0 -and $EventArgs.TotalBytesToReceive -gt $EventArgs.BytesReceived) {
                $remainingBytes = $EventArgs.TotalBytesToReceive - $EventArgs.BytesReceived
                $etaSeconds = [math]::Round($remainingBytes / $speed)
                if ($etaSeconds -ge 60) {
                    "{0}m{1}s" -f [math]::Floor($etaSeconds / 60), ($etaSeconds % 60)
                } else {
                    "${etaSeconds}s"
                }
            } else { "..." }
            
            $statusLine = "`r$progressBar ${progress}% | $receivedMB/$totalMB MB | {0:N2} MB/s | ETA: {1}" -f $speedMB, $eta
            
            Write-Host $statusLine -NoNewline -ForegroundColor Cyan
        }
    }
    
    $completedAction = {
        $global:DownloadCompleted = $true
    }
    
    Register-ObjectEvent -InputObject $webClient -EventName DownloadProgressChanged -SourceIdentifier WebClient.DownloadProgress -Action $progressAction | Out-Null
    Register-ObjectEvent -InputObject $webClient -EventName DownloadFileCompleted -SourceIdentifier WebClient.DownloadCompleted -Action $completedAction | Out-Null
    
    try {
        $webClient.DownloadFileAsync($Url, $OutputPath)
        
        while (-not $global:DownloadCompleted) {
            Start-Sleep -Milliseconds 100
        }
        
        Write-Host ""
        
        if (Test-Path $OutputPath) {
            $fileSize = (Get-Item $OutputPath).Length
            if ($fileSize -eq 0) {
                Write-ColorOutput "Download failed: File is empty" -Color Red
                exit 1
            }
            Write-ColorOutput "Download completed! ($([math]::Round($fileSize/1MB, 2)) MB)" -Color Green
        } else {
            Write-ColorOutput "Download failed: File not created" -Color Red
            exit 1
        }
    }
    catch {
        Write-Host ""
        Write-ColorOutput "Download failed: $_" -Color Red
        exit 1
    }
    finally {
        Unregister-Event -SourceIdentifier WebClient.DownloadProgress -ErrorAction SilentlyContinue
        Unregister-Event -SourceIdentifier WebClient.DownloadCompleted -ErrorAction SilentlyContinue
        $webClient.Dispose()
    }
}

function Get-FastDownloadUrl {
    param([string]$OriginalUrl)
    
    $mirrorUrls = @(
        @{ Name = "Direct"; Url = $OriginalUrl },
        @{ Name = "ghproxy.net"; Url = $OriginalUrl -replace 'https://github.com/', 'https://ghproxy.net/https://github.com/' },
        @{ Name = "mirror.ghproxy.com"; Url = $OriginalUrl -replace 'https://github.com/', 'https://mirror.ghproxy.com/' },
        @{ Name = "gh-proxy.com"; Url = $OriginalUrl -replace 'https://github.com/', 'https://gh-proxy.com/' }
    )
    
    Write-ColorOutput "`nTesting download mirrors..." -Color Yellow
    
    $fastestMirror = $null
    $fastestTime = [double]::MaxValue
    
    foreach ($mirror in $mirrorUrls) {
        try {
            $testUrl = $mirror.Url
            $request = [System.Net.WebRequest]::Create($testUrl)
            $request.Method = "HEAD"
            $request.Timeout = 5000
            
            $sw = [System.Diagnostics.Stopwatch]::StartNew()
            $response = $request.GetResponse()
            $sw.Stop()
            
            $response.Close()
            
            $responseTime = $sw.ElapsedMilliseconds
            Write-ColorOutput "  [$($mirror.Name)] Response time: ${responseTime}ms" -Color Gray
            
            if ($responseTime -lt $fastestTime) {
                $fastestTime = $responseTime
                $fastestMirror = $mirror
            }
        }
        catch {
            Write-ColorOutput "  [$($mirror.Name)] Not available" -Color DarkGray
        }
    }
    
    if ($fastestMirror) {
        Write-ColorOutput "`nUsing fastest mirror: [$($fastestMirror.Name)]" -Color Green
        return $fastestMirror.Url
    }
    
    return $OriginalUrl
}

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

function Install-SwiftInstall {
    Show-Logo
    
    Write-ColorOutput "Starting SwiftInstall installation..." -Color Cyan
    Write-ColorOutput "Version: $Version" -Color Gray
    Write-ColorOutput "Install Directory: $InstallDir" -Color Gray
    Write-ColorOutput ""
    
    if (!(Test-Path $InstallDir)) {
        New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
        Write-ColorOutput "Created directory: $InstallDir" -Color Green
    }
    
    $arch = Get-Architecture
    Write-ColorOutput "Detected architecture: $arch" -Color Gray
    
    $repoOwner = "cgartlab"
    $repoName = "SwiftInstall"
    
    if ($Version -eq "latest") {
        try {
            $releaseInfo = Invoke-RestMethod -Uri "https://api.github.com/repos/$repoOwner/$repoName/releases/latest" -UseBasicParsing
            $Version = $releaseInfo.tag_name
            Write-ColorOutput "Latest version: $Version" -Color Gray
        }
        catch {
            Write-ColorOutput "Warning: Could not fetch latest version, using 'latest' as fallback" -Color Yellow
            $Version = "latest"
        }
    }
    
    $downloadUrl = "https://github.com/$repoOwner/$repoName/releases/download/$Version/sis-windows-$arch.exe"
    
    if ($Mirror -ne "") {
        $fastUrl = switch ($Mirror.ToLower()) {
            "ghproxy" { $downloadUrl -replace 'https://github.com/', 'https://ghproxy.net/https://github.com/' }
            "mirror" { $downloadUrl -replace 'https://github.com/', 'https://mirror.ghproxy.com/' }
            "gh-proxy" { $downloadUrl -replace 'https://github.com/', 'https://gh-proxy.com/' }
            default { $downloadUrl }
        }
        Write-ColorOutput "Using specified mirror: $Mirror" -Color Yellow
    }
    elseif ($SkipMirrorTest.IsPresent) {
        $fastUrl = $downloadUrl
        Write-ColorOutput "Skipping mirror test, using direct download" -Color Gray
    }
    else {
        $fastUrl = Get-FastDownloadUrl -OriginalUrl $downloadUrl
    }
    
    $outputFile = "$InstallDir\sis.exe"
    Download-File -Url $fastUrl -OutputPath $outputFile
    
    if (Test-Path $outputFile) {
        $fileSize = (Get-Item $outputFile).Length
        Write-ColorOutput "File size: $([math]::Round($fileSize/1MB, 2)) MB" -Color Gray
        
        Write-ColorOutput "`nVerifying installation..." -Color Yellow
        try {
            $versionOutput = & $outputFile version 2>&1
            Write-ColorOutput "Installation successful!" -Color Green
            Write-ColorOutput "$versionOutput" -Color Cyan
        }
        catch {
            Write-ColorOutput "Warning: Could not verify installation" -Color Yellow
        }
    }
    else {
        Write-ColorOutput "Installation failed: File not found" -Color Red
        exit 1
    }
    
    if ($AddToPath) {
        Write-ColorOutput "`nAdding to PATH..." -Color Yellow
        Add-ToPath -Directory $InstallDir
    }
    
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

Install-SwiftInstall
