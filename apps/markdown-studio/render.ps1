[CmdletBinding()]
param(
    [Parameter(Position = 0)][string]$File = '排版示例.qmd',
    [switch]$Force,
    [switch]$ExportPages,
    [ValidateRange(72, 600)][int]$Dpi = 150
)
$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$quartoCommand = Get-Command quarto -ErrorAction SilentlyContinue
if ($quartoCommand) {
    $quartoExe = $quartoCommand.Source
} else {
    $quartoExe = Join-Path $env:LOCALAPPDATA 'Programs\Quarto\bin\quarto.cmd'
    if (-not (Test-Path -LiteralPath $quartoExe)) {
        throw '未找到 Quarto。请先安装 Quarto，或重新打开终端。'
    }
}
$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCommand) { throw '未找到 Python 3。' }
$pythonExe = $pythonCommand.Source
$inputPath = if ([IO.Path]::IsPathRooted($File)) { $File } else { Join-Path $projectRoot $File }
$inputPath = (Resolve-Path -LiteralPath $inputPath).Path
$extension = [IO.Path]::GetExtension($inputPath).ToLowerInvariant()
if ($extension -eq '.md') {
    $qmdPath = Join-Path $projectRoot ([IO.Path]::GetFileNameWithoutExtension($inputPath) + '.qmd')
    $converterArgs = @((Join-Path $projectRoot 'scripts\convert-markdown.py'), $inputPath, '--output', $qmdPath)
    if ($Force) { $converterArgs += '--force' }
    & $pythonExe @converterArgs
    if ($LASTEXITCODE -ne 0) { throw 'Markdown 转换失败。' }
    $inputPath = $qmdPath
} elseif ($extension -ne '.qmd') {
    throw '请提供 .md 或 .qmd 文件。'
}
$relativeInput = [IO.Path]::GetRelativePath($projectRoot, $inputPath)
if ($relativeInput -eq '..' -or $relativeInput.StartsWith('..' + [IO.Path]::DirectorySeparatorChar)) {
    throw '.qmd 文件必须放在项目内；外部 .md 文件会自动复制为项目内的 .qmd。'
}
Push-Location -LiteralPath $projectRoot
try {
    & $quartoExe render $relativeInput --to typst
    if ($LASTEXITCODE -ne 0) { throw 'Quarto 渲染失败。' }
    $relativeOutput = [IO.Path]::ChangeExtension($relativeInput, '.pdf')
    $pdfPath = Join-Path $projectRoot ('output\pdf\' + $relativeOutput)
    if (-not (Test-Path -LiteralPath $pdfPath)) { throw "没有找到预期 PDF：$pdfPath" }
    Write-Host "PDF 已生成：$pdfPath" -ForegroundColor Green
    if ($ExportPages) {
        $popplerCommand = Get-Command pdftoppm -ErrorAction SilentlyContinue
        if ($popplerCommand) {
            $popplerExe = $popplerCommand.Source
        } else {
            $popplerExe = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdftoppm.exe'
            if (-not (Test-Path -LiteralPath $popplerExe)) { throw 'PDF 已生成；导出页面需要 pdftoppm（Poppler）。' }
        }
        $relativePageDir = $relativeInput.Substring(0, $relativeInput.Length - [IO.Path]::GetExtension($relativeInput).Length)
        $pageRoot = Join-Path $projectRoot ('output\pages\' + $relativePageDir)
        New-Item -ItemType Directory -Path $pageRoot -Force | Out-Null
        Get-ChildItem -LiteralPath $pageRoot -Filter 'page-*.png' -File | ForEach-Object { Remove-Item -LiteralPath $_.FullName }
        & $popplerExe -png -r $Dpi $pdfPath (Join-Path $pageRoot 'page')
        if ($LASTEXITCODE -ne 0) { throw 'PDF 页面导出失败。' }
        Write-Host "页面图片已生成：$pageRoot" -ForegroundColor Green
    }
} finally {
    Pop-Location
}
