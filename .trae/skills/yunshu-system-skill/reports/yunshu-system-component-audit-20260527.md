# Yunshu System Component Audit — 2026-05-27

## Scope

This audit used Yunshu itself to inspect the updated system package in:

- `E:\traework\000 自动化工作流研究\yunshu-system-skill`
- `C:\Users\Administrator\.codex\skills\yunshu-system-skill`

The run covered the core entrypoint, components, safeguards, templates, agents,
adapters, schemas, scripts, tests, BMad examples, and a temporary external
project instance.

## Findings And Fixes

1. `version-check` read optional adapter files before checking whether they
   existed. In partial or project-root layouts this raised `FileNotFoundError`.
   Fixed by only extracting optional versions after the optional file exists.

2. `yunshu-health.ps1` did not cover adapters, its own health script, tests, or
   BMad demo examples. Fixed by expanding the health checklist from 106 to 120
   files.

3. `08-domain-guide` and `09-software-bridge` used Trae-specific
   `AskUserQuestion` wording in platform-neutral component docs. Fixed by
   routing those references through the current platform adapter.

4. `checkpoint list` lacked task filtering while `context list` already had
   `--task-id`. Fixed by adding `checkpoint list --task-id` and a regression
   test.

## Instance Run

Created `tmp-yunshu-component-audit/` as a minimal external project and ran:

- `init`
- `context record/list/show/status`
- `verify run`
- `bmad map/validate/status`
- `validate evidence`
- `checkpoint create/list/resume`
- `validate checkpoint`

The instance confirmed that Yunshu can manage a normal project root outside the
skill package and produce reusable context, evidence, mapping, and recovery
artifacts.

## Evidence

- Source package tests: `python -m pytest tests -q` -> `16 passed`
- Source package version gate: `python scripts\yunshu.py version-check` -> passed
- Source package link audit: `python scripts\yunshu.py audit links` -> passed
- Source package health gate: `scripts\yunshu-health.ps1` -> `120 passed, 0 missing`
- Codex installed package tests: `16 passed`
- Codex installed package version gate: passed
- Codex installed package link audit: passed
- Codex installed package health gate: `120 passed, 0 missing`
- JSON parse checks passed for schemas and example registries.
- Existing structured validations passed for context, checkpoint, evidence, and
  BMad mappings.
- Source package verification log contains fresh entries for regression,
  version, and link gates.

## Remaining Boundaries

- Live interactive adapter behavior was document-audited, not executed through
  Trae or Claude Code UI.
- `sync-trae.ps1` was run in dry-run mode only; it reported 134 files to sync and
  did not modify the Trae target copy.
- The temporary external project is ignored by `.gitignore` via
  `tmp-yunshu-*`.
