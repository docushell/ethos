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
RECORD = ROOT / "docs/validation/first-public-release-linux-x64-publication-closeout-validation-2026-06-23.md"
VALIDATION_README = ROOT / "docs/validation/README.md"

SOURCE_SHORT = "415a654"
SOURCE_COMMIT = "415a654e07ab2fc653d8361b104b4e40613df948"
SOURCE_TREE = "aa5fbd86c0747a036ab3040d1cf127b2f97bf1bb"
LINUX_SHA256 = "59dc8e4efe4888afe80d18488fd83b08293ea30550ab38961e601f8f18a098b2"
REQUIRED_ASSETS = (
    "ethos-linux-x64.inventory.json",
    "ethos-linux-x64.smoke.json",
    "ethos-linux-x64.tar.gz",
    "ethos-linux-x64.tar.gz.sha256",
    "ethos-macos-arm64.inventory.json",
    "ethos-macos-arm64.tar.gz",
    "ethos-macos-arm64.tar.gz.sha256",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalized(path: Path) -> str:
    return re.sub(r"\s+", " ", read(path))


class FirstPublicReleaseLinuxX64PublicationCloseoutTests(unittest.TestCase):
    def test_record_is_source_bound(self) -> None:
        record = normalized(RECORD)

        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Linux-publication closeout source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Linux-publication closeout source tree: `{SOURCE_TREE}`", record)

    def test_record_captures_upload_and_release_asset_verification(self) -> None:
        record = normalized(RECORD)

        self.assertIn("Successfully uploaded 4 assets to v0.1.0", record)
        self.assertIn("https://github.com/docushell/ethos/releases/tag/v0.1.0", record)
        self.assertIn(LINUX_SHA256, record)
        for asset in REQUIRED_ASSETS:
            self.assertIn(asset, record)

    def test_record_closes_only_bounded_public_evaluation_scope(self) -> None:
        raw = read(RECORD)
        lower = normalized(RECORD).lower()

        self.assertIn("bounded first public evaluation release is complete", raw)
        for blocker in (
            "npm publication remains blocked",
            "Hosted surfaces remain blocked",
            "Production positioning remains blocked",
            "Public benchmark reports remain blocked",
            "Public benchmark claims remain blocked",
            "Windows x64 packaged artifacts remain blocked",
            "Bundled project-maintained PDFium builds remain blocked",
            "`ethos-doc` remains blocked",
            "`ethos-rag` remains blocked",
        ):
            self.assertIn(blocker, raw)
        self.assertNotIn("production-ready", lower)
        self.assertNotIn("benchmark-validated", lower)
        self.assertNotIn("npm publication is approved", lower)

    def test_record_is_indexed_and_wired_into_release_candidate_prep(self) -> None:
        readme = normalized(VALIDATION_README)
        block = target_block("release-candidate-prep")

        self.assertIn(RECORD.name, readme)
        self.assertIn("Linux x64 publication closeout validation records successful upload", readme)
        self.assertIn("$(PYTHON) .github/scripts/test_first_public_release_linux_x64_publication_closeout.py", block)


if __name__ == "__main__":
    unittest.main()
