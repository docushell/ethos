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
import unittest
from pathlib import Path

from makefile_guard import target_block


ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "docs/validation/patch-0-1-1-artifact-publication-closeout-validation-2026-06-23.md"
VALIDATION_README = ROOT / "docs/validation/README.md"

SOURCE_SHORT = "5231b56"
SOURCE_COMMIT = "5231b56383afbc08c874325a7f47d6ae90e60a24"
SOURCE_TREE = "b0e5d2e5ac534facf9bd78a580366aab1995f0e1"
MACOS_SHA256 = "eac79cddc6f5fc834ecc279401905729978d73e99ae11a2bea82d7356a4bcd88"
LINUX_SHA256 = "842aa4b71333aecc54f344d9f5362160d0943d8efd32dffabe99dc19553916a0"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalized(path: Path) -> str:
    return re.sub(r"\s+", " ", read(path))


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args],
        cwd=ROOT,
        encoding="utf-8",
        stderr=subprocess.DEVNULL,
    ).strip()


class Patch011ArtifactPublicationCloseoutTests(unittest.TestCase):
    def test_record_is_source_bound(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)

        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", raw)
        self.assertIn(f"Patch 0.1.1 artifact publication closeout source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Patch 0.1.1 artifact publication closeout source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_record_captures_release_metadata_and_exact_assets(self) -> None:
        record = normalized(RECORD)

        for expected in (
            "Status: **patch 0.1.1 GitHub Release artifact publication complete**",
            "GitHub Release tag: `v0.1.1`",
            "Release name: `Release v0.1.1`",
            "Release draft status: `false`",
            "Release prerelease status: `false`",
            f"Tag target: `{SOURCE_COMMIT}`",
            "ethos-macos-arm64.tar.gz",
            "ethos-macos-arm64.tar.gz.sha256",
            "ethos-macos-arm64.inventory.json",
            "ethos-macos-arm64.smoke.json",
            "ethos-linux-x64.tar.gz",
            "ethos-linux-x64.tar.gz.sha256",
            "ethos-linux-x64.inventory.json",
            "ethos-linux-x64.smoke.json",
            MACOS_SHA256,
            LINUX_SHA256,
        ):
            self.assertIn(expected, record)

    def test_record_captures_sidecar_payload_and_smoke_evidence(self) -> None:
        record = normalized(RECORD)

        for expected in (
            "schema `ethos.release_artifact_inventory.v1`, target `macos-arm64`",
            "schema `ethos.release_artifact_smoke.v1`, target `macos-arm64`, version `ethos 0.1.1`",
            "schema `ethos.release_artifact_inventory.v1`, target `linux-x64`",
            "schema `ethos.release_artifact_smoke.v1`, target `linux-x64`, version `ethos 0.1.1`",
            "`LICENSE`",
            "`NOTICE`",
            "`ethos`",
            "`pdfium-manual-setup.md`",
            "`ethos doctor` preserved the caller-provided PDFium setup-warning posture",
        ):
            self.assertIn(expected, record)

    def test_record_preserves_blockers_and_private_path_safety(self) -> None:
        raw = read(RECORD)
        lower = normalized(RECORD).lower()

        for blocker in (
            "`packages/npm/ethos-pdf/vendor/manifest.json` must not be refreshed",
            "npm publication remains blocked",
            "Hosted surfaces remain blocked",
            "Production positioning remains blocked",
            "Windows packaged artifacts remain blocked",
            "Bundled project-maintained PDFium builds remain blocked",
            "Public benchmark reports remain blocked",
            "Public benchmark claims remain blocked",
            "`ethos-doc` remains blocked",
            "`ethos-rag` remains blocked",
        ):
            self.assertIn(blocker, raw)
        for forbidden in (
            "npm publication approved",
            "vendor payload refreshed",
            "production-ready",
            "benchmark-validated",
            "hosted surfaces approved",
            "bundled pdfium approved",
        ):
            self.assertNotIn(forbidden, lower)
        for private in (
            "/" + "Users/",
            "/" + "private/tmp",
            "/" + "private/var",
            "/" + "var/folders",
            "saumil" + "diwaker",
            "Desktop/" + "Stuff",
            "project/repo/" + "ethos",
        ):
            self.assertNotIn(private, raw)

    def test_record_is_indexed_and_wired_into_release_candidate_prep(self) -> None:
        readme = normalized(VALIDATION_README)
        block = target_block("release-candidate-prep")

        self.assertIn(RECORD.name, readme)
        self.assertIn("patch 0.1.1 artifact publication closeout", readme.lower())
        self.assertIn(
            "$(PYTHON) .github/scripts/test_patch_0_1_1_artifact_publication_closeout.py",
            block,
        )


if __name__ == "__main__":
    unittest.main()
