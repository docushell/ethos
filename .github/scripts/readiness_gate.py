#!/usr/bin/env python3
"""Readiness gates for phase transitions and public artifacts.

This script is intentionally dependency-free: it runs in GitHub Actions before any
project-specific environment exists.

Modes:
- week0: staffing/sign-off and dependency lockfile are complete.
- gate-zero: benchmark corpus/hardware and competitor pins are frozen.
- public: all pre-public blockers are complete, including ADR-0006.

Use --report-only for early-lane visibility without failing the job.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
EXPECTED_GATE_ZERO_COMPETITORS = {
    "opendataloader-pdf",
    "edgeparse",
    "liteparse",
    "pymupdf4llm",
}


class Gate:
    def __init__(self) -> None:
        self.failures: list[str] = []

    def require(self, condition: bool, message: str) -> None:
        if not condition:
            self.failures.append(message)

    def require_text(self, path: Path, pattern: str, message: str) -> str:
        text = path.read_text(encoding="utf-8")
        self.require(bool(re.search(pattern, text, re.MULTILINE)), message)
        return text


def is_filled(value: Any) -> bool:
    return value is not None and value != "" and value != "_____________"


def check_lockfile(gate: Gate) -> None:
    gate.require((ROOT / "Cargo.lock").exists(), "Cargo.lock is missing; generate and commit it")


def check_adr_0001(gate: Gate) -> None:
    path = ROOT / "docs/decisions/ADR-0001-staffing-confirmation.md"
    text = gate.require_text(path, r"Status:\s+\*\*Accepted\b", "ADR-0001 is not Accepted")
    checked = len(re.findall(r"^- \[x\] ", text, re.MULTILINE))
    gate.require(checked == 1, "ADR-0001 must have exactly one staffing decision checked")
    gate.require(
        not re.search(r"Actual staffing at kickoff:\s*_+", text),
        "ADR-0001 actual staffing is still blank",
    )


def check_gate_zero_manifest(gate: Gate) -> None:
    path = ROOT / "benchmarks/gate-zero/manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))

    gate.require(manifest.get("frozen") is True, "Gate Zero manifest is not frozen")
    gate.require(
        str(manifest.get("status", "")).upper() in {"FROZEN", "FROZEN-SIGNED"},
        "Gate Zero manifest status is not FROZEN/FROZEN-SIGNED",
    )

    record = manifest.get("freeze_record", {})
    gate.require(is_filled(record.get("frozen_at")), "Gate Zero freeze_record.frozen_at is blank")
    gate.require(is_filled(record.get("signed_by")), "Gate Zero freeze_record.signed_by is blank")

    corpus = manifest.get("corpus", [])
    gate.require(bool(corpus), "Gate Zero corpus[] is empty")
    for i, entry in enumerate(corpus, 1):
        prefix = f"Gate Zero corpus entry {i}"
        for field in ["file", "sha256", "pages", "subsets", "provenance", "license"]:
            gate.require(is_filled(entry.get(field)), f"{prefix} missing {field}")
        sha = str(entry.get("sha256", ""))
        gate.require(bool(re.fullmatch(r"[0-9a-f]{64}", sha)), f"{prefix} sha256 is not lowercase hex")

    performance_hosts = [
        host for host in manifest.get("hardware", []) if host.get("role") == "performance"
    ]
    gate.require(bool(performance_hosts), "Gate Zero manifest has no performance hardware host")
    for host in performance_hosts:
        if host.get("role") != "performance":
            continue
        host_id = host.get("id", "<unknown>")
        for field in ["model", "cpu", "ram", "os", "kernel", "runner"]:
            gate.require(is_filled(host.get(field)), f"hardware {host_id} missing {field}")


def check_competitor_pins(gate: Gate) -> None:
    path = ROOT / "benchmarks/competitors.lock.json"
    lock = json.loads(path.read_text(encoding="utf-8"))
    entries = lock.get("gate_zero", [])
    found = {entry.get("id") for entry in entries}
    missing = sorted(EXPECTED_GATE_ZERO_COMPETITORS - found)
    for cid in missing:
        gate.require(False, f"competitor {cid} missing from gate_zero lock")
    for entry in entries:
        cid = entry.get("id", "<unknown>")
        gate.require(entry.get("pinned") is True, f"competitor {cid} is not pinned")
        gate.require(is_filled(entry.get("version")), f"competitor {cid} missing version")
        gate.require(is_filled(entry.get("artifact_sha256")), f"competitor {cid} missing artifact_sha256")
        sha = str(entry.get("artifact_sha256", ""))
        gate.require(bool(re.fullmatch(r"[0-9a-f]{64}", sha)), f"competitor {cid} artifact_sha256 is not lowercase hex")
        if "jvm_version" in entry:
            gate.require(is_filled(entry.get("jvm_version")), f"competitor {cid} missing jvm_version")
        if "python_version" in entry:
            gate.require(is_filled(entry.get("python_version")), f"competitor {cid} missing python_version")


def check_adr_0006(gate: Gate) -> None:
    path = ROOT / "docs/decisions/ADR-0006-package-identifiers.md"
    text = gate.require_text(path, r"Status:\s+\*\*Accepted\b", "ADR-0006 is not Accepted")
    gate.require("☐" not in text, "ADR-0006 still has unchecked table cells")
    gate.require("- [ ]" not in text, "ADR-0006 still has unchecked checklist items")
    gate.require(
        bool(re.search(r"## Decision\s+\n(?!\s*Pending validation\.)", text, re.MULTILINE)),
        "ADR-0006 decision section still appears pending",
    )


def run(mode: str) -> Gate:
    gate = Gate()
    if mode in {"week0", "public"}:
        check_lockfile(gate)
        check_adr_0001(gate)
    if mode in {"gate-zero", "public"}:
        check_gate_zero_manifest(gate)
        check_competitor_pins(gate)
    if mode == "public":
        check_adr_0006(gate)
    return gate


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["week0", "gate-zero", "public"])
    parser.add_argument("--report-only", action="store_true")
    args = parser.parse_args()

    gate = run(args.mode)
    if gate.failures:
        print(f"{args.mode} readiness: BLOCKED")
        for failure in gate.failures:
            print(f"- {failure}")
        return 0 if args.report_only else 1

    print(f"{args.mode} readiness: green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
