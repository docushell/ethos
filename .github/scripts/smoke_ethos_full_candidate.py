#!/usr/bin/env python3
"""Target-host smoke for an extracted deterministic ethos-full candidate."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path


def run(command: list[str], env: dict[str, str]) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(command, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"smoke-ethos-full-candidate: error: {message}")


def smoke(root: Path, expected_version: str, fixture: Path) -> dict[str, object]:
    required = ["ethos", "bin/ethos", "LICENSE", "NOTICE", "artifact-manifest.json"]
    for name in required:
        require((root / name).is_file(), f"missing required payload: {name}")
    manifest = json.loads((root / "artifact-manifest.json").read_text(encoding="utf-8"))
    runtime = manifest["pdfium"]["runtime_library_path"]
    require((root / runtime).is_file(), f"missing PDFium runtime: {runtime}")
    env = dict(os.environ)
    env["ETHOS_PDFIUM_LIBRARY_PATH"] = "/invalid/ambient/pdfium"
    version = run([str(root / "ethos"), "--version"], env)
    require(version.returncode == 0 and version.stdout.decode().strip() == expected_version, "unexpected ethos --version result")
    doctor = run([str(root / "ethos"), "doctor", "--require-pdfium"], env)
    require(doctor.returncode == 0, f"ethos doctor --require-pdfium failed: {doctor.stderr.decode()}")
    evidence: dict[str, object] = {"schema": "ethos.full_candidate_smoke.v1", "target": manifest["target"], "version_stdout": expected_version, "runtime_library_path": runtime, "doctor_exit_code": doctor.returncode}
    require(fixture.is_file(), f"missing parse fixture: {fixture}")
    first = run([str(root / "ethos"), "doc", "parse", str(fixture), "--format", "json"], env)
    second = run([str(root / "ethos"), "doc", "parse", str(fixture), "--format", "json"], env)
    require(first.returncode == second.returncode == 0, "fixture parse failed")
    require(first.stdout == second.stdout, "fixture parses were not byte-identical")
    evidence["parse_stdout_sha256"] = hashlib.sha256(first.stdout).hexdigest()
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--expected-version", required=True)
    parser.add_argument("--fixture", required=True, type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    evidence = smoke(args.root, args.expected_version, args.fixture)
    if args.out:
        args.out.write_text(json.dumps(evidence, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
