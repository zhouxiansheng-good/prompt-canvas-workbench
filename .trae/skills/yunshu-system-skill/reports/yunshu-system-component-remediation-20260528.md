# Yunshu System Component Remediation Report — 2026-05-28

## Scope

Audit and repair `yunshu-system-skill/` after the latest Yunshu update. The review covered component presence, cross-platform consistency, executable gates, duplicate content, generated artifacts, `SKILL.md` metadata, and single-file scale.

## Defects Fixed

| ID | Severity | Defect | Evidence | Fix |
|----|----------|--------|----------|-----|
| D-001 | High | `components/01-init` still used Trae-specific `AskUserQuestion` wording in platform-neutral requirement clarification docs. | `rg "AskUserQuestion|workflow_"` found direct mentions under `components/01-init/`. | Replaced direct calls with current-platform adapter wording; kept `AskUserQuestion` only as Trae-specific example/fallback text. |
| D-002 | High | Compliance audit content was duplicated under both `components/04-accept/compliance-audit/` and `components/09-software-bridge/browser-automation/compliance/`. | SHA-256 duplicate scan found identical five compliance components, guide, and env example. | Kept `04-accept/compliance-audit` as canonical; removed duplicated legacy files; replaced old 09 path with a thin compatibility route. |
| D-003 | Medium | 22 nested `SKILL.md` entries lacked YAML metadata front matter, weakening discoverability and consistency. | Dynamic scan of all `SKILL.md` reported missing front matter for compliance, domain-guide, software-bridge, browser, Cloudflare, and Supabase child skills. | Added `name`, `description`, and relevant metadata to all active skill entry files. |
| D-004 | Medium | `scripts/yunshu-health.ps1` only checked a static file list and did not detect missing nested skill metadata, generated caches, temp folders, or oversized files. | Original health check passed while cache/temp directories and metadata gaps existed. | Added dynamic `SKILL.md` metadata gate, generated/cache directory gate, and file-size gate. |
| D-005 | Medium | `scripts/sync-trae.ps1` excluded only two hard-coded temp directories, so new `tmp-yunshu-*` runs could be synced. | Script contained `tmp-yunshu-flow-e2e` and `tmp-yunshu-full-cycle-demo` only. | Replaced fixed names with prefix-based `tmp-yunshu-*` exclusion. |
| D-006 | Medium | Generated artifacts were present in the skill package: `.pytest_cache`, `__pycache__`, and `tmp-yunshu-component-audit`. | Enhanced health gate reported generated/cache directories. | Removed generated/cache directories and kept the health gate to prevent recurrence. |

## Scale Assessment

Current largest non-report source files:

| File | Size | Assessment |
|------|------|------------|
| `scripts/yunshu.py` | 46 KB | Large but under the new 50 KB Python gate. It is a single-dependency CLI; split later only if it grows materially. |
| `README.md` | 31 KB | Under the 32 KB Markdown gate. Close to the limit; future additions should move details into component docs. |
| `SKILL.md` | 22 KB | Acceptable for the root router because it serves as the L1/L2 entrypoint. |
| `components/01-init/SKILL.md` | 22 KB | Acceptable but near a practical complexity threshold. Further requirement-clarification growth should move into `requirement-clarification/`. |

New health thresholds:

- Markdown source files outside `reports/`: <= 32 KB.
- Python files: <= 50 KB.
- PowerShell files: <= 20 KB.
- Generated directories are blocked: `.pytest_cache`, `__pycache__`, `tmp-yunshu-*`.

## Validation Evidence

| Claim | Result | Evidence |
|-------|--------|----------|
| Enhanced health gate passes in a clean tree | Passed | `.yunshu/verification/verify-20260528-221619-217489-f14a295d.log` |
| Markdown internal links pass | Passed | `.yunshu/verification/verify-20260528-221209-673797-0e255c7f.log` |
| Version metadata is consistent | Passed | `.yunshu/verification/verify-20260528-221209-899704-c28577d5.log` |
| CLI regression tests pass | Passed, 16 tests | `.yunshu/verification/verify-20260528-221209-910441-f8d9eeb6.log` |
| CLI compiles | Passed | `.yunshu/verification/verify-20260528-221409-036730-b67be6da.log` |
| Duplicate source scan after remediation | Passed, no duplicate hashes emitted | Terminal command: SHA-256 duplicate scan excluding `.yunshu/`, `reports/`, caches, and temp dirs |

Two failed health records remain in `.yunshu/verify-log.tsv` as useful process evidence. They were caused by running health checks concurrently with `pytest` / `py_compile`, which generated cache directories during the health scan. The final clean-tree health gate passed after cache cleanup.

## Remaining Non-Blocking Notes

- Existing historical reports still reference old paths and past failures by design; they were not rewritten.
- `scripts/yunshu.py` is close to the Python size threshold. If new CLI features are added, split command groups into modules.
- `README.md` is close to the Markdown size threshold. Future user-facing additions should link out to L2/L3 component docs.

