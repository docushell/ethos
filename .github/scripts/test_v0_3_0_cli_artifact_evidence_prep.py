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
RECORD = ROOT / "docs/validation/v0-3-0-cli-artifact-evidence-prep-validation-2026-07-01.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"
RELEASE_PREP = ROOT / "docs/v0-3-0-release-prep.md"
WORKFLOW = ROOT / ".github/workflows/release.yml"
MAKEFILE = ROOT / "Makefile"

SOURCE_SHORT = "3ae36b9"
SOURCE_COMMIT = "3ae36b95f9fe7c1f74f58075eacbbaaa7c469bea"
SOURCE_TREE = "d9d6313cd28b647eba89e02b29adcba54349c190"
EXPECTED_VERSION = "ethos 0.3.0"
GUARD_NAME = "test_v0_3_0_cli_artifact_evidence_prep.py"
PRIVATE_PATH_MARKERS = (
    "/" + "Users/",
    "/" + "private/tmp",
    "/" + "private/var",
    "/" + "var/folders",
    "saumil" + "diwaker",
    "Desktop/" + "Stuff",
    "project/repo/" + "ethos",
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


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalized(path: Path) -> str:
    return re.sub(r"\s+", " ", read(path))


class V030CliArtifactEvidencePrepTests(unittest.TestCase):
    def test_record_is_source_bound_and_indexed(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)

        assert_record_source_binding(
            self,
            root=ROOT,
            raw_record=raw,
            normalized_record=record,
            validated_head=SOURCE_SHORT,
            source_label="v0.3.0 CLI artifact evidence prep",
            source_commit=SOURCE_COMMIT,
            source_tree=SOURCE_TREE,
        )

        for path in (VALIDATION_README, EXECUTION_STATUS, PUBLIC_RELEASE_CHECKLIST):
            text = normalized(path)
            self.assertIn(RECORD.name, text, str(path))
            self.assertIn("v0.3.0 CLI artifact evidence prep", text, str(path))
            self.assertIn("GitHub Release artifact upload remains blocked", text, str(path))

    def test_release_workflow_is_aligned_to_v0_3_draft_artifact_smoke(self) -> None:
        workflow = read(WORKFLOW)

        self.assertIn("cli-draft-artifacts", workflow)
        self.assertIn("macos-arm64", workflow)
        self.assertIn("linux-x64", workflow)
        self.assertIn("cargo build --locked --release -p ethos-cli", workflow)
        self.assertIn("write_release_artifact_inventory.py", workflow)
        self.assertIn("smoke_release_cli_artifact.py", workflow)
        self.assertIn(f'--expected-version "{EXPECTED_VERSION}"', workflow)
        self.assertNotIn('--expected-version "ethos 0.2.0"', workflow)
        self.assertIn("validate_release_artifact_inventory.py", workflow)
        self.assertIn("actions/upload-artifact@v4", workflow)
        self.assertNotIn("gh release create", workflow)
        self.assertNotIn("gh release upload", workflow)
        self.assertNotIn("npm publish", workflow)

    def test_record_names_required_later_artifact_evidence_without_claiming_it(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)
        lower = record.lower()

        for expected in (
            "No workflow run is recorded by this prep record.",
            'The workflow now passes `--expected-version "ethos 0.3.0"`',
            "The next record must capture the workflow run URL and run id.",
            "The next record must capture macOS arm64 and Linux x64 archive SHA256 values",
            '"version_stdout": "ethos 0.3.0"',
            "GH_PROMPT_DISABLED=1 gh workflow run release.yml --repo docushell/ethos --ref dev/v0-3-cli-artifact-evidence-prep",
            "python3 .github/scripts/validate_release_artifact_inventory.py <artifact-download-dir>/*/*.inventory.json",
            "GitHub Release artifact publication remains blocked.",
            "npm vendor refresh remains blocked.",
            "npm publication remains blocked.",
            "Public installation wording remains blocked.",
            "DocuShell integration remains blocked.",
        ):
            self.assertIn(expected, record)
        for forbidden in FORBIDDEN_APPROVALS:
            self.assertNotIn(forbidden, lower)
        for marker in PRIVATE_PATH_MARKERS:
            self.assertNotIn(marker, raw)

    def test_release_prep_and_v0_3_gate_include_the_artifact_prep_guard(self) -> None:
        release_prep = normalized(RELEASE_PREP)
        makefile = read(MAKEFILE)
        block = target_block("v0-3-release-prep")
        closeout_guard = "$(PYTHON) .github/scripts/test_v0_3_0_publication_closeout.py"
        prep_guard = f"$(PYTHON) .github/scripts/{GUARD_NAME}"
        public_surface_guard = "$(PYTHON) .github/scripts/test_public_surface_posture.py"

        self.assertIn('`--expected-version "ethos 0.3.0"`', release_prep)
        self.assertIn("v0.3.0 CLI artifact evidence prep", release_prep)
        self.assertIn(prep_guard, block)
        self.assertEqual(1, makefile.count(prep_guard))
        self.assertLess(block.index(closeout_guard), block.index(prep_guard))
        self.assertLess(block.index(prep_guard), block.index(public_surface_guard))


if __name__ == "__main__":
    unittest.main()
