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
RECORD = ROOT / "docs/validation/v0-3-0-package-tag-approval-decision-validation-2026-07-02.md"
REQUEST = ROOT / "docs/validation/v0-3-0-package-tag-approval-request-validation-2026-07-02.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"
RELEASE_PREP = ROOT / "docs/v0-3-0-release-prep.md"
CHANGELOG = ROOT / "CHANGELOG.md"
MAKEFILE = ROOT / "Makefile"

SOURCE_SHORT = "81dfe10"
SOURCE_COMMIT = "81dfe102b0b21ec62e9952d844b4cfc2e177cdc4"
SOURCE_TREE = "4e3dd1f119cc274d6c31b59bfac49415cc0ec857"
PACKAGE_TAG_SOURCE_COMMIT = "39cb548cf6cfe20fbcb47ee605ba51f1ebf71f6b"
PACKAGE_TAG_SOURCE_TREE = "35076461b03ce8476cd8d73077c6f0bcaeae7dc3"
APPROVAL_TEXT = (
    "Approve exact v0.3.0 package tag creation request for "
    "ethos-package-ethos-doc-core-0.3.0, ethos-package-ethos-verify-0.3.0, and "
    "ethos-package-ethos-pdf-0.3.0, bound to package tag source commit "
    "39cb548cf6cfe20fbcb47ee605ba51f1ebf71f6b and source tree "
    "35076461b03ce8476cd8d73077c6f0bcaeae7dc3. Keep DocuShell integration, hosted "
    "surfaces, production positioning, Windows packaged artifacts, bundled "
    "project-maintained PDFium builds, public benchmark claims, ethos-doc, and ethos-rag blocked."
)
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
    "package tags are created by this record",
    "tags are pushed by this record",
    "release tag creation approved",
    "docushell integration approved",
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


class V030PackageTagApprovalDecisionTests(unittest.TestCase):
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
            source_label="v0.3.0 package tag approval decision",
            source_commit=SOURCE_COMMIT,
            source_tree=SOURCE_TREE,
        )
        self.assertIn(RECORD.name, readme)
        self.assertIn("v0.3.0 package tag approval decision", readme.lower())

    def test_decision_accepts_exact_request_packet(self) -> None:
        record = normalized(RECORD)

        self.assertIn(REQUEST.name, record)
        self.assertIn("Decision: accept exact v0.3.0 package tag creation decision packet.", record)
        self.assertIn(f"Decider approval supplied: {APPROVAL_TEXT}", record)
        self.assertIn(f"Package tag source commit accepted by this decision: `{PACKAGE_TAG_SOURCE_COMMIT}`", record)
        self.assertIn(f"Package tag source tree accepted by this decision: `{PACKAGE_TAG_SOURCE_TREE}`", record)
        self.assertEqual(PACKAGE_TAG_SOURCE_TREE, git("rev-parse", f"{PACKAGE_TAG_SOURCE_COMMIT}^{{tree}}"))
        for tag in TAGS:
            self.assertIn(tag, record)
        for command in (*TAG_COMMANDS, *PUSH_COMMANDS):
            self.assertIn(command, record)

    def test_decision_authorizes_only_later_operator_tag_creation(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)
        lower = record.lower()

        for expected in (
            "This decision record does not create package tags.",
            "This decision record does not push package tags.",
            "This decision record does not create or move GitHub Release tag `v0.3.0`.",
            "Package tag creation remains a separate operator action after this decision is merged and validation passes on merged source.",
            "After this decision record is merged and validation passes on merged source, an operator may run only these tag commands:",
            "The operator must use annotated tags.",
            "The operator must stop if any requested tag already exists locally or on `origin`,",
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

    def test_status_docs_reference_decision_and_keep_operator_action_pending(self) -> None:
        for path in (EXECUTION_STATUS, PUBLIC_RELEASE_CHECKLIST, RELEASE_PREP):
            text = normalized(path)
            self.assertIn(RECORD.name, text, str(path))
            self.assertIn("v0.3.0 package tag approval decision", text.lower(), str(path))
            self.assertIn("Package tag creation remains a separate operator action", text, str(path))
            self.assertIn("DocuShell integration remain blocked", text, str(path))
            self.assertIn("hosted", text.lower(), str(path))
            self.assertIn("production", text.lower(), str(path))

        changelog = normalized(CHANGELOG)
        self.assertIn("approve exact v0.3.0 package tag creation", changelog)
        self.assertIn("operator tag creation", changelog)

    def test_release_prep_runs_decision_after_request_before_public_surface(self) -> None:
        makefile = read(MAKEFILE)
        block = target_block("v0-3-release-prep")
        request_guard = "$(PYTHON) .github/scripts/test_v0_3_0_package_tag_approval_request.py"
        decision_guard = "$(PYTHON) .github/scripts/test_v0_3_0_package_tag_approval_decision.py"
        public_surface_guard = "$(PYTHON) .github/scripts/test_public_surface_posture.py"

        self.assertIn(request_guard, block)
        self.assertIn(decision_guard, block)
        self.assertEqual(1, makefile.count(decision_guard))
        self.assertLess(block.index(request_guard), block.index(decision_guard))
        self.assertLess(block.index(decision_guard), block.index(public_surface_guard))


if __name__ == "__main__":
    unittest.main()
