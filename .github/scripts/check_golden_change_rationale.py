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


def is_golden_like(path: str) -> bool:
    name = Path(path).name
    return (
        "/goldens/" in path
        or "fingerprint" in name
        or name.startswith("expected.")
        or name.endswith(".golden.json")
        or name.endswith(".verification_report.json")
    )


def has_golden_change() -> bool:
    return has_added_marker(CHANGELOG, "golden-change")


def main() -> int:
    golden_paths = [path for path in changed_files() if is_golden_like(path)]
    if not golden_paths:
        print("golden change rationale green")
        return 0
    if has_golden_change():
        print("golden change rationale marker found")
        for path in golden_paths:
            print(f"GOLDEN-PATH {path}")
        return 0

    print("golden/fingerprint output changed without golden-change marker in CHANGELOG.md")
    for path in golden_paths:
        print(f"GOLDEN-PATH {path}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
