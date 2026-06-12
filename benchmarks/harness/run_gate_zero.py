#!/usr/bin/env python3
"""Gate Zero harness readiness guard.

The G1/G2/G3 measurement runner must not execute until the corpus/hardware
manifest is frozen and every reference competitor is pinned. This script makes
that precondition executable and emits JSON so blocked runs are auditable.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / "benchmarks" / "gate-zero" / "manifest.json"
DEFAULT_COMPETITORS = ROOT / "benchmarks" / "competitors.lock.json"
DEFAULT_RESULTS = ROOT / "benchmarks" / "results" / "gate-zero" / "readiness.json"
HEX64 = re.compile(r"[0-9a-f]{64}")
EXPECTED_GATE_ZERO_COMPETITORS = {
    "opendataloader-pdf",
    "edgeparse",
    "liteparse",
    "pymupdf4llm",
}


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


def is_filled(value: Any) -> bool:
    return value is not None and value != "" and value != "_____________"


def check_manifest(manifest: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if manifest.get("frozen") is not True:
        blockers.append("Gate Zero manifest is not frozen")
    if str(manifest.get("status", "")).upper() not in {"FROZEN", "FROZEN-SIGNED"}:
        blockers.append("Gate Zero manifest status is not FROZEN/FROZEN-SIGNED")

    record = manifest.get("freeze_record", {})
    if not is_filled(record.get("frozen_at")):
        blockers.append("Gate Zero freeze_record.frozen_at is blank")
    if not is_filled(record.get("signed_by")):
        blockers.append("Gate Zero freeze_record.signed_by is blank")

    corpus = manifest.get("corpus", [])
    if not corpus:
        blockers.append("Gate Zero corpus[] is empty")
    for index, entry in enumerate(corpus, 1):
        prefix = f"Gate Zero corpus entry {index}"
        for field in ["file", "sha256", "pages", "subsets", "provenance", "license"]:
            if not is_filled(entry.get(field)):
                blockers.append(f"{prefix} missing {field}")
        sha = str(entry.get("sha256", ""))
        if not HEX64.fullmatch(sha):
            blockers.append(f"{prefix} sha256 is not lowercase hex")

    performance_hosts = [
        host for host in manifest.get("hardware", []) if host.get("role") == "performance"
    ]
    if not performance_hosts:
        blockers.append("Gate Zero manifest has no performance hardware host")
    for host in performance_hosts:
        host_id = host.get("id", "<unknown>")
        for field in ["model", "cpu", "ram", "os", "kernel", "runner"]:
            if not is_filled(host.get(field)):
                blockers.append(f"hardware {host_id} missing {field}")

    return blockers


def check_competitors(lock: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if str(lock.get("status", "")).upper() not in {"PINNED", "FROZEN", "FROZEN-SIGNED"}:
        blockers.append("competitors lock status is not PINNED/FROZEN/FROZEN-SIGNED")

    entries = lock.get("gate_zero", [])
    if not entries:
        blockers.append("competitors lock gate_zero[] is empty")
    found = {entry.get("id") for entry in entries}
    for competitor_id in sorted(EXPECTED_GATE_ZERO_COMPETITORS - found):
        blockers.append(f"competitor {competitor_id} missing from gate_zero lock")
    for entry in entries:
        competitor_id = entry.get("id", "<unknown>")
        if entry.get("pinned") is not True:
            blockers.append(f"competitor {competitor_id} is not pinned")
        if not is_filled(entry.get("version")):
            blockers.append(f"competitor {competitor_id} missing version")
        if not is_filled(entry.get("artifact_sha256")):
            blockers.append(f"competitor {competitor_id} missing artifact_sha256")
        sha = str(entry.get("artifact_sha256", ""))
        if not HEX64.fullmatch(sha):
            blockers.append(f"competitor {competitor_id} artifact_sha256 is not lowercase hex")
        if "jvm_version" in entry and not is_filled(entry.get("jvm_version")):
            blockers.append(f"competitor {competitor_id} missing jvm_version")
        if "python_version" in entry and not is_filled(entry.get("python_version")):
            blockers.append(f"competitor {competitor_id} missing python_version")

    return blockers


def build_report(
    repo_root: Path,
    manifest_path: Path,
    competitors_path: Path,
) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    competitors = load_json(competitors_path)
    manifest_blockers = check_manifest(manifest)
    competitor_blockers = check_competitors(competitors)
    blockers = manifest_blockers + competitor_blockers

    return {
        "schema_version": "ethos-gate-zero-readiness-v1",
        "status": "ready" if not blockers else "blocked",
        "harness": {
            "name": "gate-zero-readiness",
            "runner": "benchmarks/harness/run_gate_zero.py",
            "scope": "readiness-only",
        },
        "inputs": {
            "repo_root": str(repo_root),
            "manifest": str(manifest_path.relative_to(repo_root)),
            "manifest_sha256": sha256_file(manifest_path),
            "competitors_lock": str(competitors_path.relative_to(repo_root)),
            "competitors_lock_sha256": sha256_file(competitors_path),
        },
        "blockers": {
            "manifest": manifest_blockers,
            "competitors": competitor_blockers,
        },
        "summary": {
            "blockers_total": len(blockers),
            "manifest_blockers": len(manifest_blockers),
            "competitor_blockers": len(competitor_blockers),
        },
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--competitors-lock", type=Path, default=DEFAULT_COMPETITORS)
    parser.add_argument("--out", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--stdout", action="store_true", help="write report to stdout instead of --out")
    args = parser.parse_args(argv)

    if not args.manifest.is_file():
        parser.error(f"--manifest does not exist: {args.manifest}")
    if not args.competitors_lock.is_file():
        parser.error(f"--competitors-lock does not exist: {args.competitors_lock}")
    return args


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    repo_root = args.repo_root.resolve()
    manifest_path = args.manifest.resolve()
    competitors_path = args.competitors_lock.resolve()
    report = build_report(repo_root, manifest_path, competitors_path)
    write_json(None if args.stdout else args.out, report)
    if report["status"] == "ready":
        print("Gate Zero readiness: ready")
        return 0
    print("Gate Zero readiness: blocked", file=sys.stderr)
    for group in report["blockers"].values():
        for blocker in group:
            print(f"- {blocker}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
