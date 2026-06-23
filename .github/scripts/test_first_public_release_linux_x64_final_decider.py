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
RECORD = ROOT / "docs/validation/first-public-release-linux-x64-final-decider-validation-2026-06-23.md"
VALIDATION_README = ROOT / "docs/validation/README.md"

SOURCE_SHORT = "38a92f3"
SOURCE_COMMIT = "38a92f390c9578194467eceaacdd297a132d49c9"
SOURCE_TREE = "66a8d69a9e94c891621a77cb3b4719a9a7ffd8cd"
LINUX_SHA256 = "59dc8e4efe4888afe80d18488fd83b08293ea30550ab38961e601f8f18a098b2"
APPROVED_WORDING = (
    "Ethos is public beta for source, Rust crate, macOS arm64 CLI artifact, Linux x64 CLI artifact, "
    "and Python wheel evaluation. It verifies whether AI citations are grounded in document evidence "
    "across native Ethos JSON and supported foreign parser outputs. Rust library crates "
    "`ethos-doc-core`, `ethos-verify`, and `ethos-pdf` are available on crates.io at `0.1.0` for "
    "evaluation. The macOS arm64 and Linux x64 CLI artifacts and Python `ethos-pdf` wheel are "
    "available for evaluation with caller-provided PDFium. Hosted surfaces, production positioning, "
    "npm publication, Windows packaged artifacts, bundled project-maintained PDFium builds, "
    "`ethos-doc`, `ethos-rag`, and public benchmark claims remain blocked."
)
FORBIDDEN = (
    "production-ready",
    "launch-ready",
    "benchmark-validated",
    "npm publication is approved",
    "windows x64 packaged artifacts are approved",
    "bundled project-maintained pdfium builds are approved",
    "hosted surfaces are approved",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalized(path: Path) -> str:
    return re.sub(r"\s+", " ", read(path))


class FirstPublicReleaseLinuxX64FinalDeciderTests(unittest.TestCase):
    def test_record_is_source_bound(self) -> None:
        record = normalized(RECORD)

        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Linux-final-decider source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Linux-final-decider source tree: `{SOURCE_TREE}`", record)

    def test_record_approves_only_linux_artifact_evaluation(self) -> None:
        record = normalized(RECORD)

        self.assertIn("bounded Linux x64 artifact-evaluation publication decision recorded", record)
        self.assertIn("GitHub Release artifact evaluation for `ethos-linux-x64.tar.gz`", record)
        self.assertIn("Publication to the existing GitHub Release tag `v0.1.0`", record)
        self.assertIn(LINUX_SHA256, record)
        self.assertIn("PDFium must remain caller-provided", record)

    def test_record_contains_exact_bounded_launch_wording(self) -> None:
        record = re.sub(r"\s+", " ", read(RECORD).replace("> ", ""))

        self.assertIn(APPROVED_WORDING, record)
        self.assertIn("Any broader public wording requires a new decider record.", record)

    def test_record_preserves_retained_blockers_and_avoids_unapproved_claims(self) -> None:
        raw = read(RECORD)
        lower = normalized(RECORD).lower()

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
        for phrase in FORBIDDEN:
            self.assertNotIn(phrase, lower)

    def test_record_is_indexed_and_wired_into_release_candidate_prep(self) -> None:
        readme = normalized(VALIDATION_README)
        block = target_block("release-candidate-prep")

        self.assertIn(RECORD.name, readme)
        self.assertIn("Linux x64 final decider validation approves only attaching", readme)
        self.assertIn("$(PYTHON) .github/scripts/test_first_public_release_linux_x64_final_decider.py", block)


if __name__ == "__main__":
    unittest.main()
