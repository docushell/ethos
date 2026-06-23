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

from __future__ import annotations

import sys
from pathlib import Path

from _lightcheck import changed_files, has_added_marker


ROOT = Path(__file__).resolve().parents[2]
CHANGELOG = ROOT / "CHANGELOG.md"

HEAVY_PREFIXES = (
    ".github/workflows/",
    "profiles/",
    "schemas/",
    "docs/validation/",
)
HEAVY_EXACT = {
    "Cargo.toml",
    "Cargo.lock",
    "Makefile",
    "deny.toml",
    "rust-toolchain.toml",
    "docs/public-boundary-claims.json",
    "docs/pdfium-manual-setup.md",
    "docs/release-artifact-notices.md",
    "docs/RELEASE_OPERATOR_RUNBOOK.md",
    "packages/npm/ethos-pdf/package.json",
    "packages/npm/ethos-pdf/vendor/manifest.json",
    "python/pyproject.toml",
}
HEAVY_SUFFIXES = (
    "Cargo.toml",
    "pyproject.toml",
    "package.json",
)


def is_heavy(path: str) -> bool:
    return (
        path in HEAVY_EXACT
        or path.startswith(HEAVY_PREFIXES)
        or path.endswith(HEAVY_SUFFIXES)
    )


def has_boundary_exception() -> bool:
    return has_added_marker(CHANGELOG, "boundary-exception")


def main() -> int:
    heavy = [path for path in changed_files() if is_heavy(path)]
    if not heavy:
        print("release boundary paths green")
        return 0
    if has_boundary_exception():
        print("release boundary paths require review; boundary-exception marker found")
        for path in heavy:
            print(f"BOUNDARY-PATH {path}")
        return 0

    print("release boundary path touched without boundary-exception marker in CHANGELOG.md")
    for path in heavy:
        print(f"BOUNDARY-PATH {path}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
