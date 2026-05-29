import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import yunshu  # noqa: E402


class YunshuCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "components").mkdir()
        (self.root / "SKILL.md").write_text('---\nversion: "3.4.0"\n---\n', encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_cli(self, args: list[str]) -> int:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return yunshu.main(["--root", str(self.root), *args])

    def run_cli_capture(self, args: list[str]) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            result = yunshu.main(["--root", str(self.root), *args])
        return result, stdout.getvalue(), stderr.getvalue()

    def write_evidence(self, data: dict) -> Path:
        path = self.root / "acceptance_evidence.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def write_checkpoint(self, data: dict) -> Path:
        path = self.root / "checkpoint.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def write_version_package(
        self,
        *,
        root_version: str = "3.6.0",
        codex_version: str = "3.6.0",
        trae_version: str = "3.6.0",
    ) -> None:
        (self.root / "VERSION").write_text(root_version + "\n", encoding="utf-8")
        (self.root / "SKILL.md").write_text(
            f'---\nmetadata:\n  version: "{root_version}"\n---\n',
            encoding="utf-8",
        )
        (self.root / "README.md").write_text(
            f"[![Version](https://img.shields.io/badge/version-{root_version}-blue.svg)](x)\n",
            encoding="utf-8",
        )
        codex_dir = self.root / "adapters" / "codex"
        codex_dir.mkdir(parents=True)
        (codex_dir / "SKILL.md").write_text(
            f'---\nmetadata:\n  version: "{codex_version}"\n---\n',
            encoding="utf-8",
        )
        trae_dir = self.root / "adapters" / "trae"
        trae_dir.mkdir(parents=True)
        (trae_dir / "skill-config.example.json").write_text(
            json.dumps({"version": trae_version}),
            encoding="utf-8",
        )

    def valid_evidence(self, evidence: list[str]) -> dict:
        return {
            "task_id": "test-task",
            "run_id": "accept-1",
            "status": "passed",
            "created_at": "2026-05-09T10:12:17Z",
            "dod_items": [
                {
                    "id": "DOD-1",
                    "description": "evidence is present",
                    "status": "passed",
                    "evidence": evidence,
                }
            ],
        }

    def valid_checkpoint(self) -> dict:
        return {
            "task_id": "test-task",
            "checkpoint_id": "test-task-plan-20260509-101217",
            "phase": "plan",
            "created_at": "2026-05-09T10:12:17Z",
            "completed": ["investigated scope"],
            "pending": ["write plan"],
            "artifacts": ["checkpoint.json"],
        }

    def test_verify_run_preserves_undecodable_output_as_evidence(self) -> None:
        command = (
            f'"{sys.executable}" -c '
            f'"import sys; sys.stdout.buffer.write(bytes([0xff, 0xfe, 0xfa]))"'
        )

        result = self.run_cli(["verify", "run", "--claim", "captures raw bytes", "--command", command])

        self.assertEqual(result, 0)
        log = (self.root / ".yunshu" / "verify-log.tsv").read_text(encoding="utf-8")
        self.assertIn("passed\tcaptures raw bytes", log)
        evidence_path = self.root / log.strip().splitlines()[-1].split("\t")[-1]
        self.assertGreater(evidence_path.stat().st_size, 0)

    def test_validate_evidence_rejects_missing_local_path(self) -> None:
        evidence_path = self.write_evidence(self.valid_evidence(["missing.log"]))

        result = self.run_cli(["validate", "evidence", str(evidence_path)])

        self.assertEqual(result, 1)

    def test_validate_evidence_accepts_existing_local_path(self) -> None:
        (self.root / "evidence.log").write_text("ok\n", encoding="utf-8")
        evidence_path = self.write_evidence(self.valid_evidence(["evidence.log"]))

        result = self.run_cli(["validate", "evidence", str(evidence_path)])

        self.assertEqual(result, 0)

    def test_validate_evidence_rejects_empty_required_strings(self) -> None:
        data = self.valid_evidence(["https://example.invalid/evidence"])
        data["task_id"] = ""
        data["dod_items"][0]["description"] = " "
        evidence_path = self.write_evidence(data)

        result = self.run_cli(["validate", "evidence", str(evidence_path)])

        self.assertEqual(result, 1)

    def test_validate_evidence_rejects_invalid_created_at(self) -> None:
        data = self.valid_evidence(["https://example.invalid/evidence"])
        data["created_at"] = "not-a-date"
        evidence_path = self.write_evidence(data)

        result = self.run_cli(["validate", "evidence", str(evidence_path)])

        self.assertEqual(result, 1)

    def test_validate_checkpoint_rejects_empty_required_strings(self) -> None:
        data = self.valid_checkpoint()
        data["task_id"] = ""
        data["completed"] = [" "]
        checkpoint_path = self.write_checkpoint(data)

        result = self.run_cli(["validate", "checkpoint", str(checkpoint_path)])

        self.assertEqual(result, 1)

    def test_validate_checkpoint_rejects_invalid_created_at(self) -> None:
        data = self.valid_checkpoint()
        data["created_at"] = "2026/05/09"
        checkpoint_path = self.write_checkpoint(data)

        result = self.run_cli(["validate", "checkpoint", str(checkpoint_path)])

        self.assertEqual(result, 1)

    def test_validate_evidence_accepts_utf8_bom_json(self) -> None:
        (self.root / "evidence.log").write_text("ok\n", encoding="utf-8")
        path = self.root / "acceptance_evidence_bom.json"
        path.write_text(json.dumps(self.valid_evidence(["evidence.log"])), encoding="utf-8-sig")

        result = self.run_cli(["validate", "evidence", str(path)])

        self.assertEqual(result, 0)

    def test_context_record_captures_sources_and_freshness(self) -> None:
        source = self.root / "README.md"
        source.write_text("first\n", encoding="utf-8")

        result = self.run_cli(
            [
                "context",
                "record",
                "--task-id",
                "memory",
                "--phase",
                "init",
                "--context-id",
                "memory-init",
                "--source",
                "README.md",
                "--finding",
                "README explains project",
                "--gap",
                "Need tests",
                "--next-read",
                "tests/",
            ]
        )

        self.assertEqual(result, 0)
        context_path = self.root / ".yunshu" / "context" / "memory-init.json"
        data = json.loads(context_path.read_text(encoding="utf-8"))
        self.assertEqual(data["context_id"], "memory-init")
        self.assertEqual(data["sources"][0]["path"], "README.md")
        self.assertRegex(data["sources"][0]["sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual(data["findings"], ["README explains project"])
        self.assertEqual(self.run_cli(["validate", "context", str(context_path)]), 0)
        self.assertEqual(self.run_cli(["context", "status", "memory-init"]), 0)

        source.write_text("changed\n", encoding="utf-8")

        self.assertEqual(self.run_cli(["context", "status", "memory-init"]), 1)

    def test_context_preload_selects_matching_recent_context_without_full_history(self) -> None:
        readme = self.root / "README.md"
        readme.write_text("alpha\n", encoding="utf-8")
        notes = self.root / "notes.md"
        notes.write_text("beta\n", encoding="utf-8")
        self.assertEqual(
            self.run_cli(
                [
                    "context",
                    "record",
                    "--task-id",
                    "demo",
                    "--phase",
                    "init",
                    "--context-id",
                    "demo-alpha",
                    "--source",
                    "README.md",
                    "--finding",
                    "Alpha investigation",
                ]
            ),
            0,
        )
        self.assertEqual(
            self.run_cli(
                [
                    "context",
                    "record",
                    "--task-id",
                    "demo",
                    "--phase",
                    "plan",
                    "--context-id",
                    "demo-beta",
                    "--source",
                    "notes.md",
                    "--finding",
                    "Beta plan finding",
                ]
            ),
            0,
        )

        result, stdout, stderr = self.run_cli_capture(["context", "preload", "--task-id", "demo", "--query", "Beta"])

        self.assertEqual(result, 0)
        self.assertIn("Context: demo-beta", stdout)
        self.assertNotIn("Context: demo-alpha", stdout)
        self.assertIn("Decision: preload is fresh", stdout)
        self.assertEqual(stderr, "")

    def test_context_preload_returns_refresh_code_for_stale_source(self) -> None:
        source = self.root / "README.md"
        source.write_text("first\n", encoding="utf-8")
        self.assertEqual(
            self.run_cli(
                [
                    "context",
                    "record",
                    "--task-id",
                    "demo",
                    "--phase",
                    "init",
                    "--context-id",
                    "demo-init",
                    "--source",
                    "README.md",
                    "--finding",
                    "Initial investigation",
                ]
            ),
            0,
        )
        source.write_text("changed\n", encoding="utf-8")

        result, stdout, stderr = self.run_cli_capture(["context", "preload", "--task-id", "demo"])

        self.assertEqual(result, 2)
        self.assertIn("Refresh required:", stdout)
        self.assertIn("README.md", stdout)
        self.assertEqual(stderr, "")

    def test_checkpoint_links_latest_context_for_task(self) -> None:
        (self.root / "README.md").write_text("ok\n", encoding="utf-8")
        self.assertEqual(
            self.run_cli(
                [
                    "context",
                    "record",
                    "--task-id",
                    "demo",
                    "--phase",
                    "plan",
                    "--context-id",
                    "demo-plan",
                    "--source",
                    "README.md",
                    "--finding",
                    "Readme loaded",
                ]
            ),
            0,
        )

        result = self.run_cli(
            [
                "checkpoint",
                "create",
                "--task-id",
                "demo",
                "--phase",
                "plan",
                "--summary",
                "planned",
            ]
        )

        self.assertEqual(result, 0)
        index = json.loads((self.root / ".yunshu" / "checkpoints" / "index.json").read_text(encoding="utf-8"))
        checkpoint_id = index["checkpoints"][0]["checkpoint_id"]
        checkpoint = json.loads(
            (self.root / ".yunshu" / "checkpoints" / checkpoint_id / "checkpoint.json").read_text(encoding="utf-8")
        )
        self.assertEqual(checkpoint["context_ledger"], ".yunshu/context/demo-plan.json")
        self.assertEqual(checkpoint["context_records"], ["demo-plan"])

    def test_checkpoint_list_filters_by_task_id(self) -> None:
        for task_id in ["demo", "other"]:
            self.assertEqual(
                self.run_cli(
                    [
                        "checkpoint",
                        "create",
                        "--task-id",
                        task_id,
                        "--phase",
                        "plan",
                        "--summary",
                        "planned",
                    ]
                ),
                0,
            )

        result, stdout, stderr = self.run_cli_capture(["checkpoint", "list", "--task-id", "demo"])

        self.assertEqual(result, 0)
        self.assertIn("demo-plan", stdout)
        self.assertNotIn("other-plan", stdout)
        self.assertEqual(stderr, "")

    def test_bmad_map_records_mapping_and_context(self) -> None:
        source = self.root / "PRD.md"
        source.write_text("# PRD\n\n## Goals\n\nShip it.\n", encoding="utf-8")

        result = self.run_cli(
            [
                "bmad",
                "map",
                "--task-id",
                "demo",
                "--kind",
                "prd",
                "--source",
                "PRD.md",
                "--map-id",
                "demo-prd-map",
                "--gap",
                "Need measurable DoD",
            ]
        )

        self.assertEqual(result, 0)
        mapping_path = self.root / ".yunshu" / "bmad" / "demo-prd-map.json"
        mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
        self.assertEqual(mapping["kind"], "prd")
        self.assertEqual(mapping["sections"][0]["headings"], ["1:PRD", "2:Goals"])
        self.assertRegex(mapping["sources"][0]["sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual(self.run_cli(["bmad", "validate", str(mapping_path)]), 0)
        self.assertEqual(self.run_cli(["bmad", "status", "demo-prd-map"]), 0)

        context_path = self.root / ".yunshu" / "context" / "demo-prd-map-context.json"
        context = json.loads(context_path.read_text(encoding="utf-8"))
        self.assertEqual(context["phase"], "plan")
        self.assertEqual(context["gaps"], ["Need measurable DoD"])

    def test_bmad_status_detects_stale_source(self) -> None:
        source = self.root / "story.md"
        source.write_text("# Story\n", encoding="utf-8")
        self.assertEqual(
            self.run_cli(
                [
                    "bmad",
                    "map",
                    "--task-id",
                    "demo",
                    "--kind",
                    "story",
                    "--source",
                    "story.md",
                    "--map-id",
                    "demo-story-map",
                ]
            ),
            0,
        )

        source.write_text("# Story\n\nchanged\n", encoding="utf-8")

        self.assertEqual(self.run_cli(["bmad", "status", "demo-story-map"]), 1)

    def test_transition_gate_rejects_skipped_phases(self) -> None:
        (self.root / "README.md").write_text("ok\n", encoding="utf-8")
        self.assertEqual(
            self.run_cli(
                [
                    "context",
                    "record",
                    "--task-id",
                    "demo",
                    "--phase",
                    "init",
                    "--context-id",
                    "demo-init",
                    "--source",
                    "README.md",
                    "--finding",
                    "Task card investigation",
                ]
            ),
            0,
        )

        result, stdout, stderr = self.run_cli_capture(
            ["gate", "transition", "--task-id", "demo", "--from-phase", "init", "--to-phase", "execute"]
        )

        self.assertEqual(result, 1)
        self.assertIn("invalid transition: init -> execute", stdout)
        self.assertEqual(stderr, "")

    def test_transition_gate_requires_user_alignment_before_plan(self) -> None:
        (self.root / "README.md").write_text("ok\n", encoding="utf-8")
        self.assertEqual(
            self.run_cli(
                [
                    "context",
                    "record",
                    "--task-id",
                    "demo",
                    "--phase",
                    "init",
                    "--context-id",
                    "demo-init",
                    "--source",
                    "README.md",
                    "--finding",
                    "Task card investigation",
                ]
            ),
            0,
        )

        result, stdout, stderr = self.run_cli_capture(
            ["gate", "transition", "--task-id", "demo", "--from-phase", "init", "--to-phase", "plan"]
        )

        self.assertEqual(result, 1)
        self.assertIn("requires explicit user alignment", stdout)
        self.assertIn("requires --task-card", stdout)
        self.assertIn("requires confirmed DoD", stdout)
        self.assertEqual(stderr, "")

    def test_transition_gate_allows_init_to_plan_after_alignment_and_fresh_context(self) -> None:
        (self.root / "README.md").write_text("ok\n", encoding="utf-8")
        self.assertEqual(
            self.run_cli(
                [
                    "context",
                    "record",
                    "--task-id",
                    "demo",
                    "--phase",
                    "init",
                    "--context-id",
                    "demo-init",
                    "--source",
                    "README.md",
                    "--finding",
                    "Task card investigation",
                ]
            ),
            0,
        )

        result, stdout, stderr = self.run_cli_capture(
            [
                "gate",
                "transition",
                "--task-id",
                "demo",
                "--from-phase",
                "init",
                "--to-phase",
                "plan",
                "--user-aligned",
                "--dod-confirmed",
                "--task-card",
                ".yunshu/context/demo-init.json",
            ]
        )

        self.assertEqual(result, 0)
        self.assertIn("Transition gate: PASSED", stdout)
        self.assertEqual(stderr, "")

    def test_transition_gate_rejects_missing_artifact_paths(self) -> None:
        (self.root / "README.md").write_text("ok\n", encoding="utf-8")
        self.assertEqual(
            self.run_cli(
                [
                    "context",
                    "record",
                    "--task-id",
                    "demo",
                    "--phase",
                    "init",
                    "--context-id",
                    "demo-init",
                    "--source",
                    "README.md",
                    "--finding",
                    "Task card investigation",
                ]
            ),
            0,
        )

        result, stdout, stderr = self.run_cli_capture(
            [
                "gate",
                "transition",
                "--task-id",
                "demo",
                "--from-phase",
                "init",
                "--to-phase",
                "plan",
                "--user-aligned",
                "--dod-confirmed",
                "--task-card",
                "missing-task-card.md",
            ]
        )

        self.assertEqual(result, 1)
        self.assertIn("task-card artifact does not exist: missing-task-card.md", stdout)
        self.assertEqual(stderr, "")

    def test_version_check_accepts_matching_adapter_versions(self) -> None:
        self.write_version_package()

        self.assertEqual(self.run_cli(["version-check"]), 0)

    def test_version_check_skips_missing_optional_adapter_files(self) -> None:
        root_version = "3.6.0"
        (self.root / "VERSION").write_text(root_version + "\n", encoding="utf-8")
        (self.root / "SKILL.md").write_text(
            f'---\nmetadata:\n  version: "{root_version}"\n---\n',
            encoding="utf-8",
        )
        (self.root / "README.md").write_text(
            f"[![Version](https://img.shields.io/badge/version-{root_version}-blue.svg)](x)\n",
            encoding="utf-8",
        )

        self.assertEqual(self.run_cli(["version-check"]), 0)

    def test_version_check_rejects_stale_adapter_versions(self) -> None:
        self.write_version_package(codex_version="3.4.0", trae_version="3.4.0")

        self.assertEqual(self.run_cli(["version-check"]), 1)


if __name__ == "__main__":
    unittest.main()
