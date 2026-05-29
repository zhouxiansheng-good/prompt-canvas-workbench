# Trae IDE Adapter

This adapter makes the Yunshu core workflow explicit for Trae IDE. The core
skill stays platform-neutral; this directory documents how Trae-specific
interaction, agents, and local state should be wired.

## Install

Copy the whole skill directory into the project skill folder:

```text
<project>/.trae/skills/yunshu-system-skill/
```

Keep the copied package byte-for-byte aligned with the source package. Before
copying a release, run:

```powershell
python scripts/yunshu.py --root . version-check
python scripts/yunshu.py --root . audit links
```

When Trae is using Yunshu as an installed project skill, run the CLI from the
project root through the installed copy:

```powershell
python .trae/skills/yunshu-system-skill/scripts/yunshu.py --root . init
python .trae/skills/yunshu-system-skill/scripts/yunshu.py --root . context record --task-id demo --phase init --source README.md --finding "已了解项目入口"
python .trae/skills/yunshu-system-skill/scripts/yunshu.py --root . gate transition --task-id demo --from-phase init --to-phase plan --user-aligned --dod-confirmed --task-card .yunshu/context/<context_id>.json
```

Do not use `python scripts/yunshu.py ...` from an ordinary Trae project root
unless that project has its own root-level `scripts/yunshu.py`. Otherwise the
command fails or writes state into the wrong package directory.

## Interaction Mapping

| Yunshu capability | Trae IDE implementation |
|---|---|
| User choice / confirmation | Use `AskUserQuestion` with 2-4 concrete options. |
| File or symbol context | Use Trae file references and keep paths explicit. |
| Subagent execution | Create the three Yunshu agents from `agents/*/AGENT.md`. |
| Checkpoint state | Use `python .trae/skills/yunshu-system-skill/scripts/yunshu.py --root . checkpoint ...` inside the project. |
| Evidence log | Use `python .trae/skills/yunshu-system-skill/scripts/yunshu.py --root . verify run ...` to append `.yunshu/verify-log.tsv`. |

If a Trae tool is unavailable in a specific environment, fall back to a concise
plain-language question and record the limitation in the checkpoint or change
report. Do not pretend the unavailable tool ran.

## Agent Setup

Create these Trae IDE agents manually or via any future Trae import mechanism:

| Agent name | Source prompt |
|---|---|
| `yunshu-implementer` | `agents/yunshu-implementer/AGENT.md` |
| `yunshu-spec-reviewer` | `agents/yunshu-spec-reviewer/AGENT.md` |
| `yunshu-quality-reviewer` | `agents/yunshu-quality-reviewer/AGENT.md` |

Recommended tool permissions are documented in `skill-config.example.json`.
Use the smallest tool set that can complete the assigned role.

## Release Sync Checklist

1. Update `VERSION`, `SKILL.md`, and `README.md` together.
2. Run `python scripts/yunshu.py --root . version-check`.
3. Run `python scripts/yunshu.py --root . audit links`.
4. Preview copy with `powershell -ExecutionPolicy Bypass -File scripts/sync-trae.ps1`.
5. Apply copy with `powershell -ExecutionPolicy Bypass -File scripts/sync-trae.ps1 -Apply`.
6. Copy the package to `.trae/skills/yunshu-system-skill` only from the verified source package.
7. Run the same checks inside the copied Trae package.
8. Ensure `.trae/skills/yunshu-system-skill/.yunshu/` does not exist after sync.
9. Create a checkpoint noting source commit, copied path, and verification logs.
