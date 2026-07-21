#!/usr/bin/env python3
"""Fail-closed validation of npm B inputs against frozen core-A evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


SCHEMA = "ethos.npm_b_activation_evidence.v1"
TARGETS = ("macos-arm64", "linux-x64")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def fail(message: str) -> None:
    raise SystemExit(f"validate-npm-b-activation: error: {message}")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"invalid JSON {path}: {exc}")
    if not isinstance(value, dict):
        fail(f"expected object in {path}")
    return value


def safe_relative(value: object, label: str) -> Path:
    if not isinstance(value, str):
        fail(f"{label} must be a relative path")
    path = Path(value)
    if path.is_absolute() or not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        fail(f"{label} must be a safe relative path")
    return path


def validate(evidence: Path, package_root: Path, expected_version: str = "0.5.0") -> None:
    record = load(evidence)
    if set(record) != {"schema", "core_version", "core_commit", "targets"}:
        fail("evidence manifest has an unexpected shape")
    if record["schema"] != SCHEMA or record["core_version"] != expected_version:
        fail("evidence manifest schema or core version is invalid")
    if not isinstance(record["core_commit"], str) or not re.fullmatch(r"[0-9a-f]{40,64}", record["core_commit"]):
        fail("core_commit must be a full hexadecimal commit id")
    targets = record["targets"]
    if not isinstance(targets, dict) or set(targets) != set(TARGETS):
        fail("evidence must contain exactly macos-arm64 and linux-x64 targets")
    for target in TARGETS:
        item = targets[target]
        if not isinstance(item, dict) or set(item) != {"archive", "checksum", "inventory", "smoke"}:
            fail(f"{target} evidence has an unexpected shape")
        paths = {key: evidence.parent / safe_relative(item[key], f"{target}.{key}") for key in item}
        for key, path in paths.items():
            if not path.is_file() or path.is_symlink():
                fail(f"missing regular {target} {key}: {path}")
        inventory = load(paths["inventory"])
        if inventory.get("schema") != "ethos.full_candidate_inventory.v1" or inventory.get("target") != target:
            fail(f"{target} inventory is not a target-smoke candidate record")
        if inventory.get("status") != "release_candidate_pending_target_smoke" or inventory.get("publication") != "not_publishable_pending_release_gates":
            fail(f"{target} inventory is publishable or not smoke-bound")
        archive_hash = digest(paths["archive"])
        if inventory.get("sha256") != archive_hash or not HEX64.fullmatch(str(inventory.get("sha256", ""))):
            fail(f"{target} inventory archive hash mismatch")
        if inventory.get("size_bytes") != paths["archive"].stat().st_size:
            fail(f"{target} inventory archive size mismatch")
        checksum = paths["checksum"].read_text(encoding="utf-8")
        if checksum != f"{archive_hash}  {paths['archive'].name}\n":
            fail(f"{target} checksum is not canonical")
        smoke = load(paths["smoke"])
        if (
            smoke.get("schema") != "ethos.full_candidate_smoke.v1"
            or smoke.get("target") != target
            or smoke.get("archive_sha256") != archive_hash
            or smoke.get("archive_size_bytes") != paths["archive"].stat().st_size
            or smoke.get("version_stdout") != f"ethos {expected_version}"
        ):
            fail(f"{target} smoke evidence does not bind the frozen candidate")
    package = load(package_root / "package.json")
    lock = load(package_root / "package-lock.json")
    manifest = load(package_root / "vendor" / "manifest.json")
    root_lock = lock.get("packages", {}).get("") if isinstance(lock.get("packages"), dict) else None
    if (
        package.get("version") != expected_version
        or lock.get("version") != expected_version
        or not isinstance(root_lock, dict)
        or root_lock.get("version") != expected_version
        or manifest.get("cli_version") != expected_version
    ):
        fail("npm package, package-lock, and vendor manifest must all be refreshed to core-A version")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument("--package-root", required=True, type=Path)
    parser.add_argument("--expected-version", default="0.5.0")
    args = parser.parse_args()
    validate(args.evidence, args.package_root, args.expected_version)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
