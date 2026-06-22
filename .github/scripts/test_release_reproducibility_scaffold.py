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

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/release.yml"
INVENTORY_WRITER = ROOT / ".github/scripts/write_release_artifact_inventory.py"
INVENTORY_VALIDATOR = ROOT / ".github/scripts/validate_release_artifact_inventory.py"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class ReleaseReproducibilityScaffoldTests(unittest.TestCase):
    def test_workflow_records_rebuildable_cli_inputs(self) -> None:
        text = read(WORKFLOW)

        self.assertIn("rustup show", text)
        self.assertIn("cargo build --locked --release -p ethos-cli", text)
        self.assertIn("tar -C", text)
        self.assertIn("shasum -a 256", text)
        self.assertIn("ethos-${{ matrix.artifact_target }}", text)

    def test_inventory_binds_checksum_target_and_publication_status(self) -> None:
        writer = read(INVENTORY_WRITER)
        validator = read(INVENTORY_VALIDATOR)

        self.assertIn('"status": "draft_not_release_ready"', writer)
        self.assertIn('"artifact_class": "github-release-binary"', writer)
        self.assertIn('"pdfium_policy": "caller-provided"', writer)
        self.assertIn('"publication": "blocked"', writer)
        self.assertIn("macos-arm64", validator)
        self.assertIn("linux-x64", validator)
        self.assertIn("malformed sha256", validator)


if __name__ == "__main__":
    unittest.main()
