# Codex Automation Notes

The Yunshu package currently ships a local CLI, not a Codex MCP server. Do not
claim that `workflow_codex_*` tools exist unless they are actually registered in
the active environment.

Recommended future Codex automation:

- Wrap `scripts/yunshu.py checkpoint create/list/resume` as MCP tools.
- Wrap `scripts/yunshu.py verify run` as a verification logger.
- Add a pre-delivery automation that runs `version-check`, `audit links`, and
  evidence validation.
- Add a session-start hook that surfaces the latest checkpoint when present.
