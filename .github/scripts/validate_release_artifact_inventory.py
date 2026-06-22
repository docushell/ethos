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
import sys
from pathlib import Path


REQUIRED = {
    "schema": "ethos.release_artifact_inventory.v1",
    "status": "draft_not_release_ready",
    "artifact_class": "github-release-binary",
    "pdfium_policy": "caller-provided",
    "publication": "blocked",
}
TARGETS = {"macos-arm64", "linux-x64"}


def validate(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    for key, value in REQUIRED.items():
        if data.get(key) != value:
            raise AssertionError(f"{path}: expected {key}={value!r}")
    if data.get("target") not in TARGETS:
        raise AssertionError(f"{path}: unsupported target")
    sha = data.get("sha256")
    if not isinstance(sha, str) or len(sha) != 64 or not all(c in "0123456789abcdef" for c in sha):
        raise AssertionError(f"{path}: malformed sha256")
    notices = data.get("required_notices")
    for required in ("LICENSE", "NOTICE", "docs/pdfium-manual-setup.md"):
        if required not in notices:
            raise AssertionError(f"{path}: missing notice requirement {required}")


def main(argv: list[str]) -> int:
    if not argv:
        raise SystemExit("usage: validate_release_artifact_inventory.py <inventory>...")
    for raw in argv:
        validate(Path(raw))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
