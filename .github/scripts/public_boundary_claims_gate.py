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

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CLAIMS = ROOT / "docs/public-boundary-claims.json"


def normalized_markdown(path: Path) -> str:
    return re.sub(
        r"\s+",
        " ",
        " ".join(line.removeprefix("> ").strip() for line in path.read_text(encoding="utf-8").splitlines()),
    )


def main() -> int:
    payload = json.loads(CLAIMS.read_text(encoding="utf-8"))
    failures: list[str] = []

    if payload.get("version") != 1:
        failures.append("docs/public-boundary-claims.json must use version 1")

    for surface, spec in payload.get("surfaces", {}).items():
        surface_path = spec.get("path")
        if not surface_path:
            failures.append(f"{surface}: missing path")
            continue
        path = (ROOT / surface_path).resolve()
        try:
            path.relative_to(ROOT)
        except ValueError:
            failures.append(f"{surface}: path escapes repository root: {surface_path}")
            continue
        if not path.is_file():
            failures.append(f"{surface}: missing surface file {surface_path}")
            continue
        text = normalized_markdown(path)
        for claim in spec.get("claims", []):
            if claim not in text:
                failures.append(f"{surface}: missing boundary claim in {surface_path}: {claim}")

    if failures:
        for failure in failures:
            print(f"BOUNDARY-CLAIMS {failure}")
        return 1

    print("public boundary claims green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
