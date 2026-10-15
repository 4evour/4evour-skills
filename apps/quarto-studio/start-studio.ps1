[CmdletBinding()]
param(
    [ValidateRange(1024,65535)][int]$Port = 8766,
    [switch]$NoBrowser
)
$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$pythonExe = (Get-Command python -ErrorAction Stop).Source
$existing = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($existing) {
    try {
        $health = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/api/health" -TimeoutSec 3
        if (-not $health.ok -or $health.root -ne $projectRoot) { throw '端口由其他服务使用。' }
    } catch { throw "端口 $Port 已被其他服务占用，请用 -Port 指定其他端口。" }
} else {
    & $pythonExe -X utf8 (Join-Path $projectRoot 'scripts\download-fonts.py')
    if ($LASTEXITCODE -ne 0) { throw '字体准备失败。' }
    $arguments = @('-X','utf8','-u',('"' + (Join-Path $projectRoot 'studio_server.py') + '"'),'--port',$Port)
    Start-Process -FilePath $pythonExe -ArgumentList $arguments -WorkingDirectory $projectRoot -WindowStyle Hidden | Out-Null
    $ready = $false
    for ($attempt = 0; $attempt -lt 30; $attempt++) {
        try {
            $health = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/api/health" -TimeoutSec 1
            if ($health.ok -and $health.root -eq $projectRoot) { $ready = $true; break }
        } catch {}
        Start-Sleep -Milliseconds 200
    }
    if (-not $ready) { throw '服务未能启动，请检查 Python 环境和端口。' }
}
if (-not $NoBrowser) { Start-Process "http://127.0.0.1:$Port/app/" }
Write-Host "Quarto Studio：http://127.0.0.1:$Port/app/"
