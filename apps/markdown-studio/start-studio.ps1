[CmdletBinding()]
param(
    [ValidateRange(1024,65535)][int]$Port = 8765,
    [switch]$NoBrowser
)
$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$pythonExe = (Get-Command python -ErrorAction Stop).Source
$frontendRoot = Join-Path $projectRoot 'md2card'
$existing = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($existing) {
    try {
        $health = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/api/health" -TimeoutSec 3
        if (-not $health.ok -or $health.root -ne $projectRoot) {
            throw '此端口正在运行其他工作台。'
        }
    } catch {
        throw "端口 $Port 已被其他服务占用，请用 -Port 指定其他端口。"
    }
} else {
    $fontManifest = Get-Content -LiteralPath (Join-Path $projectRoot 'fonts\manifest.json') -Raw | ConvertFrom-Json
    $missingFonts = @($fontManifest | Where-Object {
        -not (Test-Path -LiteralPath (Join-Path $projectRoot ('fonts\' + $_.file))) -or
        -not (Test-Path -LiteralPath (Join-Path $frontendRoot ('public\fonts\' + [IO.Path]::GetFileName($_.file))))
    })
    if ($missingFonts.Count -gt 0) {
        & $pythonExe -X utf8 (Join-Path $projectRoot 'scripts\download-fonts.py')
        if ($LASTEXITCODE -ne 0) { throw '字体下载或校验失败。' }
    }
    if (-not (Test-Path -LiteralPath (Join-Path $frontendRoot 'dist\app\index.html'))) {
        Push-Location -LiteralPath $frontendRoot
        try {
            & npm ci
            if ($LASTEXITCODE -ne 0) { throw '安装 Web 依赖失败。' }
            & npm run build
            if ($LASTEXITCODE -ne 0) { throw '构建 Web 应用失败。' }
        } finally { Pop-Location }
    }
    $serverArgs = @('-X','utf8','-u',('"' + (Join-Path $projectRoot 'studio_server.py') + '"'),'--port',$Port)
    Start-Process -FilePath $pythonExe -ArgumentList $serverArgs -WorkingDirectory $projectRoot -WindowStyle Hidden | Out-Null
    $ready = $false
    for ($attempt = 0; $attempt -lt 30; $attempt++) {
        try {
            $health = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/api/health" -TimeoutSec 1
            if ($health.ok -and $health.root -eq $projectRoot) { $ready = $true; break }
        } catch {}
        Start-Sleep -Milliseconds 200
    }
    if (-not $ready) { throw '本地服务未能启动，请检查端口和 Python 环境。' }
}
if (-not $NoBrowser) { Start-Process "http://127.0.0.1:$Port/app/" }
Write-Host "可视化排版工作台：http://127.0.0.1:$Port/app/"
