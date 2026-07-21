#!/usr/bin/env python3
"""Record bounded internal v0.4-to-v0.5 verification timing evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import statistics
import subprocess
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    raise SystemExit(f"measure-v0-5-performance: error: {message}")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def median(values: list[int]) -> int:
    return int(statistics.median(values))


def run(command: list[str], expected: bytes | None = None) -> tuple[int, bytes]:
    started = time.monotonic_ns()
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    elapsed = time.monotonic_ns() - started
    if result.returncode:
        fail(f"command failed: {' '.join(command)}")
    if expected is not None and result.stdout != expected:
        fail("verification output was not canonical")
    return elapsed, result.stdout


def run_individual_32(command: list[str], expected: bytes) -> int:
    started = time.monotonic_ns()
    for _ in range(32):
        run(command, expected)
    return time.monotonic_ns() - started


def environment_record() -> dict[str, str]:
    return {
        "os": platform.system() or "unknown",
        "os_release": platform.release() or "unknown",
        "architecture": platform.machine() or "unknown",
        "cpu": platform.processor() or "unknown",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-bin", required=True, type=Path)
    parser.add_argument("--candidate-bin", required=True, type=Path)
    parser.add_argument("--source", default=ROOT / "schemas/examples/document.example.json", type=Path)
    parser.add_argument("--citations", default=ROOT / "examples/verify/native_grounded_citations.json", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    for binary, version in ((args.baseline_bin, "ethos 0.4.0"), (args.candidate_bin, "ethos 0.5.0")):
        if not binary.is_file() or binary.is_symlink() or not os.access(binary, os.X_OK):
            fail("binary must be regular executable")
        if subprocess.run([str(binary), "--version"], stdout=subprocess.PIPE).stdout.decode().strip() != version:
            fail(f"binary does not report {version}")

    baseline_command = [str(args.baseline_bin), "verify", str(args.source), "--citations", str(args.citations)]
    candidate_command = [str(args.candidate_bin), "verify", str(args.source), "--citations", str(args.citations)]
    _, expected = run(candidate_command)
    baseline: list[int] = []
    candidate: list[int] = []
    for sample in range(30):
        ordered = ((baseline_command, baseline), (candidate_command, candidate))
        if sample % 2:
            ordered = tuple(reversed(ordered))
        for command, samples in ordered:
            samples.append(run(command, expected)[0])

    with tempfile.TemporaryDirectory() as temporary:
        requests = Path(temporary) / "requests.ndjson"
        requests.write_bytes((args.citations.read_bytes().rstrip(b"\n") + b"\n") * 32)
        batch_command = [str(args.candidate_bin), "verify-batch", str(args.source), "--citations-ndjson", str(requests)]
        expected_batch = (expected.rstrip(b"\n") + b"\n") * 32
        run_individual_32(candidate_command, expected)  # non-recorded setup
        run(batch_command, expected_batch)  # non-recorded setup
        individual: list[int] = []
        batch: list[int] = []
        for sample in range(10):
            if sample % 2:
                batch.append(run(batch_command, expected_batch)[0])
                individual.append(run_individual_32(candidate_command, expected))
            else:
                individual.append(run_individual_32(candidate_command, expected))
                batch.append(run(batch_command, expected_batch)[0])

    baseline_median = median(baseline)
    candidate_median = median(candidate)
    individual_median = median(individual)
    batch_median = median(batch)
    passed = candidate_median * 100 <= baseline_median * 110 and batch_median * 2 <= individual_median
    if not passed:
        fail("performance threshold failed")
    record = {
        "schema": "ethos.v0_5_performance_record.v1",
        "baseline_version": "0.4.0",
        "candidate_version": "0.5.0",
        "baseline_binary_sha256": sha(args.baseline_bin),
        "candidate_binary_sha256": sha(args.candidate_bin),
        "source_sha256": sha(args.source),
        "citations_sha256": sha(args.citations),
        "environment": environment_record(),
        "single_request_cold_ns": {"baseline": baseline, "candidate": candidate},
        "batch_32_ns": {"individual_processes": individual, "batch_process": batch},
        "derived": {
            "baseline_median_ns": baseline_median,
            "candidate_median_ns": candidate_median,
            "individual_median_ns": individual_median,
            "batch_median_ns": batch_median,
            "passed": passed,
        },
    }
    args.out.write_text(json.dumps(record, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
