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


ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "docs/validation/patch-0-1-2-package-tag-approval-request-validation-2026-06-25.md"
CRATES_REQUEST = (
    ROOT
    / "docs/validation/patch-0-1-2-crates-publication-approval-request-validation-2026-06-25.md"
)
CRATES_DECISION = (
    ROOT
    / "docs/validation/patch-0-1-2-crates-publication-approval-decision-validation-2026-06-25.md"
)
CRATES_CLOSEOUT = (
    ROOT / "docs/validation/patch-0-1-2-crates-publication-closeout-validation-2026-06-25.md"
)
VALIDATION_README = ROOT / "docs/validation/README.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"
MAKEFILE = ROOT / "Makefile"

SOURCE_SHORT = "bc14f36"
SOURCE_COMMIT = "bc14f36931ae7453c35fc4ecd1a2a9159f2127d4"
SOURCE_TREE = "2b597508e020e8c1090508d5a60fa66af4aa7951"
PACKAGE_SOURCE_COMMIT = "3bc3564e38c1168b2db72f38863d324b6b57bd4d"
PACKAGE_SOURCE_TREE = "eda8c7a605a4eb29c155ae3b9e6e9f0c35798f8c"
TAGS = (
    "ethos-package-ethos-doc-core-0.1.2",
    "ethos-package-ethos-verify-0.1.2",
    "ethos-package-ethos-pdf-0.1.2",
)
TAG_COMMANDS = (
    f"git tag -a {TAGS[0]} {PACKAGE_SOURCE_COMMIT}",
    f"git tag -a {TAGS[1]} {PACKAGE_SOURCE_COMMIT}",
    f"git tag -a {TAGS[2]} {PACKAGE_SOURCE_COMMIT}",
)
FORBIDDEN = (
    "package tags are created",
    "tag creation approved",
    "hosted surfaces approved",
    "production-ready",
    "windows packaged artifacts approved",
    "bundled pdfium approved",
    "ethos-doc approved",
    "ethos-rag approved",
    "public benchmark claims approved",
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


class Patch012PackageTagApprovalRequestTests(unittest.TestCase):
    def test_record_is_source_bound_and_indexed(self) -> None:
        record = normalized(RECORD)
        readme = normalized(VALIDATION_README)

        self.assertIn(RECORD.name, readme)
        self.assertIn("patch 0.1.2 package tag approval request", readme.lower())
        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Patch 0.1.2 package tag approval request source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Patch 0.1.2 package tag approval request source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_request_binds_exact_published_package_tag_set(self) -> None:
        record = normalized(RECORD)

        self.assertIn(CRATES_REQUEST.name, record)
        self.assertIn(CRATES_DECISION.name, record)
        self.assertIn(CRATES_CLOSEOUT.name, record)
        self.assertIn(f"Package tag source commit requested: `{PACKAGE_SOURCE_COMMIT}`", record)
        self.assertIn(f"Package tag source tree requested: `{PACKAGE_SOURCE_TREE}`", record)
        self.assertEqual(PACKAGE_SOURCE_TREE, git("rev-parse", f"{PACKAGE_SOURCE_COMMIT}^{{tree}}"))
        for tag in TAGS:
            self.assertIn(tag, record)
        for command in TAG_COMMANDS:
            self.assertIn(command, record)

    def test_request_remains_non_executing_and_retains_boundaries(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)
        lower = record.lower()

        for expected in (
            "This request record does not create package tags.",
            "This request record does not approve package tag creation.",
            "Tag creation remains blocked until a separate explicit approval decision is recorded.",
            "Public beta evaluation surfaces remain unchanged.",
            "Hosted surfaces remain blocked.",
            "Production positioning remains blocked.",
            "Windows packaged artifacts remain blocked.",
            "Bundled project-maintained PDFium builds remain blocked.",
            "`ethos-doc` remains blocked.",
            "`ethos-rag` remains blocked.",
            "Public benchmark claims remain blocked.",
        ):
            self.assertIn(expected, record)
        for forbidden in FORBIDDEN:
            self.assertNotIn(forbidden, lower)
        self.assertNotIn("/Users/", raw)
        self.assertNotIn("/private/tmp", raw)
        self.assertNotIn("/private/var", raw)
        self.assertNotIn("/var/folders", raw)
        self.assertNotIn("saumildiwaker", raw)

    def test_status_docs_reference_request_and_keep_tag_creation_blocked(self) -> None:
        for path in (EXECUTION_STATUS, PUBLIC_RELEASE_CHECKLIST):
            text = normalized(path)
            self.assertIn(RECORD.name, text, str(path))
            self.assertIn("Package tag creation remains blocked", text, str(path))
            self.assertIn("hosted", text.lower(), str(path))
            self.assertIn("production", text.lower(), str(path))

    def test_release_candidate_prep_runs_after_python_wording_before_artifact_checks(self) -> None:
        makefile = read(MAKEFILE)
        python_wording_guard = "$(PYTHON) .github/scripts/test_patch_0_1_2_python_public_install_wording_closeout.py"
        tag_request_guard = "$(PYTHON) .github/scripts/test_patch_0_1_2_package_tag_approval_request.py"
        first_public_guard = "$(PYTHON) .github/scripts/test_first_public_release_artifact_evidence.py"
        block = target_block("release-candidate-prep")

        self.assertIn(tag_request_guard, block)
        self.assertEqual(1, makefile.count(tag_request_guard))
        self.assertLess(block.index(python_wording_guard), block.index(tag_request_guard))
        self.assertLess(block.index(tag_request_guard), block.index(first_public_guard))


if __name__ == "__main__":
    unittest.main()
