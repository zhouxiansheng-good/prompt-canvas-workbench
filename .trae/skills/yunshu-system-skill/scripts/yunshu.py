#!/usr/bin/env python3
"""Small executable layer for the Yunshu workflow skill.

The script intentionally has no third-party dependencies so it can run inside
Trae, Codex, CI jobs, and constrained project workspaces.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import locale
import os
import re
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


PHASES = {"init", "plan", "execute", "subagent", "accept", "deliver", "recover"}
STATUS = {"passed", "failed", "inconclusive"}
LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
BMAD_KINDS = {"prd", "architecture", "story", "project-context"}
BMAD_PHASE = {
    "prd": "plan",
    "architecture": "plan",
    "story": "execute",
    "project-context": "plan",
}
ALLOWED_TRANSITIONS = {
    "init": {"plan"},
    "plan": {"execute", "subagent"},
    "execute": {"accept"},
    "subagent": {"accept"},
    "accept": {"deliver"},
    "recover": {"init", "plan", "execute", "subagent", "accept", "deliver"},
}
MAX_PRELOAD_CONTEXTS = 5


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slug(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-")
    return cleaned or "task"


def split_items(values: Iterable[str] | None) -> list[str]:
    items: list[str] = []
    for value in values or []:
        for part in re.split(r"\s*;\s*", value):
            if part.strip():
                items.append(part.strip())
    return items


def find_root(root_arg: str | None) -> Path:
    if root_arg:
        return Path(root_arg).resolve()
    current = Path.cwd().resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "SKILL.md").exists() and (candidate / "components").is_dir():
            return candidate
    return current


def ensure_state(root: Path) -> Path:
    state = root / ".yunshu"
    (state / "checkpoints").mkdir(parents=True, exist_ok=True)
    (state / "context").mkdir(parents=True, exist_ok=True)
    (state / "verification").mkdir(parents=True, exist_ok=True)
    (state / "memory").mkdir(parents=True, exist_ok=True)
    (state / "tasks").mkdir(parents=True, exist_ok=True)
    (state / "gates").mkdir(parents=True, exist_ok=True)
    return state


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def decode_process_output(data: bytes) -> str:
    """Decode command output without letting platform code pages hide evidence."""
    if not data:
        return ""
    encodings = ["utf-8", locale.getpreferredencoding(False), sys.getdefaultencoding()]
    tried: set[str] = set()
    for encoding in encodings:
        normalized = encoding.lower()
        if normalized in tried:
            continue
        tried.add(normalized)
        try:
            return data.decode(encoding)
        except (LookupError, UnicodeDecodeError):
            continue
    return data.decode("utf-8", errors="replace")


def run_command(command: str, root: Path) -> tuple[int, str, str]:
    try:
        result = subprocess.run(command, shell=True, cwd=root, capture_output=True)
    except OSError as exc:
        return 1, "", f"{type(exc).__name__}: {exc}\n"
    return result.returncode, decode_process_output(result.stdout), decode_process_output(result.stderr)


def load_index(state: Path) -> dict[str, Any]:
    index_path = state / "checkpoints" / "index.json"
    if not index_path.exists():
        return {"checkpoints": []}
    return read_json(index_path)


def save_index(state: Path, index: dict[str, Any]) -> None:
    write_json(state / "checkpoints" / "index.json", index)


def context_index_path(state: Path) -> Path:
    return state / "context" / "index.json"


def context_entry_path(state: Path, context_id: str) -> Path:
    return state / "context" / f"{context_id}.json"


def load_context_index(state: Path) -> dict[str, Any]:
    path = context_index_path(state)
    if not path.exists():
        return {"contexts": []}
    return read_json(path)


def context_entry_matches(root: Path, state: Path, entry: dict[str, Any], query: str | None) -> bool:
    if not query or not query.strip():
        return True
    context_id = entry.get("context_id")
    if not isinstance(context_id, str):
        return False
    path = context_entry_path(state, context_id)
    tokens = [part.lower() for part in re.split(r"\s+", query.strip()) if part.strip()]
    if not tokens:
        return True
    chunks = [str(entry.get(key, "")) for key in ["context_id", "task_id", "phase", "updated_at", "path"]]
    if path.exists():
        try:
            data = read_json(path)
        except (json.JSONDecodeError, ValueError):
            data = {}
        for key in ["findings", "actions", "decisions", "gaps", "next_read"]:
            value = data.get(key, [])
            if isinstance(value, list):
                chunks.extend(str(item) for item in value)
        for source in data.get("sources", []):
            if isinstance(source, dict):
                chunks.append(str(source.get("path", "")))
    text = " ".join(chunks).lower()
    return all(token in text for token in tokens)


def selected_context_entries(
    root: Path,
    state: Path,
    *,
    task_id: str | None = None,
    query: str | None = None,
    limit: int = 3,
    checkpoint_id: str | None = None,
) -> list[dict[str, Any]]:
    contexts = load_context_index(state).get("contexts", [])
    if checkpoint_id:
        checkpoint_dir = state / "checkpoints" / checkpoint_id
        context_ids: list[str] = []
        for filename in ["phase_memory.json", "checkpoint.json"]:
            path = checkpoint_dir / filename
            if path.exists():
                data = read_json(path)
                for context_id in data.get("context_records", []):
                    if isinstance(context_id, str) and context_id not in context_ids:
                        context_ids.append(context_id)
                ledger = data.get("context_ledger")
                if isinstance(ledger, str) and ledger:
                    ledger_id = Path(ledger).stem
                    if ledger_id not in context_ids:
                        context_ids.append(ledger_id)
        if context_ids:
            by_id = {entry.get("context_id"): entry for entry in contexts}
            contexts = [by_id[context_id] for context_id in context_ids if context_id in by_id]
        else:
            return []
    if task_id:
        normalized_task_id = slug(task_id)
        contexts = [entry for entry in contexts if entry.get("task_id") == normalized_task_id]
    contexts = [entry for entry in contexts if context_entry_matches(root, state, entry, query)]
    bounded_limit = max(1, min(limit, MAX_PRELOAD_CONTEXTS))
    return contexts[:bounded_limit]


def source_requiring_refresh(freshness_line: str) -> str | None:
    for suffix in [": stale", ": missing", ": present, no prior digest"]:
        if freshness_line.endswith(suffix):
            return freshness_line[: -len(suffix)]
    return None


def has_freshness_problem(freshness: list[str]) -> bool:
    return any(source_requiring_refresh(item) for item in freshness)


def save_context_index(state: Path, index: dict[str, Any]) -> None:
    write_json(context_index_path(state), index)


def bmad_index_path(state: Path) -> Path:
    return state / "bmad" / "index.json"


def bmad_entry_path(state: Path, map_id: str) -> Path:
    return state / "bmad" / f"{map_id}.json"


def load_bmad_index(state: Path) -> dict[str, Any]:
    path = bmad_index_path(state)
    if not path.exists():
        return {"mappings": []}
    return read_json(path)


def save_bmad_index(state: Path, index: dict[str, Any]) -> None:
    write_json(bmad_index_path(state), index)


def relative_posix(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def context_source(root: Path, value: str) -> dict[str, Any]:
    source = value.strip()
    item: dict[str, Any] = {"path": source}
    if looks_like_local_path(source):
        path = resolve_evidence_path(root, source)
        if path.exists() and path.is_file():
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            item.update(
                {
                    "exists": True,
                    "sha256": digest,
                    "size": path.stat().st_size,
                    "modified_at": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
                    .replace(microsecond=0)
                    .isoformat()
                    .replace("+00:00", "Z"),
                }
            )
        elif path.exists() and path.is_dir():
            children = "\n".join(sorted(child.name for child in path.iterdir()))
            digest = hashlib.sha256(children.encode("utf-8")).hexdigest()
            item.update(
                {
                    "exists": True,
                    "kind": "directory",
                    "sha256": digest,
                    "size": len(children),
                    "modified_at": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
                    .replace(microsecond=0)
                    .isoformat()
                    .replace("+00:00", "Z"),
                }
            )
        else:
            item["exists"] = False
    return item


def save_context_record(
    root: Path,
    state: Path,
    *,
    task_id: str,
    phase: str,
    context_id: str,
    sources: list[dict[str, Any]],
    findings: list[str] | None = None,
    actions: list[str] | None = None,
    decisions: list[str] | None = None,
    gaps: list[str] | None = None,
    next_read: list[str] | None = None,
    created_at: str | None = None,
    associated_checkpoints: list[str] | None = None,
) -> tuple[Path, Path]:
    data = {
        "task_id": task_id,
        "context_id": context_id,
        "phase": phase,
        "created_at": created_at or utc_now(),
        "updated_at": utc_now(),
        "sources": sources,
        "findings": findings or [],
        "actions": actions or [],
        "decisions": decisions or [],
        "gaps": gaps or [],
        "next_read": next_read or [],
        "associated_checkpoints": associated_checkpoints or [],
    }
    path = context_entry_path(state, context_id)
    write_json(path, data)
    freshness = context_freshness(root, data)
    markdown_path = state / "context" / f"{context_id}.md"
    markdown_path.write_text(render_context_markdown(data, freshness), encoding="utf-8", newline="\n")
    index = load_context_index(state)
    entries = [entry for entry in index.get("contexts", []) if entry.get("context_id") != context_id]
    entries.append(
        {
            "context_id": context_id,
            "task_id": task_id,
            "phase": phase,
            "updated_at": data["updated_at"],
            "path": relative_posix(path, root),
        }
    )
    index["contexts"] = sorted(entries, key=lambda item: item["updated_at"], reverse=True)
    save_context_index(state, index)
    return path, markdown_path


def render_context_markdown(data: dict[str, Any], freshness: list[str]) -> str:
    def lines(items: list[str] | None) -> str:
        return "\n".join(f"- {item}" for item in items or []) or "- (none)"

    sources = "\n".join(
        f"- {item.get('path')} — sha256={item.get('sha256', 'n/a')} exists={item.get('exists', 'external/unknown')}"
        for item in data.get("sources", [])
    ) or "- (none)"
    associated = "\n".join(f"- {cp}" for cp in data.get("associated_checkpoints", [])) or "- (none)"
    return f"""# Yunshu Context: {data['context_id']}

- task_id: {data['task_id']}
- phase: {data['phase']}
- created_at: {data['created_at']}
- updated_at: {data.get('updated_at', data['created_at'])}

## Sources

{sources}

## Findings

{lines(data.get('findings'))}

## Actions

{lines(data.get('actions'))}

## Decisions

{lines(data.get('decisions'))}

## Gaps

{lines(data.get('gaps'))}

## Next Read

{lines(data.get('next_read'))}

## Associated Checkpoints

{associated}

## Freshness

{lines(freshness)}
"""


def extract_markdown_headings(root: Path, source: str) -> list[str]:
    if not looks_like_local_path(source):
        return []
    path = resolve_evidence_path(root, source)
    if not path.exists() or not path.is_file():
        return []
    headings: list[str] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if match:
            headings.append(f"{len(match.group(1))}:{match.group(2).strip()}")
    return headings


def render_bmad_markdown(data: dict[str, Any], freshness: list[str]) -> str:
    def lines(items: list[str] | None) -> str:
        return "\n".join(f"- {item}" for item in items or []) or "- (none)"

    sections = []
    for section in data.get("sections", []):
        headings = lines(section.get("headings") or [])
        sections.append(f"### {section.get('path')}\n\n{headings}")
    section_text = "\n\n".join(sections) or "- (none)"
    return f"""# BMad Mapping: {data['map_id']}

- task_id: {data['task_id']}
- kind: {data['kind']}
- created_at: {data['created_at']}
- updated_at: {data['updated_at']}

## Sources

{lines([item.get('path', '') for item in data.get('sources', [])])}

## Sections

{section_text}

## Gaps

{lines(data.get('gaps'))}

## Freshness

{lines(freshness)}
"""


def context_freshness(root: Path, data: dict[str, Any]) -> list[str]:
    results: list[str] = []
    for source in data.get("sources", []):
        path_value = source.get("path")
        if not isinstance(path_value, str):
            continue
        if not looks_like_local_path(path_value):
            results.append(f"{path_value}: external or non-local source, freshness not checked")
            continue
        path = resolve_evidence_path(root, path_value)
        old_digest = source.get("sha256")
        if not path.exists():
            results.append(f"{path_value}: missing")
        elif not old_digest:
            results.append(f"{path_value}: present, no prior digest")
        else:
            if path.is_dir():
                children = "\n".join(sorted(child.name for child in path.iterdir()))
                current_digest = hashlib.sha256(children.encode("utf-8")).hexdigest()
            else:
                current_digest = hashlib.sha256(path.read_bytes()).hexdigest()
            status = "fresh" if current_digest == old_digest else "stale"
            results.append(f"{path_value}: {status}")
    return results


def render_handoff(checkpoint: dict[str, Any], phase_memory: dict[str, Any]) -> str:
    completed = "\n".join(f"- {item}" for item in checkpoint["completed"]) or "- (none)"
    pending = "\n".join(f"- {item}" for item in checkpoint["pending"]) or "- (none)"
    artifacts = "\n".join(f"- {item}" for item in checkpoint["artifacts"]) or "- (none)"
    decisions = "\n".join(f"- {item}" for item in checkpoint.get("decisions", [])) or "- (none)"
    risks = "\n".join(f"- {item}" for item in checkpoint.get("risks", [])) or "- (none)"
    context_ledger = checkpoint.get("context_ledger") or phase_memory.get("context_ledger") or "(none)"
    gate_status = checkpoint.get("gate_status", "not-checked")
    return f"""# Yunshu Handoff: {checkpoint['checkpoint_id']}

- task_id: {checkpoint['task_id']}
- checkpoint_id: {checkpoint['checkpoint_id']}
- phase: {checkpoint['phase']}
- created_at: {checkpoint['created_at']}
- gate_status: {gate_status}

## Summary

{checkpoint.get('summary') or '(none)'}

## Completed

{completed}

## Pending

{pending}

## Decisions

{decisions}

## Artifacts

{artifacts}

## Risks

{risks}

## Context Ledger

{context_ledger}

## Next Action

{checkpoint.get('next_action') or phase_memory.get('next_action') or '(none)'}

## Resume Prompt

使用云舒系统，从 checkpoint_id={checkpoint['checkpoint_id']} 恢复继续执行；以 phase_memory 为唯一历史事实来源。
"""


def cmd_init(args: argparse.Namespace) -> int:
    root = find_root(args.root)
    state = ensure_state(root)
    print(f"Yunshu state initialized: {state}")
    return 0


def cmd_checkpoint_create(args: argparse.Namespace) -> int:
    root = find_root(args.root)
    state = ensure_state(root)
    task_id = slug(args.task_id)
    phase = args.phase
    if phase not in PHASES:
        print(f"Invalid phase: {phase}", file=sys.stderr)
        return 2
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    checkpoint_id = f"{task_id}-{phase}-{stamp}"
    checkpoint_dir = state / "checkpoints" / checkpoint_id
    completed = split_items(args.completed)
    pending = split_items(args.pending)
    artifacts = split_items(args.artifact)
    decisions = split_items(args.decision)
    risks = split_items(args.risk)
    context_entries = [
        entry
        for entry in load_context_index(state).get("contexts", [])
        if entry.get("task_id") == task_id
    ]
    latest_context = context_entries[0] if context_entries else None
    checkpoint = {
        "task_id": task_id,
        "checkpoint_id": checkpoint_id,
        "phase": phase,
        "created_at": utc_now(),
        "summary": args.summary or "",
        "completed": completed,
        "pending": pending,
        "decisions": decisions,
        "artifacts": artifacts,
        "risks": risks,
        "next_action": args.next_action or "",
    }
    if latest_context:
        checkpoint["context_ledger"] = latest_context.get("path")
        checkpoint["context_records"] = [entry.get("context_id", "") for entry in context_entries if entry.get("context_id")]
    checkpoint["gate_status"] = args.gate_status or "not-checked"
    phase_memory = {
        "task_id": task_id,
        "checkpoint_id": checkpoint_id,
        "phase": phase,
        "created_at": checkpoint["created_at"],
        "progress_summary": checkpoint["summary"],
        "completed": completed,
        "pending": pending,
        "key_decisions": decisions,
        "critical_artifacts": artifacts,
        "known_risks": risks,
        "next_action": checkpoint["next_action"],
        "gate_status": checkpoint["gate_status"],
    }
    if latest_context:
        phase_memory["context_ledger"] = latest_context.get("path")
        phase_memory["context_records"] = checkpoint.get("context_records", [])
    write_json(checkpoint_dir / "checkpoint.json", checkpoint)
    write_json(checkpoint_dir / "phase_memory.json", phase_memory)
    handoff = render_handoff(checkpoint, phase_memory)
    (checkpoint_dir / "handoff.md").write_text(handoff, encoding="utf-8", newline="\n")
    index = load_index(state)
    entries = [entry for entry in index.get("checkpoints", []) if entry.get("checkpoint_id") != checkpoint_id]
    entries.append(
        {
            "checkpoint_id": checkpoint_id,
            "task_id": task_id,
            "phase": phase,
            "created_at": checkpoint["created_at"],
            "path": relative_posix(checkpoint_dir, root),
        }
    )
    index["checkpoints"] = sorted(entries, key=lambda item: item["created_at"], reverse=True)
    save_index(state, index)
    print(f"Created checkpoint: {checkpoint_id}")
    print(f"Path: {checkpoint_dir}")
    return 0


def cmd_checkpoint_list(args: argparse.Namespace) -> int:
    root = find_root(args.root)
    state = ensure_state(root)
    checkpoints = load_index(state).get("checkpoints", [])
    if args.task_id:
        task_id = slug(args.task_id)
        checkpoints = [item for item in checkpoints if item.get("task_id") == task_id]
    if not checkpoints:
        print("No checkpoints found.")
        return 0
    for item in checkpoints:
        print(f"{item['created_at']}  {item['checkpoint_id']}  {item['phase']}  {item['path']}")
    return 0


def cmd_checkpoint_resume(args: argparse.Namespace) -> int:
    root = find_root(args.root)
    state = ensure_state(root)
    checkpoint_dir = state / "checkpoints" / args.checkpoint_id
    checkpoint_path = checkpoint_dir / "checkpoint.json"
    phase_memory_path = checkpoint_dir / "phase_memory.json"
    if not checkpoint_path.exists() or not phase_memory_path.exists():
        print(f"Checkpoint not found or incomplete: {args.checkpoint_id}", file=sys.stderr)
        return 1
    checkpoint = read_json(checkpoint_path)
    print(f"checkpoint_id: {checkpoint['checkpoint_id']}")
    print(f"phase: {checkpoint['phase']}")
    print(f"checkpoint: {checkpoint_path}")
    print(f"phase_memory: {phase_memory_path}")
    print()
    print(f"使用云舒系统，从 checkpoint_id={checkpoint['checkpoint_id']} 恢复继续执行；以 phase_memory 为唯一历史事实来源。")
    return 0


def cmd_context_record(args: argparse.Namespace) -> int:
    root = find_root(args.root)
    state = ensure_state(root)
    task_id = slug(args.task_id)
    phase = args.phase
    if phase not in PHASES:
        print(f"Invalid phase: {phase}", file=sys.stderr)
        return 2
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    context_id = args.context_id or f"{task_id}-{phase}-{stamp}"
    context_id = slug(context_id)
    path = context_entry_path(state, context_id)
    if path.exists():
        data = read_json(path)
        created_at = data.get("created_at") or utc_now()
        sources = data.get("sources", [])
        findings = data.get("findings", [])
        actions = data.get("actions", [])
        decisions = data.get("decisions", [])
        gaps = data.get("gaps", [])
        next_read = data.get("next_read", [])
    else:
        created_at = utc_now()
        sources = []
        findings = []
        actions = []
        decisions = []
        gaps = []
        next_read = []
    sources.extend(context_source(root, item) for item in args.source or [])
    findings.extend(split_items(args.finding))
    actions.extend(split_items(args.action))
    decisions.extend(split_items(args.decision))
    gaps.extend(split_items(args.gap))
    next_read.extend(split_items(args.next_read))
    associated_checkpoints = []
    if args.associated_checkpoint:
        associated_checkpoints.extend(split_items(args.associated_checkpoint))
    path, markdown_path = save_context_record(
        root,
        state,
        task_id=task_id,
        phase=phase,
        context_id=context_id,
        sources=sources,
        findings=findings,
        actions=actions,
        decisions=decisions,
        gaps=gaps,
        next_read=next_read,
        created_at=created_at,
        associated_checkpoints=associated_checkpoints,
    )
    print(f"Recorded context: {context_id}")
    print(f"JSON: {path}")
    print(f"Markdown: {markdown_path}")
    return 0


def cmd_context_show(args: argparse.Namespace) -> int:
    root = find_root(args.root)
    state = ensure_state(root)
    index = load_context_index(state)
    contexts = index.get("contexts", [])
    if not contexts:
        print("No context records found.")
        return 0
    context_id = args.context_id or contexts[0].get("context_id")
    path = context_entry_path(state, context_id)
    if not path.exists():
        print(f"Context not found: {context_id}", file=sys.stderr)
        return 1
    data = read_json(path)
    freshness = context_freshness(root, data)
    print(f"context_id: {data['context_id']}")
    print(f"task_id: {data['task_id']}")
    print(f"phase: {data['phase']}")
    print(f"updated_at: {data.get('updated_at', data.get('created_at', ''))}")
    print(f"context: {path}")
    print()
    print("Freshness:")
    for item in freshness or ["(none)"]:
        print(f"- {item}")
    print()
    print("Findings:")
    for item in data.get("findings") or ["(none)"]:
        print(f"- {item}")
    print()
    print("Gaps:")
    for item in data.get("gaps") or ["(none)"]:
        print(f"- {item}")
    print()
    print("Next read:")
    for item in data.get("next_read") or ["(none)"]:
        print(f"- {item}")
    return 0


def cmd_context_list(args: argparse.Namespace) -> int:
    root = find_root(args.root)
    state = ensure_state(root)
    contexts = load_context_index(state).get("contexts", [])
    if args.task_id:
        task_id = slug(args.task_id)
        contexts = [item for item in contexts if item.get("task_id") == task_id]
    if not contexts:
        print("No context records found.")
        return 0
    for item in contexts:
        print(f"{item['updated_at']}  {item['context_id']}  {item['phase']}  {item['path']}")
    return 0


def cmd_context_preload(args: argparse.Namespace) -> int:
    root = find_root(args.root)
    state = ensure_state(root)
    selected = selected_context_entries(
        root,
        state,
        task_id=args.task_id,
        query=args.query,
        limit=args.limit,
        checkpoint_id=args.checkpoint_id,
    )
    if not selected:
        print("No matching context records found.")
        print("Action: run 01-init investigation, then record a new context ledger.")
        return 1
    should_refresh = False
    print(f"Selected {len(selected)} context record(s). Read these before any full repository scan.")
    for entry in selected:
        context_id = entry.get("context_id", "")
        path = context_entry_path(state, context_id)
        if not path.exists():
            print()
            print(f"Context: {context_id}")
            print("Status: missing context file")
            should_refresh = True
            continue
        data = read_json(path)
        freshness = context_freshness(root, data)
        refresh_sources = [source for source in (source_requiring_refresh(item) for item in freshness) if source]
        should_refresh = should_refresh or bool(refresh_sources)
        print()
        print(f"Context: {context_id}")
        print(f"Task: {data.get('task_id', '')}")
        print(f"Phase: {data.get('phase', '')}")
        print(f"Updated: {data.get('updated_at', data.get('created_at', ''))}")
        print(f"Path: {path}")
        print("Findings:")
        for item in data.get("findings") or ["(none)"]:
            print(f"- {item}")
        print("Gaps:")
        for item in data.get("gaps") or ["(none)"]:
            print(f"- {item}")
        print("Next read:")
        for item in data.get("next_read") or ["(none)"]:
            print(f"- {item}")
        if refresh_sources:
            print("Refresh required:")
            for item in refresh_sources:
                print(f"- {item}")
        else:
            print("Refresh required: none; reuse ledger conclusions unless the current request adds new scope.")
    print()
    if should_refresh:
        print("Decision: preload found stale/missing sources. Re-read only the listed sources plus any new user-scope files.")
        return 2
    print("Decision: preload is fresh. Do not reread full history; load only new or uncovered sources.")
    return 0


def cmd_context_status(args: argparse.Namespace) -> int:
    root = find_root(args.root)
    state = ensure_state(root)
    index = load_context_index(state)
    contexts = index.get("contexts", [])
    context_id = args.context_id or (contexts[0].get("context_id") if contexts else None)
    if not context_id:
        print("No context records found.")
        return 0
    path = context_entry_path(state, context_id)
    if not path.exists():
        print(f"Context not found: {context_id}", file=sys.stderr)
        return 1
    freshness = context_freshness(root, read_json(path))
    has_problem = False
    for item in freshness or ["(none)"]:
        print(item)
        if item.endswith(": stale") or item.endswith(": missing"):
            has_problem = True
    return 1 if has_problem else 0


def validate_bmad_mapping(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ["task_id", "map_id", "kind", "created_at", "updated_at", "sources", "sections", "gaps"]
    for key in required:
        if key not in data:
            errors.append(f"missing required field: {key}")
    for key in ["task_id", "map_id"]:
        if key in data:
            validate_non_empty_string(data, key, errors)
    if data.get("kind") not in BMAD_KINDS:
        errors.append("kind must be one of: " + ", ".join(sorted(BMAD_KINDS)))
    for key in ["created_at", "updated_at"]:
        if key in data:
            validate_datetime_string(data, key, errors)
    sources = data.get("sources")
    if not isinstance(sources, list) or not sources:
        errors.append("sources must be a non-empty array")
    else:
        for index, item in enumerate(sources, start=1):
            if not isinstance(item, dict):
                errors.append(f"sources[{index}] must be an object")
                continue
            if not isinstance(item.get("path"), str) or not item["path"].strip():
                errors.append(f"sources[{index}].path must be a non-empty string")
            digest = item.get("sha256")
            if digest is not None and (not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest)):
                errors.append(f"sources[{index}].sha256 must be a hex sha256 digest")
    sections = data.get("sections")
    if not isinstance(sections, list):
        errors.append("sections must be an array")
    else:
        for index, item in enumerate(sections, start=1):
            if not isinstance(item, dict):
                errors.append(f"sections[{index}] must be an object")
                continue
            if not isinstance(item.get("path"), str) or not item["path"].strip():
                errors.append(f"sections[{index}].path must be a non-empty string")
            headings = item.get("headings")
            if not isinstance(headings, list):
                errors.append(f"sections[{index}].headings must be an array")
            else:
                for heading_index, heading in enumerate(headings, start=1):
                    if not isinstance(heading, str) or not heading.strip():
                        errors.append(f"sections[{index}].headings[{heading_index}] must be a non-empty string")
    if "context_id" in data and (not isinstance(data["context_id"], str) or not data["context_id"].strip()):
        errors.append("context_id must be a non-empty string")
    for key in ["gaps", "next_read"]:
        if key in data:
            validate_string_array(data, key, errors)
    return errors


def cmd_bmad_map(args: argparse.Namespace) -> int:
    root = find_root(args.root)
    state = ensure_state(root)
    task_id = slug(args.task_id)
    kind = args.kind
    if kind not in BMAD_KINDS:
        print(f"Invalid kind: {kind}", file=sys.stderr)
        return 2
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    map_id = slug(args.map_id or f"{task_id}-{kind}-{stamp}")
    sources = [context_source(root, item) for item in args.source]
    sections = [{"path": item, "headings": extract_markdown_headings(root, item)} for item in args.source]
    context_id = slug(args.context_id or f"{map_id}-context")
    gaps = split_items(args.gap)
    next_read = split_items(args.next_read) or list(args.source)
    data = {
        "task_id": task_id,
        "map_id": map_id,
        "kind": kind,
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "sources": sources,
        "sections": sections,
        "gaps": gaps,
        "next_read": next_read,
        "context_id": context_id,
    }
    errors = validate_bmad_mapping(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    path = bmad_entry_path(state, map_id)
    write_json(path, data)
    freshness = context_freshness(root, data)
    markdown_path = state / "bmad" / f"{map_id}.md"
    markdown_path.write_text(render_bmad_markdown(data, freshness), encoding="utf-8", newline="\n")
    index = load_bmad_index(state)
    entries = [entry for entry in index.get("mappings", []) if entry.get("map_id") != map_id]
    entries.append(
        {
            "map_id": map_id,
            "task_id": task_id,
            "kind": kind,
            "updated_at": data["updated_at"],
            "path": relative_posix(path, root),
        }
    )
    index["mappings"] = sorted(entries, key=lambda item: item["updated_at"], reverse=True)
    save_bmad_index(state, index)
    phase = BMAD_PHASE[kind]
    context_path, context_markdown_path = save_context_record(
        root,
        state,
        task_id=task_id,
        phase=phase,
        context_id=context_id,
        sources=sources,
        findings=[f"BMad {kind} mapping recorded: {map_id}"],
        actions=[f"Created {relative_posix(path, root)}"],
        gaps=gaps,
        next_read=next_read,
    )
    print(f"Recorded BMad mapping: {map_id}")
    print(f"JSON: {path}")
    print(f"Markdown: {markdown_path}")
    print(f"Context: {context_path}")
    print(f"Context Markdown: {context_markdown_path}")
    return 0


def cmd_bmad_status(args: argparse.Namespace) -> int:
    root = find_root(args.root)
    state = ensure_state(root)
    index = load_bmad_index(state)
    mappings = index.get("mappings", [])
    map_id = args.map_id or (mappings[0].get("map_id") if mappings else None)
    if not map_id:
        print("No BMad mappings found.")
        return 0
    path = bmad_entry_path(state, map_id)
    if not path.exists():
        print(f"BMad mapping not found: {map_id}", file=sys.stderr)
        return 1
    data = read_json(path)
    freshness = context_freshness(root, data)
    print(f"map_id: {data['map_id']}")
    print(f"task_id: {data['task_id']}")
    print(f"kind: {data['kind']}")
    print(f"mapping: {path}")
    has_problem = False
    for item in freshness or ["(none)"]:
        print(item)
        if item.endswith(": stale") or item.endswith(": missing"):
            has_problem = True
    return 1 if has_problem else 0


def cmd_bmad_validate(args: argparse.Namespace) -> int:
    root = find_root(args.root)
    path = resolve_validation_file(root, args.file)
    data = read_json(path)
    errors = validate_bmad_mapping(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"VALID bmad mapping: {args.file}")
    return 0


def cmd_verify_run(args: argparse.Namespace) -> int:
    root = find_root(args.root)
    state = ensure_state(root)
    command = args.command or ""
    exit_code: int | str = "not-run"
    output_path = ""
    inferred_status = args.status
    if command:
        run_id = f"{datetime.now().strftime('%Y%m%d-%H%M%S-%f')}-{uuid.uuid4().hex[:8]}"
        output_file = state / "verification" / f"verify-{run_id}.log"
        exit_code, stdout, stderr = run_command(command, root)
        output_file.write_text(stdout + stderr, encoding="utf-8", newline="\n")
        output_path = relative_posix(output_file, root)
        if not inferred_status:
            inferred_status = "passed" if exit_code == 0 else "failed"
    status = inferred_status or "inconclusive"
    if status not in STATUS:
        print(f"Invalid status: {status}", file=sys.stderr)
        return 2
    log = state / "verify-log.tsv"
    if not log.exists():
        log.write_text("timestamp\tstatus\tclaim\tcommand\texit_code\tevidence\n", encoding="utf-8", newline="\n")
    row = "\t".join(
        [
            utc_now(),
            status,
            args.claim.replace("\t", " "),
            command.replace("\t", " "),
            str(exit_code),
            output_path,
        ]
    )
    with log.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(row + "\n")
    print(f"{status.upper()}: {args.claim}")
    print(f"Log: {log}")
    if output_path:
        print(f"Evidence: {root / output_path}")
    return 0 if status == "passed" else 1


def validate_non_empty_string(data: dict[str, Any], key: str, errors: list[str]) -> None:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{key} must be a non-empty string")


def validate_datetime_string(data: dict[str, Any], key: str, errors: list[str]) -> None:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{key} must be a non-empty date-time string")
        return
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{key} must be an ISO 8601 date-time")


def validate_string_array(data: dict[str, Any], key: str, errors: list[str]) -> None:
    value = data.get(key)
    if not isinstance(value, list):
        errors.append(f"{key} must be an array")
        return
    for index, item in enumerate(value, start=1):
        if not isinstance(item, str) or not item.strip():
            errors.append(f"{key}[{index}] must be a non-empty string")


def is_external_or_fragment(value: str) -> bool:
    stripped = value.strip()
    if not stripped or stripped.startswith("#"):
        return True
    return bool(re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", stripped))


def looks_like_local_path(value: str) -> bool:
    stripped = value.strip().strip("<>")
    if is_external_or_fragment(stripped):
        return False
    if stripped.startswith((".", "/", "\\")):
        return True
    if "/" in stripped or "\\" in stripped:
        return True
    return bool(Path(stripped).suffix)


def resolve_validation_file(root: Path, file_value: str) -> Path:
    path = Path(file_value)
    if path.is_absolute() or path.exists():
        return path
    return root / path


def resolve_evidence_path(root: Path, evidence: str) -> Path:
    value = evidence.strip().strip("<>")
    path = Path(value)
    return path if path.is_absolute() else root / path


def validate_checkpoint(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ["task_id", "checkpoint_id", "phase", "created_at", "completed", "pending", "artifacts"]
    for key in required:
        if key not in data:
            errors.append(f"missing required field: {key}")
    for key in ["task_id", "checkpoint_id"]:
        if key in data:
            validate_non_empty_string(data, key, errors)
    if "created_at" in data:
        validate_datetime_string(data, "created_at", errors)
    if data.get("phase") not in PHASES:
        errors.append("phase must be one of: " + ", ".join(sorted(PHASES)))
    for key in ["completed", "pending", "artifacts"]:
        if key in data:
            validate_string_array(data, key, errors)
    return errors


def validate_context(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ["task_id", "context_id", "phase", "created_at", "updated_at", "sources"]
    for key in required:
        if key not in data:
            errors.append(f"missing required field: {key}")
    for key in ["task_id", "context_id"]:
        if key in data:
            validate_non_empty_string(data, key, errors)
    if data.get("phase") not in PHASES:
        errors.append("phase must be one of: " + ", ".join(sorted(PHASES)))
    for key in ["created_at", "updated_at"]:
        if key in data:
            validate_datetime_string(data, key, errors)
    sources = data.get("sources")
    if not isinstance(sources, list):
        errors.append("sources must be an array")
    else:
        for index, item in enumerate(sources, start=1):
            if not isinstance(item, dict):
                errors.append(f"sources[{index}] must be an object")
                continue
            if not isinstance(item.get("path"), str) or not item["path"].strip():
                errors.append(f"sources[{index}].path must be a non-empty string")
            digest = item.get("sha256")
            if digest is not None and (not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest)):
                errors.append(f"sources[{index}].sha256 must be a hex sha256 digest")
    for key in ["findings", "actions", "decisions", "gaps", "next_read"]:
        if key in data:
            validate_string_array(data, key, errors)
    return errors


def validate_evidence(data: dict[str, Any], root: Path | None = None) -> list[str]:
    errors: list[str] = []
    required = ["task_id", "run_id", "status", "created_at", "dod_items"]
    for key in required:
        if key not in data:
            errors.append(f"missing required field: {key}")
    for key in ["task_id", "run_id"]:
        if key in data:
            validate_non_empty_string(data, key, errors)
    if "created_at" in data:
        validate_datetime_string(data, "created_at", errors)
    if data.get("status") not in STATUS:
        errors.append("status must be passed, failed, or inconclusive")
    dod_items = data.get("dod_items")
    if not isinstance(dod_items, list) or not dod_items:
        errors.append("dod_items must be a non-empty array")
    else:
        for index, item in enumerate(dod_items, start=1):
            if not isinstance(item, dict):
                errors.append(f"dod_items[{index}] must be an object")
                continue
            for key in ["id", "description", "status", "evidence"]:
                if key not in item:
                    errors.append(f"dod_items[{index}] missing field: {key}")
            for key in ["id", "description"]:
                if key in item and (not isinstance(item[key], str) or not item[key].strip()):
                    errors.append(f"dod_items[{index}].{key} must be a non-empty string")
            if item.get("status") not in STATUS:
                errors.append(f"dod_items[{index}].status is invalid")
            evidence = item.get("evidence")
            if not isinstance(evidence, list) or not evidence:
                errors.append(f"dod_items[{index}].evidence must be a non-empty array")
            else:
                for evidence_index, evidence_item in enumerate(evidence, start=1):
                    if not isinstance(evidence_item, str) or not evidence_item.strip():
                        errors.append(f"dod_items[{index}].evidence[{evidence_index}] must be a non-empty string")
                        continue
                    if root and looks_like_local_path(evidence_item):
                        evidence_path = resolve_evidence_path(root, evidence_item)
                        if not evidence_path.exists():
                            errors.append(
                                f"dod_items[{index}].evidence[{evidence_index}] path does not exist: {evidence_item}"
                            )
    return errors


def cmd_validate(args: argparse.Namespace) -> int:
    root = find_root(args.root)
    validation_file = resolve_validation_file(root, args.file)
    data = read_json(validation_file)
    validators = {
        "checkpoint": lambda: validate_checkpoint(data),
        "context": lambda: validate_context(data),
        "evidence": lambda: validate_evidence(data, root),
    }
    errors = validators[args.kind]()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"VALID {args.kind}: {args.file}")
    return 0


def normalize_link_target(raw: str) -> str | None:
    target = raw.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    if not target or target.startswith("#"):
        return None
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
        return None
    return target.split("#", 1)[0]


def cmd_audit_links(args: argparse.Namespace) -> int:
    root = find_root(args.root)
    broken: list[str] = []
    for md_file in root.rglob("*.md"):
        if ".git" in md_file.parts or ".yunshu" in md_file.parts:
            continue
        text = md_file.read_text(encoding="utf-8", errors="replace")
        for match in LINK_RE.finditer(text):
            target = normalize_link_target(match.group(1))
            if target is None:
                continue
            target_path = (md_file.parent / target).resolve()
            try:
                target_path.relative_to(root)
            except ValueError:
                continue
            if not target_path.exists():
                line = text[: match.start()].count("\n") + 1
                broken.append(f"{md_file.relative_to(root)}:{line} -> {target}")
    if broken:
        for item in broken:
            print(f"BROKEN: {item}", file=sys.stderr)
        return 1
    print("Markdown link audit passed.")
    return 0


def extract_skill_version(skill_path: Path) -> str | None:
    text = skill_path.read_text(encoding="utf-8", errors="replace")
    match = re.search(r'^version:\s*["\']?([^"\'\s]+)', text, flags=re.MULTILINE)
    if match:
        return match.group(1)
    in_metadata = False
    for line in text.splitlines():
        if re.match(r"^metadata:\s*$", line):
            in_metadata = True
            continue
        if in_metadata and line.strip() and not line.startswith((" ", "\t")):
            in_metadata = False
        if in_metadata:
            nested = re.match(r'^\s+version:\s*["\']?([^"\'\s]+)', line)
            if nested:
                return nested.group(1)
    return None


def extract_json_version(json_path: Path) -> str | None:
    if not json_path.exists():
        return None
    try:
        value = read_json(json_path).get("version")
    except (OSError, json.JSONDecodeError, ValueError):
        return None
    return value if isinstance(value, str) and value.strip() else None


def resolve_artifact_path(root: Path, raw_path: str) -> Path:
    expanded = os.path.expandvars(os.path.expanduser(raw_path.strip()))
    artifact_path = Path(expanded)
    if not artifact_path.is_absolute():
        artifact_path = root / artifact_path
    return artifact_path.resolve()


def validate_transition_artifact(root: Path, label: str, raw_path: str | None, errors: list[str]) -> None:
    if not raw_path:
        return
    artifact_path = resolve_artifact_path(root, raw_path)
    if not artifact_path.exists():
        errors.append(f"{label} artifact does not exist: {raw_path}")
        return
    if artifact_path.is_file() and artifact_path.stat().st_size == 0:
        errors.append(f"{label} artifact is empty: {raw_path}")


def extract_readme_version(readme_path: Path) -> str | None:
    text = readme_path.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"version-([0-9A-Za-z._-]+)-blue", text)
    return match.group(1) if match else None


def cmd_version_check(args: argparse.Namespace) -> int:
    root = find_root(args.root)
    expected = (root / "VERSION").read_text(encoding="utf-8").strip() if (root / "VERSION").exists() else None
    checks = {
        "VERSION": expected,
        "SKILL.md": extract_skill_version(root / "SKILL.md"),
        "README.md": extract_readme_version(root / "README.md"),
    }
    optional_paths = {
        "adapters/codex/SKILL.md": root / "adapters" / "codex" / "SKILL.md",
        "adapters/trae/SKILL.md": root / "adapters" / "trae" / "SKILL.md",
        "adapters/trae/skill-config.example.json": root / "adapters" / "trae" / "skill-config.example.json",
    }
    for name, path in optional_paths.items():
        if not path.exists():
            continue
        if path.suffix == ".json":
            checks[name] = extract_json_version(path)
        else:
            checks[name] = extract_skill_version(path)
    mismatches = []
    for name, version in checks.items():
        if not version:
            mismatches.append(f"{name}: missing version")
        elif expected and version != expected:
            mismatches.append(f"{name}: {version} != {expected}")
    if mismatches:
        for item in mismatches:
            print(f"VERSION ERROR: {item}", file=sys.stderr)
        return 1
    print(f"Version check passed: {expected}")
    return 0


def memory_path(state: Path, tier: str) -> Path:
    return state / "memory" / f"{tier}.json"


def load_memory(state: Path, tier: str) -> dict[str, Any]:
    path = memory_path(state, tier)
    if not path.exists():
        return {"entries": []}
    return read_json(path)


def save_memory(state: Path, tier: str, data: dict[str, Any]) -> None:
    write_json(memory_path(state, tier), data)


def cmd_memory_read(args: argparse.Namespace) -> int:
    root = find_root(args.root)
    state = ensure_state(root)
    tier = args.tier
    if tier not in {"short-term", "long-term", "permanent"}:
        print(f"Invalid tier: {tier}", file=sys.stderr)
        return 2
    data = load_memory(state, tier)
    entries = data.get("entries", [])
    if args.category:
        entries = [e for e in entries if e.get("category") == args.category]
    if not entries:
        print(f"No entries in {tier} memory.")
        return 0
    for entry in entries:
        print(f"[{entry.get('timestamp', 'n/a')}] {entry.get('category', 'general')}: {entry.get('summary', '')}")
    return 0


def cmd_memory_write(args: argparse.Namespace) -> int:
    root = find_root(args.root)
    state = ensure_state(root)
    tier = args.tier
    if tier not in {"short-term", "long-term", "permanent"}:
        print(f"Invalid tier: {tier}", file=sys.stderr)
        return 2
    data = load_memory(state, tier)
    entries = data.get("entries", [])
    entry = {
        "timestamp": utc_now(),
        "category": args.category or "general",
        "summary": args.summary or "",
        "detail": args.detail or "",
    }
    entries.append(entry)
    if tier == "short-term" and len(entries) > 20:
        entries = entries[-20:]
    data["entries"] = entries
    save_memory(state, tier, data)
    print(f"Written to {tier} memory: {entry['summary']}")
    return 0


def cmd_memory_promote(args: argparse.Namespace) -> int:
    root = find_root(args.root)
    state = ensure_state(root)
    source_tier = args.from_tier
    target_tier = args.to_tier
    if source_tier not in {"short-term", "long-term"} or target_tier not in {"long-term", "permanent"}:
        print("Invalid tier combination", file=sys.stderr)
        return 2
    source_data = load_memory(state, source_tier)
    target_data = load_memory(state, target_tier)
    entries = source_data.get("entries", [])
    if args.index is not None:
        if args.index < 0 or args.index >= len(entries):
            print(f"Invalid index: {args.index}", file=sys.stderr)
            return 1
        to_promote = [entries[args.index]]
    else:
        to_promote = entries
    target_entries = target_data.get("entries", [])
    for entry in to_promote:
        promoted = dict(entry)
        promoted["promoted_at"] = utc_now()
        promoted["promoted_from"] = source_tier
        target_entries.append(promoted)
    target_data["entries"] = target_entries
    save_memory(state, target_tier, target_data)
    print(f"Promoted {len(to_promote)} entries from {source_tier} to {target_tier}")
    return 0


def task_index_path(state: Path) -> Path:
    return state / "tasks" / "index.json"


def task_entry_path(state: Path, task_id: str) -> Path:
    return state / "tasks" / f"{task_id}.json"


def load_task_index(state: Path) -> dict[str, Any]:
    path = task_index_path(state)
    if not path.exists():
        return {"tasks": []}
    return read_json(path)


def save_task_index(state: Path, index: dict[str, Any]) -> None:
    write_json(task_index_path(state), index)


def cmd_task_create(args: argparse.Namespace) -> int:
    root = find_root(args.root)
    state = ensure_state(root)
    task_id = slug(args.task_id)
    task_data = {
        "task_id": task_id,
        "goal": args.goal or "",
        "phase": args.phase or "init",
        "status": "active",
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "dod_items": [{"id": f"DOD-{i+1}", "description": d, "status": "pending", "evidence": []} for i, d in enumerate(args.dod or [])],
        "completed_steps": [],
        "pending_steps": args.pending_steps or [],
        "blocked_by": [],
        "context_ledger": "",
        "latest_checkpoint": "",
    }
    path = task_entry_path(state, task_id)
    write_json(path, task_data)
    index = load_task_index(state)
    entries = [e for e in index.get("tasks", []) if e.get("task_id") != task_id]
    entries.append({"task_id": task_id, "status": "active", "updated_at": task_data["updated_at"], "path": relative_posix(path, root)})
    index["tasks"] = sorted(entries, key=lambda x: x["updated_at"], reverse=True)
    save_task_index(state, index)
    print(f"Created task: {task_id}")
    print(f"Path: {path}")
    return 0


def cmd_task_status(args: argparse.Namespace) -> int:
    root = find_root(args.root)
    state = ensure_state(root)
    task_id = slug(args.task_id)
    path = task_entry_path(state, task_id)
    if not path.exists():
        print(f"Task not found: {task_id}", file=sys.stderr)
        return 1
    data = read_json(path)
    print(f"task_id: {data['task_id']}")
    print(f"goal: {data.get('goal', '')}")
    print(f"phase: {data['phase']}")
    print(f"status: {data['status']}")
    print(f"updated_at: {data['updated_at']}")
    print()
    print("DoD Items:")
    for item in data.get("dod_items", []):
        print(f"  [{item['status']}] {item['id']}: {item['description']}")
    print()
    print("Completed Steps:")
    for step in data.get("completed_steps", []):
        print(f"  - {step}")
    print()
    print("Pending Steps:")
    for step in data.get("pending_steps", []):
        print(f"  - {step}")
    if data.get("blocked_by"):
        print()
        print("Blocked By:")
        for b in data["blocked_by"]:
            print(f"  - {b}")
    return 0


def cmd_task_update(args: argparse.Namespace) -> int:
    root = find_root(args.root)
    state = ensure_state(root)
    task_id = slug(args.task_id)
    path = task_entry_path(state, task_id)
    if not path.exists():
        print(f"Task not found: {task_id}", file=sys.stderr)
        return 1
    data = read_json(path)
    if args.phase and args.phase in PHASES:
        data["phase"] = args.phase
    if args.status:
        data["status"] = args.status
    if args.complete_step:
        step = args.complete_step
        if step in data.get("pending_steps", []):
            data["pending_steps"].remove(step)
        if step not in data.get("completed_steps", []):
            data["completed_steps"].append(step)
    if args.add_step:
        data.setdefault("pending_steps", []).append(args.add_step)
    if args.blocked_by:
        data.setdefault("blocked_by", []).append(args.blocked_by)
    if args.unblock:
        if args.unblock in data.get("blocked_by", []):
            data["blocked_by"].remove(args.unblock)
    if args.dod_status:
        for item in data.get("dod_items", []):
            if item["id"] == args.dod_status:
                item["status"] = args.dod_status_value or "passed"
                break
    if args.checkpoint:
        data["latest_checkpoint"] = args.checkpoint
    if args.context_ledger:
        data["context_ledger"] = args.context_ledger
    data["updated_at"] = utc_now()
    write_json(path, data)
    index = load_task_index(state)
    for entry in index.get("tasks", []):
        if entry.get("task_id") == task_id:
            entry["updated_at"] = data["updated_at"]
            entry["status"] = data["status"]
            break
    save_task_index(state, index)
    print(f"Updated task: {task_id}")
    return 0


def cmd_task_list(args: argparse.Namespace) -> int:
    root = find_root(args.root)
    state = ensure_state(root)
    index = load_task_index(state)
    tasks = index.get("tasks", [])
    if args.status:
        tasks = [t for t in tasks if t.get("status") == args.status]
    if not tasks:
        print("No tasks found.")
        return 0
    for item in tasks:
        print(f"{item['updated_at']}  {item['task_id']}  {item['status']}  {item['path']}")
    return 0


def gate_path(state: Path, gate_id: str) -> Path:
    return state / "gates" / f"{gate_id}.json"


def cmd_gate_check(args: argparse.Namespace) -> int:
    root = find_root(args.root)
    state = ensure_state(root)
    phase = args.phase
    if phase not in PHASES:
        print(f"Invalid phase: {phase}", file=sys.stderr)
        return 2
    gate_id = args.gate_id or f"gate-{phase}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    signals = []
    if args.memory_confusion:
        signals.append({"signal": "memory_confusion", "severity": "critical", "description": "重复问已确认的问题或自相矛盾"})
    if args.quality_drop:
        signals.append({"signal": "quality_drop", "severity": "critical", "description": "出现低级错误或忽略已知约束"})
    if args.slow_response:
        signals.append({"signal": "slow_response", "severity": "warning", "description": "思考时间明显变长或输出冗余增加"})
    if args.context_loss:
        signals.append({"signal": "context_loss", "severity": "critical", "description": "需要重新读取之前已读的文件或丢失任务上下文"})
    critical_count = sum(1 for s in signals if s["severity"] == "critical")
    warning_count = sum(1 for s in signals if s["severity"] == "warning")
    if critical_count >= 1 or warning_count >= 2:
        overall = "warning"
    elif warning_count == 1:
        overall = "attention"
    else:
        overall = "healthy"
    gate_data = {
        "gate_id": gate_id,
        "phase": phase,
        "checked_at": utc_now(),
        "overall_status": overall,
        "signals": signals,
        "recommendation": "save-context-and-continue" if overall == "attention" else ("save-context-and-switch-session" if overall == "warning" else "continue"),
    }
    write_json(gate_path(state, gate_id), gate_data)
    print(f"Gate check: {overall.upper()}")
    print(f"Gate ID: {gate_id}")
    for s in signals:
        print(f"  [{s['severity']}] {s['signal']}: {s['description']}")
    if overall == "warning":
        print("Recommendation: Save context and switch session")
    elif overall == "attention":
        print("Recommendation: Save context and continue")
    else:
        print("Recommendation: Continue")
    return 0 if overall == "healthy" else (1 if overall == "attention" else 2)


def cmd_gate_show(args: argparse.Namespace) -> int:
    root = find_root(args.root)
    state = ensure_state(root)
    gate_id = args.gate_id
    path = gate_path(state, gate_id)
    if not path.exists():
        print(f"Gate not found: {gate_id}", file=sys.stderr)
        return 1
    data = read_json(path)
    print(f"gate_id: {data['gate_id']}")
    print(f"phase: {data['phase']}")
    print(f"checked_at: {data['checked_at']}")
    print(f"overall_status: {data['overall_status']}")
    print(f"recommendation: {data['recommendation']}")
    return 0


def cmd_gate_transition(args: argparse.Namespace) -> int:
    root = find_root(args.root)
    state = ensure_state(root)
    from_phase = args.from_phase
    to_phase = args.to_phase
    task_id = slug(args.task_id) if args.task_id else ""
    gate_id = args.gate_id or f"transition-{from_phase}-to-{to_phase}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    errors: list[str] = []
    warnings: list[str] = []
    allowed_next = ALLOWED_TRANSITIONS.get(from_phase, set())
    if to_phase not in allowed_next:
        errors.append(f"invalid transition: {from_phase} -> {to_phase}; allowed next phases: {', '.join(sorted(allowed_next)) or '(none)'}")
    if task_id:
        task_path = task_entry_path(state, task_id)
        if task_path.exists():
            task_data = read_json(task_path)
            if task_data.get("phase") != from_phase:
                warnings.append(f"task phase is {task_data.get('phase')}, transition requested from {from_phase}")
        else:
            warnings.append(f"task record not found: {task_id}")
    context_entries = selected_context_entries(root, state, task_id=task_id or None, limit=1)
    latest_context = context_entries[0] if context_entries else None
    context_id = latest_context.get("context_id") if latest_context else ""
    context_fresh = False
    if latest_context and context_id:
        context_path = context_entry_path(state, context_id)
        if context_path.exists():
            freshness = context_freshness(root, read_json(context_path))
            context_fresh = not has_freshness_problem(freshness)
        else:
            errors.append(f"context ledger file missing: {context_id}")
    else:
        errors.append("no context ledger found for transition")
    if from_phase == "init" and to_phase == "plan":
        if not args.user_aligned:
            errors.append("init -> plan requires explicit user alignment/approval of the task card or design")
        if not args.task_card:
            errors.append("init -> plan requires --task-card pointing to the approved task card or recorded task artifact")
        if not args.dod_confirmed:
            errors.append("init -> plan requires confirmed DoD")
    if from_phase == "plan" and to_phase in {"execute", "subagent"}:
        if not args.plan:
            errors.append("plan -> execution requires --plan")
        if not args.spec:
            errors.append("plan -> execution requires --spec")
    if to_phase == "accept" and not args.verification:
        errors.append("execution -> accept requires --verification evidence")
    if to_phase == "deliver" and not args.verification:
        errors.append("accept -> deliver requires --verification evidence")
    validate_transition_artifact(root, "task-card", args.task_card, errors)
    validate_transition_artifact(root, "plan", args.plan, errors)
    validate_transition_artifact(root, "spec", args.spec, errors)
    validate_transition_artifact(root, "verification", args.verification, errors)
    if latest_context and not context_fresh:
        errors.append("latest context ledger has stale or missing sources; run context preload/status and refresh before transitioning")
    gate_data = {
        "gate_id": gate_id,
        "kind": "transition",
        "task_id": task_id,
        "from_phase": from_phase,
        "to_phase": to_phase,
        "checked_at": utc_now(),
        "context_id": context_id,
        "context_fresh": context_fresh,
        "artifacts": {
            "task_card": args.task_card or "",
            "plan": args.plan or "",
            "spec": args.spec or "",
            "verification": args.verification or "",
        },
        "user_aligned": bool(args.user_aligned),
        "dod_confirmed": bool(args.dod_confirmed),
        "warnings": warnings,
        "errors": errors,
        "overall_status": "passed" if not errors else "failed",
    }
    write_json(gate_path(state, gate_id), gate_data)
    print(f"Transition gate: {gate_data['overall_status'].upper()}")
    print(f"Gate ID: {gate_id}")
    print(f"Transition: {from_phase} -> {to_phase}")
    if context_id:
        print(f"Context: {context_id} ({'fresh' if context_fresh else 'not fresh'})")
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    return 0 if not errors else 1


def cmd_health_check(args: argparse.Namespace) -> int:
    root = find_root(args.root)
    state = ensure_state(root)
    issues: list[str] = []
    checks = []
    if not (state / "context" / "index.json").exists():
        issues.append("Context ledger index missing")
    else:
        checks.append("context_index")
    if not (state / "checkpoints" / "index.json").exists():
        issues.append("Checkpoint index missing")
    else:
        checks.append("checkpoint_index")
    ctx_index = load_context_index(state)
    for entry in ctx_index.get("contexts", []):
        ctx_path = state / "context" / f"{entry['context_id']}.json"
        if not ctx_path.exists():
            issues.append(f"Context ledger missing: {entry['context_id']}")
    cp_index = load_index(state)
    for entry in cp_index.get("checkpoints", []):
        cp_path = state / "checkpoints" / entry["checkpoint_id"] / "checkpoint.json"
        if not cp_path.exists():
            issues.append(f"Checkpoint missing: {entry['checkpoint_id']}")
    task_index = load_task_index(state)
    for entry in task_index.get("tasks", []):
        task_path = task_entry_path(state, entry["task_id"])
        if not task_path.exists():
            issues.append(f"Task record missing: {entry['task_id']}")
    for tier in ["short-term", "long-term", "permanent"]:
        mem_path = memory_path(state, tier)
        if mem_path.exists():
            try:
                read_json(mem_path)
                checks.append(f"memory_{tier}")
            except (json.JSONDecodeError, ValueError):
                issues.append(f"Memory file corrupt: {tier}")
    gate_dir = state / "gates"
    if gate_dir.exists():
        gate_files = list(gate_dir.glob("*.json"))
        checks.append(f"gates:{len(gate_files)}")
    if issues:
        for issue in issues:
            print(f"ISSUE: {issue}", file=sys.stderr)
        print(f"Health check FAILED: {len(issues)} issues, {len(checks)} checks passed")
        return 1
    print(f"Health check PASSED: {len(checks)} checks passed")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="yunshu", description="Yunshu workflow utility")
    parser.add_argument("--root", help="Yunshu skill root or project root")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="Create .yunshu state directories")
    init.set_defaults(func=cmd_init)

    checkpoint = sub.add_parser("checkpoint", help="Manage checkpoints")
    checkpoint_sub = checkpoint.add_subparsers(dest="checkpoint_command", required=True)
    create = checkpoint_sub.add_parser("create", help="Create a checkpoint")
    create.add_argument("--task-id", required=True)
    create.add_argument("--phase", required=True, choices=sorted(PHASES))
    create.add_argument("--summary", default="")
    create.add_argument("--completed", action="append")
    create.add_argument("--pending", action="append")
    create.add_argument("--decision", action="append")
    create.add_argument("--artifact", action="append")
    create.add_argument("--risk", action="append")
    create.add_argument("--next-action", default="")
    create.add_argument("--gate-status", default="not-checked", choices=["not-checked", "healthy", "attention", "warning", "passed"])
    create.set_defaults(func=cmd_checkpoint_create)
    list_cmd = checkpoint_sub.add_parser("list", help="List checkpoints")
    list_cmd.add_argument("--task-id")
    list_cmd.set_defaults(func=cmd_checkpoint_list)
    resume = checkpoint_sub.add_parser("resume", help="Print resume prompt for a checkpoint")
    resume.add_argument("checkpoint_id")
    resume.set_defaults(func=cmd_checkpoint_resume)

    context = sub.add_parser("context", help="Manage reusable context records")
    context_sub = context.add_subparsers(dest="context_command", required=True)
    record = context_sub.add_parser("record", help="Record sources, findings, actions, and gaps")
    record.add_argument("--task-id", required=True)
    record.add_argument("--phase", required=True, choices=sorted(PHASES))
    record.add_argument("--context-id")
    record.add_argument("--source", action="append")
    record.add_argument("--finding", action="append")
    record.add_argument("--action", action="append")
    record.add_argument("--decision", action="append")
    record.add_argument("--gap", action="append")
    record.add_argument("--next-read", action="append")
    record.add_argument("--associated-checkpoint", action="append")
    record.set_defaults(func=cmd_context_record)
    list_context = context_sub.add_parser("list", help="List context records")
    list_context.add_argument("--task-id")
    list_context.set_defaults(func=cmd_context_list)
    preload = context_sub.add_parser("preload", help="Select the minimal recent/relevant context records to load")
    preload.add_argument("--task-id")
    preload.add_argument("--checkpoint-id")
    preload.add_argument("--query")
    preload.add_argument("--limit", type=int, default=3)
    preload.set_defaults(func=cmd_context_preload)
    show = context_sub.add_parser("show", help="Show the latest or selected context record")
    show.add_argument("context_id", nargs="?")
    show.set_defaults(func=cmd_context_show)
    status_context = context_sub.add_parser("status", help="Check whether recorded local sources changed")
    status_context.add_argument("context_id", nargs="?")
    status_context.set_defaults(func=cmd_context_status)

    bmad = sub.add_parser("bmad", help="Manage BMad enhancement mappings")
    bmad_sub = bmad.add_subparsers(dest="bmad_command", required=True)
    bmad_map = bmad_sub.add_parser("map", help="Record a BMad artifact mapping")
    bmad_map.add_argument("--task-id", required=True)
    bmad_map.add_argument("--kind", required=True, choices=sorted(BMAD_KINDS))
    bmad_map.add_argument("--source", action="append", required=True)
    bmad_map.add_argument("--map-id")
    bmad_map.add_argument("--context-id")
    bmad_map.add_argument("--gap", action="append")
    bmad_map.add_argument("--next-read", action="append")
    bmad_map.set_defaults(func=cmd_bmad_map)
    bmad_status = bmad_sub.add_parser("status", help="Check BMad mapping source freshness")
    bmad_status.add_argument("map_id", nargs="?")
    bmad_status.set_defaults(func=cmd_bmad_status)
    bmad_validate = bmad_sub.add_parser("validate", help="Validate a BMad mapping JSON")
    bmad_validate.add_argument("file")
    bmad_validate.set_defaults(func=cmd_bmad_validate)

    verify = sub.add_parser("verify", help="Verification commands")
    verify_sub = verify.add_subparsers(dest="verify_command", required=True)
    run = verify_sub.add_parser("run", help="Run or record a claim verification")
    run.add_argument("--claim", required=True)
    run.add_argument("--command")
    run.add_argument("--status", choices=sorted(STATUS))
    run.set_defaults(func=cmd_verify_run)

    validate = sub.add_parser("validate", help="Validate structured Yunshu JSON")
    validate.add_argument("kind", choices=["checkpoint", "context", "evidence"])
    validate.add_argument("file")
    validate.set_defaults(func=cmd_validate)

    audit = sub.add_parser("audit", help="Audit repository assets")
    audit_sub = audit.add_subparsers(dest="audit_command", required=True)
    links = audit_sub.add_parser("links", help="Check internal Markdown links")
    links.set_defaults(func=cmd_audit_links)

    version = sub.add_parser("version-check", help="Check VERSION/SKILL/README consistency")
    version.set_defaults(func=cmd_version_check)

    memory = sub.add_parser("memory", help="Manage session memory")
    memory_sub = memory.add_subparsers(dest="memory_command", required=True)
    memory_read = memory_sub.add_parser("read", help="Read memory entries")
    memory_read.add_argument("tier", choices=["short-term", "long-term", "permanent"])
    memory_read.add_argument("--category")
    memory_read.set_defaults(func=cmd_memory_read)
    memory_write = memory_sub.add_parser("write", help="Write a memory entry")
    memory_write.add_argument("tier", choices=["short-term", "long-term", "permanent"])
    memory_write.add_argument("--summary", required=True)
    memory_write.add_argument("--category", default="general")
    memory_write.add_argument("--detail", default="")
    memory_write.set_defaults(func=cmd_memory_write)
    memory_promote = memory_sub.add_parser("promote", help="Promote memory entries to higher tier")
    memory_promote.add_argument("--from-tier", required=True, choices=["short-term", "long-term"])
    memory_promote.add_argument("--to-tier", required=True, choices=["long-term", "permanent"])
    memory_promote.add_argument("--index", type=int)
    memory_promote.set_defaults(func=cmd_memory_promote)

    task = sub.add_parser("task", help="Manage task tracking")
    task_sub = task.add_subparsers(dest="task_command", required=True)
    task_create = task_sub.add_parser("create", help="Create a new task")
    task_create.add_argument("--task-id", required=True)
    task_create.add_argument("--goal", default="")
    task_create.add_argument("--phase", choices=sorted(PHASES))
    task_create.add_argument("--dod", action="append")
    task_create.add_argument("--pending-step", action="append", dest="pending_steps")
    task_create.set_defaults(func=cmd_task_create)
    task_status = task_sub.add_parser("status", help="Show task status")
    task_status.add_argument("--task-id", required=True)
    task_status.set_defaults(func=cmd_task_status)
    task_update = task_sub.add_parser("update", help="Update task progress")
    task_update.add_argument("--task-id", required=True)
    task_update.add_argument("--phase", choices=sorted(PHASES))
    task_update.add_argument("--status", choices=["active", "blocked", "completed", "abandoned"])
    task_update.add_argument("--complete-step")
    task_update.add_argument("--add-step")
    task_update.add_argument("--blocked-by")
    task_update.add_argument("--unblock")
    task_update.add_argument("--dod-id")
    task_update.add_argument("--dod-status", choices=["pending", "passed", "failed"])
    task_update.add_argument("--checkpoint")
    task_update.add_argument("--context-ledger")
    task_update.set_defaults(func=cmd_task_update)
    task_list = task_sub.add_parser("list", help="List tasks")
    task_list.add_argument("--status")
    task_list.set_defaults(func=cmd_task_list)

    gate = sub.add_parser("gate", help="Manage phase transition gates")
    gate_sub = gate.add_subparsers(dest="gate_command", required=True)
    gate_check = gate_sub.add_parser("check", help="Run gate check for phase transition")
    gate_check.add_argument("--phase", required=True, choices=sorted(PHASES))
    gate_check.add_argument("--gate-id")
    gate_check.add_argument("--memory-confusion", action="store_true")
    gate_check.add_argument("--quality-drop", action="store_true")
    gate_check.add_argument("--slow-response", action="store_true")
    gate_check.add_argument("--context-loss", action="store_true")
    gate_check.set_defaults(func=cmd_gate_check)
    gate_show = gate_sub.add_parser("show", help="Show gate check result")
    gate_show.add_argument("gate_id")
    gate_show.set_defaults(func=cmd_gate_show)
    gate_transition = gate_sub.add_parser("transition", help="Validate an ordered phase transition")
    gate_transition.add_argument("--task-id", required=True)
    gate_transition.add_argument("--from-phase", required=True, choices=sorted(PHASES))
    gate_transition.add_argument("--to-phase", required=True, choices=sorted(PHASES))
    gate_transition.add_argument("--gate-id")
    gate_transition.add_argument("--user-aligned", action="store_true")
    gate_transition.add_argument("--dod-confirmed", action="store_true")
    gate_transition.add_argument("--task-card")
    gate_transition.add_argument("--plan")
    gate_transition.add_argument("--spec")
    gate_transition.add_argument("--verification")
    gate_transition.set_defaults(func=cmd_gate_transition)

    health = sub.add_parser("health", help="Run full health check on .yunshu state")
    health.set_defaults(func=cmd_health_check)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
