#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().with_name("gate_zero_evidence_preflight.py")
SPEC = importlib.util.spec_from_file_location("gate_zero_evidence_preflight", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
preflight = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = preflight
SPEC.loader.exec_module(preflight)

HEX = "a" * 64
TIMESTAMP = "20260616T120000Z"


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def init_git(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "-C", str(path), "init"], check=True, stdout=subprocess.DEVNULL)
    subprocess.run(
        ["git", "-C", str(path), "config", "user.email", "test@example.com"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(path), "config", "user.name", "Test User"],
        check=True,
    )
    write_text(path / "README.md", "# ethos-bench\n")
    subprocess.run(["git", "-C", str(path), "add", "README.md"], check=True)
    subprocess.run(
        ["git", "-C", str(path), "commit", "-m", "init"],
        check=True,
        stdout=subprocess.DEVNULL,
    )


def g1_result(platform: str) -> dict[str, object]:
    return {
        "schema_version": "ethos-gate-zero-result-v1",
        "status": "pass",
        "host": {"selected": {"platform": platform}},
        "summary": {"status": "pass"},
    }


def g2_result(platform: str) -> dict[str, object]:
    return {
        "schema_version": "ethos-gate-zero-g2-result-v1",
        "gate": "g2",
        "status": "pass",
        "platform": platform,
        "summary": {"status": "pass"},
    }


def g3_result() -> dict[str, object]:
    return {
        "schema_version": "ethos-gate-zero-g3-result-v1",
        "gate": "g3",
        "status": "pass",
        "platforms": ["macos-arm64", "linux-x64"],
        "summary": {"status": "pass"},
    }


def result_for(spec: preflight.ResultSpec) -> dict[str, object]:
    if spec.gate == "g1":
        return g1_result(spec.platform)
    if spec.gate == "g2":
        return g2_result(spec.platform)
    return g3_result()


def write_complete_bundle(bench: Path, spec: preflight.ResultSpec) -> None:
    result_path = bench / spec.result_path
    result_sha256 = preflight.sha256_file(result_path)
    bundle = bench / spec.evidence_root / TIMESTAMP
    write_text(bundle / "SUMMARY.md", "summary\n")
    write_text(bundle / "reproduction-command.txt", "make gate-zero\n")
    write_json(
        bundle / "reproduction-env.json",
        {
            "schema_version": "ethos-gate-zero-reproduction-env-v1",
            "status": "complete",
            "variables": [],
            "blockers": [],
        },
    )
    write_json(bundle / "host-attestation.json", {"source_result_sha256": result_sha256})
    write_json(
        bundle / "evidence-manifest.json",
        {
            "schema_version": "ethos-gate-zero-evidence-v1",
            "gate": spec.gate,
            "platform": spec.platform,
            "source_result_sha256": result_sha256,
        },
    )
    write_json(bundle / "raw" / f"{spec.gate}-{spec.platform}-{TIMESTAMP}.json", result_for(spec))
    checksum_rows = []
    for path in sorted(
        [
            bundle / "SUMMARY.md",
            bundle / "reproduction-command.txt",
            bundle / "reproduction-env.json",
            bundle / "host-attestation.json",
            bundle / "evidence-manifest.json",
            bundle / "raw" / f"{spec.gate}-{spec.platform}-{TIMESTAMP}.json",
        ],
        key=lambda item: item.relative_to(bundle).as_posix(),
    ):
        checksum_rows.append(
            f"{preflight.sha256_file(path)}  {path.relative_to(bundle).as_posix()}\n"
        )
    write_text(bundle / "SHA256SUMS", "".join(checksum_rows))
    write_json(
        bundle / "SHA256SUMS.digest.json",
        {
            "schema_version": "ethos-gate-zero-checksum-digest-v1",
            "digest_type": "sha256",
            "payload": "SHA256SUMS",
            "payload_sha256": preflight.sha256_file(bundle / "SHA256SUMS"),
        },
    )


class GateZeroEvidencePreflightTests(unittest.TestCase):
    def test_prepare_blocks_generated_results_in_ethos_and_missing_bench(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "ethos"
            write_text(root / "benchmarks/results/gate-zero/README.md", "# pointer\n")
            write_json(root / "benchmarks/results/gate-zero/macos-arm64/g1.json", {})

            gate = preflight.run("prepare", repo_root=root, ethos_bench=Path(tmp) / "ethos-bench")

        self.assertTrue(
            any("generated Gate Zero output must live in ethos-bench" in f for f in gate.failures)
        )
        self.assertTrue(any("ethos-bench checkout does not exist" in f for f in gate.failures))

    def test_prepare_requires_clean_ethos_bench_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "ethos"
            write_text(root / "benchmarks/results/gate-zero/README.md", "# pointer\n")
            bench = Path(tmp) / "ethos-bench"
            init_git(bench)
            write_text(bench / "untracked.txt", "dirty\n")

            gate = preflight.run("prepare", repo_root=root, ethos_bench=bench)

        self.assertIn(
            "ethos-bench checkout is not clean before controlled output generation",
            gate.failures,
        )

    def test_decision_blocks_missing_result_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "ethos"
            write_text(root / "benchmarks/results/gate-zero/README.md", "# pointer\n")
            bench = Path(tmp) / "ethos-bench"
            init_git(bench)

            gate = preflight.run("decision", repo_root=root, ethos_bench=bench)

        self.assertTrue(any("missing Gate Zero G1 result" in f for f in gate.failures))
        self.assertTrue(any("missing Gate Zero G2 result" in f for f in gate.failures))
        self.assertTrue(any("missing Gate Zero G3 result" in f for f in gate.failures))

    def test_decision_green_with_complete_results_and_bundles(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "ethos"
            write_text(root / "benchmarks/results/gate-zero/README.md", "# pointer\n")
            bench = Path(tmp) / "ethos-bench"
            init_git(bench)
            for spec in preflight.RESULT_SPECS:
                write_json(bench / spec.result_path, result_for(spec))
                write_complete_bundle(bench, spec)

            gate = preflight.run("decision", repo_root=root, ethos_bench=bench)

        self.assertEqual(gate.failures, [])

    def test_decision_blocks_incomplete_evidence_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "ethos"
            write_text(root / "benchmarks/results/gate-zero/README.md", "# pointer\n")
            bench = Path(tmp) / "ethos-bench"
            init_git(bench)
            for spec in preflight.RESULT_SPECS:
                write_json(bench / spec.result_path, result_for(spec))
                write_complete_bundle(bench, spec)
            env_path = (
                bench
                / "benchmarks/results/gate-zero/macos-arm64/evidence/g1"
                / TIMESTAMP
                / "reproduction-env.json"
            )
            write_json(
                env_path,
                {
                    "schema_version": "ethos-gate-zero-reproduction-env-v1",
                    "status": "incomplete",
                    "variables": [],
                    "blockers": ["missing env"],
                },
            )

            gate = preflight.run("decision", repo_root=root, ethos_bench=bench)

        self.assertTrue(any("status is not complete" in failure for failure in gate.failures))
        self.assertTrue(any("sha256 mismatch" in failure for failure in gate.failures))


if __name__ == "__main__":
    unittest.main()
