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
RECORD = ROOT / "docs/validation/patch-0-1-2-draft-artifact-evidence-validation-2026-06-24.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"

SOURCE_SHORT = "2cb092b"
SOURCE_COMMIT = "2cb092b403eefe937e30c902fcebf7bb5754d590"
SOURCE_TREE = "9e23207526591813c4aaf311ec8788b94e6a95ab"
RUN_URL = "https://github.com/docushell/ethos/actions/runs/28102259869"
MACOS_SHA256 = "7da7da71fb0c21b25cd2ffc198480ee80bf9f0c9e70e461cffbdcbdda8d7023c"
LINUX_SHA256 = "4e260b464dc9557bc31c29fb1d1dfa75311fe12734bc79af4a31e1649797e456"
EXPECTED_ARTIFACTS = (
    "ethos-cli-draft-macos-arm64/ethos-macos-arm64.tar.gz",
    "ethos-cli-draft-macos-arm64/ethos-macos-arm64.tar.gz.sha256",
    "ethos-cli-draft-macos-arm64/ethos-macos-arm64.inventory.json",
    "ethos-cli-draft-macos-arm64/ethos-macos-arm64.smoke.json",
    "ethos-cli-draft-linux-x64/ethos-linux-x64.tar.gz",
    "ethos-cli-draft-linux-x64/ethos-linux-x64.tar.gz.sha256",
    "ethos-cli-draft-linux-x64/ethos-linux-x64.inventory.json",
    "ethos-cli-draft-linux-x64/ethos-linux-x64.smoke.json",
)
RETAINED_BLOCKERS = (
    "GitHub Release artifact publication remains blocked",
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
)
FORBIDDEN_APPROVALS = (
    "github release artifact publication approved",
    "github release publication approved",
    "registry publication approved",
    "npm vendor refresh approved",
    "npm publication approved",
    "public installation wording approved",
    "production-ready",
    "hosted surfaces approved",
    "windows packaged artifacts approved",
    "bundled pdfium approved",
    "public benchmark claims approved",
)
PRIVATE_PATH_MARKERS = (
    "/" + "Users/",
    "/" + "private/tmp",
    "/" + "private/var",
    "/" + "var/folders",
    "saumil" + "diwaker",
    "Desktop/" + "Stuff",
    "project/repo/" + "ethos",
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


class Patch012DraftArtifactEvidenceTests(unittest.TestCase):
    def test_record_is_source_and_workflow_bound(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)

        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", raw)
        self.assertIn(f"Patch 0.1.2 draft artifact evidence source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Patch 0.1.2 draft artifact evidence source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))
        self.assertIn(RUN_URL, record)
        self.assertIn("event: `workflow_dispatch`", record)
        self.assertIn("branch: `main`", record)
        self.assertIn("head SHA: `2cb092b403eefe937e30c902fcebf7bb5754d590`", record)
        self.assertIn("conclusion: `success`", record)

    def test_record_captures_both_platform_artifacts_inventory_and_smoke(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)

        for artifact in EXPECTED_ARTIFACTS:
            self.assertIn(artifact, record)
        self.assertIn(MACOS_SHA256, record)
        self.assertIn(LINUX_SHA256, record)
        self.assertEqual(2, raw.count('"schema": "ethos.release_artifact_inventory.v1"'))
        self.assertEqual(2, raw.count('"schema": "ethos.release_artifact_smoke.v1"'))
        self.assertEqual(2, raw.count('"version_stdout": "ethos 0.1.2"'))
        self.assertEqual(2, raw.count('"missing_pdfium_exit_code": 12'))
        self.assertEqual(2, raw.count('"publication": "blocked"'))
        self.assertEqual(2, raw.count('"status": "draft_not_release_ready"'))
        self.assertIn("caller-provided", record)

    def test_record_keeps_publication_install_wording_and_npm_blocked(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)
        lower = record.lower()

        self.assertIn("public install baseline remains `0.1.1`", record)
        self.assertIn("This record does not approve GitHub Release artifact publication.", record)
        self.assertIn("This record does not approve registry publication.", record)
        self.assertIn("This record does not refresh the checked-in npm vendor payload.", record)
        for blocker in RETAINED_BLOCKERS:
            self.assertIn(blocker, record)
        for forbidden in FORBIDDEN_APPROVALS:
            self.assertNotIn(forbidden, lower)
        for marker in PRIVATE_PATH_MARKERS:
            self.assertNotIn(marker, raw)

    def test_record_is_indexed_and_wired_after_package_evidence_guard(self) -> None:
        readme = normalized(VALIDATION_README)
        execution = normalized(EXECUTION_STATUS)
        checklist = normalized(PUBLIC_RELEASE_CHECKLIST)
        block = target_block("release-candidate-prep")
        package_guard = "$(PYTHON) .github/scripts/test_patch_0_1_2_artifact_package_evidence.py"
        draft_guard = "$(PYTHON) .github/scripts/test_patch_0_1_2_draft_artifact_evidence.py"
        first_public_guard = "$(PYTHON) .github/scripts/test_first_public_release_artifact_evidence.py"

        self.assertIn(RECORD.name, readme)
        self.assertIn("patch 0.1.2 draft artifact evidence validation", readme)
        self.assertIn(RECORD.name, execution)
        self.assertIn(RECORD.name, checklist)
        self.assertIn(draft_guard, block)
        self.assertEqual(1, block.count(draft_guard))
        self.assertLess(block.index(package_guard), block.index(draft_guard))
        self.assertLess(block.index(draft_guard), block.index(first_public_guard))


if __name__ == "__main__":
    unittest.main()
