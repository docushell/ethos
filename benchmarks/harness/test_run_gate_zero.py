#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

import run_gate_zero


HEX = "a" * 64


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


def write_executable(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    path.chmod(path.stat().st_mode | 0o111)


def frozen_manifest(root: Path) -> Path:
    corpus_file = root / "benchmarks" / "gate-zero" / "corpus" / "sample.pdf"
    corpus_file.parent.mkdir(parents=True)
    corpus_file.write_bytes(b"%PDF-1.7\n")
    manifest_path = root / "manifest.json"
    write_json(
        manifest_path,
        {
            "manifest_version": "1.0.0",
            "status": "FROZEN-SIGNED",
            "frozen": True,
            "freeze_record": {
                "frozen_at": "2026-06-12T00:00:00Z",
                "signed_by": "benchmark owner",
            },
            "corpus_id": "gate-zero-test",
            "corpus": [
                {
                    "id": "sample",
                    "file": "benchmarks/gate-zero/corpus/sample.pdf",
                    "sha256": run_gate_zero.sha256_file(corpus_file),
                    "pages": 1,
                    "subsets": ["born_digital"],
                    "provenance": "synthetic",
                    "license": "CC0",
                }
            ],
            "hardware": [
                {
                    "id": "mac-m4pro-arm64",
                    "role": "performance",
                    "platform": "macos-arm64",
                    "model": "Mac (M4 Pro)",
                    "cpu": "Apple M4 Pro",
                    "ram": "48 GB",
                    "os": "macOS",
                    "kernel": "Darwin",
                    "runner": "local",
                }
            ],
        },
    )
    return manifest_path


def frozen_competitors(root: Path) -> Path:
    competitors_path = root / "competitors.lock.json"
    write_json(
        competitors_path,
        {
            "status": "FROZEN",
            "gate_zero": [
                {
                    "id": "opendataloader-pdf",
                    "version": "1.0.0",
                    "artifact_sha256": HEX,
                    "jvm_version": "21.0.1",
                    "pinned": True,
                },
                {
                    "id": "edgeparse",
                    "version": "2.0.0",
                    "artifact_sha256": HEX,
                    "pinned": True,
                },
                {
                    "id": "liteparse",
                    "version": "3.0.0",
                    "artifact_sha256": HEX,
                    "pinned": True,
                },
                {
                    "id": "pymupdf4llm",
                    "version": "0.1.0",
                    "python_version": "3.12.0",
                    "artifact_sha256": HEX,
                    "pinned": True,
                },
            ],
        },
    )
    return competitors_path


def fake_ethos(root: Path, unstable: bool = False, missing_fingerprint: bool = False) -> Path:
    script = root / "ethos"
    payload = {
        "fingerprint": "sha256:" + HEX,
        "payload": {
            "security_warnings": [],
            "parser_warnings": [],
        },
    }
    if missing_fingerprint:
        payload.pop("fingerprint")
    if unstable:
        text = """#!/usr/bin/env python3
import json, time
print(json.dumps({"fingerprint": "sha256:" + ("b" * 64), "payload": {"security_warnings": [], "parser_warnings": []}, "nonce": time.time()}))
"""
    else:
        text = f"""#!/usr/bin/env python3
import json
print(json.dumps({payload!r}, sort_keys=True))
"""
    write_executable(script, text)
    return script


def result_args(
    root: Path,
    manifest: Path,
    competitors: Path,
    ethos_bin: Path,
    profile: Path,
) -> Namespace:
    return Namespace(
        mode="ethos",
        repo_root=root,
        manifest=manifest,
        competitors_lock=competitors,
        out=root / "result.json",
        stdout=False,
        ethos_bin=ethos_bin,
        host_id="mac-m4pro-arm64",
        deterministic_profile=profile,
        install_path=ethos_bin,
        iterations=2,
        timeout_sec=5.0,
        opendataloader_root=None,
        opendataloader_command=None,
        opendataloader_artifact=None,
        opendataloader_install_path=None,
    )


def fake_odl(root: Path, *, fail: bool = False) -> Path:
    script = root / "opendataloader-pdf"
    if fail:
        text = """#!/usr/bin/env python3
import sys
print("intentional odl failure", file=sys.stderr)
raise SystemExit(7)
"""
    else:
        text = """#!/usr/bin/env python3
import json
import pathlib
import sys

args = sys.argv[1:]
output_dir = pathlib.Path(args[args.index("--output-dir") + 1])
input_pdf = pathlib.Path(args[-1])
output_dir.mkdir(parents=True, exist_ok=True)
(output_dir / f"{input_pdf.stem}.json").write_text(
    json.dumps({"file name": input_pdf.name, "kids": [{"content": "Hello"}]}, sort_keys=True),
    encoding="utf-8",
)
"""
    write_executable(script, text)
    return script


class GateZeroReadinessTests(unittest.TestCase):
    def test_draft_inputs_block_gate_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = root / "manifest.json"
            competitors_path = root / "competitors.lock.json"
            write_json(
                manifest_path,
                {
                    "status": "DRAFT-UNFROZEN",
                    "frozen": False,
                    "freeze_record": {"frozen_at": None, "signed_by": None},
                    "corpus": [],
                    "hardware": [
                        {
                            "id": "mac-m4pro-arm64",
                            "role": "performance",
                            "model": "Mac (M4 Pro)",
                            "cpu": None,
                            "ram": None,
                            "os": None,
                            "kernel": None,
                            "runner": None,
                        }
                    ],
                },
            )
            write_json(
                competitors_path,
                {
                    "status": "PIN-PENDING",
                    "gate_zero": [
                        {
                            "id": "opendataloader-pdf",
                            "version": None,
                            "artifact_sha256": None,
                            "jvm_version": None,
                            "pinned": False,
                        }
                    ],
                },
            )

            report = run_gate_zero.build_report(root, manifest_path, competitors_path)

        self.assertEqual(report["status"], "blocked")
        self.assertIn("Gate Zero manifest is not frozen", report["blockers"]["manifest"])
        self.assertIn("Gate Zero corpus[] is empty", report["blockers"]["manifest"])
        self.assertIn("hardware mac-m4pro-arm64 missing cpu", report["blockers"]["manifest"])
        self.assertIn("competitor opendataloader-pdf is not pinned", report["blockers"]["competitors"])
        self.assertIn(
            "competitor opendataloader-pdf missing jvm_version",
            report["blockers"]["competitors"],
        )

    def test_frozen_inputs_are_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = root / "manifest.json"
            competitors_path = root / "competitors.lock.json"
            write_json(
                manifest_path,
                {
                    "status": "FROZEN-SIGNED",
                    "frozen": True,
                    "freeze_record": {
                        "frozen_at": "2026-06-12T00:00:00Z",
                        "signed_by": "Gate Zero decider",
                    },
                    "corpus": [
                        {
                            "file": "sample.pdf",
                            "sha256": HEX,
                            "pages": 1,
                            "subsets": ["born_digital"],
                            "provenance": "synthetic",
                            "license": "CC0",
                        }
                    ],
                    "hardware": [
                        {
                            "id": "mac-m4pro-arm64",
                            "role": "performance",
                            "model": "Mac (M4 Pro)",
                            "cpu": "Apple M4 Pro",
                            "ram": "48 GB",
                            "os": "macOS 15.0",
                            "kernel": "Darwin 24.0.0",
                            "runner": "local",
                        }
                    ],
                },
            )
            write_json(
                competitors_path,
                {
                    "status": "PINNED",
                    "gate_zero": [
                        {
                            "id": "opendataloader-pdf",
                            "version": "1.2.3",
                            "artifact_sha256": HEX,
                            "jvm_version": "21.0.1",
                            "pinned": True,
                        },
                        {
                            "id": "edgeparse",
                            "version": "2.0.0",
                            "artifact_sha256": HEX,
                            "pinned": True,
                        },
                        {
                            "id": "liteparse",
                            "version": "3.0.0",
                            "artifact_sha256": HEX,
                            "pinned": True,
                        },
                        {
                            "id": "pymupdf4llm",
                            "version": "0.1.0",
                            "artifact_sha256": HEX,
                            "python_version": "3.12.0",
                            "pinned": True,
                        },
                    ],
                },
            )

            report = run_gate_zero.build_report(root, manifest_path, competitors_path)

        self.assertEqual(report["status"], "ready")
        self.assertEqual(report["summary"]["blockers_total"], 0)
        self.assertEqual(report["blockers"], {"manifest": [], "competitors": []})

    def test_blocked_inputs_do_not_invoke_ethos_result_runner(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = root / "manifest.json"
            competitors_path = root / "competitors.lock.json"
            profile = root / "profile.json"
            profile.write_text("{}", encoding="utf-8")
            ethos_bin = root / "ethos"
            write_executable(
                ethos_bin,
                "#!/usr/bin/env python3\nraise SystemExit('should not run')\n",
            )
            write_json(
                manifest_path,
                {
                    "status": "DRAFT-UNFROZEN",
                    "frozen": False,
                    "freeze_record": {"frozen_at": None, "signed_by": None},
                    "corpus": [],
                    "hardware": [],
                },
            )
            write_json(
                competitors_path,
                {"status": "PIN-PENDING", "gate_zero": []},
            )

            report = run_gate_zero.build_result_report(
                result_args(root, manifest_path, competitors_path, ethos_bin, profile)
            )

        self.assertEqual(report["status"], "blocked")
        self.assertEqual(report["runs"], [])
        self.assertIn("Gate Zero readiness is blocked", report["blockers"])

    def test_frozen_inputs_emit_ethos_result_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            profile = root / "profile.json"
            profile.write_text("{}", encoding="utf-8")
            manifest_path = frozen_manifest(root)
            competitors_path = frozen_competitors(root)
            ethos_bin = fake_ethos(root)

            report = run_gate_zero.build_result_report(
                result_args(root, manifest_path, competitors_path, ethos_bin, profile)
            )
            second_report = run_gate_zero.build_result_report(
                result_args(root, manifest_path, competitors_path, ethos_bin, profile)
            )

        self.assertEqual(report["schema_version"], "ethos-gate-zero-result-v1")
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["parser_target"], "ethos")
        self.assertEqual(report["summary"]["runs_total"], 1)
        self.assertEqual(report["runs"][0]["status"], "pass")
        self.assertEqual(report["runs"][0]["document_fingerprint"], "sha256:" + HEX)
        self.assertIsNotNone(report["output_sha256"])
        self.assertEqual(report["competitors"]["adapters"][0]["status"], "not_configured")
        self.assertEqual(report["output_sha256"], second_report["output_sha256"])
        self.assertNotIn(str(root), json.dumps(report))
        self.assertEqual(report["runs"][0]["command"][0], "ethos")
        self.assertEqual(report["runs"][0]["command"][3], "benchmarks/gate-zero/corpus/sample.pdf")
        self.assertEqual(report["inputs"]["deterministic_profile"], "profile.json")

    def test_output_hash_instability_fails_result(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            profile = root / "profile.json"
            profile.write_text("{}", encoding="utf-8")
            manifest_path = frozen_manifest(root)
            competitors_path = frozen_competitors(root)
            ethos_bin = fake_ethos(root, unstable=True)

            report = run_gate_zero.build_result_report(
                result_args(root, manifest_path, competitors_path, ethos_bin, profile)
            )

        self.assertEqual(report["status"], "fail")
        self.assertIn("output_sha256 changed across iterations", report["runs"][0]["failures"])

    def test_corpus_hash_mismatch_fails_before_invoking_ethos(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            profile = root / "profile.json"
            profile.write_text("{}", encoding="utf-8")
            manifest_path = frozen_manifest(root)
            competitors_path = frozen_competitors(root)
            ethos_bin = root / "ethos"
            write_executable(
                ethos_bin,
                "#!/usr/bin/env python3\nraise SystemExit('should not run')\n",
            )
            corpus_file = root / "benchmarks" / "gate-zero" / "corpus" / "sample.pdf"
            corpus_file.write_bytes(b"%PDF-1.7\nchanged\n")

            report = run_gate_zero.build_result_report(
                result_args(root, manifest_path, competitors_path, ethos_bin, profile)
            )

        self.assertEqual(report["status"], "fail")
        self.assertIn("corpus sha256 mismatch", report["runs"][0]["failures"][0])

    def test_missing_document_fingerprint_fails_result(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            profile = root / "profile.json"
            profile.write_text("{}", encoding="utf-8")
            manifest_path = frozen_manifest(root)
            competitors_path = frozen_competitors(root)
            ethos_bin = fake_ethos(root, missing_fingerprint=True)

            report = run_gate_zero.build_result_report(
                result_args(root, manifest_path, competitors_path, ethos_bin, profile)
            )

        self.assertEqual(report["status"], "fail")
        self.assertIn(
            "document fingerprint is missing or malformed",
            report["runs"][0]["failures"],
        )

    def test_opendataloader_adapter_is_ready_when_artifact_command_and_install_are_valid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            command = fake_odl(root)
            artifact = root / "opendataloader_pdf-1.0.0-py3-none-any.whl"
            artifact.write_bytes(b"artifact")
            artifact_sha256 = run_gate_zero.sha256_file(artifact)
            install_path = root / "venv"
            install_path.mkdir()
            lock = json.loads(frozen_competitors(root).read_text(encoding="utf-8"))
            lock["gate_zero"][0]["artifact_sha256"] = artifact_sha256

            adapter = run_gate_zero.build_opendataloader_adapter(
                command,
                artifact,
                install_path,
                run_gate_zero.opendataloader_lock_entry(lock),
            )

        self.assertEqual(adapter["status"], "ready")
        self.assertEqual(adapter["mode"], "execute")
        self.assertEqual(adapter["command"], "<opendataloader-command>")
        self.assertEqual(adapter["command_template"][0], "<opendataloader-command>")
        self.assertEqual(adapter["artifact"]["path"], "<opendataloader-artifact>")
        self.assertEqual(adapter["artifact"]["sha256"], artifact_sha256)
        self.assertIn("<input-pdf>", adapter["command_template"])

    def test_opendataloader_adapter_blocks_mismatched_artifact_hash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            command = fake_odl(root)
            artifact = root / "opendataloader_pdf-1.0.0-py3-none-any.whl"
            artifact.write_bytes(b"not the locked artifact")
            install_path = root / "venv"
            install_path.mkdir()
            lock = json.loads(frozen_competitors(root).read_text(encoding="utf-8"))

            adapter = run_gate_zero.build_opendataloader_adapter(
                command,
                artifact,
                install_path,
                run_gate_zero.opendataloader_lock_entry(lock),
            )

        self.assertEqual(adapter["status"], "blocked")
        self.assertIn(
            "opendataloader-pdf artifact sha256 does not match lock",
            adapter["blockers"],
        )

    def test_frozen_inputs_execute_opendataloader_competitor(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            profile = root / "profile.json"
            profile.write_text("{}", encoding="utf-8")
            manifest_path = frozen_manifest(root)
            competitors_path = frozen_competitors(root)
            ethos_bin = fake_ethos(root)
            odl_command = fake_odl(root)
            odl_artifact = root / "opendataloader_pdf-1.0.0-py3-none-any.whl"
            odl_artifact.write_bytes(b"artifact")
            lock = json.loads(competitors_path.read_text(encoding="utf-8"))
            lock["gate_zero"][0]["artifact_sha256"] = run_gate_zero.sha256_file(odl_artifact)
            write_json(competitors_path, lock)
            args = result_args(root, manifest_path, competitors_path, ethos_bin, profile)
            args.opendataloader_command = odl_command
            args.opendataloader_artifact = odl_artifact
            args.opendataloader_install_path = root

            report = run_gate_zero.build_result_report(args)

        runs = report["competitors"]["runs"]["opendataloader-pdf"]
        summary = report["competitors"]["summaries"]["opendataloader-pdf"]
        adapter = report["competitors"]["adapters"][0]
        self.assertEqual(report["status"], "pass")
        self.assertEqual(adapter["status"], "ready")
        self.assertEqual(adapter["mode"], "execute")
        self.assertEqual(summary["runs_total"], 1)
        self.assertEqual(summary["runs_failed"], 0)
        self.assertEqual(runs[0]["parser_target"], "opendataloader-pdf")
        self.assertIsNone(runs[0]["document_fingerprint"])
        self.assertEqual(runs[0]["warning_ids"], [])
        self.assertEqual(runs[0]["status"], "pass")
        self.assertEqual(runs[0]["failures"], [])
        self.assertRegex(runs[0]["output_sha256"], run_gate_zero.HEX64)
        self.assertNotIn(str(root), json.dumps(report))

    def test_opendataloader_competitor_failure_is_reported_as_data(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            profile = root / "profile.json"
            profile.write_text("{}", encoding="utf-8")
            manifest_path = frozen_manifest(root)
            competitors_path = frozen_competitors(root)
            ethos_bin = fake_ethos(root)
            odl_command = fake_odl(root, fail=True)
            odl_artifact = root / "opendataloader_pdf-1.0.0-py3-none-any.whl"
            odl_artifact.write_bytes(b"artifact")
            lock = json.loads(competitors_path.read_text(encoding="utf-8"))
            lock["gate_zero"][0]["artifact_sha256"] = run_gate_zero.sha256_file(odl_artifact)
            write_json(competitors_path, lock)
            args = result_args(root, manifest_path, competitors_path, ethos_bin, profile)
            args.opendataloader_command = odl_command
            args.opendataloader_artifact = odl_artifact
            args.opendataloader_install_path = root

            report = run_gate_zero.build_result_report(args)

        run = report["competitors"]["runs"]["opendataloader-pdf"][0]
        self.assertEqual(report["status"], "fail")
        self.assertEqual(run["status"], "fail")
        self.assertIn("exit 7:", run["failures"][0])

    def test_missing_deterministic_profile_blocks_result(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            profile = root / "missing-profile.json"
            manifest_path = frozen_manifest(root)
            competitors_path = frozen_competitors(root)
            ethos_bin = fake_ethos(root)

            report = run_gate_zero.build_result_report(
                result_args(root, manifest_path, competitors_path, ethos_bin, profile)
            )

        self.assertEqual(report["status"], "blocked")
        self.assertIn("deterministic profile is missing", report["blockers"])


if __name__ == "__main__":
    unittest.main()
