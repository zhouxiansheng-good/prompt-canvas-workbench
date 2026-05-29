# Story: Summarize Verification Evidence

## User Story

As a Yunshu reviewer, I want a CLI command that lists recent verification evidence so I can check delivery readiness quickly.

## Acceptance Criteria

- Given three verification rows, the command prints the newest rows first.
- Given no verification log, the command prints a clear empty-state message.
- Given `--limit 0`, the command fails with an invalid argument error.

## Dev Notes

- Reuse existing `.yunshu/verify-log.tsv` format.
- Do not modify `verify run`.
- Keep the feature read-only.

## Tasks

- Add evidence summary command.
- Add parser tests.
- Update README command list.
