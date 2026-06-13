#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

import build_gate_zero_evidence
import gate_zero_gates
import run_gate_zero
import run_gate_zero_g3


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")


def fake_manifest(root: Path) -> Path:
    path = root / "benchmarks" / "gate-zero" / "manifest.json"
    write_json(
        path,
        {
            "corpus_id": "gate-zero-test",
            "determinism_platforms": ["macos-arm64", "linux-x64"],
            "corpus": [
                {
                    "id": "sample",
                    "file": "benchmarks/gate-zero/corpus/sample.pdf",
                    "sha256": "a" * 64,
                    "pages": 1,
                    "subsets": ["born_digital"],
                }
            ],
        },
    )
    return path


def fake_gates(root: Path) -> Path:
    path = root / "benchmarks" / "gate-zero" / "gates.json"
    write_json(
        path,
        {
            "schema_version": "ethos-gate-zero-gates-v1",
            "gates": {
                "g3": {
                    "id": "g3",
                    "status": "defined-not-run",
                    "completion_policy": "G3 cannot pass from a single platform result.",
                    "corpus_scope": "full frozen Gate Zero manifest",
                    "platforms": ["macos-arm64", "linux-x64"],
                    "required_evidence": ["equal warning_ids"],
                    "thresholds": {
                        "canonical_payload_divergences_allowed": 0,
                        "document_fingerprint_divergences_allowed": 0,
                    },
                }
            },
        },
    )
    return path


def fake_profile(root: Path) -> Path:
    path = root / "profiles" / "ethos-deterministic-v1.json"
    write_json(path, {"profile_id": "test-profile", "backend": {"id": "pdfium"}})
    return path


def fake_competitors(root: Path) -> Path:
    path = root / "benchmarks" / "competitors.lock.json"
    write_json(path, {"status": "FROZEN", "gate_zero": []})
    return path


def fake_g1_result(
    root: Path,
    platform: str,
    *,
    output_sha256: str = "b" * 64,
    document_fingerprint: str = "sha256:" + "c" * 64,
    warning_ids: list[str] | None = None,
) -> Path:
    path = root / "benchmarks" / "results" / "gate-zero" / platform / "g1.json"
    write_json(
        path,
        {
            "schema_version": "ethos-gate-zero-result-v1",
            "status": "pass",
            "corpus": {
                "id": "gate-zero-test",
                "manifest": "benchmarks/gate-zero/manifest.json",
                "manifest_sha256": run_gate_zero.sha256_file(root / "benchmarks" / "gate-zero" / "manifest.json"),
            },
            "host": {"selected": {"id": platform, "platform": platform}},
            "deterministic_profile_sha256": run_gate_zero.sha256_c14n_file(
                root / "profiles" / "ethos-deterministic-v1.json"
            ),
            "inputs": {},
            "runs": [
                {
                    "corpus_file": {
                        "actual_sha256": "a" * 64,
                        "file": "benchmarks/gate-zero/corpus/sample.pdf",
                        "id": "sample",
                        "pages": 1,
                        "sha256": "a" * 64,
                        "subsets": ["born_digital"],
                    },
                    "document_fingerprint": document_fingerprint,
                    "output_sha256": output_sha256,
                    "warning_ids": warning_ids or [],
                }
            ],
            "summary": {"status": "pass"},
        },
    )
    return path


def fake_args(root: Path, *, out: Path | None = None) -> Namespace:
    return Namespace(
        repo_root=root,
        manifest=root / "benchmarks" / "gate-zero" / "manifest.json",
        competitors_lock=root / "benchmarks" / "competitors.lock.json",
        gates=root / "benchmarks" / "gate-zero" / "gates.json",
        deterministic_profile=root / "profiles" / "ethos-deterministic-v1.json",
        platforms=None,
        platform_result=[],
        out=out or root / "benchmarks" / "results" / "gate-zero" / "g3.json",
        stdout=False,
    )


class GateZeroG3ResultTests(unittest.TestCase):
    def test_g3_result_passes_matching_platform_results(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fake_manifest(root)
            fake_gates(root)
            fake_profile(root)
            fake_competitors(root)
            fake_g1_result(root, "macos-arm64")
            fake_g1_result(root, "linux-x64")

            result = run_gate_zero_g3.build_g3_result(fake_args(root))

        self.assertEqual(result["status"], gate_zero_gates.PASS)
        self.assertEqual(result["summary"]["canonical_payload_divergences"], 0)
        self.assertEqual(result["summary"]["document_fingerprint_divergences"], 0)
        self.assertEqual(result["summary"]["warning_id_divergences"], 0)
        self.assertEqual(result["blockers"], [])
        self.assertEqual(result["failures"], [])

    def test_g3_result_fails_cross_platform_divergences(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fake_manifest(root)
            fake_gates(root)
            fake_profile(root)
            fake_competitors(root)
            fake_g1_result(root, "macos-arm64")
            fake_g1_result(
                root,
                "linux-x64",
                output_sha256="d" * 64,
                document_fingerprint="sha256:" + "e" * 64,
                warning_ids=["W001"],
            )

            result = run_gate_zero_g3.build_g3_result(fake_args(root))

        self.assertEqual(result["status"], gate_zero_gates.FAIL)
        self.assertEqual(result["summary"]["canonical_payload_divergences"], 1)
        self.assertEqual(result["summary"]["document_fingerprint_divergences"], 1)
        self.assertEqual(result["summary"]["warning_id_divergences"], 1)
        self.assertIn("sample canonical payload differs on linux-x64", result["failures"])
        self.assertIn("sample document fingerprint differs on linux-x64", result["failures"])
        self.assertIn("sample warning ids differ on linux-x64", result["failures"])

    def test_g3_result_blocks_missing_required_platform_result(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fake_manifest(root)
            fake_gates(root)
            fake_profile(root)
            fake_competitors(root)
            fake_g1_result(root, "macos-arm64")

            result = run_gate_zero_g3.build_g3_result(fake_args(root))

        self.assertEqual(result["status"], gate_zero_gates.BLOCKED)
        self.assertTrue(any("linux-x64 G1 result does not exist" in b for b in result["blockers"]))
        self.assertIn("missing required platform result: linux-x64", result["blockers"])
        self.assertEqual(result["failures"], [])

    def test_g3_evidence_bundle_has_complete_empty_reproduction_env(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fake_manifest(root)
            fake_gates(root)
            fake_profile(root)
            fake_competitors(root)
            fake_g1_result(root, "macos-arm64")
            fake_g1_result(root, "linux-x64")
            result = run_gate_zero_g3.build_g3_result(fake_args(root))
            result_path = root / "benchmarks" / "results" / "gate-zero" / "g3.json"
            write_json(result_path, result)

            report = build_gate_zero_evidence.build_evidence_bundle(
                repo_root=root,
                result_path=result_path,
                out_root=root / "benchmarks" / "results" / "gate-zero",
                platform_key="cross-platform",
                gate="g3",
                timestamp="20260613T120000Z",
                reproduction_command="python3 benchmarks/harness/run_gate_zero_g3.py ...",
                environment={},
                benchmark_commit="c" * 40,
            )
            bundle_dir = Path(report["bundle_dir"])
            reproduction_env = json.loads(
                (bundle_dir / "reproduction-env.json").read_text(encoding="utf-8")
            )
            summary = (bundle_dir / "SUMMARY.md").read_text(encoding="utf-8")
            checksum_failures = build_gate_zero_evidence.verify_checksums(bundle_dir)

            self.assertEqual(reproduction_env["status"], "complete")
            self.assertEqual(reproduction_env["blockers"], [])
            self.assertEqual(reproduction_env["variables"], [])
            self.assertIn("## Determinism Result", summary)
            self.assertEqual(checksum_failures, [])


if __name__ == "__main__":
    unittest.main()
