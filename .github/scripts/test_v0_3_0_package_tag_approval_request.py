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
RECORD = ROOT / "docs/validation/v0-3-0-package-tag-approval-request-validation-2026-07-02.md"
PACKAGE_REQUEST = ROOT / (
    "docs/validation/v0-3-0-package-publication-approval-request-validation-2026-07-01.md"
)
PACKAGE_DECISION = ROOT / (
    "docs/validation/v0-3-0-publication-approval-decision-validation-2026-07-01.md"
)
PACKAGE_CLOSEOUT = ROOT / "docs/validation/v0-3-0-publication-closeout-validation-2026-07-01.md"
ARTIFACT_CLOSEOUT = ROOT / (
    "docs/validation/v0-3-0-artifact-publication-closeout-validation-2026-07-02.md"
)
NPM_CLOSEOUT = ROOT / (
    "docs/validation/v0-3-0-npm-publication-closeout-validation-2026-07-02.md"
)
PUBLIC_INSTALL_CLOSEOUT = ROOT / (
    "docs/validation/v0-3-0-public-install-wording-closeout-validation-2026-07-02.md"
)
VALIDATION_README = ROOT / "docs/validation/README.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"
RELEASE_PREP = ROOT / "docs/v0-3-0-release-prep.md"
CHANGELOG = ROOT / "CHANGELOG.md"
MAKEFILE = ROOT / "Makefile"

SOURCE_SHORT = "77e452b"
SOURCE_COMMIT = "77e452b447c93fd93b3deac72a325cbb2441fa87"
SOURCE_TREE = "76bd5c69c16aee50b7eb7b8736156876598161a2"
PACKAGE_TAG_SOURCE_COMMIT = "39cb548cf6cfe20fbcb47ee605ba51f1ebf71f6b"
PACKAGE_TAG_SOURCE_TREE = "35076461b03ce8476cd8d73077c6f0bcaeae7dc3"
TAGS = (
    "ethos-package-ethos-doc-core-0.3.0",
    "ethos-package-ethos-verify-0.3.0",
    "ethos-package-ethos-pdf-0.3.0",
)
TAG_COMMANDS = tuple(f"git tag -a {tag} {PACKAGE_TAG_SOURCE_COMMIT}" for tag in TAGS)
PUSH_COMMANDS = tuple(f"git push origin refs/tags/{tag}" for tag in TAGS)
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
    "package tags are created",
    "package tag creation approved",
    "release tag creation approved",
    "hosted surfaces approved",
    "production-ready",
    "windows packaged artifacts approved",
    "bundled pdfium approved",
    "docushell integration approved",
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


class V030PackageTagApprovalRequestTests(unittest.TestCase):
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
            source_label="v0.3.0 package tag approval request",
            source_commit=SOURCE_COMMIT,
            source_tree=SOURCE_TREE,
        )
        self.assertIn(RECORD.name, readme)
        self.assertIn("v0.3.0 package tag approval request", readme.lower())

    def test_request_binds_exact_package_tag_set_and_source(self) -> None:
        record = normalized(RECORD)

        for expected_record in (
            PACKAGE_REQUEST.name,
            PACKAGE_DECISION.name,
            PACKAGE_CLOSEOUT.name,
            ARTIFACT_CLOSEOUT.name,
            NPM_CLOSEOUT.name,
            PUBLIC_INSTALL_CLOSEOUT.name,
        ):
            self.assertIn(expected_record, record)
        self.assertIn(f"Package tag source commit requested: `{PACKAGE_TAG_SOURCE_COMMIT}`", record)
        self.assertIn(f"Package tag source tree requested: `{PACKAGE_TAG_SOURCE_TREE}`", record)
        self.assertEqual(PACKAGE_TAG_SOURCE_TREE, git("rev-parse", f"{PACKAGE_TAG_SOURCE_COMMIT}^{{tree}}"))
        for tag in TAGS:
            self.assertIn(tag, record)
        for command in (*TAG_COMMANDS, *PUSH_COMMANDS):
            self.assertIn(command, record)

    def test_request_is_non_executing_and_keeps_boundaries(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)
        lower = record.lower()

        for expected in (
            "This request record does not create package tags.",
            "This request record does not approve package tag creation.",
            "This request record does not create a release tag.",
            "This request record does not move or replace GitHub Release tag `v0.3.0`.",
            "No additional release tag or GitHub Release target is approved by this package-tag request.",
            "Package tag creation remains blocked until a separate explicit approval decision is recorded.",
            "DocuShell integration remains blocked.",
            "Hosted surfaces remain blocked.",
            "Production positioning remains blocked.",
            "Windows packaged artifacts remain blocked.",
            "Bundled project-maintained PDFium builds remain blocked.",
            "Public benchmark claims remain blocked.",
            "`ethos-doc` remains blocked.",
            "`ethos-rag` remains blocked.",
            "PDFium remains caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`.",
        ):
            self.assertIn(expected, record)
        for phrase in FORBIDDEN:
            self.assertNotIn(phrase, lower)
        for marker in PRIVATE_PATH_MARKERS:
            self.assertNotIn(marker, raw)

    def test_status_docs_reference_request_and_keep_creation_blocked(self) -> None:
        for path in (EXECUTION_STATUS, PUBLIC_RELEASE_CHECKLIST, RELEASE_PREP):
            text = normalized(path)
            self.assertIn(RECORD.name, text, str(path))
            self.assertIn("v0.3.0 package tag approval request", text.lower(), str(path))
            self.assertIn("Package tag creation remains blocked", text, str(path))
            self.assertIn("DocuShell integration remain blocked", text, str(path))
            self.assertIn("hosted", text.lower(), str(path))
            self.assertIn("production", text.lower(), str(path))

        changelog = normalized(CHANGELOG)
        self.assertIn("request decider review for exact v0.3.0 package tags", changelog)
        self.assertIn("blocked", changelog.lower())

    def test_release_prep_runs_package_tag_request_after_install_wording_closeout(self) -> None:
        makefile = read(MAKEFILE)
        block = target_block("v0-3-release-prep")
        closeout_guard = "$(PYTHON) .github/scripts/test_v0_3_0_public_install_wording_closeout.py"
        tag_request_guard = "$(PYTHON) .github/scripts/test_v0_3_0_package_tag_approval_request.py"
        public_surface_guard = "$(PYTHON) .github/scripts/test_public_surface_posture.py"

        self.assertIn(closeout_guard, block)
        self.assertIn(tag_request_guard, block)
        self.assertEqual(1, makefile.count(tag_request_guard))
        self.assertLess(block.index(closeout_guard), block.index(tag_request_guard))
        self.assertLess(block.index(tag_request_guard), block.index(public_surface_guard))


if __name__ == "__main__":
    unittest.main()
