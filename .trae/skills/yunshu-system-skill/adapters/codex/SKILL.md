---
name: yunshu-system-skill-codex-adapter
description: Codex adapter for Yunshu. Maps the core workflow to Codex tools without referencing unavailable Trae-only tools.
metadata:
  version: "3.6.0"
---

# Yunshu Codex Adapter

Use the core Yunshu workflow from `../../SKILL.md`, with these Codex mappings.

## Tool Mapping

| Yunshu capability | Codex implementation |
|---|---|
| User choice / confirmation | Use the available Codex user-input mechanism when present; otherwise ask one concise question. |
| Subagent execution | Use Codex subagents only when the user explicitly authorizes delegation. |
| Checkpoint state | Use `python scripts/yunshu.py checkpoint ...`. |
| Context ledger | Use `python scripts/yunshu.py context ...` before repeating repository investigation. |
| Evidence log | Use `python scripts/yunshu.py verify run ...`. |
| Browser/UI validation | Use the available Codex browser or Playwright tools for local targets. |

## Codex Rules

- Do not mention or call `AskUserQuestion` unless the active platform provides it.
- Do not mention non-existent `workflow_codex_*` tools.
- Do not spawn subagents merely because Yunshu recommends parallel work; Codex
  requires explicit user authorization for subagents.
- Keep checkpoints in `.yunshu/checkpoints/` and treat `phase_memory.json` as the
  only resume authority after compaction or thread interruption.

## Startup Checklist

1. Check for `.yunshu/checkpoints/index.json`.
2. Check for `.yunshu/context/index.json`; use `context list/show/status` to reuse fresh context before rereading files.
3. If the user supplied a checkpoint id, run:
   `python scripts/yunshu.py checkpoint resume <checkpoint_id>`.
4. Run `python scripts/yunshu.py version-check` when editing the Yunshu package.
5. Run `python scripts/yunshu.py audit links` before delivery.
