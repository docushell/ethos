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


ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "docs/validation/patch-0-1-1-release-artifact-evidence-validation-2026-06-23.md"
VALIDATION_README = ROOT / "docs/validation/README.md"

SOURCE_SHORT = "3cbbb8f"
SOURCE_COMMIT = "3cbbb8f8b8195fe0f964ab4e5d2bf0458770ad11"
SOURCE_TREE = "2791caca23354bd11974f391fa94c5de02df91a4"
RUN_URL = "https://github.com/docushell/ethos/actions/runs/28040466463"

EXPECTED_ARTIFACTS = {
    "macos-arm64": {
        "archive": "ethos-macos-arm64.tar.gz",
        "sha256": "eac79cddc6f5fc834ecc279401905729978d73e99ae11a2bea82d7356a4bcd88",
    },
    "linux-x64": {
        "archive": "ethos-linux-x64.tar.gz",
        "sha256": "842aa4b71333aecc54f344d9f5362160d0943d8efd32dffabe99dc19553916a0",
    },
}

RETAINED_BLOCKERS = (
    "GitHub Release publication remains blocked",
    "packages/npm/ethos-pdf/vendor/manifest.json",
    "npm publication remains blocked",
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
    "publish approval granted",
    "npm publication approved",
    "github release publication approved",
    "production positioning approved",
    "hosted surfaces approved",
    "bundled pdfium approved",
    "public benchmark claims approved",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalized(path: Path) -> str:
    return re.sub(r"\s+", " ", read(path))


class Patch011ReleaseArtifactEvidenceTests(unittest.TestCase):
    def test_record_binds_source_and_workflow_run(self) -> None:
        text = normalized(RECORD)
        raw = read(RECORD)

        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", raw)
        self.assertIn(f"Artifact-evidence source commit: `{SOURCE_COMMIT}`", text)
        self.assertIn(f"Artifact-evidence source tree: `{SOURCE_TREE}`", text)
        self.assertIn(RUN_URL, text)
        self.assertIn("conclusion: `success`", text)
        self.assertIn("event: `workflow_dispatch`", text)
        self.assertIn("branch: `main`", text)

    def test_record_captures_both_platform_artifacts_and_smoke(self) -> None:
        text = normalized(RECORD)

        for target, expected in EXPECTED_ARTIFACTS.items():
            self.assertIn(f"inventory target: `{target}`", text)
            self.assertIn(f"smoke target: `{target}`", text)
            self.assertIn(expected["archive"], text)
            self.assertIn(expected["sha256"], text)
        self.assertEqual(2, text.count("smoke version stdout: `ethos 0.1.1`"))
        self.assertEqual(2, text.count("inventory status: `draft_not_release_ready`"))
        self.assertEqual(2, text.count("inventory publication: `blocked`"))
        self.assertIn("validate_release_artifact_inventory.py", text)

    def test_record_keeps_publication_and_vendor_refresh_blocked(self) -> None:
        text = normalized(RECORD)
        lower = text.lower()

        for blocker in RETAINED_BLOCKERS:
            self.assertIn(blocker, text)
        for phrase in FORBIDDEN_APPROVALS:
            self.assertNotIn(phrase, lower)
        self.assertIn("not itself a publish approval", text)

    def test_record_is_indexed(self) -> None:
        readme = read(VALIDATION_README)
        readme_normalized = normalized(VALIDATION_README).lower()

        self.assertIn(RECORD.name, readme)
        self.assertIn("patch 0.1.1 release artifact evidence", readme_normalized)

    def test_record_avoids_local_private_paths(self) -> None:
        text = read(RECORD)

        for private in (
            "/" + "Users/",
            "/" + "private/tmp",
            "/" + "private/var",
            "/" + "var/folders",
            "saumil" + "diwaker",
            "Desktop/" + "Stuff",
            "project/repo/" + "ethos",
        ):
            self.assertNotIn(private, text)


if __name__ == "__main__":
    unittest.main()
