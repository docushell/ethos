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
        edgeparse_command=None,
        edgeparse_artifact=None,
        edgeparse_install_path=None,
        liteparse_command=None,
        liteparse_artifact=None,
        liteparse_install_path=None,
        pymupdf4llm_python=None,
        pymupdf4llm_artifact=None,
        pymupdf4llm_install_path=None,
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


def fake_edgeparse(root: Path) -> Path:
    script = root / "edgeparse"
    text = """#!/usr/bin/env python3
import json
import pathlib
import sys

args = sys.argv[1:]
input_pdf = pathlib.Path(args[0])
output_dir = pathlib.Path(args[args.index("--output-dir") + 1])
output_dir.mkdir(parents=True, exist_ok=True)
(output_dir / f"{input_pdf.stem}.json").write_text(
    json.dumps({"source": "edgeparse", "file": input_pdf.name}, sort_keys=True),
    encoding="utf-8",
)
"""
    write_executable(script, text)
    return script


def fake_liteparse(root: Path) -> Path:
    script = root / "lit"
    text = """#!/usr/bin/env python3
import json
import pathlib
import sys

args = sys.argv[1:]
input_pdf = pathlib.Path(args[1])
output_file = pathlib.Path(args[args.index("--output") + 1])
output_file.parent.mkdir(parents=True, exist_ok=True)
output_file.write_text(
    json.dumps({"source": "liteparse", "file": input_pdf.name}, sort_keys=True),
    encoding="utf-8",
)
"""
    write_executable(script, text)
    return script


def fake_pymupdf4llm(root: Path) -> Path:
    script = root / "python"
    text = """#!/usr/bin/env python3
import json
import pathlib
import sys

input_pdf = pathlib.Path(sys.argv[-1])
print(json.dumps({"source": "pymupdf4llm", "file": input_pdf.name}, sort_keys=True))
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
        self.assertEqual(
            set(report["competitors"]["runs"]),
            set(run_gate_zero.COMPETITOR_IDS),
        )
        self.assertEqual(
            set(report["competitors"]["summaries"]),
            set(run_gate_zero.COMPETITOR_IDS),
        )
        self.assertTrue(
            all(adapter["status"] == "not_configured" for adapter in report["competitors"]["adapters"])
        )
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
        self.assertEqual(adapter["artifact"]["path"], "<opendataloader-pdf-artifact>")
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

    def test_lock_artifact_hash_prefers_requested_platform_artifact(self) -> None:
        lock_entry = {
            "artifact_sha256": "a" * 64,
            "platform_artifacts": {
                "macos-arm64": {
                    "artifact_filename": "package-macos.whl",
                    "artifact_sha256": "b" * 64,
                },
                "linux-x64": {
                    "artifact_filename": "package-linux.whl",
                    "artifact_sha256": "c" * 64,
                },
            },
        }

        self.assertEqual(run_gate_zero.lock_artifact_hash(lock_entry, "macos-arm64"), "b" * 64)
        self.assertEqual(run_gate_zero.lock_artifact_hash(lock_entry, "linux-x64"), "c" * 64)
        self.assertEqual(run_gate_zero.lock_artifact_hash(lock_entry, "windows-x64"), "a" * 64)

    def test_competitor_adapter_uses_selected_platform_artifact_hash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            command = fake_edgeparse(root)
            artifact = root / "edgeparse-0.2.5-linux.whl"
            artifact.write_bytes(b"linux artifact")
            artifact_sha256 = run_gate_zero.sha256_file(artifact)
            install_path = root / "venv"
            install_path.mkdir()
            lock_entry = {
                "id": "edgeparse",
                "version": "0.2.5",
                "artifact_sha256": "a" * 64,
                "pinned": True,
                "platform_artifacts": {
                    "macos-arm64": {
                        "artifact_filename": "edgeparse-0.2.5-macos.whl",
                        "artifact_sha256": "b" * 64,
                    },
                    "linux-x64": {
                        "artifact_filename": artifact.name,
                        "artifact_sha256": artifact_sha256,
                    },
                },
            }

            adapter = run_gate_zero.build_competitor_adapter(
                "edgeparse",
                command,
                artifact,
                install_path,
                lock_entry,
                "linux-x64",
            )

        self.assertEqual(adapter["status"], "ready")
        self.assertEqual(adapter["artifact"]["sha256"], artifact_sha256)
        self.assertEqual(adapter["artifact"]["expected_sha256"], artifact_sha256)

    def test_result_report_selects_artifact_hash_from_selected_host_platform(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            profile = root / "profile.json"
            profile.write_text("{}", encoding="utf-8")
            manifest_path = frozen_manifest(root)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["hardware"][0]["id"] = "linux-x64-1"
            manifest["hardware"][0]["platform"] = "linux-x64"
            write_json(manifest_path, manifest)
            competitors_path = frozen_competitors(root)
            ethos_bin = fake_ethos(root)
            edgeparse_command = fake_edgeparse(root)
            edgeparse_artifact = root / "edgeparse-0.2.5-linux.whl"
            edgeparse_artifact.write_bytes(b"linux artifact")
            linux_sha256 = run_gate_zero.sha256_file(edgeparse_artifact)
            lock = json.loads(competitors_path.read_text(encoding="utf-8"))
            edgeparse_entry = next(entry for entry in lock["gate_zero"] if entry["id"] == "edgeparse")
            edgeparse_entry["platform_artifacts"] = {
                "macos-arm64": {
                    "artifact_filename": "edgeparse-0.2.5-macos.whl",
                    "artifact_sha256": "b" * 64,
                },
                "linux-x64": {
                    "artifact_filename": edgeparse_artifact.name,
                    "artifact_sha256": linux_sha256,
                },
            }
            write_json(competitors_path, lock)
            args = result_args(root, manifest_path, competitors_path, ethos_bin, profile)
            args.host_id = "linux-x64-1"
            args.edgeparse_command = edgeparse_command
            args.edgeparse_artifact = edgeparse_artifact
            args.edgeparse_install_path = root

            report = run_gate_zero.build_result_report(args)

        adapters = {adapter["id"]: adapter for adapter in report["competitors"]["adapters"]}
        self.assertEqual(report["status"], "pass")
        self.assertEqual(adapters["edgeparse"]["status"], "ready")
        self.assertEqual(adapters["edgeparse"]["artifact"]["expected_sha256"], linux_sha256)

    def test_check_competitors_validates_platform_artifact_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            lock = json.loads(frozen_competitors(Path(tmp)).read_text(encoding="utf-8"))
            lock["gate_zero"][1]["platform_artifacts"] = {
                "linux-x64": {
                    "artifact_filename": "",
                    "artifact_sha256": "not-a-sha",
                }
            }

            blockers = run_gate_zero.check_competitors(lock)

        self.assertIn(
            "competitor edgeparse platform_artifacts.linux-x64 "
            "artifact_sha256 is not lowercase hex",
            blockers,
        )
        self.assertIn(
            "competitor edgeparse platform_artifacts.linux-x64 missing artifact_filename",
            blockers,
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

    def test_frozen_inputs_execute_all_configured_competitors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            profile = root / "profile.json"
            profile.write_text("{}", encoding="utf-8")
            manifest_path = frozen_manifest(root)
            competitors_path = frozen_competitors(root)
            ethos_bin = fake_ethos(root)
            args = result_args(root, manifest_path, competitors_path, ethos_bin, profile)
            args.opendataloader_command = fake_odl(root)
            args.edgeparse_command = fake_edgeparse(root)
            args.liteparse_command = fake_liteparse(root)
            args.pymupdf4llm_python = fake_pymupdf4llm(root)

            lock = json.loads(competitors_path.read_text(encoding="utf-8"))
            artifact_paths: dict[str, Path] = {}
            for entry in lock["gate_zero"]:
                artifact = root / f"{entry['id']}.artifact"
                artifact.write_bytes(f"{entry['id']} artifact".encode("utf-8"))
                entry["artifact_sha256"] = run_gate_zero.sha256_file(artifact)
                artifact_paths[entry["id"]] = artifact
            write_json(competitors_path, lock)

            args.opendataloader_artifact = artifact_paths["opendataloader-pdf"]
            args.opendataloader_install_path = root
            args.edgeparse_artifact = artifact_paths["edgeparse"]
            args.edgeparse_install_path = root
            args.liteparse_artifact = artifact_paths["liteparse"]
            args.liteparse_install_path = root
            args.pymupdf4llm_artifact = artifact_paths["pymupdf4llm"]
            args.pymupdf4llm_install_path = root

            report = run_gate_zero.build_result_report(args)

        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["parser_target"], "ethos")
        self.assertEqual(report["summary"]["runs_total"], 1)
        self.assertEqual(set(report["competitors"]["runs"]), set(run_gate_zero.COMPETITOR_IDS))
        self.assertEqual(set(report["competitors"]["summaries"]), set(run_gate_zero.COMPETITOR_IDS))
        adapters = {adapter["id"]: adapter for adapter in report["competitors"]["adapters"]}
        self.assertEqual(set(adapters), set(run_gate_zero.COMPETITOR_IDS))
        for competitor_id in run_gate_zero.COMPETITOR_IDS:
            self.assertEqual(adapters[competitor_id]["status"], "ready")
            self.assertEqual(adapters[competitor_id]["mode"], "execute")
            summary = report["competitors"]["summaries"][competitor_id]
            runs = report["competitors"]["runs"][competitor_id]
            self.assertEqual(summary["runs_total"], 1)
            self.assertEqual(summary["runs_failed"], 0)
            self.assertEqual(runs[0]["parser_target"], competitor_id)
            self.assertEqual(runs[0]["status"], "pass")
            self.assertRegex(runs[0]["output_sha256"], run_gate_zero.HEX64)
        self.assertNotIn(str(root), json.dumps(report))

    def test_pymupdf4llm_runner_preserves_configured_python_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            profile = root / "profile.json"
            profile.write_text("{}", encoding="utf-8")
            manifest_path = frozen_manifest(root)
            competitors_path = frozen_competitors(root)
            ethos_bin = fake_ethos(root)
            base_python = root / "base-python"
            write_executable(
                base_python,
                """#!/usr/bin/env python3
import json
import sys

if not sys.argv[0].endswith("/venv/bin/python"):
    raise SystemExit(9)
print(json.dumps({"source": "pymupdf4llm", "argv0": sys.argv[0]}, sort_keys=True))
""",
            )
            venv_bin = root / "venv" / "bin"
            venv_bin.mkdir(parents=True)
            venv_python = venv_bin / "python"
            venv_python.symlink_to(base_python)

            lock = json.loads(competitors_path.read_text(encoding="utf-8"))
            pymupdf_entry = next(entry for entry in lock["gate_zero"] if entry["id"] == "pymupdf4llm")
            artifact = root / "pymupdf4llm.artifact"
            artifact.write_bytes(b"pymupdf4llm artifact")
            pymupdf_entry["artifact_sha256"] = run_gate_zero.sha256_file(artifact)
            write_json(competitors_path, lock)

            args = result_args(root, manifest_path, competitors_path, ethos_bin, profile)
            args.pymupdf4llm_python = venv_python
            args.pymupdf4llm_artifact = artifact
            args.pymupdf4llm_install_path = root / "venv"

            report = run_gate_zero.build_result_report(args)

        run = report["competitors"]["runs"]["pymupdf4llm"][0]
        self.assertEqual(report["status"], "pass")
        self.assertEqual(run["status"], "pass")

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
