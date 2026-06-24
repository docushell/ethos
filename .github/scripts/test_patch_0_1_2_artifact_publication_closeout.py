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
RECORD = ROOT / "docs/validation/patch-0-1-2-artifact-publication-closeout-validation-2026-06-24.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"

SOURCE_SHORT = "6cc9a93"
SOURCE_COMMIT = "6cc9a933a7eb2684f8f2ccc78039ed5440e6af08"
SOURCE_TREE = "84712214e430977f857a7f5d0c4440523c86a2a4"
MACOS_SHA256 = "7da7da71fb0c21b25cd2ffc198480ee80bf9f0c9e70e461cffbdcbdda8d7023c"
LINUX_SHA256 = "4e260b464dc9557bc31c29fb1d1dfa75311fe12734bc79af4a31e1649797e456"

APPROVED_WORDING = (
    "Ethos patch `0.1.2` CLI artifacts for macOS arm64 and Linux x64 are requested for public beta "
    "evaluation with caller-provided PDFium. Rust crates, the Python wheel, npm package install "
    "instructions, and public README installation examples remain on the published `0.1.1` baseline "
    "until separate registry, npm vendor refresh, and public wording closeout records pass. Hosted "
    "surfaces, production positioning, Windows packaged artifacts, bundled project-maintained PDFium "
    "builds, `ethos-doc`, `ethos-rag`, public benchmark reports, public benchmark claims, and speed, "
    "footprint, parser-quality, table-quality, or production claims remain blocked."
)


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


class Patch012ArtifactPublicationCloseoutTests(unittest.TestCase):
    def test_record_is_source_bound(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)

        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", raw)
        self.assertIn(f"Patch 0.1.2 artifact publication closeout source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Patch 0.1.2 artifact publication closeout source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_record_captures_release_metadata_and_exact_assets(self) -> None:
        record = normalized(RECORD)

        for expected in (
            "Status: **patch 0.1.2 GitHub Release artifact publication complete**",
            "GitHub Release tag: `v0.1.2`",
            "Release name: `Release v0.1.2`",
            "Release draft status: `false`",
            "Release prerelease status: `false`",
            "Release targetCommitish display value: `main`",
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
            "sha256:7da7da71fb0c21b25cd2ffc198480ee80bf9f0c9e70e461cffbdcbdda8d7023c",
            "sha256:4e260b464dc9557bc31c29fb1d1dfa75311fe12734bc79af4a31e1649797e456",
        ):
            self.assertIn(expected, record)

    def test_record_captures_sidecar_payload_and_release_wording(self) -> None:
        record = normalized(RECORD)
        wording_record = re.sub(r"\s+", " ", read(RECORD).replace("> ", ""))

        for expected in (
            "schema `ethos.release_artifact_inventory.v1`, target `macos-arm64`",
            "schema `ethos.release_artifact_smoke.v1`, target `macos-arm64`, version `ethos 0.1.2`",
            "schema `ethos.release_artifact_inventory.v1`, target `linux-x64`",
            "schema `ethos.release_artifact_smoke.v1`, target `linux-x64`, version `ethos 0.1.2`",
            "`LICENSE`",
            "`NOTICE`",
            "`ethos`",
            "`pdfium-manual-setup.md`",
            "missing-PDFium guidance preserved the caller-provided PDFium posture",
        ):
            self.assertIn(expected, record)
        self.assertIn(APPROVED_WORDING, wording_record)

    def test_record_preserves_blockers_and_private_path_safety(self) -> None:
        raw = read(RECORD)
        lower = normalized(RECORD).lower()

        for blocker in (
            "`packages/npm/ethos-pdf/vendor/manifest.json` must not be refreshed",
            "The public install baseline remains `0.1.1`",
            "README installation examples remain unchanged",
            "Registry publication remains blocked",
            "npm vendor refresh remains blocked",
            "npm publication remains blocked",
            "Public installation wording remains blocked",
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
            "registry publication approved",
            "npm vendor refresh approved",
            "npm publication approved",
            "public installation wording approved",
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

    def test_record_is_indexed_statused_and_wired_into_release_candidate_prep(self) -> None:
        readme = normalized(VALIDATION_README)
        execution = normalized(EXECUTION_STATUS)
        checklist = normalized(PUBLIC_RELEASE_CHECKLIST)
        block = target_block("release-candidate-prep")
        decision_guard = "$(PYTHON) .github/scripts/test_patch_0_1_2_artifact_publication_approval_decision.py"
        closeout_guard = "$(PYTHON) .github/scripts/test_patch_0_1_2_artifact_publication_closeout.py"
        first_public_guard = "$(PYTHON) .github/scripts/test_first_public_release_artifact_evidence.py"

        self.assertIn(RECORD.name, readme)
        self.assertIn("patch 0.1.2 artifact publication closeout", readme.lower())
        self.assertIn(RECORD.name, execution)
        self.assertIn(RECORD.name, checklist)
        self.assertIn(closeout_guard, block)
        self.assertEqual(1, block.count(closeout_guard))
        self.assertLess(block.index(decision_guard), block.index(closeout_guard))
        self.assertLess(block.index(closeout_guard), block.index(first_public_guard))


if __name__ == "__main__":
    unittest.main()
