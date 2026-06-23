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
RECORD = ROOT / (
    "docs/validation/"
    "patch-0-1-1-artifact-publication-approval-decision-validation-2026-06-23.md"
)
VALIDATION_README = ROOT / "docs/validation/README.md"

SOURCE_SHORT = "7df928c"
SOURCE_COMMIT = "7df928cd453decd273a5e83fc2b2191a0edf654e"
SOURCE_TREE = "6b9ebbb7087604367f53022406c50a4ec8509992"
RUN_URL = "https://github.com/docushell/ethos/actions/runs/28040466463"
WORKFLOW_HEAD = "3cbbb8f8b8195fe0f964ab4e5d2bf0458770ad11"
MACOS_SHA256 = "eac79cddc6f5fc834ecc279401905729978d73e99ae11a2bea82d7356a4bcd88"
LINUX_SHA256 = "842aa4b71333aecc54f344d9f5362160d0943d8efd32dffabe99dc19553916a0"

APPROVED_WORDING = (
    "Ethos is public beta for source, Rust crate, Python wheel, macOS arm64 CLI artifact, Linux x64 "
    "CLI artifact, and npm `@docushell/ethos-pdf` evaluation. It verifies whether AI citations are "
    "grounded in document evidence across native Ethos JSON and supported foreign parser outputs. "
    "Rust library crates `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` are available on crates.io "
    "at `0.1.1` for evaluation. The Python `ethos-pdf` wheel, npm `@docushell/ethos-pdf@0.1.1` "
    "package, and macOS arm64/Linux x64 CLI artifacts are available for evaluation with "
    "caller-provided PDFium. Hosted surfaces, production positioning, Windows packaged artifacts, "
    "bundled project-maintained PDFium builds, `ethos-doc`, `ethos-rag`, public benchmark reports, "
    "public benchmark claims, and speed, footprint, parser-quality, table-quality, or production "
    "claims remain blocked."
)

FORBIDDEN_SCOPE_EXPANSION = (
    "npm publication approved",
    "vendor payload refreshed",
    "hosted surfaces approved",
    "production positioning approved",
    "windows packaged artifacts approved",
    "bundled pdfium approved",
    "public benchmark claims approved",
    "production-ready",
    "benchmark-validated",
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


class Patch011ArtifactPublicationApprovalDecisionTests(unittest.TestCase):
    def test_record_is_source_bound(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)

        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", raw)
        self.assertIn(
            f"Patch 0.1.1 artifact publication approval decision source commit: `{SOURCE_COMMIT}`",
            record,
        )
        self.assertIn(
            f"Patch 0.1.1 artifact publication approval decision source tree: `{SOURCE_TREE}`",
            record,
        )
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_decision_accepts_exact_release_assets_only(self) -> None:
        record = normalized(RECORD)

        for expected in (
            "Decision: accept the exact patch `0.1.1` artifact publication request.",
            "Exact GitHub Release tag accepted by this decision: `v0.1.1`",
            RUN_URL,
            WORKFLOW_HEAD,
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
            "Exact CLI smoke accepted by this decision: `ethos 0.1.1`",
            "caller-provided PDFium only through `ETHOS_PDFIUM_LIBRARY_PATH`",
        ):
            self.assertIn(expected, record)

    def test_decision_preserves_bounded_public_wording(self) -> None:
        record = re.sub(r"\s+", " ", read(RECORD).replace("> ", ""))

        self.assertIn(APPROVED_WORDING, record)
        self.assertIn("Any broader public wording requires a separate decider record.", record)

    def test_decision_requires_later_operator_upload_and_closeout(self) -> None:
        record = normalized(RECORD)

        self.assertIn("This decision does not itself upload artifacts.", record)
        self.assertIn("Publication remains an explicit later operator action.", record)
        self.assertIn("post-upload closeout evidence", record)
        self.assertIn("python3 .github/scripts/test_patch_0_1_1_artifact_publication_approval_decision.py", record)
        self.assertIn("make release-candidate-prep PYTHON=python3", record)

    def test_retains_unrelated_blockers_and_avoids_scope_expansion(self) -> None:
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
        for phrase in FORBIDDEN_SCOPE_EXPANSION:
            self.assertNotIn(phrase, lower)
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
        self.assertIn("patch 0.1.1 artifact publication approval decision", readme.lower())
        self.assertIn(
            "$(PYTHON) .github/scripts/test_patch_0_1_1_artifact_publication_approval_decision.py",
            block,
        )


if __name__ == "__main__":
    unittest.main()
