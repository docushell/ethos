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

"""Check the Gate Zero evidence handoff between ethos and ethos-bench.

The checker does not generate benchmark results. It only reports whether the
source repository and sibling evidence repository are ready for a controlled run
or for the ADR-0005 decision review.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
TIMESTAMP_RE = re.compile(r"^[0-9]{8}T[0-9]{6}Z$")
REQUIRED_PLATFORMS = ("macos-arm64", "linux-x64")


@dataclass(frozen=True)
class ResultSpec:
    platform: str
    gate: str
    result_path: Path
    evidence_root: Path
    schema_version: str


RESULT_SPECS = (
    ResultSpec(
        platform="macos-arm64",
        gate="g1",
        result_path=Path("benchmarks/results/gate-zero/macos-arm64/g1.json"),
        evidence_root=Path("benchmarks/results/gate-zero/macos-arm64/evidence/g1"),
        schema_version="ethos-gate-zero-result-v1",
    ),
    ResultSpec(
        platform="macos-arm64",
        gate="g2",
        result_path=Path("benchmarks/results/gate-zero/macos-arm64/g2.json"),
        evidence_root=Path("benchmarks/results/gate-zero/macos-arm64/evidence/g2"),
        schema_version="ethos-gate-zero-g2-result-v1",
    ),
    ResultSpec(
        platform="linux-x64",
        gate="g1",
        result_path=Path("benchmarks/results/gate-zero/linux-x64/g1.json"),
        evidence_root=Path("benchmarks/results/gate-zero/linux-x64/evidence/g1"),
        schema_version="ethos-gate-zero-result-v1",
    ),
    ResultSpec(
        platform="linux-x64",
        gate="g2",
        result_path=Path("benchmarks/results/gate-zero/linux-x64/g2.json"),
        evidence_root=Path("benchmarks/results/gate-zero/linux-x64/evidence/g2"),
        schema_version="ethos-gate-zero-g2-result-v1",
    ),
    ResultSpec(
        platform="cross-platform",
        gate="g3",
        result_path=Path("benchmarks/results/gate-zero/g3.json"),
        evidence_root=Path("benchmarks/results/gate-zero/cross-platform/evidence/g3"),
        schema_version="ethos-gate-zero-g3-result-v1",
    ),
)


class Gate:
    def __init__(self) -> None:
        self.failures: list[str] = []

    def require(self, condition: bool, message: str) -> None:
        if not condition:
            self.failures.append(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def run_git(path: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(path), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )


def check_no_generated_results_in_ethos(gate: Gate, repo_root: Path) -> None:
    results_root = repo_root / "benchmarks" / "results" / "gate-zero"
    if not results_root.exists():
        return
    allowed = {(results_root / "README.md").resolve()}
    generated = [
        path
        for path in results_root.rglob("*")
        if path.is_file() and path.resolve() not in allowed
    ]
    for path in sorted(generated):
        gate.require(
            False,
            f"generated Gate Zero output must live in ethos-bench, not ethos: {rel(path, repo_root)}",
        )


def check_ethos_bench_checkout(gate: Gate, repo_root: Path, ethos_bench: Path) -> None:
    if not ethos_bench.exists():
        gate.require(False, f"ethos-bench checkout does not exist: {ethos_bench}")
        return
    if not ethos_bench.is_dir():
        gate.require(False, f"ethos-bench path is not a directory: {ethos_bench}")
        return
    gate.require(
        ethos_bench.resolve() != repo_root.resolve(),
        "ethos-bench path must not point at the ethos repository",
    )
    git_root = run_git(ethos_bench, ["rev-parse", "--show-toplevel"])
    gate.require(
        git_root.returncode == 0,
        f"ethos-bench path is not a Git checkout: {ethos_bench}",
    )


def check_ethos_bench_clean(gate: Gate, ethos_bench: Path) -> None:
    if not ethos_bench.exists() or not ethos_bench.is_dir():
        return
    status = run_git(ethos_bench, ["status", "--short"])
    if status.returncode != 0:
        return
    dirty = [line for line in status.stdout.splitlines() if line.strip()]
    gate.require(
        not dirty,
        "ethos-bench checkout is not clean before controlled output generation",
    )


def validate_result_shape(
    gate: Gate,
    result: dict[str, Any],
    spec: ResultSpec,
    path: Path,
) -> None:
    gate.require(
        result.get("schema_version") == spec.schema_version,
        f"{path} schema_version is not {spec.schema_version}",
    )
    if spec.gate == "g1":
        selected = result.get("host", {}).get("selected", {})
        platform = selected.get("platform") if isinstance(selected, dict) else None
        gate.require(platform == spec.platform, f"{path} host platform is not {spec.platform}")
        return
    if spec.gate == "g2":
        gate.require(result.get("gate") == "g2", f"{path} gate is not g2")
        gate.require(result.get("platform") == spec.platform, f"{path} platform is not {spec.platform}")
        return
    if spec.gate == "g3":
        platforms = result.get("platforms", [])
        gate.require(result.get("gate") == "g3", f"{path} gate is not g3")
        gate.require(
            all(platform in platforms for platform in REQUIRED_PLATFORMS),
            f"{path} does not include required G3 platforms: {', '.join(REQUIRED_PLATFORMS)}",
        )


def load_result_for_spec(gate: Gate, ethos_bench: Path, spec: ResultSpec) -> dict[str, Any] | None:
    path = ethos_bench / spec.result_path
    if not path.is_file():
        gate.require(False, f"missing Gate Zero {spec.gate.upper()} result: {spec.result_path}")
        return None
    try:
        result = load_json(path)
    except json.JSONDecodeError as exc:
        gate.require(False, f"invalid JSON in {spec.result_path}: {exc}")
        return None
    if not isinstance(result, dict):
        gate.require(False, f"{spec.result_path} must be a JSON object")
        return None
    validate_result_shape(gate, result, spec, spec.result_path)
    return result


def parse_checksum_line(line: str, index: int, bundle_dir: Path) -> tuple[str, Path] | str:
    try:
        expected, relative_path = line.split("  ", 1)
    except ValueError:
        return f"{bundle_dir / 'SHA256SUMS'} line {index} is malformed"
    if not re.fullmatch(r"[0-9a-f]{64}", expected):
        return f"{bundle_dir / 'SHA256SUMS'} line {index} has invalid SHA256"
    return expected, bundle_dir / relative_path


def verify_checksum_manifest(bundle_dir: Path) -> list[str]:
    checksum_path = bundle_dir / "SHA256SUMS"
    failures: list[str] = []
    if not checksum_path.is_file():
        return [f"{checksum_path} is missing"]
    for index, line in enumerate(checksum_path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        parsed = parse_checksum_line(line, index, bundle_dir)
        if isinstance(parsed, str):
            failures.append(parsed)
            continue
        expected, path = parsed
        if not path.is_file():
            failures.append(f"{path} is missing")
            continue
        actual = sha256_file(path)
        if actual != expected:
            failures.append(f"{path} sha256 mismatch: expected={expected} actual={actual}")
    return failures


def validate_bundle(
    bundle_dir: Path,
    spec: ResultSpec,
    result_sha256: str,
) -> list[str]:
    failures: list[str] = []
    required = [
        "SUMMARY.md",
        "host-attestation.json",
        "evidence-manifest.json",
        "reproduction-command.txt",
        "reproduction-env.json",
        "SHA256SUMS",
        "SHA256SUMS.digest.json",
    ]
    for name in required:
        if not (bundle_dir / name).is_file():
            failures.append(f"{bundle_dir / name} is missing")

    raw_dir = bundle_dir / "raw"
    if not raw_dir.is_dir() or not list(raw_dir.glob("*.json")):
        failures.append(f"{raw_dir} is missing a raw result JSON archive")

    try:
        reproduction_env = load_json(bundle_dir / "reproduction-env.json")
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        failures.append(f"{bundle_dir / 'reproduction-env.json'} is invalid: {exc}")
    else:
        if not isinstance(reproduction_env, dict):
            failures.append(f"{bundle_dir / 'reproduction-env.json'} must be a JSON object")
        elif reproduction_env.get("status") != "complete":
            failures.append(f"{bundle_dir / 'reproduction-env.json'} status is not complete")

    try:
        manifest = load_json(bundle_dir / "evidence-manifest.json")
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        failures.append(f"{bundle_dir / 'evidence-manifest.json'} is invalid: {exc}")
    else:
        if not isinstance(manifest, dict):
            failures.append(f"{bundle_dir / 'evidence-manifest.json'} must be a JSON object")
        else:
            if manifest.get("gate") != spec.gate:
                failures.append(f"{bundle_dir / 'evidence-manifest.json'} gate is not {spec.gate}")
            if manifest.get("platform") != spec.platform:
                failures.append(
                    f"{bundle_dir / 'evidence-manifest.json'} platform is not {spec.platform}"
                )
            if manifest.get("source_result_sha256") != result_sha256:
                failures.append(
                    f"{bundle_dir / 'evidence-manifest.json'} source_result_sha256 does not match {spec.result_path}"
                )

    failures.extend(verify_checksum_manifest(bundle_dir))

    digest_path = bundle_dir / "SHA256SUMS.digest.json"
    try:
        digest = load_json(digest_path)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        failures.append(f"{digest_path} is invalid: {exc}")
    else:
        if not isinstance(digest, dict):
            failures.append(f"{digest_path} must be a JSON object")
        elif (bundle_dir / "SHA256SUMS").is_file() and digest.get(
            "payload_sha256"
        ) != sha256_file(bundle_dir / "SHA256SUMS"):
            failures.append(f"{digest_path} payload_sha256 does not match SHA256SUMS")

    return failures


def check_evidence_bundle(gate: Gate, ethos_bench: Path, spec: ResultSpec) -> None:
    result_path = ethos_bench / spec.result_path
    if not result_path.is_file():
        return
    result_sha256 = sha256_file(result_path)
    evidence_root = ethos_bench / spec.evidence_root
    if not evidence_root.is_dir():
        gate.require(False, f"missing Gate Zero {spec.gate.upper()} evidence root: {spec.evidence_root}")
        return
    bundles = sorted(
        path
        for path in evidence_root.iterdir()
        if path.is_dir() and TIMESTAMP_RE.fullmatch(path.name)
    )
    if not bundles:
        gate.require(False, f"no timestamped evidence bundle under {spec.evidence_root}")
        return
    valid_bundle_count = 0
    latest_failures: list[str] = []
    for bundle_dir in bundles:
        failures = validate_bundle(bundle_dir, spec, result_sha256)
        if failures:
            latest_failures = failures
        else:
            valid_bundle_count += 1
    if valid_bundle_count == 0:
        gate.require(False, f"no complete evidence bundle under {spec.evidence_root}")
        for failure in latest_failures[:8]:
            gate.require(False, failure)


def run(mode: str, *, repo_root: Path = ROOT, ethos_bench: Path | None = None) -> Gate:
    repo_root = repo_root.resolve()
    ethos_bench = (ethos_bench or repo_root.parent / "ethos-bench").resolve()
    gate = Gate()
    check_no_generated_results_in_ethos(gate, repo_root)
    check_ethos_bench_checkout(gate, repo_root, ethos_bench)
    if mode == "prepare":
        check_ethos_bench_clean(gate, ethos_bench)
        return gate
    for spec in RESULT_SPECS:
        load_result_for_spec(gate, ethos_bench, spec)
    for spec in RESULT_SPECS:
        check_evidence_bundle(gate, ethos_bench, spec)
    return gate


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["prepare", "decision"])
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--ethos-bench", type=Path)
    parser.add_argument("--report-only", action="store_true")
    args = parser.parse_args()

    gate = run(args.mode, repo_root=args.repo_root, ethos_bench=args.ethos_bench)
    label = f"gate-zero evidence {args.mode}"
    if gate.failures:
        print(f"{label}: BLOCKED")
        for failure in gate.failures:
            print(f"- {failure}")
        return 0 if args.report_only else 1
    print(f"{label}: green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
