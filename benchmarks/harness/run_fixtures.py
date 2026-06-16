#!/usr/bin/env python3
#
# Copyright 2026 The Ethos maintainers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""Run Ethos over the fixture corpus and emit harness JSON.

This is the first WS-HARNESS runner. It is deliberately fixture-scoped:
successful PDFs are parsed through the public CLI, then checked against the
stage goldens committed beside each fixture. Failure fixtures are checked
against their stable error envelope. Gate Zero G1/G2/G3 reporting builds on
this once the frozen corpus and competitor pins are complete.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / "fixtures" / "manifest.json"
DEFAULT_RESULTS = ROOT / "benchmarks" / "results" / "fixtures" / "baseline.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path | None, value: Any) -> None:
    text = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)
    if path is None:
        print(text)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{text}\n", encoding="utf-8")


def percentile(values: list[float], pct: float) -> float | None:
    if not values:
        return None
    if len(values) == 1:
        return values[0]
    ordered = sorted(values)
    rank = (len(ordered) - 1) * pct
    lower = int(rank)
    upper = min(lower + 1, len(ordered) - 1)
    weight = rank - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def c14n_projection_from_document(doc: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    payload = doc["payload"]
    extraction_spans = []
    for span in payload["spans"]:
        projected = dict(span)
        projected.pop("char_start", None)
        projected.pop("char_end", None)
        extraction_spans.append(projected)

    extraction = {
        "pages": payload["pages"],
        "regions": payload["regions"],
        "spans": extraction_spans,
        "warnings": payload["parser_warnings"],
    }
    layout = {
        "elements": payload["elements"],
        "warnings": [],
    }
    return extraction, layout


def check_equal(name: str, actual: Any, expected: Any, failures: list[str]) -> None:
    if actual != expected:
        failures.append(f"{name} does not match golden")


def run_command(args: list[str], timeout_sec: float) -> tuple[subprocess.CompletedProcess[bytes] | None, float, str | None]:
    start = time.perf_counter()
    try:
        completed = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_sec,
            check=False,
        )
        return completed, (time.perf_counter() - start) * 1000.0, None
    except subprocess.TimeoutExpired:
        return None, (time.perf_counter() - start) * 1000.0, "timeout"


def success_fixture_result(
    ethos_bin: Path,
    fixtures_root: Path,
    entry: dict[str, Any],
    iterations: int,
    timeout_sec: float,
) -> dict[str, Any]:
    fixture_file = fixtures_root / entry["file"]
    fixture_dir = fixture_file.parent
    extraction_golden = load_json(fixture_dir / "extraction.json")
    layout_golden = load_json(fixture_dir / "layout.json")

    durations = []
    failures: list[str] = []
    first_doc: dict[str, Any] | None = None
    stdout_bytes = 0

    for _ in range(iterations):
        completed, duration_ms, timeout = run_command(
            [str(ethos_bin), "doc", "parse", str(fixture_file), "--format", "json"],
            timeout_sec,
        )
        durations.append(duration_ms)
        if timeout is not None:
            failures.append(f"command timed out after {timeout_sec:g}s")
            continue
        assert completed is not None
        stdout_bytes = len(completed.stdout)
        if completed.returncode != 0:
            stderr = completed.stderr.decode("utf-8", errors="replace").strip()
            failures.append(f"expected success, got exit {completed.returncode}: {stderr}")
            continue
        try:
            doc = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            failures.append(f"stdout is not JSON: {exc}")
            continue
        if first_doc is None:
            first_doc = doc
        elif doc.get("fingerprint") != first_doc.get("fingerprint"):
            failures.append("fingerprint changed across iterations")

    if first_doc is not None:
        extraction, layout = c14n_projection_from_document(first_doc)
        check_equal("extraction", extraction, extraction_golden, failures)
        check_equal("layout", layout, layout_golden, failures)

    pages = len(first_doc["payload"]["pages"]) if first_doc is not None else entry["pages"]
    p50 = percentile(durations, 0.50)
    pages_per_second = (pages * 1000.0 / p50) if p50 and p50 > 0 else None
    return {
        "id": entry["id"],
        "file": entry["file"],
        "subsets": entry["subsets"],
        "kind": "success",
        "status": "pass" if not failures else "fail",
        "failures": failures,
        "metrics": {
            "iterations": iterations,
            "duration_ms_p50": p50,
            "duration_ms_p95": percentile(durations, 0.95),
            "duration_ms_p99": percentile(durations, 0.99),
            "pages": pages,
            "pages_per_second_p50": pages_per_second,
            "stdout_bytes": stdout_bytes,
        },
        "fingerprint": first_doc.get("fingerprint") if first_doc else None,
        "payload_sha256": first_doc.get("payload_sha256") if first_doc else None,
        "source_fingerprint": first_doc["source"]["fingerprint"] if first_doc else None,
    }


def failure_fixture_result(
    ethos_bin: Path,
    fixtures_root: Path,
    entry: dict[str, Any],
    timeout_sec: float,
) -> dict[str, Any]:
    fixture_file = fixtures_root / entry["file"]
    metadata = load_json(fixture_file.parent / "fixture.json")
    expected = metadata.get("expected_error", {})
    failures: list[str] = []
    completed, duration_ms, timeout = run_command(
        [str(ethos_bin), "doc", "parse", str(fixture_file), "--format", "json"],
        timeout_sec,
    )
    envelope: dict[str, Any] | None = None
    if timeout is not None:
        failures.append(f"command timed out after {timeout_sec:g}s")
    else:
        assert completed is not None
        if completed.returncode == 0:
            failures.append("expected stable failure, got success")
        if completed.stdout:
            failures.append("failure fixture wrote stdout")
        try:
            envelope = json.loads(completed.stderr)
        except json.JSONDecodeError as exc:
            failures.append(f"stderr is not JSON: {exc}")
        if envelope is not None:
            error = envelope.get("error", {})
            if error.get("code") != expected.get("code"):
                failures.append(f"error code {error.get('code')} != {expected.get('code')}")
            if error.get("message") != expected.get("message"):
                failures.append("error message does not match fixture.json")

    return {
        "id": entry["id"],
        "file": entry["file"],
        "subsets": entry["subsets"],
        "kind": "failure",
        "status": "pass" if not failures else "fail",
        "failures": failures,
        "metrics": {
            "duration_ms": duration_ms,
            "pages": entry["pages"],
        },
        "expected_error": expected,
        "observed_error": envelope.get("error") if envelope else None,
    }


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = args.repo_root.resolve()
    manifest_path = args.manifest.resolve()
    fixtures_root = manifest_path.parent
    ethos_bin = args.ethos_bin.resolve()
    manifest = load_json(manifest_path)
    entries = manifest["fixtures"]

    fixture_results = []
    for entry in entries:
        if "failure" in entry["subsets"]:
            fixture_results.append(
                failure_fixture_result(ethos_bin, fixtures_root, entry, args.timeout_sec)
            )
        else:
            fixture_results.append(
                success_fixture_result(
                    ethos_bin,
                    fixtures_root,
                    entry,
                    args.iterations,
                    args.timeout_sec,
                )
            )

    failed = [result for result in fixture_results if result["status"] != "pass"]
    success_results = [result for result in fixture_results if result["kind"] == "success"]
    p50_pps_values = [
        result["metrics"]["pages_per_second_p50"]
        for result in success_results
        if result["metrics"]["pages_per_second_p50"] is not None
    ]
    total_pages = sum(result["metrics"]["pages"] for result in fixture_results)
    return {
        "schema_version": "ethos-harness-fixtures-v1",
        "status": "pass" if not failed else "fail",
        "harness": {
            "name": "fixtures-baseline",
            "runner": "benchmarks/harness/run_fixtures.py",
            "iterations": args.iterations,
            "timeout_sec": args.timeout_sec,
        },
        "inputs": {
            "repo_root": str(repo_root),
            "manifest": str(manifest_path.relative_to(repo_root)),
            "manifest_sha256": sha256_file(manifest_path),
            "ethos_bin": str(ethos_bin),
            "ethos_bin_sha256": sha256_file(ethos_bin),
        },
        "environment": {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "python": platform.python_version(),
            "pdfium_library_path": os.environ.get("ETHOS_PDFIUM_LIBRARY_PATH"),
            "pdfium_version": os.environ.get("ETHOS_PDFIUM_VERSION"),
            "pdfium_artifact_path": os.environ.get("ETHOS_PDFIUM_ARTIFACT_PATH"),
        },
        "summary": {
            "fixtures_total": len(fixture_results),
            "fixtures_passed": len(fixture_results) - len(failed),
            "fixtures_failed": len(failed),
            "success_fixtures": len(success_results),
            "failure_fixtures": len(fixture_results) - len(success_results),
            "pages_total": total_pages,
            "pages_per_second_p50_median": statistics.median(p50_pps_values)
            if p50_pps_values
            else None,
        },
        "fixtures": fixture_results,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--ethos-bin", type=Path, default=ROOT / "target" / "release" / "ethos")
    parser.add_argument("--out", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--stdout", action="store_true", help="write report to stdout instead of --out")
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument("--timeout-sec", type=float, default=30.0)
    args = parser.parse_args(argv)

    if args.iterations < 1:
        parser.error("--iterations must be >= 1")
    if args.timeout_sec <= 0:
        parser.error("--timeout-sec must be > 0")
    if not args.ethos_bin.is_file():
        parser.error(f"--ethos-bin does not exist: {args.ethos_bin}")
    if not args.manifest.is_file():
        parser.error(f"--manifest does not exist: {args.manifest}")
    return args


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    report = build_report(args)
    write_json(None if args.stdout else args.out, report)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
