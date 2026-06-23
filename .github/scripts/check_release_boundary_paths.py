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

import os
import subprocess
import sys
from pathlib import Path


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


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, encoding="utf-8", stderr=subprocess.DEVNULL).strip()


def base_ref() -> str:
    configured = os.environ.get("ETHOS_LIGHT_CHECK_BASE")
    if configured:
        return configured
    try:
        return git("merge-base", "HEAD", "origin/main")
    except subprocess.CalledProcessError:
        return "HEAD"


def changed_files() -> list[str]:
    base = base_ref()
    output = git("diff", "--name-only", f"{base}...HEAD")
    staged = git("diff", "--name-only", "--cached")
    unstaged = git("diff", "--name-only")
    untracked = git("ls-files", "--others", "--exclude-standard")
    return sorted({line for blob in (output, staged, unstaged, untracked) for line in blob.splitlines() if line})


def is_heavy(path: str) -> bool:
    return (
        path in HEAVY_EXACT
        or path.startswith(HEAVY_PREFIXES)
        or path.endswith(HEAVY_SUFFIXES)
    )


def has_boundary_exception() -> bool:
    if not CHANGELOG.is_file():
        return False
    return "boundary-exception:" in CHANGELOG.read_text(encoding="utf-8")


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
