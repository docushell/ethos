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
    "patch-0-1-2-artifact-publication-approval-request-validation-2026-06-24.md"
)
VALIDATION_README = ROOT / "docs/validation/README.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"

SOURCE_SHORT = "09750a8"
SOURCE_COMMIT = "09750a81cb72cbc91f9e0c35e52ae2711c2ee7b7"
SOURCE_TREE = "7a7eeb7b3b258facd4f171ce00ed4df5533259b1"
RUN_URL = "https://github.com/docushell/ethos/actions/runs/28102259869"
WORKFLOW_HEAD = "2cb092b403eefe937e30c902fcebf7bb5754d590"
MACOS_SHA256 = "7da7da71fb0c21b25cd2ffc198480ee80bf9f0c9e70e461cffbdcbdda8d7023c"
LINUX_SHA256 = "4e260b464dc9557bc31c29fb1d1dfa75311fe12734bc79af4a31e1649797e456"

REQUESTED_WORDING = (
    "Ethos patch `0.1.2` CLI artifacts for macOS arm64 and Linux x64 are requested for public beta "
    "evaluation with caller-provided PDFium. Rust crates, the Python wheel, npm package install "
    "instructions, and public README installation examples remain on the published `0.1.1` baseline "
    "until separate registry, npm vendor refresh, and public wording closeout records pass. Hosted "
    "surfaces, production positioning, Windows packaged artifacts, bundled project-maintained PDFium "
    "builds, `ethos-doc`, `ethos-rag`, public benchmark reports, public benchmark claims, and speed, "
    "footprint, parser-quality, table-quality, or production claims remain blocked."
)
FORBIDDEN_SCOPE_EXPANSION = (
    "publication approved",
    "published artifacts",
    "uploaded",
    "release complete",
    "tag created",
    "github release artifact publication approved",
    "github release publication approved",
    "registry publication approved",
    "npm vendor refresh approved",
    "npm publication approved",
    "public installation wording approved",
    "public install wording approved",
    "vendor payload refreshed",
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


class Patch012ArtifactPublicationApprovalRequestTests(unittest.TestCase):
    def test_record_binds_source_and_draft_artifact_evidence(self) -> None:
        raw = read(RECORD)
        text = normalized(RECORD)

        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", raw)
        self.assertIn(f"Patch 0.1.2 artifact publication approval request source commit: `{SOURCE_COMMIT}`", text)
        self.assertIn(f"Patch 0.1.2 artifact publication approval request source tree: `{SOURCE_TREE}`", text)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))
        self.assertIn("patch-0-1-2-draft-artifact-evidence-validation-2026-06-24.md", text)
        self.assertIn(RUN_URL, text)
        self.assertIn("Run status: `completed`", text)
        self.assertIn("Run conclusion: `success`", text)
        self.assertIn("Run event: `workflow_dispatch`", text)
        self.assertIn("Run branch: `main`", text)
        self.assertIn(f"Run head SHA: `{WORKFLOW_HEAD}`", text)

    def test_record_requests_only_exact_cli_artifacts_for_v0_1_2(self) -> None:
        text = normalized(RECORD)

        self.assertIn("GitHub Release `v0.1.2`", text)
        for artifact in (
            "ethos-macos-arm64.tar.gz",
            "ethos-macos-arm64.tar.gz.sha256",
            "ethos-macos-arm64.inventory.json",
            "ethos-macos-arm64.smoke.json",
            "ethos-linux-x64.tar.gz",
            "ethos-linux-x64.tar.gz.sha256",
            "ethos-linux-x64.inventory.json",
            "ethos-linux-x64.smoke.json",
        ):
            self.assertIn(artifact, text)
        self.assertIn(MACOS_SHA256, text)
        self.assertIn(LINUX_SHA256, text)
        self.assertIn("Both smoke sidecars report `ethos 0.1.2`", text)
        self.assertIn("Both inventory sidecars report `draft_not_release_ready`", text)
        self.assertIn("`publication: blocked`", text)

    def test_record_preserves_bounded_request_wording_and_public_install_baseline(self) -> None:
        record = re.sub(r"\s+", " ", read(RECORD).replace("> ", ""))

        self.assertIn(REQUESTED_WORDING, record)
        self.assertIn("Any broader public wording requires a separate decision record.", record)
        self.assertIn("public install baseline remains `0.1.1`", record)
        self.assertIn("README installation examples remain unchanged", record)

    def test_record_keeps_publication_blocked_until_explicit_decision(self) -> None:
        raw = read(RECORD)
        text = normalized(RECORD)
        lower = text.lower()

        for blocker in (
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
        ):
            self.assertIn(blocker, raw)
        self.assertIn("Publication remains blocked until explicit approval is recorded.", text)
        for forbidden in FORBIDDEN_SCOPE_EXPANSION:
            self.assertNotIn(forbidden, lower)
        for private in PRIVATE_PATH_MARKERS:
            self.assertNotIn(private, raw)

    def test_record_is_indexed_statused_and_wired_into_release_candidate_prep(self) -> None:
        readme = normalized(VALIDATION_README)
        execution = normalized(EXECUTION_STATUS)
        checklist = normalized(PUBLIC_RELEASE_CHECKLIST)
        block = target_block("release-candidate-prep")
        draft_guard = "$(PYTHON) .github/scripts/test_patch_0_1_2_draft_artifact_evidence.py"
        request_guard = "$(PYTHON) .github/scripts/test_patch_0_1_2_artifact_publication_approval_request.py"
        first_public_guard = "$(PYTHON) .github/scripts/test_first_public_release_artifact_evidence.py"

        self.assertIn(RECORD.name, readme)
        self.assertIn("patch 0.1.2 artifact publication approval request", readme.lower())
        self.assertIn(RECORD.name, execution)
        self.assertIn(RECORD.name, checklist)
        self.assertIn(request_guard, block)
        self.assertEqual(1, block.count(request_guard))
        self.assertLess(block.index(draft_guard), block.index(request_guard))
        self.assertLess(block.index(request_guard), block.index(first_public_guard))


if __name__ == "__main__":
    unittest.main()
