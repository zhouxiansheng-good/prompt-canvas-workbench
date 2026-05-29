---
name: yunshu-system-skill-trae-adapter
description: Trae IDE adapter for Yunshu. Makes Trae skill loading, AskUserQuestion usage, project-root state, and installed-copy CLI paths explicit.
metadata:
  version: "3.6.0"
---

# Yunshu Trae IDE Adapter

Use the core Yunshu workflow from `../../SKILL.md`, with these Trae-specific
rules. This file is intentionally named `SKILL.md` so Trae and other skill
loaders can discover the adapter as an executable instruction layer, not only
as README documentation.

## Startup Checklist

1. Confirm the active project root. Yunshu state belongs in the user's project
   `.yunshu/`, never inside `.trae/skills/yunshu-system-skill/.yunshu/`.
2. Prefer the installed-copy CLI from the project root:
   `python .trae/skills/yunshu-system-skill/scripts/yunshu.py --root . <command>`.
3. If working from the source package itself, use:
   `python scripts/yunshu.py --root <project-root> <command>`.
4. Check `.yunshu/context/index.json` and `.yunshu/checkpoints/index.json`
   before rereading large context.
5. If an installed skill copy contains `.yunshu/`, treat it as stale package
   pollution and resync with `scripts/sync-trae.ps1 -Apply`.

## Tool Mapping

| Yunshu capability | Trae IDE implementation |
|---|---|
| User choice / confirmation | Use `AskUserQuestion` with 2-4 concrete options. |
| File or symbol context | Use Trae file references and explicit project-root relative paths. |
| Subagent execution | Use the three Yunshu agents from `agents/*/AGENT.md` after setup. |
| Checkpoint state | Use the installed-copy CLI with `--root .` so state lands in the project. |
| Context ledger | Record with `context record` after investigation and before phase transitions. |
| Evidence log | Use `verify run`; do not claim evidence without a created log or artifact. |

## Trae Rules

- Do not run `python scripts/yunshu.py ...` from a normal project root unless
  that project actually has a root-level `scripts/yunshu.py`.
- Do not store task checkpoints, context ledgers, gates, or verification logs
  under the skill installation directory.
- Do not skip transition gates. Required artifacts must be real files with
  content, not placeholder paths.
- If `AskUserQuestion` is unavailable, ask one concise question and record the
  fallback in the context ledger or checkpoint.
- Before using subagents, make sure `yunshu-implementer`,
  `yunshu-spec-reviewer`, and `yunshu-quality-reviewer` were created from the
  prompts in `agents/`.

