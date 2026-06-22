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
RECORD = ROOT / "docs/validation/first-public-release-artifact-evidence-validation-2026-06-23.md"
VALIDATION_README = ROOT / "docs/validation/README.md"

SOURCE_SHORT = "7c99a33"
SOURCE_COMMIT = "7c99a338819d580dd0537af9062d069c052944ac"
SOURCE_TREE = "7f7952c001256a493b3fce81ad7a1851a495a34a"
MACOS_SHA256 = "35c7cc19ea51231edb1a0cfb6d160d3a2e620ba9357d116ef071f66ebc5e236f"
NPM_SHASUM = "cf83c7e0196d451f169f3dcbee26e4d009e5da82"

REQUIRED_EVIDENCE = (
    "make release-candidate-prep PYTHON=/private/tmp/ethos-jsonschema-venv-main/bin/python",
    "ethos-macos-arm64.tar.gz",
    "ethos 0.1.0",
    "exit_code=12",
    "ethos_pdf-0.1.0-py3-none-any.whl",
    "version 0.1.0",
    "EthosCli",
    "EthosCommandError",
    "@docushell/ethos-pdf@0.1.0",
    "docushell-ethos-pdf-0.1.0.tgz",
    "Windows x64 was rejected as unsupported",
)
RETAINED_BLOCKERS = (
    "Public artifact publication remains blocked",
    "Launch wording remains blocked",
    "Hosted surfaces remain blocked",
    "Production positioning remains blocked",
    "Public benchmark reports remain blocked",
    "Public benchmark claims remain blocked",
    "Windows x64 packaged artifacts remain blocked",
    "Bundled project-maintained PDFium builds remain blocked",
    "`ethos-doc` remains blocked",
    "`ethos-rag` remains blocked",
)
REQUIRED_CAVEATS = (
    "unused import `Write`",
    "project.license` as a TOML table is deprecated",
    "license classifiers are deprecated",
    "contains no `vendor/` binary payload yet",
)
FORBIDDEN = (
    "public artifact publication approved",
    "launch wording approved",
    "hosted surfaces approved",
    "production positioning approved",
    "public benchmark claims approved",
    "public benchmark reports approved",
    "windows x64 packaged artifacts approved",
    "bundled project-maintained pdfium builds approved",
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


class FirstPublicReleaseArtifactEvidenceTests(unittest.TestCase):
    def test_record_is_source_bound(self) -> None:
        record = normalized(RECORD)

        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Release-candidate source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Release-candidate source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_record_captures_artifact_python_and_npm_evidence(self) -> None:
        record = normalized(RECORD)

        self.assertIn(MACOS_SHA256, record)
        self.assertIn(NPM_SHASUM, record)
        for evidence in REQUIRED_EVIDENCE:
            self.assertIn(evidence, record)
        for caveat in REQUIRED_CAVEATS:
            self.assertIn(caveat, record)

    def test_record_retains_publication_and_claim_blockers(self) -> None:
        record = normalized(RECORD)
        lower = record.lower()

        for blocker in RETAINED_BLOCKERS:
            self.assertIn(blocker, record)
        for forbidden in FORBIDDEN:
            self.assertNotIn(forbidden, lower)

    def test_record_is_indexed_and_wired_into_release_candidate_prep(self) -> None:
        readme = normalized(VALIDATION_README)
        block = target_block("release-candidate-prep")

        self.assertIn(RECORD.name, readme)
        self.assertIn("first public release artifact evidence validation", readme)
        self.assertIn("public artifact publication remains blocked", readme)
        self.assertIn("$(PYTHON) .github/scripts/test_first_public_release_artifact_evidence.py", block)


if __name__ == "__main__":
    unittest.main()
