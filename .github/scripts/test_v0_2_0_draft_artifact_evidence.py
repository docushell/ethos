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
RECORD = ROOT / "docs/validation/v0-2-0-draft-artifact-evidence-validation-2026-06-25.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"

SOURCE_SHORT = "36955ca"
SOURCE_COMMIT = "36955cac69dc4eed624feb22b1a8c5e8a811d3bd"
SOURCE_TREE = "7ca47e76dfa2d23d40768dbcb88e2b97fba619b2"
RUN_URL = "https://github.com/docushell/ethos/actions/runs/28175143857"
RUN_ID = "28175143857"
MACOS_SHA256 = "c588ee77bbaf99a7d933673e6cd9db190f5992e47d40955def803435a9f9fc5a"
LINUX_SHA256 = "00137b20ca2c2a2d2089df1d135920b021b0905d779b1347d134e8a2fb7bfa23"
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
    "Registry publication remains blocked",
    "PyPI upload remains blocked",
    "npm vendor refresh remains blocked pending a separate refresh record",
    "npm publication remains blocked",
    "Release tag creation remains blocked",
    "Package tag creation remains blocked",
    "Public installation wording remains blocked",
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
    "registry publication approved",
    "pypi upload approved",
    "npm vendor refresh approved",
    "npm publication approved",
    "release tag creation approved",
    "package tag creation approved",
    "public installation wording approved",
    "installable 0.2.0 wording approved",
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


class V020DraftArtifactEvidenceTests(unittest.TestCase):
    def test_record_is_source_and_workflow_bound(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)

        assert_record_source_binding(
            self,
            root=ROOT,
            raw_record=raw,
            normalized_record=record,
            validated_head=SOURCE_SHORT,
            source_label="v0.2.0 draft artifact evidence",
            source_commit=SOURCE_COMMIT,
            source_tree=SOURCE_TREE,
        )
        self.assertIn(RUN_URL, record)
        self.assertIn(f"run watch {RUN_ID}", record)
        self.assertIn("event: `workflow_dispatch`", record)
        self.assertIn("branch: `dev/v0-2-approval-packet`", record)
        self.assertIn(f"head SHA: `{SOURCE_COMMIT}`", record)
        self.assertIn("status: `completed`", record)
        self.assertIn("conclusion: `success`", record)
        self.assertIn("created at: `2026-06-25T13:52:38Z`", record)
        self.assertIn("updated at: `2026-06-25T13:53:52Z`", record)

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
            '"version_stdout": "ethos 0.2.0"',
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

        self.assertIn("public install baseline remains `0.1.2`", record)
        self.assertIn("This record does not approve GitHub Release artifact publication.", record)
        self.assertIn("This record does not approve npm vendor refresh.", record)
        self.assertIn("This record does not create or approve release tags or package tags.", record)
        for blocker in RETAINED_BLOCKERS:
            self.assertIn(blocker, record)
        for forbidden in FORBIDDEN_APPROVALS:
            self.assertNotIn(forbidden, lower)
        for marker in PRIVATE_PATH_MARKERS:
            self.assertNotIn(marker, raw)

    def test_record_is_indexed_and_wired_after_package_build_evidence_guard(self) -> None:
        readme = normalized(VALIDATION_README)
        execution = normalized(EXECUTION_STATUS)
        checklist = normalized(PUBLIC_RELEASE_CHECKLIST)
        block = target_block("v0-2-release-prep")
        package_guard = "$(PYTHON) .github/scripts/test_v0_2_0_package_build_evidence.py"
        draft_guard = "$(PYTHON) .github/scripts/test_v0_2_0_draft_artifact_evidence.py"
        claims = "$(PYTHON) .github/scripts/claims_gate.py"

        for text in (readme, execution, checklist):
            self.assertIn(RECORD.name, text)
            self.assertIn("draft artifact evidence", text.lower())
            self.assertIn("ethos 0.2.0", text)
        self.assertIn(draft_guard, block)
        self.assertEqual(1, block.count(draft_guard))
        self.assertLess(block.index(package_guard), block.index(draft_guard))
        self.assertLess(block.index(draft_guard), block.index(claims))


if __name__ == "__main__":
    unittest.main()
