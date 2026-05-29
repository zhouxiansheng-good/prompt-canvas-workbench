# Claude Code Adapter

This directory documents how Yunshu can be installed into Claude Code style
environments that support skills, subagents, and hooks.

## Suggested Layout

```text
.claude/
  agents/
    yunshu-implementer.md
    yunshu-spec-reviewer.md
    yunshu-quality-reviewer.md
  settings.json
```

## Mapping

| Yunshu capability | Claude Code concept |
|---|---|
| Core workflow | Skill `SKILL.md` |
| Role agents | Subagents under `.claude/agents/` |
| Checkpoint before compaction | PreCompact hook invoking `scripts/yunshu.py checkpoint create` |
| Post-tool evidence | PostToolUse hook invoking `scripts/yunshu.py verify run` when appropriate |
| Session resume | SessionStart hook listing recent checkpoints |

## Minimal Hook Candidates

- `PreCompact`: create or refresh a checkpoint.
- `SubagentStop`: require spec review before quality review.
- `SessionStart`: print latest checkpoint ids.

This adapter is intentionally documentation-only until the concrete host
project decides which hooks are safe to enable.
