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
import unittest
from pathlib import Path

from makefile_guard import target_block


ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "docs/validation/first-public-release-linux-x64-artifact-evidence-validation-2026-06-23.md"
DECIDER = ROOT / "docs/validation/first-public-release-linux-x64-final-decider-validation-2026-06-23.md"
VALIDATION_README = ROOT / "docs/validation/README.md"

SOURCE_SHORT = "38a92f3"
SOURCE_COMMIT = "38a92f390c9578194467eceaacdd297a132d49c9"
SOURCE_TREE = "66a8d69a9e94c891621a77cb3b4719a9a7ffd8cd"
LINUX_SHA256 = "59dc8e4efe4888afe80d18488fd83b08293ea30550ab38961e601f8f18a098b2"
MACOS_PUBLISHED_SHA256 = "9cb66dac20f93c55f574357dd0494e0cad711e1e5969cdfb29ae4c64ddf7c95d"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalized(path: Path) -> str:
    return re.sub(r"\s+", " ", read(path))


class FirstPublicReleaseLinuxX64ArtifactEvidenceTests(unittest.TestCase):
    def test_record_is_source_and_workflow_bound(self) -> None:
        record = normalized(RECORD)

        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Linux-artifact evidence source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Linux-artifact evidence source tree: `{SOURCE_TREE}`", record)
        self.assertIn("https://github.com/docushell/ethos/actions/runs/28004938177", record)
        self.assertIn("cli-draft-artifacts (linux-x64, ubuntu-latest, tar.gz)` passed", record)

    def test_record_captures_linux_artifact_inventory_and_smoke(self) -> None:
        record = normalized(RECORD)

        self.assertIn("ethos-linux-x64.tar.gz", record)
        self.assertIn("ethos-linux-x64.tar.gz.sha256", record)
        self.assertIn("ethos-linux-x64.inventory.json", record)
        self.assertIn("ethos-linux-x64.smoke.json", record)
        self.assertIn(LINUX_SHA256, record)
        self.assertIn('"schema": "ethos.release_artifact_inventory.v1"', read(RECORD))
        self.assertIn('"schema": "ethos.release_artifact_smoke.v1"', read(RECORD))
        self.assertIn('"version_stdout": "ethos 0.1.0"', read(RECORD))
        self.assertIn('"missing_pdfium_exit_code": 12', read(RECORD))
        self.assertIn("ethos-linux-x64/pdfium-manual-setup.md", record)

    def test_record_reconciles_published_macos_checksum(self) -> None:
        record = normalized(RECORD)

        self.assertIn(MACOS_PUBLISHED_SHA256, record)
        self.assertIn("The recomputed archive SHA256, `.sha256` sidecar, and inventory `sha256` all matched", record)

    def test_record_retains_blockers_until_decider(self) -> None:
        record = normalized(RECORD)

        self.assertIn("Linux x64 CLI artifact publication remains blocked until the final Linux x64 decider record", record)
        self.assertIn("npm publication remains blocked", record)
        self.assertIn("Public benchmark claims remain blocked", record)

    def test_decider_and_release_candidate_prep_are_wired(self) -> None:
        readme = normalized(VALIDATION_README)
        block = target_block("release-candidate-prep")

        self.assertIn(RECORD.name, readme)
        self.assertIn(DECIDER.name, readme)
        self.assertIn("$(PYTHON) .github/scripts/test_first_public_release_linux_x64_artifact_evidence.py", block)


if __name__ == "__main__":
    unittest.main()
