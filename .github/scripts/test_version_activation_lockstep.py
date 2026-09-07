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
"""Version lockstep guards, read from the ledger rather than a hard-coded release.

This replaces `test_v0_6_0_version_activation.py`, the sixth hand-written generation of one
gate. That module hard-coded ACTIVATED and PUBLISHED, so every release needed a new copy and
the old one asserted a premise that had become false. Both constants now come from
`docs/release-state.json`: `release.activated` is what the tree prepares, `release.version` is
what is published.

Two assertions are worth keeping across releases:

1. Core release metadata moves in lockstep. A version bump that reaches Cargo.toml but not
   pyproject.toml, or the workspace but not the CLI manifest, ships a tree that disagrees with
   itself about what it is.

2. The npm payload's four version fields move as one set. 1d23604 moved three of them and left
   `vendor/manifest.json` behind, producing a package labelled 0.6.0 whose vendored CLI reported
   `ethos 0.5.0` with the full suite green; 46d9584 had to revert it. The set may sit at the
   published version, or at the activated version with its recorded boundary exception, and
   nothing else.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INTERNAL_WORKSPACE_DEPENDENCIES = ("ethos-core", "ethos-layout", "ethos-tables")
INTERNAL_CLI_DEPENDENCIES = ("ethos-pdf", "ethos-verify", "ethos-grounding-opendataloader-json")


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def ledger() -> dict:
    return json.loads(read("docs/release-state.json"))["release"]


class VersionActivationLockstepTests(unittest.TestCase):
    def setUp(self) -> None:
        release = ledger()
        self.activated = release["activated"]
        self.published = release["version"]

    def test_core_release_metadata_is_activated_in_lockstep(self) -> None:
        activated = self.activated
        cargo = read("Cargo.toml")
        cli = read("crates/ethos-cli/Cargo.toml")
        lock = read("Cargo.lock")

        self.assertIn(f'version = "{activated}"', cargo)
        for dependency in INTERNAL_WORKSPACE_DEPENDENCIES:
            line = next(line for line in cargo.splitlines() if line.startswith(dependency))
            self.assertIn(f'version = "{activated}"', line, dependency)
        for dependency in INTERNAL_CLI_DEPENDENCIES:
            line = next(line for line in cli.splitlines() if line.startswith(dependency))
            self.assertIn(f'version = "{activated}"', line, dependency)

        # Every workspace member resolves at the activated version.
        self.assertGreaterEqual(lock.count(f'version = "{activated}"'), 7)
        self.assertIn(f'version = "{activated}"', read("pyproject.toml"))
        self.assertIn(f'__version__ = "{activated}"', read("python/ethos_pdf/__init__.py"))

    def test_npm_payload_versions_move_as_one_set(self) -> None:
        manifest = json.loads(read("packages/npm/ethos-pdf/vendor/manifest.json"))
        package = json.loads(read("packages/npm/ethos-pdf/package.json"))
        lock = json.loads(read("packages/npm/ethos-pdf/package-lock.json"))
        versions = {
            manifest["cli_version"],
            package["version"],
            lock["version"],
            lock["packages"][""].get("version"),
        }

        self.assertEqual(1, len(versions), f"npm payload versions disagree: {sorted(versions)}")
        moved = versions.pop()

        if moved != self.published:
            # A payload ahead of the published release is a refresh, allowed only with its
            # recorded exception — the governance 46d9584 restored after 1d23604 skipped it.
            self.assertEqual(self.activated, moved)
            self.assertIn(
                f"boundary-exception: refresh the v{moved} npm B payload from frozen core-A",
                read("CHANGELOG.md"),
            )


if __name__ == "__main__":
    unittest.main()
