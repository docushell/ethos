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

"""Enforce the parser-neutral direct dependency boundary of ethos-verify."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PACKAGE_NAME = "ethos-verify"
ALLOWED_NORMAL_DEPENDENCIES = {"ethos-doc-core", "serde", "sha2"}
ETHOS_CORE_FEATURES = {"grounding", "verify-types"}


def normal_dependencies(package: dict[str, Any]) -> list[dict[str, Any]]:
    return [dependency for dependency in package["dependencies"] if dependency["kind"] is None]


def boundary_errors(package: dict[str, Any]) -> list[str]:
    """Return policy violations from one cargo-metadata package object."""

    errors: list[str] = []
    dependencies = normal_dependencies(package)
    names = [dependency["name"] for dependency in dependencies]
    actual = set(names)

    unexpected = sorted(actual - ALLOWED_NORMAL_DEPENDENCIES)
    missing = sorted(ALLOWED_NORMAL_DEPENDENCIES - actual)
    if unexpected:
        errors.append(f"unexpected normal dependencies: {', '.join(unexpected)}")
    if missing:
        errors.append(f"missing normal dependencies: {', '.join(missing)}")

    duplicates = sorted(name for name in actual if names.count(name) > 1)
    if duplicates:
        errors.append(f"duplicate normal dependencies: {', '.join(duplicates)}")

    core_dependencies = [
        dependency for dependency in dependencies if dependency["name"] == "ethos-doc-core"
    ]
    if len(core_dependencies) != 1:
        return errors

    core = core_dependencies[0]
    if core.get("rename") != "ethos-core":
        errors.append("ethos-doc-core must be imported as ethos-core")
    if core.get("uses_default_features") is not False:
        errors.append("ethos-core default features must be disabled")

    features = set(core.get("features", []))
    if features != ETHOS_CORE_FEATURES:
        expected = ", ".join(sorted(ETHOS_CORE_FEATURES))
        actual_features = ", ".join(sorted(features)) or "<none>"
        errors.append(
            f"ethos-core features must be exactly [{expected}], got [{actual_features}]"
        )
    if core.get("optional") is not False:
        errors.append("ethos-core must be a required dependency")
    if core.get("target") is not None:
        errors.append("ethos-core must not be target-specific")

    return errors


def load_metadata() -> dict[str, Any]:
    result = subprocess.run(
        ["cargo", "metadata", "--locked", "--format-version", "1", "--no-deps"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def main() -> None:
    metadata = load_metadata()
    packages = [package for package in metadata["packages"] if package["name"] == PACKAGE_NAME]
    if len(packages) != 1:
        raise SystemExit(
            f"expected exactly one {PACKAGE_NAME} package in cargo metadata, got {len(packages)}"
        )

    errors = boundary_errors(packages[0])
    if errors:
        details = "\n".join(f"- {error}" for error in errors)
        raise SystemExit(f"{PACKAGE_NAME} parser-neutral dependency boundary violated:\n{details}")

    dependencies = ", ".join(sorted(ALLOWED_NORMAL_DEPENDENCIES))
    features = ", ".join(sorted(ETHOS_CORE_FEATURES))
    print(
        f"ok: {PACKAGE_NAME} normal dependencies are [{dependencies}]; "
        f"ethos-core default features are disabled and features are [{features}]"
    )


if __name__ == "__main__":
    main()
