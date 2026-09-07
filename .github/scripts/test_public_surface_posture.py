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
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"
EXAMPLES_README = ROOT / "examples/README.md"
CLAIMS_GATE = ROOT / ".github/scripts/claims_gate.py"
BOUNDARY_CLAIMS = ROOT / "docs/public-boundary-claims.json"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def readme_boundary_claims() -> list[str]:
    payload = json.loads(read(BOUNDARY_CLAIMS))
    return payload["surfaces"]["readme"]["claims"]


class PublicSurfacePostureTests(unittest.TestCase):
    def test_readme_status_matches_supported_release_scope(self) -> None:
        text = read(README)
        normalized = " ".join(line.removeprefix("> ").strip() for line in text.splitlines())

        for claim in readme_boundary_claims():
            self.assertIn(claim, normalized)
        self.assertIn("deterministic document evidence layer", text)
        self.assertIn("Rust library crates `ethos-doc-core`, `ethos-verify`, and `ethos-pdf`", normalized)
        self.assertIn("Python `ethos-pdf` wheel", normalized)
        self.assertIn("caller-provided PDFium", text)
        # Derived from the ledger, not transcribed. These were hand-pinned literals that needed
        # editing every release and were the last version strings in this file anchored to
        # nothing. `release.version` is what is published, so an install command naming any
        # other version is by definition wrong.
        published = json.loads(read(ROOT / "docs/release-state.json"))["release"]["version"]
        for command in (
            f"cargo add ethos-doc-core@{published}",
            f"cargo add ethos-verify@{published}",
            f"cargo add ethos-pdf@{published}",
            f"python3 -m pip install ethos-pdf=={published}",
            f"npm install -g @docushell/ethos-pdf@{published}",
            f"GitHub Release `v{published}`",
        ):
            self.assertIn(command, text, command)

        # No install command may name any version other than the published one. This replaces
        # the negative assertions retired with test_v0_6_0_version_activation.py, which were
        # the only guard against a stale install string surviving in README.md.
        for pattern, label in (
            (r"cargo add ethos-(?:doc-core|verify|pdf)@([0-9]+\.[0-9]+\.[0-9]+)", "cargo add"),
            (r"pip install ethos-pdf==([0-9]+\.[0-9]+\.[0-9]+)", "pip install"),
            (r"npm install -g @docushell/ethos-pdf@([0-9]+\.[0-9]+\.[0-9]+)", "npm install"),
        ):
            found = set(re.findall(pattern, text))
            self.assertEqual({published}, found, f"{label} versions in README.md: {sorted(found)}")
        self.assertNotIn("not production-ready", text.lower())
        self.assertNotIn("not stable production surfaces", text.lower())
        self.assertNotIn("contracts phase", text)
        self.assertNotIn("has not run", text)
        self.assertNotIn("public beta", text.lower())
        self.assertNotIn("beta evaluation", text.lower())
        self.assertNotIn("pre-alpha", text.lower())

    def test_examples_readme_stays_fixture_scoped(self) -> None:
        text = read(EXAMPLES_README)

        self.assertIn("Pinned fixture set", text)
        self.assertIn("Pinned fixtures only", text)
        self.assertNotIn("launch package", text.lower())

    def test_claims_gate_blocks_stale_public_posture_terms(self) -> None:
        text = read(CLAIMS_GATE)

        self.assertIn("contracts phase", text)
        self.assertIn("Gate Zero[^\\n]*has not run", text)
        self.assertIn("benchmark[- ]validated", text)
        self.assertIn("pre[- ]alpha", text)
        self.assertIn("public beta", text)
        self.assertIn("beta evaluation", text)


if __name__ == "__main__":
    unittest.main()
