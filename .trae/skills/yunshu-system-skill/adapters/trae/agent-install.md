# Trae Agent Install Guide

## Required Agents

### yunshu-implementer

- Prompt: `agents/yunshu-implementer/AGENT.md`
- Role: implement bounded tasks, write tests, self-verify, and report changed
  files plus evidence.
- Suggested tools: file read/write, terminal, test runner, search.

### yunshu-spec-reviewer

- Prompt: `agents/yunshu-spec-reviewer/AGENT.md`
- Role: verify whether implementation matches the approved spec and DoD.
- Suggested tools: file read, search, terminal read-only verification commands.

### yunshu-quality-reviewer

- Prompt: `agents/yunshu-quality-reviewer/AGENT.md`
- Role: review maintainability, safety, regression risk, and evidence quality.
- Suggested tools: file read, search, terminal read-only verification commands.

## Dispatch Discipline

- Implementers may run in parallel only when write scopes are disjoint.
- Spec review must pass before quality review starts.
- Any reviewer finding must be fixed and reviewed again.
- If an agent asks for missing context, the controller supplies only the minimum
  needed context and records the exchange in the checkpoint.

## Trae-Specific Notes

- Keep agent prompts in Chinese by default to match the Yunshu package.
- Prefer explicit absolute or project-relative paths in every assignment.
- Store long-running handoffs under `.yunshu/checkpoints/<checkpoint_id>/`.
- Do not rely on conversation memory as the source of truth after a checkpoint;
  use `phase_memory.json` and `checkpoint.json`.
