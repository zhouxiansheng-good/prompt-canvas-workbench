# Project Context

## Technology Stack & Versions

- Python 3.10+ compatible standard library only.
- No third-party runtime dependency for `scripts/yunshu.py`.

## Critical Implementation Rules

- CLI commands must be zero-dependency.
- Verification logs are append-only audit records.
- New CLI behavior requires tests in `tests/test_yunshu_cli.py`.

## Testing

- Use `python -m pytest tests`.
- Keep fixtures inside temporary directories.
