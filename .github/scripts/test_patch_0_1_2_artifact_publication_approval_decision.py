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
    "patch-0-1-2-artifact-publication-approval-decision-validation-2026-06-24.md"
)
VALIDATION_README = ROOT / "docs/validation/README.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"

SOURCE_SHORT = "94c2ea4"
SOURCE_COMMIT = "94c2ea490883a042ee026c9c3565e92121f16c3f"
SOURCE_TREE = "6016ad317aae4efe01eadcd1d643f9c2f0be2ee5"
ARTIFACT_SOURCE_SHORT = "09750a8"
ARTIFACT_SOURCE_COMMIT = "09750a81cb72cbc91f9e0c35e52ae2711c2ee7b7"
ARTIFACT_SOURCE_TREE = "7a7eeb7b3b258facd4f171ce00ed4df5533259b1"
RUN_URL = "https://github.com/docushell/ethos/actions/runs/28102259869"
WORKFLOW_HEAD = "2cb092b403eefe937e30c902fcebf7bb5754d590"
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
FORBIDDEN_SCOPE_EXPANSION = (
    "registry publication approved",
    "npm vendor refresh approved",
    "npm publication approved",
    "public installation wording approved",
    "public install wording approved",
    "vendor payload refreshed",
    "hosted surfaces approved",
    "production positioning approved",
    "windows packaged artifacts approved",
    "bundled pdfium approved",
    "public benchmark claims approved",
    "production-ready",
    "benchmark-validated",
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


class Patch012ArtifactPublicationApprovalDecisionTests(unittest.TestCase):
    def test_record_is_source_bound(self) -> None:
        raw = read(RECORD)
        text = normalized(RECORD)

        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", raw)
        self.assertIn(f"Patch 0.1.2 artifact publication approval decision source commit: `{SOURCE_COMMIT}`", text)
        self.assertIn(f"Patch 0.1.2 artifact publication approval decision source tree: `{SOURCE_TREE}`", text)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_decision_accepts_exact_release_assets_only(self) -> None:
        text = normalized(RECORD)

        for expected in (
            "Decision: accept the exact patch `0.1.2` artifact publication request.",
            "Exact GitHub Release tag accepted by this decision: `v0.1.2`",
            "patch-0-1-2-artifact-publication-approval-request-validation-2026-06-24.md",
            "patch-0-1-2-draft-artifact-evidence-validation-2026-06-24.md",
            f"Exact artifact source commit accepted by this decision: `{ARTIFACT_SOURCE_COMMIT}`",
            f"Exact artifact source tree accepted by this decision: `{ARTIFACT_SOURCE_TREE}`",
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
            "Exact CLI smoke accepted by this decision: `ethos 0.1.2`",
            "caller-provided PDFium only through `ETHOS_PDFIUM_LIBRARY_PATH`",
        ):
            self.assertIn(expected, text)
        self.assertEqual(ARTIFACT_SOURCE_COMMIT, git("rev-parse", ARTIFACT_SOURCE_SHORT))
        self.assertEqual(ARTIFACT_SOURCE_TREE, git("rev-parse", f"{ARTIFACT_SOURCE_SHORT}^{{tree}}"))

    def test_decision_preserves_bounded_public_wording_and_install_baseline(self) -> None:
        record = re.sub(r"\s+", " ", read(RECORD).replace("> ", ""))

        self.assertIn(APPROVED_WORDING, record)
        self.assertIn("Any broader public wording requires a separate decider record.", record)
        self.assertIn("public install baseline remains `0.1.1`", record)
        self.assertIn("README installation examples remain unchanged", record)

    def test_decision_requires_later_operator_upload_and_closeout(self) -> None:
        text = normalized(RECORD)

        self.assertIn("This decision does not itself upload artifacts.", text)
        self.assertIn("Publication remains an explicit later operator action.", text)
        self.assertIn("post-upload closeout evidence", text)
        self.assertIn("python3 .github/scripts/test_patch_0_1_2_artifact_publication_approval_decision.py", text)
        self.assertIn("make release-candidate-prep PYTHON=python3", text)

    def test_retains_unrelated_blockers_and_avoids_scope_expansion(self) -> None:
        raw = read(RECORD)
        lower = normalized(RECORD).lower()

        for blocker in (
            "`packages/npm/ethos-pdf/vendor/manifest.json` must not be refreshed",
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
        for phrase in FORBIDDEN_SCOPE_EXPANSION:
            self.assertNotIn(phrase, lower)
        for private in PRIVATE_PATH_MARKERS:
            self.assertNotIn(private, raw)

    def test_record_is_indexed_statused_and_wired_into_release_candidate_prep(self) -> None:
        readme = normalized(VALIDATION_README)
        execution = normalized(EXECUTION_STATUS)
        checklist = normalized(PUBLIC_RELEASE_CHECKLIST)
        block = target_block("release-candidate-prep")
        request_guard = "$(PYTHON) .github/scripts/test_patch_0_1_2_artifact_publication_approval_request.py"
        decision_guard = "$(PYTHON) .github/scripts/test_patch_0_1_2_artifact_publication_approval_decision.py"
        first_public_guard = "$(PYTHON) .github/scripts/test_first_public_release_artifact_evidence.py"

        self.assertIn(RECORD.name, readme)
        self.assertIn("patch 0.1.2 artifact publication approval decision", readme.lower())
        self.assertIn(RECORD.name, execution)
        self.assertIn(RECORD.name, checklist)
        self.assertIn(decision_guard, block)
        self.assertEqual(1, block.count(decision_guard))
        self.assertLess(block.index(request_guard), block.index(decision_guard))
        self.assertLess(block.index(decision_guard), block.index(first_public_guard))


if __name__ == "__main__":
    unittest.main()
