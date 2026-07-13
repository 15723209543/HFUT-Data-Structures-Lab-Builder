param(
    [switch]$Force
)

$ErrorActionPreference = 'Stop'
$source = Join-Path $PSScriptRoot 'hfut-ds-shiyanbaogao'
$skillsRoot = Join-Path $HOME '.codex\skills'
$target = Join-Path $skillsRoot 'hfut-ds-shiyanbaogao'

if (-not (Test-Path -LiteralPath (Join-Path $source 'SKILL.md'))) {
    throw "Skill source is incomplete: $source"
}

New-Item -ItemType Directory -Force -Path $skillsRoot | Out-Null

if (Test-Path -LiteralPath $target) {
    if (-not $Force) {
        throw "Target already exists. Review it first, then rerun with -Force if replacement is intended: $target"
    }
    $resolvedRoot = [IO.Path]::GetFullPath($skillsRoot)
    $resolvedTarget = [IO.Path]::GetFullPath($target)
    if (-not $resolvedTarget.StartsWith($resolvedRoot, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to replace a path outside the Codex skills directory: $resolvedTarget"
    }
    Remove-Item -Recurse -Force -LiteralPath $resolvedTarget
}

Copy-Item -Recurse -LiteralPath $source -Destination $target
Write-Host "Installed: $target"
Write-Host "Restart Codex, then invoke `$hfut-ds-shiyanbaogao with an experiment DOCX."
