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

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from claims_gate import find_claim_hits


REGISTRY_SURFACES = (
    "python/README.md",
    "python/QUICKSTART.md",
    "packages/npm/ethos-pdf/README.md",
    "packages/npm/ethos-pdf/QUICKSTART.md",
)


def write_surface(root: Path, relative_path: str, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class ClaimsGateRegistrySurfaceTests(unittest.TestCase):
    def test_registry_surfaces_accept_bounded_wording(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ethos-claims-registry-") as temp:
            root = Path(temp)
            for relative_path in REGISTRY_SURFACES:
                write_surface(root, relative_path, "Current published package.\n")
            hits = find_claim_hits(root, REGISTRY_SURFACES)
        self.assertEqual([], hits)

    def test_python_readme_rejects_banned_claim(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ethos-claims-registry-") as temp:
            root = Path(temp)
            write_surface(root, "python/README.md", "The fastest document verifier.\n")
            hits = find_claim_hits(root, REGISTRY_SURFACES)
        self.assertEqual(Path("python/README.md"), hits[0][0])
        self.assertEqual("speed superlative (needs reproducible benchmark + G1 pass)", hits[0][2])

    def test_npm_quickstart_rejects_banned_claim(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ethos-claims-registry-") as temp:
            root = Path(temp)
            write_surface(
                root,
                "packages/npm/ethos-pdf/QUICKSTART.md",
                "Install this public beta package.\n",
            )
            hits = find_claim_hits(root, REGISTRY_SURFACES)
        self.assertEqual(Path("packages/npm/ethos-pdf/QUICKSTART.md"), hits[0][0])
        self.assertEqual("stale public-beta posture", hits[0][2])

    def test_missing_optional_surface_does_not_fail_scan(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ethos-claims-registry-") as temp:
            hits = find_claim_hits(Path(temp), REGISTRY_SURFACES)
        self.assertEqual([], hits)


if __name__ == "__main__":
    unittest.main()
