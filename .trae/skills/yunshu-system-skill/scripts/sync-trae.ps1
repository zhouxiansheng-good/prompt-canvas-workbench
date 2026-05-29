param(
    [string]$Source = "",
    [string]$Target = "",
    [switch]$Apply,
    [switch]$NoClean
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($Source)) {
    $Source = Resolve-Path (Join-Path $PSScriptRoot "..")
} else {
    $Source = Resolve-Path $Source
}

if ([string]::IsNullOrWhiteSpace($Target)) {
    $projectRoot = Resolve-Path (Join-Path $Source "..")
    $Target = Join-Path $projectRoot ".trae\skills\yunshu-system-skill"
}

$Source = [System.IO.Path]::GetFullPath($Source)
$Target = [System.IO.Path]::GetFullPath($Target)

Write-Host "Source: $Source"
Write-Host "Target: $Target"

$excludedNames = @(".git", ".yunshu", ".pytest_cache", "__pycache__")
$excludedPrefixes = @("tmp-yunshu-")

function Test-ExcludedRelativePath {
    param([string]$RelativePath)

    $parts = $RelativePath -split "[\\/]"
    foreach ($part in $parts) {
        if ($excludedNames -contains $part) {
            return $true
        }
        foreach ($prefix in $excludedPrefixes) {
            if ($part.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)) {
                return $true
            }
        }
    }
    return $false
}

$files = Get-ChildItem -LiteralPath $Source -Recurse -File | Where-Object {
    $relative = $_.FullName.Substring($Source.Length).TrimStart("\", "/")
    -not (Test-ExcludedRelativePath $relative)
}

Write-Host "Files to sync: $($files.Count)"

if (-not $Apply) {
    Write-Host "Dry run only. Re-run with -Apply to copy files."
    $files | Select-Object -First 20 | ForEach-Object {
        $relative = $_.FullName.Substring($Source.Length).TrimStart("\", "/")
        Write-Host "  $relative"
    }
    if ($files.Count -gt 20) {
        Write-Host "  ... $($files.Count - 20) more"
    }
    if ((Test-Path -LiteralPath $Target) -and (-not $NoClean)) {
        $targetFiles = Get-ChildItem -LiteralPath $Target -Recurse -Force | Where-Object { -not $_.PSIsContainer }
        $staleFiles = @()
        foreach ($targetFile in $targetFiles) {
            $relative = $targetFile.FullName.Substring($Target.Length).TrimStart("\", "/")
            $sourcePath = Join-Path $Source $relative
            if ((Test-ExcludedRelativePath $relative) -or (-not (Test-Path -LiteralPath $sourcePath))) {
                $staleFiles += $relative
            }
        }
        Write-Host "Stale target files to remove on apply: $($staleFiles.Count)"
        $staleFiles | Select-Object -First 20 | ForEach-Object {
            Write-Host "  stale $_"
        }
        if ($staleFiles.Count -gt 20) {
            Write-Host "  ... $($staleFiles.Count - 20) more stale files"
        }
    }
    exit 0
}

if ((Test-Path -LiteralPath $Target) -and (-not $NoClean)) {
    $resolvedTarget = (Resolve-Path -LiteralPath $Target).Path
    $expectedSuffix = ".trae\skills\yunshu-system-skill"
    if (-not $resolvedTarget.EndsWith($expectedSuffix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to clean unexpected target path: $resolvedTarget"
    }

    $targetFiles = Get-ChildItem -LiteralPath $Target -Recurse -Force | Where-Object { -not $_.PSIsContainer }
    foreach ($targetFile in $targetFiles) {
        $relative = $targetFile.FullName.Substring($Target.Length).TrimStart("\", "/")
        $sourcePath = Join-Path $Source $relative
        if ((Test-ExcludedRelativePath $relative) -or (-not (Test-Path -LiteralPath $sourcePath))) {
            Remove-Item -LiteralPath $targetFile.FullName -Force
        }
    }

    $targetDirs = Get-ChildItem -LiteralPath $Target -Recurse -Force -Directory | Sort-Object FullName -Descending
    foreach ($targetDir in $targetDirs) {
        $children = Get-ChildItem -LiteralPath $targetDir.FullName -Force
        if ($children.Count -eq 0) {
            Remove-Item -LiteralPath $targetDir.FullName -Force
        }
    }
}

foreach ($file in $files) {
    $relative = $file.FullName.Substring($Source.Length).TrimStart("\", "/")
    $destination = Join-Path $Target $relative
    $destinationDir = Split-Path -Parent $destination
    New-Item -ItemType Directory -Force -Path $destinationDir | Out-Null
    Copy-Item -LiteralPath $file.FullName -Destination $destination -Force
}

Write-Host "Sync complete."
