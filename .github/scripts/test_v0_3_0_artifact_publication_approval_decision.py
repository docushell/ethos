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
    "v0-3-0-artifact-publication-approval-decision-validation-2026-07-01.md"
)
REQUEST = ROOT / (
    "docs/validation/"
    "v0-3-0-artifact-publication-approval-request-validation-2026-07-01.md"
)
DRAFT_EVIDENCE = ROOT / "docs/validation/v0-3-0-draft-artifact-evidence-validation-2026-07-01.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"
RELEASE_PREP = ROOT / "docs/v0-3-0-release-prep.md"

SOURCE_SHORT = "a20b42a"
SOURCE_COMMIT = "a20b42a7927052f727fcaaa585a7a050aec02abe"
SOURCE_TREE = "ed4f624ad29a8c8c457b045b2519b5aadb2c4f40"
REQUEST_SOURCE_COMMIT = "d6496e82e613e653edc197db4cf4153271d131dc"
REQUEST_SOURCE_TREE = "2594c63071c512f2c61e78b223a74406440a8516"
ARTIFACT_SOURCE_COMMIT = "7287358475a96e827d536f0d2d250a1c2961ba84"
ARTIFACT_SOURCE_TREE = "84d7908f91f3bb2024acb6bad4c71b6c75d4f357"
RUN_URL = "https://github.com/docushell/ethos/actions/runs/28531102130"
MACOS_SHA256 = "efb163f140bf4afffd1caeb396f79e42f484591c3e90a86810ca6c0f0c209c96"
LINUX_SHA256 = "b549ba5968e04b7679a8d3e879cd45d27f3e9a6fd226eee5c270a4e4f5c01405"

APPROVED_WORDING = (
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
    "npm vendor refresh approved",
    "npm publication approved",
    "package tag creation approved",
    "public installation wording approved",
    "public install wording approved",
    "installable 0.3.0 wording approved",
    "docushell integration approved",
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


class V030ArtifactPublicationApprovalDecisionTests(unittest.TestCase):
    def test_record_is_source_bound(self) -> None:
        raw = read(RECORD)
        text = normalized(RECORD)

        assert_record_source_binding(
            self,
            root=ROOT,
            raw_record=raw,
            normalized_record=text,
            validated_head=SOURCE_SHORT,
            source_label="v0.3.0 artifact publication approval decision",
            source_commit=SOURCE_COMMIT,
            source_tree=SOURCE_TREE,
        )

    def test_decision_accepts_exact_release_assets_only(self) -> None:
        text = normalized(RECORD)

        for expected in (
            "Decision: accept the exact v0.3.0 artifact publication request.",
            "Exact GitHub Release target accepted by this decision: `v0.3.0`",
            REQUEST.name,
            DRAFT_EVIDENCE.name,
            f"Exact request source commit accepted by this decision: `{REQUEST_SOURCE_COMMIT}`",
            f"Exact request source tree accepted by this decision: `{REQUEST_SOURCE_TREE}`",
            f"Exact artifact source commit accepted by this decision: `{ARTIFACT_SOURCE_COMMIT}`",
            f"Exact artifact source tree accepted by this decision: `{ARTIFACT_SOURCE_TREE}`",
            RUN_URL,
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
            "Exact CLI smoke accepted by this decision: `ethos 0.3.0`",
            "caller-provided PDFium only through `ETHOS_PDFIUM_LIBRARY_PATH`",
        ):
            self.assertIn(expected, text)

    def test_decision_preserves_bounded_public_wording_and_install_baseline(self) -> None:
        record = re.sub(r"\s+", " ", read(RECORD).replace("> ", ""))

        self.assertIn(APPROVED_WORDING, record)
        self.assertIn("Any broader public wording requires a separate decider record.", record)
        self.assertIn(
            "public install baseline remains current published `0.2.0` Rust/Python and `0.2.1` npm",
            record,
        )
        self.assertIn("README installation examples remain unchanged", record)

    def test_decision_requires_later_operator_upload_and_closeout(self) -> None:
        text = normalized(RECORD)

        self.assertIn("This decision does not itself upload artifacts.", text)
        self.assertIn("Publication remains an explicit later operator action.", text)
        self.assertIn("post-upload closeout evidence", text)
        self.assertIn(
            "operator may attach only the exact accepted asset names above to GitHub Release target `v0.3.0`",
            text,
        )
        self.assertIn("The operator must not create or use any other release target.", text)
        self.assertIn(
            "python3 .github/scripts/test_v0_3_0_artifact_publication_approval_decision.py",
            text,
        )
        self.assertIn("make v0-3-release-prep PYTHON=python3", text)

    def test_retains_unrelated_blockers_and_avoids_scope_expansion(self) -> None:
        raw = read(RECORD)
        lower = normalized(RECORD).lower()

        for blocker in (
            "`packages/npm/ethos-pdf/vendor/manifest.json` must not be refreshed",
            "npm vendor refresh remains blocked",
            "npm publication remains blocked",
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
        for phrase in FORBIDDEN_SCOPE_EXPANSION:
            self.assertNotIn(phrase, lower)
        for private in PRIVATE_PATH_MARKERS:
            self.assertNotIn(private, raw)

    def test_record_is_indexed_statused_and_wired_after_request_guard(self) -> None:
        readme = normalized(VALIDATION_README)
        execution = normalized(EXECUTION_STATUS)
        checklist = normalized(PUBLIC_RELEASE_CHECKLIST)
        release_prep = normalized(RELEASE_PREP)
        block = target_block("v0-3-release-prep")
        request_guard = "$(PYTHON) .github/scripts/test_v0_3_0_artifact_publication_approval_request.py"
        decision_guard = "$(PYTHON) .github/scripts/test_v0_3_0_artifact_publication_approval_decision.py"
        public_surface_guard = "$(PYTHON) .github/scripts/test_public_surface_posture.py"

        for text in (readme, execution, checklist, release_prep):
            self.assertIn(RECORD.name, text)
            self.assertIn("v0.3.0 artifact publication approval decision", text.lower())
            self.assertIn("GitHub Release artifact upload remains blocked", text)
            self.assertIn("operator action and closeout", text)
        self.assertIn(decision_guard, block)
        self.assertEqual(1, block.count(decision_guard))
        self.assertLess(block.index(request_guard), block.index(decision_guard))
        self.assertLess(block.index(decision_guard), block.index(public_surface_guard))


if __name__ == "__main__":
    unittest.main()
