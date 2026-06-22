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
RECORD = ROOT / "docs/validation/first-public-release-final-decider-validation-2026-06-23.md"
VALIDATION_README = ROOT / "docs/validation/README.md"

SOURCE_SHORT = "858bf0f"
SOURCE_COMMIT = "858bf0fbcac38040ee68f714c302672a72fb27d9"
SOURCE_TREE = "86b7cc44e28a1308af3c29632c7d9e90a0270bfb"
MACOS_SHA256 = "35c7cc19ea51231edb1a0cfb6d160d3a2e620ba9357d116ef071f66ebc5e236f"

APPROVED_SURFACES = (
    "GitHub Release artifact evaluation for `ethos-macos-arm64.tar.gz`",
    "Python package artifact evaluation for `ethos-pdf` / `ethos_pdf` at `0.1.0`",
    "Caller-provided PDFium only, through `ETHOS_PDFIUM_LIBRARY_PATH`",
)
APPROVED_WORDING = (
    "Ethos is public beta for source, Rust crate, macOS arm64 CLI artifact, and Python wheel "
    "evaluation. It verifies whether AI citations are grounded in document evidence across native "
    "Ethos JSON and supported foreign parser outputs. Rust library crates `ethos-doc-core`, "
    "`ethos-verify`, and `ethos-pdf` are available on crates.io at `0.1.0` for evaluation. The "
    "macOS arm64 CLI artifact and Python `ethos-pdf` wheel are available for evaluation with "
    "caller-provided PDFium. Hosted surfaces, production positioning, npm publication, Windows "
    "packaged artifacts, bundled project-maintained PDFium builds, `ethos-doc`, `ethos-rag`, and "
    "public benchmark claims remain blocked."
)
RETAINED_BLOCKERS = (
    "Linux x64 CLI artifact publication remains blocked",
    "npm publication remains blocked",
    "Hosted surfaces remain blocked",
    "Production positioning remains blocked",
    "Public benchmark reports remain blocked",
    "Public benchmark claims remain blocked",
    "Windows x64 packaged artifacts remain blocked",
    "Bundled project-maintained PDFium builds remain blocked",
    "`ethos-doc` remains blocked",
    "`ethos-rag` remains blocked",
)
FORBIDDEN = (
    "production-ready",
    "release-ready",
    "launch-ready",
    "benchmark-validated",
    "speed claims are approved",
    "footprint claims are approved",
    "table-quality claims are approved",
    "parser-quality claims are approved",
    "hosted surfaces are approved",
    "npm publication is approved",
    "windows x64 packaged artifacts are approved",
    "bundled project-maintained pdfium builds are approved",
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


def git_object_available(rev: str) -> bool:
    return subprocess.run(
        ["git", "cat-file", "-e", rev],
        cwd=ROOT,
        stderr=subprocess.DEVNULL,
    ).returncode == 0


class FirstPublicReleaseFinalDeciderTests(unittest.TestCase):
    def test_record_is_source_bound(self) -> None:
        record = normalized(RECORD)

        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Final-decider source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Final-decider source tree: `{SOURCE_TREE}`", record)
        if git_object_available(SOURCE_COMMIT):
            self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
            self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_record_approves_only_evidenced_artifact_evaluation_surfaces(self) -> None:
        record = normalized(RECORD)

        self.assertIn("bounded artifact-evaluation publication decision recorded", record)
        self.assertIn(MACOS_SHA256, record)
        self.assertIn("ethos 0.1.0", record)
        self.assertIn("Python `ethos-pdf` must continue to report `0.1.0`", record)
        for surface in APPROVED_SURFACES:
            self.assertIn(surface, record)
        for blocker in RETAINED_BLOCKERS:
            self.assertIn(blocker, record)

    def test_record_contains_exact_approved_launch_wording(self) -> None:
        record = re.sub(r"\s+", " ", read(RECORD).replace("> ", ""))

        self.assertIn(APPROVED_WORDING, record)
        self.assertIn("Any broader public wording requires a new decider record.", record)

    def test_record_avoids_unapproved_claims_and_private_paths(self) -> None:
        raw = read(RECORD)
        lower = normalized(RECORD).lower()

        for phrase in FORBIDDEN:
            self.assertNotIn(phrase, lower)
        self.assertNotIn("/Users/", raw)
        self.assertNotIn("/private/tmp", raw)
        self.assertNotIn("/private/var", raw)
        self.assertNotIn("saumildiwaker", raw)

    def test_record_is_indexed_and_wired_into_release_candidate_prep(self) -> None:
        readme = normalized(VALIDATION_README)
        block = target_block("release-candidate-prep")

        self.assertIn(RECORD.name, readme)
        self.assertIn("first public release final decider validation", readme)
        self.assertIn("npm publication remains blocked", readme)
        self.assertIn("$(PYTHON) .github/scripts/test_first_public_release_final_decider.py", block)


if __name__ == "__main__":
    unittest.main()
