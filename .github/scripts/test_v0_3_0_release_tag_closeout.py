#!/usr/bin/env python3
#
# Copyright 2026 The Ethos maintainers
#
# Licensed under the Apache License, Version 2.0 (the "License");
#

from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path

from makefile_guard import target_block
from validation_record_source import assert_record_source_binding


ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "docs/validation/v0-3-0-release-tag-closeout-validation-2026-07-02.md"
ARTIFACT_CLOSEOUT = ROOT / (
    "docs/validation/v0-3-0-artifact-publication-closeout-validation-2026-07-02.md"
)
PACKAGE_TAG_CLOSEOUT = ROOT / (
    "docs/validation/v0-3-0-package-tag-closeout-validation-2026-07-02.md"
)
VALIDATION_README = ROOT / "docs/validation/README.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"
RELEASE_PREP = ROOT / "docs/v0-3-0-release-prep.md"
CHANGELOG = ROOT / "CHANGELOG.md"
MAKEFILE = ROOT / "Makefile"

SOURCE_SHORT = "59471a6"
SOURCE_COMMIT = "59471a61b723c8a7de9173f804874b1d2e387c43"
SOURCE_TREE = "4fc35f5774d21cbe34804996dd5866b995fdf9e3"
RELEASE_TAG = "v0.3.0"
RELEASE_TARGET = "4aa8b8bf25685f9cd6691669ea791a38ecc1a84a"
RELEASE_URL = "https://github.com/docushell/ethos/releases/tag/v0.3.0"
PRIVATE_PATH_MARKERS = (
    "/" + "Users/",
    "/" + "private/tmp",
    "/" + "private/var",
    "/" + "var/folders",
    "saumil" + "diwaker",
    "Desktop/" + "Stuff",
    "project/repo/" + "ethos",
)
FORBIDDEN = (
    "docushell integration approved",
    "hosted surfaces approved",
    "production-ready",
    "windows packaged artifacts approved",
    "bundled pdfium approved",
    "ethos-doc approved",
    "ethos-rag approved",
    "public benchmark claims approved",
    "additional release tag approved",
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


def remote_release_tag_refs() -> dict[str, str]:
    output = git("ls-remote", "--tags", "origin", f"refs/tags/{RELEASE_TAG}*")
    refs: dict[str, str] = {}
    for line in output.splitlines():
        sha, ref = line.split("\t", 1)
        refs[ref] = sha
    return refs


class V030ReleaseTagCloseoutTests(unittest.TestCase):
    def test_record_is_source_bound_and_indexed(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)
        readme = normalized(VALIDATION_README)

        assert_record_source_binding(
            self,
            root=ROOT,
            raw_record=raw,
            normalized_record=record,
            validated_head=SOURCE_SHORT,
            source_label="v0.3.0 release tag closeout",
            source_commit=SOURCE_COMMIT,
            source_tree=SOURCE_TREE,
        )
        self.assertIn(RECORD.name, readme)
        self.assertIn("v0.3.0 release tag closeout", readme.lower())

    def test_closeout_records_existing_remote_release_tag(self) -> None:
        record = normalized(RECORD)
        refs = remote_release_tag_refs()

        for expected in (
            ARTIFACT_CLOSEOUT.name,
            PACKAGE_TAG_CLOSEOUT.name,
            f"GitHub Release tag: `{RELEASE_TAG}`",
            f"GitHub Release URL: `{RELEASE_URL}`",
            f"Remote tag target: `{RELEASE_TARGET}`",
            "Tag type observed on origin: `lightweight`",
            "This closeout did not create, move, delete, or replace `v0.3.0`.",
            "Release tag closeout is complete for existing GitHub Release tag `v0.3.0`.",
        ):
            self.assertIn(expected, record)

        self.assertEqual(RELEASE_TARGET, refs[f"refs/tags/{RELEASE_TAG}"])
        self.assertNotIn(f"refs/tags/{RELEASE_TAG}^{{}}", refs)

    def test_current_status_docs_reference_closeout_without_widening_scope(self) -> None:
        for path in (EXECUTION_STATUS, PUBLIC_RELEASE_CHECKLIST, RELEASE_PREP):
            text = normalized(path)
            self.assertIn(RECORD.name, text, str(path))
            self.assertIn("v0.3.0 release tag closeout", text.lower(), str(path))
            self.assertIn(
                "Release tag closeout is complete for existing GitHub Release tag `v0.3.0`.",
                text,
                str(path),
            )
            self.assertIn("Additional release tags or release targets remain blocked.", text, str(path))
            self.assertIn("DocuShell integration remain blocked", text, str(path))

        changelog = normalized(CHANGELOG)
        self.assertIn("close existing v0.3.0 GitHub Release tag evidence", changelog)
        self.assertIn("additional release tags or release targets", changelog)

    def test_closeout_keeps_unrelated_surfaces_blocked(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)
        lower = record.lower()

        for expected in (
            "Additional release tags or release targets remain blocked.",
            "DocuShell integration remains blocked.",
            "Hosted surfaces remain blocked.",
            "Production positioning remains blocked.",
            "Windows packaged artifacts remain blocked.",
            "Bundled project-maintained PDFium builds remain blocked.",
            "`ethos-doc` remains blocked.",
            "`ethos-rag` remains blocked.",
            "Public benchmark claims remain blocked.",
            "PDFium remains caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`.",
        ):
            self.assertIn(expected, record)
        for forbidden in FORBIDDEN:
            self.assertNotIn(forbidden, lower)
        for marker in PRIVATE_PATH_MARKERS:
            self.assertNotIn(marker, raw)

    def test_release_prep_runs_closeout_after_package_tags_before_public_surface(self) -> None:
        makefile = read(MAKEFILE)
        block = target_block("v0-3-release-prep")
        package_closeout_guard = "$(PYTHON) .github/scripts/test_v0_3_0_package_tag_closeout.py"
        release_tag_closeout_guard = "$(PYTHON) .github/scripts/test_v0_3_0_release_tag_closeout.py"
        public_surface_guard = "$(PYTHON) .github/scripts/test_public_surface_posture.py"

        self.assertIn(release_tag_closeout_guard, block)
        self.assertEqual(1, makefile.count(release_tag_closeout_guard))
        self.assertLess(block.index(package_closeout_guard), block.index(release_tag_closeout_guard))
        self.assertLess(block.index(release_tag_closeout_guard), block.index(public_surface_guard))


if __name__ == "__main__":
    unittest.main()
