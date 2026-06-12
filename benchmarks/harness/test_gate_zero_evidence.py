#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import build_gate_zero_evidence
import run_gate_zero


ROOT = Path(__file__).resolve().parents[2]
REAL_MACOS_G1 = ROOT / "benchmarks" / "results" / "gate-zero" / "macos-arm64" / "g1.json"
TIMESTAMP = "20260612T081702Z"
BENCHMARK_COMMIT = "c68389c28535bbab74a1efbe5bd923c8ff4ec341"
REPRODUCTION_COMMAND = (
    "python3 benchmarks/harness/run_gate_zero.py --mode ethos --repo-root . "
    "--manifest benchmarks/gate-zero/manifest.json "
    "--competitors-lock benchmarks/competitors.lock.json "
    "--host-id mac-m4pro-arm64 "
    "--deterministic-profile profiles/ethos-deterministic-v1.json "
    "--ethos-bin target/release/ethos --install-path target/release/ethos "
    "--iterations 3 --out benchmarks/results/gate-zero/macos-arm64/g1.json"
)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")


def build_real_bundle(out_root: Path) -> Path:
    report = build_gate_zero_evidence.build_evidence_bundle(
        repo_root=ROOT,
        result_path=REAL_MACOS_G1,
        out_root=out_root,
        platform_key="macos-arm64",
        gate="g1",
        timestamp=TIMESTAMP,
        reproduction_command=REPRODUCTION_COMMAND,
        benchmark_commit=BENCHMARK_COMMIT,
    )
    return Path(report["bundle_dir"])


class GateZeroEvidenceBundleTests(unittest.TestCase):
    def test_evidence_bundle_from_existing_macos_g1_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle_dir = build_real_bundle(Path(tmp))
            raw_path = bundle_dir / "raw" / f"g1-macos-arm64-{TIMESTAMP}.json"
            summary_path = bundle_dir / "SUMMARY.md"
            host_path = bundle_dir / "host-attestation.json"
            manifest_path = bundle_dir / "evidence-manifest.json"
            checksums_path = bundle_dir / "SHA256SUMS"
            digest_path = bundle_dir / "SHA256SUMS.digest.json"

            self.assertEqual(bundle_dir.name, TIMESTAMP)
            self.assertEqual(bundle_dir.parent.name, "g1")
            self.assertTrue(raw_path.is_file())
            self.assertTrue(summary_path.is_file())
            self.assertTrue(host_path.is_file())
            self.assertTrue(manifest_path.is_file())
            self.assertTrue(checksums_path.is_file())
            self.assertTrue(digest_path.is_file())
            self.assertEqual(raw_path.read_bytes(), REAL_MACOS_G1.read_bytes())
            self.assertEqual(build_gate_zero_evidence.verify_checksums(bundle_dir), [])

            digest = json.loads(digest_path.read_text(encoding="utf-8"))
            self.assertEqual(digest["digest_type"], "sha256")
            self.assertEqual(digest["payload"], "SHA256SUMS")
            self.assertEqual(digest["payload_sha256"], run_gate_zero.sha256_file(checksums_path))
            self.assertIn("not a public-key signature", digest["note"])

    def test_host_attestation_matches_result(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle_dir = build_real_bundle(Path(tmp))
            attestation = json.loads(
                (bundle_dir / "host-attestation.json").read_text(encoding="utf-8")
            )
            result = json.loads(REAL_MACOS_G1.read_text(encoding="utf-8"))

            self.assertEqual(attestation["platform"], "macos-arm64")
            self.assertEqual(attestation["gate"], "g1")
            self.assertEqual(attestation["benchmark_commit"], BENCHMARK_COMMIT)
            self.assertEqual(attestation["result_host"], result["host"])
            self.assertEqual(attestation["result_inputs"], result["inputs"])
            self.assertEqual(attestation["source_result_sha256"], run_gate_zero.sha256_file(REAL_MACOS_G1))
            self.assertEqual(
                attestation["source_result_canonical_sha256"],
                run_gate_zero.sha256_c14n_value(result),
            )
            self.assertEqual(attestation["result_host"]["selected"]["id"], "mac-m4pro-arm64")

    def test_human_summary_preserves_edgeparse_failure_truth(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle_dir = build_real_bundle(Path(tmp))
            summary = (bundle_dir / "SUMMARY.md").read_text(encoding="utf-8")

            self.assertIn("Overall status: `fail`", summary)
            self.assertIn("Ethos status: `pass`", summary)
            self.assertIn("| Ethos | `pass` | 0/10 |", summary)
            self.assertIn("| EdgeParse | `fail` | 3/10 |", summary)
            self.assertIn("EdgeParse is recorded as a context/non-gating competitor row", summary)
            self.assertIn("`output_sha256 changed across iterations`", summary)
            self.assertIn("`cfpb-home-loan-toolkit`", summary)
            self.assertIn("`nist-sp-800-53r5`", summary)
            self.assertIn("`nist-sp-800-63b`", summary)
            self.assertIn("Ethos passed all top-level G1 determinism checks", summary)
            self.assertIn("does not claim Ethos is the fastest parser overall", summary)

    def test_checksum_verifier_detects_tampered_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle_dir = build_real_bundle(Path(tmp))
            summary_path = bundle_dir / "SUMMARY.md"
            summary_path.write_text(
                summary_path.read_text(encoding="utf-8") + "\ntampered\n",
                encoding="utf-8",
            )

            failures = build_gate_zero_evidence.verify_checksums(bundle_dir)

        self.assertEqual(len(failures), 1)
        self.assertIn("SUMMARY.md sha256 mismatch", failures[0])

    def test_blank_reproduction_command_fails_without_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_root = Path(tmp) / "out"

            with self.assertRaisesRegex(ValueError, "reproduction command is required"):
                build_gate_zero_evidence.build_evidence_bundle(
                    repo_root=ROOT,
                    result_path=REAL_MACOS_G1,
                    out_root=out_root,
                    platform_key="macos-arm64",
                    gate="g1",
                    timestamp=TIMESTAMP,
                    reproduction_command="",
                )

        self.assertFalse(out_root.exists())

    def test_missing_result_file_fails_without_partial_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out_root = root / "out"

            with self.assertRaisesRegex(FileNotFoundError, "result JSON does not exist"):
                build_gate_zero_evidence.build_evidence_bundle(
                    repo_root=root,
                    result_path=root / "missing-g1.json",
                    out_root=out_root,
                    platform_key="macos-arm64",
                    gate="g1",
                    timestamp=TIMESTAMP,
                    reproduction_command=REPRODUCTION_COMMAND,
                )

        self.assertFalse(out_root.exists())

    def test_bad_json_fails_with_filename(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result_path = root / "g1.json"
            result_path.write_text("{bad json", encoding="utf-8")
            out_root = root / "out"

            with self.assertRaisesRegex(ValueError, "result JSON is invalid: .*g1.json"):
                build_gate_zero_evidence.build_evidence_bundle(
                    repo_root=root,
                    result_path=result_path,
                    out_root=out_root,
                    platform_key="macos-arm64",
                    gate="g1",
                    timestamp=TIMESTAMP,
                    reproduction_command=REPRODUCTION_COMMAND,
                )

        self.assertFalse(out_root.exists())

    def test_git_status_filter_ignores_bundle_output_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            evidence_root = root / "benchmarks" / "results" / "gate-zero" / "macos-arm64" / "evidence"
            bundle_dir = evidence_root / "g1" / TIMESTAMP

            self.assertTrue(
                build_gate_zero_evidence.is_ignored_status_line(
                    root,
                    f"?? {evidence_root.relative_to(root).as_posix()}/",
                    [evidence_root],
                )
            )
            self.assertTrue(
                build_gate_zero_evidence.is_ignored_status_line(
                    root,
                    f" M {bundle_dir.relative_to(root).as_posix()}/SUMMARY.md",
                    [evidence_root],
                )
            )
            self.assertFalse(
                build_gate_zero_evidence.is_ignored_status_line(
                    root,
                    " M benchmarks/harness/build_gate_zero_evidence.py",
                    [evidence_root],
                )
            )

    def test_schema_invalid_result_fails_without_partial_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result_path = root / "g1.json"
            write_json(result_path, {"schema_version": "ethos-gate-zero-result-v1"})
            out_root = root / "out"

            with self.assertRaisesRegex(ValueError, "missing required keys"):
                build_gate_zero_evidence.build_evidence_bundle(
                    repo_root=root,
                    result_path=result_path,
                    out_root=out_root,
                    platform_key="macos-arm64",
                    gate="g1",
                    timestamp=TIMESTAMP,
                    reproduction_command=REPRODUCTION_COMMAND,
                )

        self.assertFalse(out_root.exists())


if __name__ == "__main__":
    unittest.main()
