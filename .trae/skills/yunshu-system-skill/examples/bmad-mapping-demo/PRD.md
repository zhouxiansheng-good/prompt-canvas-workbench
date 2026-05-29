# PRD: CLI Evidence Dashboard

## Problem Statement

Yunshu users can record verification evidence, but they need a small dashboard command to summarize recent evidence without opening TSV files manually.

## Product Goal

Provide a read-only CLI summary of recent verification evidence.

## Users

- Developers running Yunshu locally.
- Reviewers checking whether a task has fresh evidence.

## Acceptance Criteria

- The command prints the latest verification claims with status and evidence path.
- The command never modifies verification logs.
- The command handles an empty verification log with a clear message.

## Out of Scope

- Web UI.
- Editing evidence records.
- Remote artifact upload.

## Open Questions

- How many recent records should be shown by default?
