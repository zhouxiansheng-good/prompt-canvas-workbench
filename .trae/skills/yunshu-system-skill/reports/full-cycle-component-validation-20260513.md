# Yunshu Full-Cycle Component Validation

> Date: 2026-05-13
> Scope: Run one contained instance through Yunshu's core workflow and audit component usability.
> Demo root: `tmp-yunshu-full-cycle-demo/`

## 1. Goal

Validate whether the current Yunshu system components are complete, usable, coherent, and free of obvious conflicts, redundancy, or errors after adding the BMad enhancement layer.

## 2. Instance Task

Implemented a read-only demo helper:

```text
summarize_verify_log(root, limit=5)
```

The helper reads `.yunshu/verify-log.tsv` and returns recent verification records newest-first. The implementation is intentionally contained under `tmp-yunshu-full-cycle-demo/` and does not change production Yunshu CLI behavior.

## 3. Workflow Coverage

| Stage | Component | Evidence | Result |
|-------|-----------|----------|--------|
| 0 | 01-init | `tmp-yunshu-full-cycle-demo/docs/task_card.md` | Passed |
| 1 | 02-plan | `docs/plan.md`, `docs/spec.md`, `docs/tasks.md` | Passed |
| Optional | bmad-enhance | `bmad status demo-*` all fresh | Passed |
| 2a | 03-execute | Red/green TDD via pytest | Passed |
| 2b | 07-subagent | Adapter-gated; docs/routes/templates inspected | Conditionally usable |
| 3 | 04-accept | `tmp-yunshu-full-cycle-demo/acceptance_evidence.json` validates | Passed |
| 4 | 05-deliver | This report + checkpoints + verification log | Passed |
| Recover | 06-recover | checkpoint resume + validate checkpoint | Passed |

## 4. Verification Evidence

| Claim | Evidence |
|-------|----------|
| Red test fails before implementation | `.yunshu/verification/verify-20260513-102518-435224-dd67bd46.log` |
| Green demo tests pass | `.yunshu/verification/verify-20260513-102610-102677-b7b01529.log` |
| Yunshu CLI regression tests pass | `.yunshu/verification/verify-20260513-102610-341322-6cecd807.log` |
| Markdown links pass | `.yunshu/verification/verify-20260513-102610-468033-a4045660.log` |
| Version check remains 3.6.0 | `.yunshu/verification/verify-20260513-102610-512191-05a3d8e2.log` |
| BMad demo mappings remain fresh | `.yunshu/verification/verify-20260513-102634-226169-754b0f76.log` |
| Acceptance evidence validates | `.yunshu/verification/verify-20260513-102731-443659-1eba9254.log` |

Additional direct checks:

```text
python scripts/yunshu.py audit links                  -> passed
python scripts/yunshu.py version-check                -> passed: 3.6.0
python -m pytest tests                                -> 12 passed
python -m pytest tmp-yunshu-full-cycle-demo/tests/... -> 3 passed
python scripts/yunshu.py checkpoint resume ...        -> passed
python scripts/yunshu.py validate checkpoint ...      -> passed
```

## 5. Component Findings

### 01-init

Usable. The task-card format is sufficient for a contained implementation. No conflict found with BMad; BMad is correctly placed after the task card, not before it.

### 02-plan

Usable. Plan/spec/tasks artifacts were enough to define scope, rollback, contract, and tests. The phase is somewhat document-heavy, but not conflicting.

### bmad-enhance

Usable. Existing demo mappings validate and report fresh status. The enhancement layer does not bypass Yunshu gates. `bmad map/status/validate` provides a machine-checkable bridge.

### 03-execute

Usable. TDD red/green loop worked as intended. The demo implementation was isolated and did not touch production CLI behavior.

### 07-subagent

Conditionally usable. In Codex, actual subagent execution requires explicit user authorization. The component's own docs correctly state that task count alone does not authorize subagents in Codex. No conflict found, but runtime delegation was not exercised in this run.

### 04-accept

Usable. Structured acceptance evidence validates and maps to DoD items.

### 05-deliver

Usable. Report, verification log, context ledger, and checkpoint form a recoverable handoff.

### 06-recover

Usable. `checkpoint resume` and `validate checkpoint` both worked for the acceptance checkpoint.

## 6. Conflict / Redundancy / Error Review

### Conflicts

- No blocking route conflict found between BMad and Yunshu. BMad remains optional and cannot replace Yunshu task card, plan, execution, or acceptance.
- Codex subagent gating is explicit in `adapters/codex/SKILL.md`, `components/02-plan/SKILL.md`, and `components/07-subagent/SKILL.md`.

### Redundancy

- Some overlap exists between `bmad-enhance/project-context-sync.md` and Yunshu context ledger rules. This is acceptable: project-context is long-lived project guidance, while context ledger records task-specific investigation and freshness.
- Some README and SKILL tables repeat the BMad command list. This is intentional discoverability, not harmful duplication.

### Errors / Gaps

- No broken links or version mismatch found.
- No failing tests found.
- `07-subagent` was validated by route and documentation, not actual spawned agents, because Codex requires explicit delegation authorization.
- The BMad demo is synthetic. Real official BMad artifacts may require field calibration later.

## 7. Verdict

The Yunshu system is complete and usable for the tested workflow. The new BMad enhancement layer is feasible and does not introduce a blocking conflict with Yunshu's evidence-first workflow.

Recommended next hardening step: run `bmad map/status/validate` against real BMad-generated PRD, architecture, story, and project-context files to calibrate section extraction and field expectations.
