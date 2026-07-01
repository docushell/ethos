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
RECORD = ROOT / "docs/validation/v0-3-0-draft-artifact-evidence-validation-2026-07-01.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"
RELEASE_PREP = ROOT / "docs/v0-3-0-release-prep.md"
MAKEFILE = ROOT / "Makefile"

SOURCE_SHORT = "7287358"
SOURCE_COMMIT = "7287358475a96e827d536f0d2d250a1c2961ba84"
SOURCE_TREE = "84d7908f91f3bb2024acb6bad4c71b6c75d4f357"
RUN_URL = "https://github.com/docushell/ethos/actions/runs/28531102130"
RUN_ID = "28531102130"
MACOS_SHA256 = "efb163f140bf4afffd1caeb396f79e42f484591c3e90a86810ca6c0f0c209c96"
LINUX_SHA256 = "b549ba5968e04b7679a8d3e879cd45d27f3e9a6fd226eee5c270a4e4f5c01405"
EXPECTED_ARTIFACTS = (
    "ethos-cli-draft-macos-arm64/ethos-macos-arm64.tar.gz",
    "ethos-cli-draft-macos-arm64/ethos-macos-arm64.tar.gz.sha256",
    "ethos-cli-draft-macos-arm64/ethos-macos-arm64.inventory.json",
    "ethos-cli-draft-macos-arm64/ethos-macos-arm64.smoke.json",
    "ethos-cli-draft-linux-x64/ethos-linux-x64.tar.gz",
    "ethos-cli-draft-linux-x64/ethos-linux-x64.tar.gz.sha256",
    "ethos-cli-draft-linux-x64/ethos-linux-x64.inventory.json",
    "ethos-cli-draft-linux-x64/ethos-linux-x64.smoke.json",
)
RETAINED_BLOCKERS = (
    "GitHub Release artifact publication remains blocked",
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
)
FORBIDDEN_APPROVALS = (
    "github release artifact publication approved",
    "github release publication approved",
    "npm vendor refresh approved",
    "npm publication approved",
    "release tag creation approved",
    "package tag creation approved",
    "public installation wording approved",
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


class V030DraftArtifactEvidenceTests(unittest.TestCase):
    def test_record_is_source_and_workflow_bound(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)

        assert_record_source_binding(
            self,
            root=ROOT,
            raw_record=raw,
            normalized_record=record,
            validated_head=SOURCE_SHORT,
            source_label="v0.3.0 draft CLI artifact evidence",
            source_commit=SOURCE_COMMIT,
            source_tree=SOURCE_TREE,
        )
        self.assertIn(RUN_URL, record)
        self.assertIn(f"run watch {RUN_ID}", record)
        self.assertIn("event: `workflow_dispatch`", record)
        self.assertIn("branch: `main`", record)
        self.assertIn(f"head SHA: `{SOURCE_COMMIT}`", record)
        self.assertIn("status: `completed`", record)
        self.assertIn("conclusion: `success`", record)
        self.assertIn("created at: `2026-07-01T16:06:05Z`", record)
        self.assertIn("updated at: `2026-07-01T16:07:15Z`", record)

    def test_record_captures_both_platform_artifacts_inventory_smoke_and_archives(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)

        for artifact in EXPECTED_ARTIFACTS:
            self.assertIn(artifact, record)
        for expected in (
            "cli-draft-artifacts (macos-arm64, macos-14, tar.gz)",
            "cli-draft-artifacts (linux-x64, ubuntu-latest, tar.gz)",
            MACOS_SHA256,
            LINUX_SHA256,
            "ethos-macos-arm64/",
            "ethos-linux-x64/",
            "pdfium-manual-setup.md",
            '"version_stdout": "ethos 0.3.0"',
            '"missing_pdfium_exit_code": 12',
            "ETHOS_PDFIUM_LIBRARY_PATH",
        ):
            self.assertIn(expected, record)
        self.assertEqual(2, raw.count('"schema": "ethos.release_artifact_inventory.v1"'))
        self.assertEqual(2, raw.count('"schema": "ethos.release_artifact_smoke.v1"'))
        self.assertEqual(2, raw.count('"publication": "blocked"'))
        self.assertEqual(2, raw.count('"status": "draft_not_release_ready"'))
        self.assertEqual(2, raw.count('"pdfium_policy": "caller-provided"'))

    def test_record_keeps_publication_vendor_tags_and_install_wording_blocked(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)
        lower = record.lower()

        self.assertIn(
            "public install baseline remains current published `0.2.0` Rust/Python and `0.2.1` npm",
            record,
        )
        self.assertIn("This record does not approve GitHub Release artifact publication.", record)
        self.assertIn("This record does not approve npm vendor refresh.", record)
        self.assertIn("This record does not create or approve release tags or package tags.", record)
        for blocker in RETAINED_BLOCKERS:
            self.assertIn(blocker, record)
        for forbidden in FORBIDDEN_APPROVALS:
            self.assertNotIn(forbidden, lower)
        for marker in PRIVATE_PATH_MARKERS:
            self.assertNotIn(marker, raw)

    def test_record_is_indexed_and_wired_after_artifact_prep_guard(self) -> None:
        readme = normalized(VALIDATION_README)
        execution = normalized(EXECUTION_STATUS)
        checklist = normalized(PUBLIC_RELEASE_CHECKLIST)
        block = target_block("v0-3-release-prep")
        prep_guard = "$(PYTHON) .github/scripts/test_v0_3_0_cli_artifact_evidence_prep.py"
        draft_guard = "$(PYTHON) .github/scripts/test_v0_3_0_draft_artifact_evidence.py"
        public_surface_guard = "$(PYTHON) .github/scripts/test_public_surface_posture.py"

        for text in (readme, execution, checklist):
            self.assertIn(RECORD.name, text)
            self.assertIn("v0.3.0 draft CLI artifact evidence", text)
            self.assertIn("ethos 0.3.0", text)
            self.assertIn("GitHub Release artifact upload remains blocked", text)
        self.assertIn(draft_guard, block)
        self.assertEqual(1, block.count(draft_guard))
        self.assertLess(block.index(prep_guard), block.index(draft_guard))
        self.assertLess(block.index(draft_guard), block.index(public_surface_guard))

    def test_release_prep_names_draft_artifact_evidence_without_publication(self) -> None:
        release_prep = normalized(RELEASE_PREP)

        self.assertIn("v0.3.0 CLI artifact evidence prep", release_prep)
        self.assertIn("v0.3.0 draft CLI artifact evidence", release_prep)
        self.assertIn(RUN_URL, release_prep)
        self.assertIn("Draft artifacts remain CI evidence only", release_prep)
        self.assertIn("GitHub Release artifact upload remains blocked", release_prep)
        self.assertIn("npm vendor refresh remains blocked", release_prep)
        self.assertIn("public install wording remains blocked", release_prep)


if __name__ == "__main__":
    unittest.main()
