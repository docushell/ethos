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

import re
import subprocess
import sys
from pathlib import Path

from _lightcheck import changed_files


ROOT = Path(__file__).resolve().parents[2]
VALIDATION_DIR = ROOT / "docs/validation"
VALIDATION_README = VALIDATION_DIR / "README.md"
HEX_REF = re.compile(r"`([0-9a-f]{7,40})`")
PRIVATE_MARKERS = (
    "/" + "Users/",
    "/" + "private/tmp",
    "/" + "private/var",
    "/" + "var/folders",
    "saumil" + "diwaker",
    "Desktop/" + "Stuff",
    "project/repo/" + "ethos",
)


def changed_validation_records() -> list[Path]:
    paths = [
        line
        for line in changed_files()
        if line.startswith("docs/validation/") and line.endswith(".md")
    ]
    return [ROOT / path for path in paths if (ROOT / path).is_file()]


def object_exists(ref: str) -> bool:
    type_result = subprocess.run(
        ["git", "cat-file", "-t", ref],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        encoding="utf-8",
    )
    if type_result.returncode != 0:
        return False
    return type_result.stdout.strip() in {"commit", "tree"}


def main() -> int:
    failures: list[str] = []
    index = VALIDATION_README.read_text(encoding="utf-8") if VALIDATION_README.is_file() else ""

    for path in changed_validation_records():
        relative = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        if path.name != "README.md" and path.name not in index:
            failures.append(f"{relative}: not indexed in docs/validation/README.md")
        for marker in PRIVATE_MARKERS:
            if marker in text:
                failures.append(f"{relative}: contains private marker {marker}")
        for ref in sorted(set(HEX_REF.findall(text))):
            if not object_exists(ref):
                failures.append(f"{relative}: git commit/tree ref does not exist: {ref}")

    if failures:
        for failure in failures:
            print(f"VALIDATION-INTEGRITY {failure}")
        return 1

    print("validation record integrity green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
