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
RECORD = ROOT / (
    "docs/validation/"
    "patch-0-1-1-artifact-publication-approval-request-validation-2026-06-23.md"
)
VALIDATION_README = ROOT / "docs/validation/README.md"

SOURCE_SHORT = "bfc6dc1"
SOURCE_COMMIT = "bfc6dc11801af4416b6760c1bbd216c5a1a22809"
SOURCE_TREE = "41680dbd9d506df280a5ca246c4225db6a047be7"
RUN_URL = "https://github.com/docushell/ethos/actions/runs/28040466463"
MACOS_SHA256 = "eac79cddc6f5fc834ecc279401905729978d73e99ae11a2bea82d7356a4bcd88"
LINUX_SHA256 = "842aa4b71333aecc54f344d9f5362160d0943d8efd32dffabe99dc19553916a0"

APPROVAL_REQUEST_WORDING = (
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


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalized(path: Path) -> str:
    return re.sub(r"\s+", " ", read(path))


class Patch011ArtifactPublicationApprovalRequestTests(unittest.TestCase):
    def test_record_binds_current_source_and_workflow_evidence(self) -> None:
        raw = read(RECORD)
        text = normalized(RECORD)

        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", raw)
        self.assertIn(f"Artifact-publication-request source commit: `{SOURCE_COMMIT}`", text)
        self.assertIn(f"Artifact-publication-request source tree: `{SOURCE_TREE}`", text)
        self.assertIn(RUN_URL, text)
        self.assertIn("Run conclusion: `success`", text)
        self.assertIn("Run event: `workflow_dispatch`", text)
        self.assertIn("Run branch: `main`", text)

    def test_record_requests_only_exact_cli_artifacts_for_v0_1_1(self) -> None:
        text = normalized(RECORD)

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
        self.assertIn("GitHub Release tag `v0.1.1`", text)
        self.assertIn(MACOS_SHA256, text)
        self.assertIn(LINUX_SHA256, text)
        self.assertIn("Both smoke sidecars report `ethos 0.1.1`", text)
        self.assertIn("Both inventory sidecars report `draft_not_release_ready`", text)
        self.assertIn("`publication: blocked`", text)

    def test_record_preserves_bounded_public_wording(self) -> None:
        record = re.sub(r"\s+", " ", read(RECORD).replace("> ", ""))

        self.assertIn(APPROVAL_REQUEST_WORDING, record)
        self.assertIn("Any broader public wording requires a separate decider record.", record)

    def test_record_keeps_publication_blocked_until_explicit_approval(self) -> None:
        raw = read(RECORD)
        text = normalized(RECORD)
        lower = text.lower()

        for blocker in (
            "GitHub Release artifact publication remains blocked",
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
        self.assertIn("Publication remains blocked until explicit approval is recorded.", text)
        for forbidden in (
            "publication approved",
            "published artifacts",
            "npm publication approved",
            "vendor payload refreshed",
            "production-ready",
            "benchmark-validated",
            "bundled pdfium approved",
        ):
            self.assertNotIn(forbidden, lower)

    def test_record_is_indexed_and_wired_into_release_candidate_prep(self) -> None:
        readme = normalized(VALIDATION_README)
        block = target_block("release-candidate-prep")

        self.assertIn(RECORD.name, readme)
        self.assertIn("patch 0.1.1 artifact publication approval request", readme.lower())
        self.assertIn(
            "$(PYTHON) .github/scripts/test_patch_0_1_1_artifact_publication_approval_request.py",
            block,
        )

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
