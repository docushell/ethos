#!/usr/bin/env python3
#
# Copyright 2026 The Ethos maintainers
#
# Licensed under the Apache License, Version 2.0 (the "License");
#

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from makefile_guard import target_block
from validation_record_source import assert_record_source_binding


ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "docs/validation/v0-3-0-release-metadata-closeout-validation-2026-07-03.md"
NOTES = ROOT / "docs/releases/v0.3.0.md"
STATE = ROOT / "docs/release-state.json"
VALIDATION_README = ROOT / "docs/validation/README.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"
RELEASE_PREP = ROOT / "docs/v0-3-0-release-prep.md"
MAKEFILE = ROOT / "Makefile"

SOURCE_SHORT = "37c9ecd"
SOURCE_COMMIT = "37c9ecde01ec51fb425c6834a8526b45f9376655"
SOURCE_TREE = "c3d0da06122fcedf8c4279cbd44a668cbfe02720"
ASSETS = (
    "ethos-macos-arm64.tar.gz",
    "ethos-macos-arm64.tar.gz.sha256",
    "ethos-macos-arm64.inventory.json",
    "ethos-macos-arm64.smoke.json",
    "ethos-linux-x64.tar.gz",
    "ethos-linux-x64.tar.gz.sha256",
    "ethos-linux-x64.inventory.json",
    "ethos-linux-x64.smoke.json",
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


class V030ReleaseMetadataCloseoutTests(unittest.TestCase):
    def test_record_is_source_bound_and_indexed(self) -> None:
        raw = read(RECORD)
        text = normalized(RECORD)
        assert_record_source_binding(
            self,
            root=ROOT,
            raw_record=raw,
            normalized_record=text,
            validated_head=SOURCE_SHORT,
            source_label="v0.3.0 release metadata closeout",
            source_commit=SOURCE_COMMIT,
            source_tree=SOURCE_TREE,
        )
        self.assertIn(RECORD.name, read(VALIDATION_README))
        for marker in PRIVATE_PATH_MARKERS:
            self.assertNotIn(marker, raw)

    def test_record_closes_latest_body_and_asset_state(self) -> None:
        text = normalized(RECORD)
        for expected in (
            "Status: **v0.3.0 final GitHub Release metadata and latest pointer closed out**",
            "Release database id: `347912285`",
            "Latest release API tag: `v0.3.0`",
            "Release draft status: `false`",
            "Release prerelease status: `false`",
            "Canonical release notes: `docs/releases/v0.3.0.md`",
            "Published asset count: `8`",
            "--latest=false",
            "--latest",
            "check_github_release_metadata.py",
        ):
            self.assertIn(expected, text)
        for asset in ASSETS:
            self.assertIn(f"`{asset}`", text)

    def test_release_state_declares_exact_live_intent(self) -> None:
        state = json.loads(read(STATE))
        github = state["release"]["github_release"]
        self.assertEqual("v0.3.0", github["tag"])
        self.assertEqual("Release v0.3.0", github["name"])
        self.assertIs(True, github["latest"])
        self.assertEqual("docs/releases/v0.3.0.md", github["notes"])
        self.assertEqual(list(ASSETS), github["assets"])
        self.assertEqual(
            "docs/validation/v0-3-0-release-metadata-closeout-validation-2026-07-03.md",
            state["closed_lanes"]["release_metadata"],
        )

    def test_notes_explain_inventory_provenance_and_current_scope(self) -> None:
        notes = normalized(NOTES)
        for expected in (
            "public-beta evaluation release",
            "@docushell/ethos-pdf@0.3.0",
            "proof-summary and app-answer-release helpers",
            "draft_not_release_ready",
            "publication: blocked",
            "pre-publication CI provenance",
            "ETHOS_PDFIUM_LIBRARY_PATH",
            "DocuShell integration",
        ):
            self.assertIn(expected, notes)

    def test_current_docs_and_release_gate_include_metadata_closeout(self) -> None:
        for path in (EXECUTION_STATUS, PUBLIC_RELEASE_CHECKLIST, RELEASE_PREP):
            text = normalized(path)
            self.assertIn(RECORD.name, text, str(path))
            self.assertIn("repository's latest release", text, str(path))

        block = target_block("v0-3-release-prep")
        release_tag = "$(PYTHON) .github/scripts/test_v0_3_0_release_tag_closeout.py"
        metadata = "$(PYTHON) .github/scripts/test_v0_3_0_release_metadata_closeout.py"
        public_surface = "$(PYTHON) .github/scripts/test_public_surface_posture.py"
        self.assertIn(metadata, block)
        self.assertEqual(1, read(MAKEFILE).count(metadata))
        self.assertLess(block.index(release_tag), block.index(metadata))
        self.assertLess(block.index(metadata), block.index(public_surface))


if __name__ == "__main__":
    unittest.main()
