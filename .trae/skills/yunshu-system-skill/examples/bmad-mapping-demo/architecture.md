# Architecture: CLI Evidence Dashboard

## Components

### Evidence Reader

Reads `.yunshu/verify-log.tsv` and parses tab-separated rows.

### Summary Renderer

Formats recent rows for terminal output.

## Interfaces

### Command

`python scripts/yunshu.py evidence summary --limit <n>`

Input:

- `--limit`: positive integer, default 5.

Output:

- status, claim, evidence path for each row.

Errors:

- Missing log prints an empty-state message and exits 0.
- Invalid limit exits 2.

## Decisions

### ADR-001: Keep the dashboard read-only

**Decision**: The command reads verification logs but does not rewrite or normalize them.

**Reason**: Evidence logs are audit records and should remain append-only.

## Testing

- Unit test empty log.
- Unit test recent row rendering.
- Unit test invalid limit.
