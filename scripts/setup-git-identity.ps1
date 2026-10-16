param(
    [ValidateNotNullOrEmpty()][string]$Name = '4evour',
    [ValidateNotNullOrEmpty()][string]$Email = '167200760+4evour@users.noreply.github.com'
)

$ErrorActionPreference = 'Stop'
$repository = Split-Path -Parent $PSScriptRoot

function Set-RepositoryConfig([string]$Key, [string]$Value) {
    & git -C $repository config --local $Key $Value
    if ($LASTEXITCODE -ne 0) { throw "无法设置 Git 配置：$Key" }
}

$existingHooks = & git -C $repository config --get core.hooksPath
if ($LASTEXITCODE -notin @(0, 1)) { throw '无法读取 Git 钩子配置。' }
if ($existingHooks -and $existingHooks -ne '.githooks') {
    throw "已有钩子目录 $existingHooks，请先整合其中的检查，再设置 .githooks。"
}

Set-RepositoryConfig 'user.name' $Name
Set-RepositoryConfig 'user.email' $Email
Set-RepositoryConfig 'user.useConfigOnly' 'true'
Set-RepositoryConfig 'identity.name' $Name
Set-RepositoryConfig 'identity.email' $Email
Set-RepositoryConfig 'core.hooksPath' '.githooks'

foreach ($variable in @('GIT_AUTHOR_IDENT', 'GIT_COMMITTER_IDENT')) {
    $identity = & git -C $repository var $variable
    if ($LASTEXITCODE -ne 0 -or $identity -notmatch ('^' + [regex]::Escape("$Name <$Email>") + ' [0-9]+ [+-][0-9]{4}$')) {
        throw "$variable 与仓库身份不符，请检查 GIT_AUTHOR_* / GIT_COMMITTER_* 环境变量。"
    }
    Write-Output "$variable = $identity"
}
Write-Output '已启用仓库身份与提交、推送校验。'
