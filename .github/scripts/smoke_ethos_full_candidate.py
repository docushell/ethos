#!/usr/bin/env python3
"""Validate and smoke an ethos-full release-candidate archive on its target host."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tarfile
from pathlib import Path


INVENTORY_SCHEMA = "ethos.full_candidate_inventory.v1"
STATUS = "release_candidate_pending_target_smoke"
PUBLICATION = "not_publishable_pending_release_gates"


def run(command: list[str], env: dict[str, str]) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(command, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"smoke-ethos-full-candidate: error: {message}")


def required_regular(path: Path, label: str) -> None:
    require(path.is_file() and not path.is_symlink(), f"missing regular {label}: {path}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_metadata(archive: Path, checksum: Path, inventory: Path) -> dict[str, object]:
    for path, label in ((archive, "archive"), (checksum, "checksum"), (inventory, "inventory")):
        required_regular(path, label)
    digest = sha256_file(archive)
    expected_checksum = f"{digest}  {archive.name}\n"
    require(checksum.read_text(encoding="utf-8") == expected_checksum, "checksum must bind the archive basename and sha256 canonically")
    try:
        record = json.loads(inventory.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SystemExit(f"smoke-ethos-full-candidate: error: invalid inventory: {error}") from error
    require(isinstance(record, dict), "inventory must be an object")
    require(
        set(record) == {"schema", "status", "publication", "artifact", "sha256", "size_bytes", "target"},
        "inventory has an unexpected shape",
    )
    require(record["schema"] == INVENTORY_SCHEMA, "inventory schema is unsupported")
    require(record["status"] == STATUS, "inventory status is not a release candidate")
    require(record["publication"] == PUBLICATION, "inventory publication state is invalid")
    require(record["artifact"] == archive.name, "inventory artifact does not match archive")
    require(record["sha256"] == digest, "inventory sha256 does not match archive")
    require(record["size_bytes"] == archive.stat().st_size, "inventory size does not match archive")
    require(record["target"] in {"macos-arm64", "linux-x64"}, "inventory target is unsupported")
    return record


def extract_candidate(archive: Path, extract_dir: Path) -> Path:
    require(not extract_dir.exists(), f"extract directory already exists: {extract_dir}")
    try:
        with tarfile.open(archive, "r:gz") as bundle:
            members = bundle.getmembers()
            require(members, "archive has no members")
            roots: set[str] = set()
            for member in members:
                path = Path(member.name)
                require(not path.is_absolute() and all(part not in {"", ".", ".."} for part in path.parts), "archive contains an unsafe member path")
                require(member.isfile(), f"archive member is not a regular file: {member.name}")
                roots.add(path.parts[0])
            require(len(roots) == 1, "archive must contain exactly one top-level directory")
            root_name = next(iter(roots))
            extract_dir.mkdir(parents=True)
            root = extract_dir / root_name
            root.mkdir()
            for member in members:
                destination = extract_dir / member.name
                destination.parent.mkdir(parents=True, exist_ok=True)
                source = bundle.extractfile(member)
                require(source is not None, f"archive member is unreadable: {member.name}")
                with destination.open("wb") as output:
                    shutil.copyfileobj(source, output)
                destination.chmod(member.mode)
            return root
    except (OSError, tarfile.TarError) as error:
        raise SystemExit(f"smoke-ethos-full-candidate: error: invalid archive: {error}") from error


def smoke(root: Path, expected_version: str, fixture: Path, record: dict[str, object], archive: Path) -> dict[str, object]:
    required = ["ethos", "bin/ethos", "LICENSE", "NOTICE", "artifact-manifest.json"]
    for name in required:
        required_regular(root / name, f"payload {name}")
    manifest = json.loads((root / "artifact-manifest.json").read_text(encoding="utf-8"))
    require(manifest.get("target") == record["target"], "payload target does not match inventory")
    runtime = manifest["pdfium"]["runtime_library_path"]
    required_regular(root / runtime, f"PDFium runtime {runtime}")
    env = dict(os.environ)
    env["ETHOS_PDFIUM_LIBRARY_PATH"] = "/invalid/ambient/pdfium"
    version = run([str(root / "ethos"), "--version"], env)
    require(version.returncode == 0 and version.stdout.decode().strip() == expected_version, "unexpected ethos --version result")
    doctor = run([str(root / "ethos"), "doctor", "--require-pdfium"], env)
    require(doctor.returncode == 0, f"ethos doctor --require-pdfium failed: {doctor.stderr.decode()}")
    evidence: dict[str, object] = {
        "schema": "ethos.full_candidate_smoke.v1",
        "artifact": archive.name,
        "archive_sha256": record["sha256"],
        "archive_size_bytes": record["size_bytes"],
        "target": record["target"],
        "version_stdout": expected_version,
        "runtime_library_path": runtime,
        "doctor_exit_code": doctor.returncode,
    }
    require(fixture.is_file(), f"missing parse fixture: {fixture}")
    first = run([str(root / "ethos"), "doc", "parse", str(fixture), "--format", "json"], env)
    second = run([str(root / "ethos"), "doc", "parse", str(fixture), "--format", "json"], env)
    require(first.returncode == second.returncode == 0, "fixture parse failed")
    require(first.stdout == second.stdout, "fixture parses were not byte-identical")
    evidence["parse_stdout_sha256"] = hashlib.sha256(first.stdout).hexdigest()
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--checksum", required=True, type=Path)
    parser.add_argument("--inventory", required=True, type=Path)
    parser.add_argument("--extract-dir", required=True, type=Path)
    parser.add_argument("--expected-version", required=True)
    parser.add_argument("--fixture", required=True, type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    record = validate_metadata(args.archive, args.checksum, args.inventory)
    root = extract_candidate(args.archive, args.extract_dir)
    evidence = smoke(root, args.expected_version, args.fixture, record, args.archive)
    if args.out:
        args.out.write_text(json.dumps(evidence, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
