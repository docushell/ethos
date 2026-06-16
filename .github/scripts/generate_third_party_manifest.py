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

"""Generate a Cargo third-party license manifest.

This is a source dependency manifest input for release review. It is not a complete release
artifact license bundle: binaries, PDFium, fonts, wheels, npm packages, and other packaged
payloads still need artifact-specific notice assembly.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent


def cargo_metadata() -> dict[str, Any]:
    proc = subprocess.run(
        ["cargo", "metadata", "--locked", "--offline", "--format-version", "1"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    return json.loads(proc.stdout)


def cargo_lock_checksums() -> dict[tuple[str, str, str], str]:
    lock_packages = []
    current: dict[str, str] | None = None
    for raw_line in (ROOT / "Cargo.lock").read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line == "[[package]]":
            if current is not None:
                lock_packages.append(current)
            current = {}
            continue
        if current is None or "=" not in line:
            continue
        key, raw_value = [part.strip() for part in line.split("=", 1)]
        if key not in {"name", "version", "source", "checksum"}:
            continue
        if not raw_value.startswith('"'):
            continue
        current[key] = json.loads(raw_value)
    if current is not None:
        lock_packages.append(current)

    checksums: dict[tuple[str, str, str], str] = {}
    for package in lock_packages:
        name = str(package.get("name", ""))
        version = str(package.get("version", ""))
        source = str(package.get("source", ""))
        checksum = package.get("checksum")
        if name and version and source and checksum:
            checksums[(name, version, source)] = str(checksum)
    return checksums


def license_file_name(value: str | None) -> str | None:
    if not value:
        return None
    return Path(value).name


def generate() -> dict[str, Any]:
    metadata = cargo_metadata()
    checksums = cargo_lock_checksums()
    resolved_ids = {node["id"] for node in metadata["resolve"]["nodes"]}
    workspace_member_ids = set(metadata["workspace_members"])
    packages_by_id = {package["id"]: package for package in metadata["packages"]}

    workspace_packages = []
    third_party_packages = []
    missing_license = []
    missing_checksum = []

    for package_id in sorted(workspace_member_ids):
        package = packages_by_id[package_id]
        workspace_packages.append(
            {
                "name": package["name"],
                "version": package["version"],
                "license": package.get("license"),
                "publish": package.get("publish"),
            }
        )

    for package_id in sorted(resolved_ids):
        package = packages_by_id[package_id]
        source = package.get("source")
        if not source:
            continue
        key = (package["name"], package["version"], source)
        checksum = checksums.get(key)
        license_expr = package.get("license")
        license_file = license_file_name(package.get("license_file"))

        if not license_expr and not license_file:
            missing_license.append(f"{package['name']} {package['version']}")
        if source.startswith("registry+") and not checksum:
            missing_checksum.append(f"{package['name']} {package['version']} {source}")

        third_party_packages.append(
            {
                "name": package["name"],
                "version": package["version"],
                "source": source,
                "checksum": checksum,
                "license": license_expr,
                "license_file": license_file,
                "repository": package.get("repository"),
                "homepage": package.get("homepage"),
                "description": package.get("description"),
            }
        )

    if missing_license or missing_checksum:
        if missing_license:
            print("missing license metadata:", file=sys.stderr)
            for item in missing_license:
                print(f"- {item}", file=sys.stderr)
        if missing_checksum:
            print("missing registry checksum metadata:", file=sys.stderr)
            for item in missing_checksum:
                print(f"- {item}", file=sys.stderr)
        raise SystemExit(1)

    third_party_packages.sort(key=lambda item: (item["name"], item["version"], item["source"]))
    workspace_packages.sort(key=lambda item: (item["name"], item["version"]))

    licenses = sorted({pkg["license"] or f"file:{pkg['license_file']}" for pkg in third_party_packages})
    return {
        "schema_version": 1,
        "scope": "cargo locked resolved workspace dependency graph",
        "source_commands": [
            "cargo metadata --locked --offline --format-version 1",
            "Cargo.lock package checksums",
        ],
        "release_boundary": (
            "This manifest covers Cargo registry dependencies only. Release artifacts still "
            "need artifact-specific license and NOTICE assembly."
        ),
        "summary": {
            "workspace_package_count": len(workspace_packages),
            "third_party_package_count": len(third_party_packages),
            "license_expressions": licenses,
        },
        "workspace_packages": workspace_packages,
        "third_party_packages": third_party_packages,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="-", help="Output path, or '-' for stdout")
    args = parser.parse_args()

    manifest = generate()
    text = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    if args.out == "-":
        print(text, end="")
        return 0

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
