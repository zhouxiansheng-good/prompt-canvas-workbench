param()

$ErrorActionPreference = "Stop"

if ($PSScriptRoot) {
    $SkillRoot = Split-Path -Parent $PSScriptRoot
} else {
    $SkillRoot = $PWD.Path
}

$checks = @(
    @{ Group = "root"; Path = "SKILL.md" },
    @{ Group = "root"; Path = "VERSION" },
    @{ Group = "root"; Path = "README.md" },
    @{ Group = "root"; Path = "LICENSE" },
    @{ Group = "components/01-init"; Path = "SKILL.md" },
    @{ Group = "components/02-plan"; Path = "SKILL.md" },
    @{ Group = "components/02-plan"; Path = "gates.md" },
    @{ Group = "components/03-execute"; Path = "SKILL.md" },
    @{ Group = "components/03-execute"; Path = "debug.md" },
    @{ Group = "components/03-execute"; Path = "gates.md" },
    @{ Group = "components/03-execute"; Path = "verify.md" },
    @{ Group = "components/03-execute/frontend-design"; Path = "design-thinking.md" },
    @{ Group = "components/03-execute/frontend-design"; Path = "aesthetic-checklist.md" },
    @{ Group = "components/03-execute/frontend-design"; Path = "banned-patterns.md" },
    @{ Group = "components/03-execute/frontend-design"; Path = "plan.md" },
    @{ Group = "components/03-execute/frontend-design"; Path = "TASK_CARD.md" },
    @{ Group = "components/03-execute/frontend-design"; Path = "ACCEPTANCE_REPORT.md" },
    @{ Group = "components/03-execute/frontend-design"; Path = "CHANGE_REPORT.md" },
    @{ Group = "components/03-execute/frontend-design"; Path = "README.md" },
    @{ Group = "components/03-execute/frontend-design/design-templates"; Path = "brutalist.md" },
    @{ Group = "components/03-execute/frontend-design/design-templates"; Path = "maximalist.md" },
    @{ Group = "components/03-execute/frontend-design/design-templates"; Path = "minimal.md" },
    @{ Group = "components/03-execute/frontend-design/design-templates"; Path = "retro-futuristic.md" },
    @{ Group = "components/03-execute/webapp-testing"; Path = "SKILL.md" },
    @{ Group = "components/03-execute/webapp-testing/examples"; Path = "console_logging.py" },
    @{ Group = "components/03-execute/webapp-testing/examples"; Path = "element_discovery.py" },
    @{ Group = "components/03-execute/webapp-testing/examples"; Path = "static_html_automation.py" },
    @{ Group = "components/03-execute/webapp-testing/scripts"; Path = "with_server.py" },
    @{ Group = "components/04-accept"; Path = "SKILL.md" },
    @{ Group = "components/04-accept"; Path = "gates.md" },
    @{ Group = "components/05-deliver"; Path = "SKILL.md" },
    @{ Group = "components/06-recover"; Path = "SKILL.md" },
    @{ Group = "components/07-subagent"; Path = "SKILL.md" },
    @{ Group = "components/07-subagent"; Path = "dispatch.md" },
    @{ Group = "components/bmad-enhance"; Path = "SKILL.md" },
    @{ Group = "components/bmad-enhance"; Path = "architecture-map.md" },
    @{ Group = "components/bmad-enhance"; Path = "bmad-cli-adapter.md" },
    @{ Group = "components/bmad-enhance"; Path = "party-mode-gate.md" },
    @{ Group = "components/bmad-enhance"; Path = "prd-map.md" },
    @{ Group = "components/bmad-enhance"; Path = "project-context-sync.md" },
    @{ Group = "components/bmad-enhance"; Path = "story-map.md" },
    @{ Group = "safeguards"; Path = "agent-safety.md" },
    @{ Group = "safeguards"; Path = "architecture.md" },
    @{ Group = "safeguards"; Path = "bias-calibration.md" },
    @{ Group = "safeguards"; Path = "chinese-dev.md" },
    @{ Group = "safeguards"; Path = "code-quality.md" },
    @{ Group = "safeguards"; Path = "cognition.md" },
    @{ Group = "safeguards"; Path = "concurrency.md" },
    @{ Group = "safeguards"; Path = "context.md" },
    @{ Group = "safeguards"; Path = "database.md" },
    @{ Group = "safeguards"; Path = "dependency-analysis.md" },
    @{ Group = "safeguards"; Path = "dependency.md" },
    @{ Group = "safeguards"; Path = "legacy.md" },
    @{ Group = "safeguards"; Path = "maintenance.md" },
    @{ Group = "safeguards"; Path = "meta-cognition.md" },
    @{ Group = "safeguards"; Path = "microservice.md" },
    @{ Group = "safeguards"; Path = "refactor.md" },
    @{ Group = "safeguards"; Path = "security.md" },
    @{ Group = "safeguards"; Path = "skill-preserve.md" },
    @{ Group = "safeguards"; Path = "sustainability.md" },
    @{ Group = "safeguards"; Path = "talent-pipeline.md" },
    @{ Group = "safeguards"; Path = "team-norms.md" },
    @{ Group = "safeguards"; Path = "team.md" },
    @{ Group = "safeguards"; Path = "understanding.md" },
    @{ Group = "safeguards"; Path = "vibe-coding.md" },
    @{ Group = "schemas"; Path = "acceptance_evidence.schema.json" },
    @{ Group = "schemas"; Path = "bmad_mapping.schema.json" },
    @{ Group = "schemas"; Path = "checkpoint.schema.json" },
    @{ Group = "schemas"; Path = "context_ledger.schema.json" },
    @{ Group = "adapters/codex"; Path = "SKILL.md" },
    @{ Group = "adapters/codex"; Path = "AGENTS.md.example" },
    @{ Group = "adapters/codex"; Path = "automation-notes.md" },
    @{ Group = "adapters/trae"; Path = "README.md" },
    @{ Group = "adapters/trae"; Path = "agent-install.md" },
    @{ Group = "adapters/trae"; Path = "skill-config.example.json" },
    @{ Group = "adapters/claude-code"; Path = "README.md" },
    @{ Group = "scripts"; Path = "yunshu.py" },
    @{ Group = "scripts"; Path = "sync-trae.ps1" },
    @{ Group = "scripts"; Path = "yunshu-health.ps1" },
    @{ Group = "templates"; Path = "acceptance_runbook.md" },
    @{ Group = "templates"; Path = "bmad_architecture_map.md" },
    @{ Group = "templates"; Path = "bmad_prd_map.md" },
    @{ Group = "templates"; Path = "bmad_project_context.md" },
    @{ Group = "templates"; Path = "bmad_story_map.md" },
    @{ Group = "templates"; Path = "bug_knowledge.md" },
    @{ Group = "templates"; Path = "change_report.md" },
    @{ Group = "templates"; Path = "context_ledger.md" },
    @{ Group = "templates"; Path = "debug_session.md" },
    @{ Group = "templates"; Path = "gsd_project.md" },
    @{ Group = "templates"; Path = "gsd_requirements.md" },
    @{ Group = "templates"; Path = "gsd_roadmap.md" },
    @{ Group = "templates"; Path = "gsd_state.md" },
    @{ Group = "templates"; Path = "handoff.md" },
    @{ Group = "templates"; Path = "phase_memory_card.md" },
    @{ Group = "templates"; Path = "plan.md" },
    @{ Group = "templates"; Path = "spec.md" },
    @{ Group = "templates"; Path = "subagent_implementer.md" },
    @{ Group = "templates"; Path = "subagent_quality_reviewer.md" },
    @{ Group = "templates"; Path = "subagent_spec_reviewer.md" },
    @{ Group = "templates"; Path = "tasks.md" },
    @{ Group = "agents/yunshu-implementer"; Path = "AGENT.md" },
    @{ Group = "agents/yunshu-quality-reviewer"; Path = "AGENT.md" },
    @{ Group = "agents/yunshu-spec-reviewer"; Path = "AGENT.md" },
    @{ Group = "agents"; Path = "openai.yaml" },
    @{ Group = "components/08-domain-guide"; Path = "SKILL.md" },
    @{ Group = "components/08-domain-guide"; Path = "decision-tree-schema.json" },
    @{ Group = "components/08-domain-guide"; Path = "guide-engine.md" },
    @{ Group = "components/08-domain-guide"; Path = "atomic-task-criteria.md" },
    @{ Group = "components/08-domain-guide/examples/road-design"; Path = "decision-tree.json" },
    @{ Group = "components/09-software-bridge"; Path = "SKILL.md" },
    @{ Group = "components/09-software-bridge"; Path = "software-registry-schema.json" },
    @{ Group = "components/09-software-bridge"; Path = "command-builder.md" },
    @{ Group = "components/09-software-bridge"; Path = "execution-sandbox.md" },
    @{ Group = "components/09-software-bridge/registry"; Path = "example-software.json" },
    @{ Group = "examples/bmad-mapping-demo"; Path = "README.md" },
    @{ Group = "examples/bmad-mapping-demo"; Path = "PRD.md" },
    @{ Group = "examples/bmad-mapping-demo"; Path = "architecture.md" },
    @{ Group = "examples/bmad-mapping-demo"; Path = "project-context.md" },
    @{ Group = "examples/bmad-mapping-demo"; Path = "story-cli-evidence-dashboard.md" },
    @{ Group = "tests"; Path = "test_yunshu_cli.py" }
)

$TotalCount = 0
$PassCount = 0
$FailCount = 0
$CurrentGroup = ""
$MissingFiles = @()
$HygieneFailures = @()
$SizeFailures = @()
$MetadataFailures = @()

Write-Host ""
Write-Host "=== Yunshu Health Check ===" -ForegroundColor Cyan
Write-Host "Root: $SkillRoot" -ForegroundColor Gray
Write-Host ""

foreach ($check in $checks) {
    $Group = $check.Group
    $File = $check.Path
    if ($Group -eq "root") {
        $FullPath = Join-Path $SkillRoot $File
    } else {
        $FullPath = Join-Path (Join-Path $SkillRoot $Group) $File
    }

    if ($Group -ne $CurrentGroup) {
        if ($CurrentGroup -ne "") {
            Write-Host ""
        }
        $CurrentGroup = $Group
        Write-Host "[$Group]" -ForegroundColor Yellow
    }

    $TotalCount++
    if (Test-Path -LiteralPath $FullPath) {
        $PassCount++
        Write-Host "  OK  $File" -ForegroundColor Green
    } else {
        $FailCount++
        $MissingFiles += "$Group/$File"
        Write-Host "  MISS  $File" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=== Summary ===" -ForegroundColor Cyan
Write-Host "  Total:  $TotalCount" -ForegroundColor White
Write-Host "  Passed: $PassCount" -ForegroundColor Green
Write-Host "  Missing: $FailCount" -ForegroundColor $(if ($FailCount -gt 0) { "Red" } else { "Green" })

if ($FailCount -gt 0) {
    Write-Host ""
    Write-Host "Missing files:" -ForegroundColor Red
    foreach ($missing in $MissingFiles) {
        Write-Host "  - $missing" -ForegroundColor Red
    }
}

$skillFiles = Get-ChildItem -LiteralPath $SkillRoot -Recurse -File -Filter "SKILL.md" | Where-Object {
    $relative = $_.FullName.Substring($SkillRoot.Length).TrimStart("\", "/")
    $parts = $relative -split "[\\/]"
    -not [bool]($parts | Where-Object { $_ -in @(".git", ".yunshu", ".pytest_cache", "__pycache__") -or $_ -like "tmp-yunshu-*" })
}

Write-Host ""
Write-Host "=== Skill Metadata ===" -ForegroundColor Cyan
Write-Host "  SKILL.md files: $($skillFiles.Count)" -ForegroundColor White

foreach ($skill in $skillFiles) {
    $relative = $skill.FullName.Substring($SkillRoot.Length).TrimStart("\", "/")
    $text = Get-Content -Raw -Encoding UTF8 -LiteralPath $skill.FullName
    if ($text -notmatch "(?s)^---\s*\r?\n.*?\r?\n---") {
        $MetadataFailures += "$relative missing YAML front matter"
        continue
    }
    if ($text -notmatch "(?m)^name:\s*.+$") {
        $MetadataFailures += "$relative missing name"
    }
    if ($text -notmatch "(?m)^description:\s*.+$") {
        $MetadataFailures += "$relative missing description"
    }
}

if ($MetadataFailures.Count -gt 0) {
    Write-Host ""
    Write-Host "Skill metadata problems:" -ForegroundColor Red
    foreach ($failure in $MetadataFailures) {
        Write-Host "  - $failure" -ForegroundColor Red
    }
} else {
    Write-Host "  Metadata: passed" -ForegroundColor Green
}

$generatedDirs = Get-ChildItem -LiteralPath $SkillRoot -Recurse -Directory | Where-Object {
    $_.Name -in @(".pytest_cache", "__pycache__") -or $_.Name -like "tmp-yunshu-*"
}

if ($generatedDirs.Count -gt 0) {
    Write-Host ""
    Write-Host "Generated/cache directories found:" -ForegroundColor Red
    foreach ($dir in $generatedDirs) {
        $relative = $dir.FullName.Substring($SkillRoot.Length).TrimStart("\", "/")
        $HygieneFailures += $relative
        Write-Host "  - $relative" -ForegroundColor Red
    }
}

$ignoredParts = @(".git", ".yunshu", ".pytest_cache", "__pycache__")
$sizeLimits = @(
    @{ Extension = ".md"; MaxBytes = 32768; Label = "Markdown files should stay <= 32 KB" },
    @{ Extension = ".py"; MaxBytes = 51200; Label = "Python files should stay <= 50 KB" },
    @{ Extension = ".ps1"; MaxBytes = 20480; Label = "PowerShell files should stay <= 20 KB" }
)

foreach ($limit in $sizeLimits) {
    $oversized = Get-ChildItem -LiteralPath $SkillRoot -Recurse -File | Where-Object {
        $relative = $_.FullName.Substring($SkillRoot.Length).TrimStart("\", "/")
        $parts = $relative -split "[\\/]"
        $isIgnored = [bool]($parts | Where-Object { $ignoredParts -contains $_ -or $_ -like "tmp-yunshu-*" })
        -not $isIgnored -and
            $_.Extension -eq $limit.Extension -and
            $_.Length -gt $limit.MaxBytes -and
            $parts[0] -ne "reports"
    }

    if ($oversized.Count -gt 0) {
        Write-Host ""
        Write-Host $limit.Label -ForegroundColor Red
        foreach ($file in $oversized) {
            $relative = $file.FullName.Substring($SkillRoot.Length).TrimStart("\", "/")
            $SizeFailures += "$relative ($($file.Length) bytes)"
            Write-Host "  - $relative ($($file.Length) bytes)" -ForegroundColor Red
        }
    }
}

Write-Host ""

if ($FailCount -gt 0 -or $HygieneFailures.Count -gt 0 -or $SizeFailures.Count -gt 0 -or $MetadataFailures.Count -gt 0) {
    exit 1
}
exit 0
