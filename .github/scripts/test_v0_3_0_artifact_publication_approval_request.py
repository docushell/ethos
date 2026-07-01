#!/usr/bin/env python3
#
# Copyright 2026 The Ethos maintainers
#
# Licensed under the Apache License, Version 2.0 (the "License");
#

from __future__ import annotations

import re
import unittest
from pathlib import Path

from makefile_guard import target_block
from validation_record_source import assert_record_source_binding


ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / (
    "docs/validation/"
    "v0-3-0-artifact-publication-approval-request-validation-2026-07-01.md"
)
DRAFT_EVIDENCE = ROOT / "docs/validation/v0-3-0-draft-artifact-evidence-validation-2026-07-01.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"
RELEASE_PREP = ROOT / "docs/v0-3-0-release-prep.md"
MAKEFILE = ROOT / "Makefile"

SOURCE_SHORT = "d6496e8"
SOURCE_COMMIT = "d6496e82e613e653edc197db4cf4153271d131dc"
SOURCE_TREE = "2594c63071c512f2c61e78b223a74406440a8516"
RUN_URL = "https://github.com/docushell/ethos/actions/runs/28531102130"
WORKFLOW_HEAD = "7287358475a96e827d536f0d2d250a1c2961ba84"
MACOS_SHA256 = "efb163f140bf4afffd1caeb396f79e42f484591c3e90a86810ca6c0f0c209c96"
LINUX_SHA256 = "b549ba5968e04b7679a8d3e879cd45d27f3e9a6fd226eee5c270a4e4f5c01405"

REQUESTED_WORDING = (
    "Ethos v0.3.0 CLI artifacts for macOS arm64 and Linux x64 are requested for GitHub "
    "Release evaluation with caller-provided PDFium. Rust crates `ethos-doc-core`, "
    "`ethos-verify`, and `ethos-pdf` at `0.3.0`, plus the Python `ethos-pdf` wheel at "
    "`0.3.0`, are already live. npm alignment/publication, public `0.3.0` install wording, "
    "release/package tags, DocuShell integration, hosted surfaces, production positioning, "
    "Windows packaged artifacts, bundled project-maintained PDFium builds, `ethos-doc`, "
    "`ethos-rag`, public benchmark reports, public benchmark claims, and speed, footprint, "
    "parser-quality, table-quality, or production claims remain blocked."
)
FORBIDDEN_SCOPE_EXPANSION = (
    "publication approved",
    "published artifacts",
    "uploaded",
    "release complete",
    "tag created",
    "github release artifact publication approved",
    "github release publication approved",
    "npm vendor refresh approved",
    "npm publication approved",
    "release tag creation approved",
    "package tag creation approved",
    "public installation wording approved",
    "public install wording approved",
    "installable 0.3.0 wording approved",
    "docushell integration approved",
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


class V030ArtifactPublicationApprovalRequestTests(unittest.TestCase):
    def test_record_binds_source_and_draft_artifact_evidence(self) -> None:
        raw = read(RECORD)
        text = normalized(RECORD)

        assert_record_source_binding(
            self,
            root=ROOT,
            raw_record=raw,
            normalized_record=text,
            validated_head=SOURCE_SHORT,
            source_label="v0.3.0 artifact publication approval request",
            source_commit=SOURCE_COMMIT,
            source_tree=SOURCE_TREE,
        )
        self.assertIn(DRAFT_EVIDENCE.name, text)
        self.assertIn(RUN_URL, text)
        self.assertIn("Run status: `completed`", text)
        self.assertIn("Run conclusion: `success`", text)
        self.assertIn("Run event: `workflow_dispatch`", text)
        self.assertIn("Run branch: `main`", text)
        self.assertIn(f"Run head SHA: `{WORKFLOW_HEAD}`", text)

    def test_record_requests_only_exact_cli_artifacts_for_v0_3_0(self) -> None:
        text = normalized(RECORD)

        self.assertIn("GitHub Release `v0.3.0`", text)
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
        self.assertIn("Both smoke sidecars report `ethos 0.3.0`", text)
        self.assertIn("Both inventory sidecars report `draft_not_release_ready`", text)
        self.assertIn("`publication: blocked`", text)

    def test_record_preserves_bounded_request_wording_and_current_install_baseline(self) -> None:
        record = re.sub(r"\s+", " ", read(RECORD).replace("> ", ""))

        self.assertIn(REQUESTED_WORDING, record)
        self.assertIn("Any broader public wording requires a separate decision record.", record)
        self.assertIn(
            "public install baseline remains current published `0.2.0` Rust/Python and `0.2.1` npm",
            record,
        )
        self.assertIn("README installation examples remain unchanged", record)

    def test_record_keeps_upload_tags_npm_and_install_wording_blocked(self) -> None:
        raw = read(RECORD)
        text = normalized(RECORD)
        lower = text.lower()

        for blocker in (
            "GitHub Release artifact publication remains blocked",
            "GitHub Release artifact upload remains blocked",
            "npm vendor refresh remains blocked",
            "npm publication remains blocked",
            "Release tag creation remains blocked",
            "Package tag creation remains blocked",
            "Public installation wording remains blocked",
            "DocuShell integration remains blocked",
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
        self.assertIn("Upload remains blocked until explicit approval is recorded.", text)
        for forbidden in FORBIDDEN_SCOPE_EXPANSION:
            self.assertNotIn(forbidden, lower)
        for private in PRIVATE_PATH_MARKERS:
            self.assertNotIn(private, raw)

    def test_record_is_indexed_statused_and_wired_after_draft_artifact_guard(self) -> None:
        readme = normalized(VALIDATION_README)
        execution = normalized(EXECUTION_STATUS)
        checklist = normalized(PUBLIC_RELEASE_CHECKLIST)
        release_prep = normalized(RELEASE_PREP)
        block = target_block("v0-3-release-prep")
        draft_guard = "$(PYTHON) .github/scripts/test_v0_3_0_draft_artifact_evidence.py"
        request_guard = "$(PYTHON) .github/scripts/test_v0_3_0_artifact_publication_approval_request.py"
        public_surface_guard = "$(PYTHON) .github/scripts/test_public_surface_posture.py"

        for text in (readme, execution, checklist, release_prep):
            self.assertIn(RECORD.name, text)
            self.assertIn("v0.3.0 artifact publication approval request", text.lower())
            self.assertIn("GitHub Release artifact upload remains blocked", text)
        self.assertIn(request_guard, block)
        self.assertEqual(1, block.count(request_guard))
        self.assertLess(block.index(draft_guard), block.index(request_guard))
        self.assertLess(block.index(request_guard), block.index(public_surface_guard))


if __name__ == "__main__":
    unittest.main()
