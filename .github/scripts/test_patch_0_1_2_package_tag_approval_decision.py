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
RECORD = ROOT / "docs/validation/patch-0-1-2-package-tag-approval-decision-validation-2026-06-25.md"
REQUEST = ROOT / "docs/validation/patch-0-1-2-package-tag-approval-request-validation-2026-06-25.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"
MAKEFILE = ROOT / "Makefile"

SOURCE_SHORT = "070a5c5"
SOURCE_COMMIT = "070a5c54afe780f95fc6fbe4598558107949695c"
SOURCE_TREE = "93e025c44993c18a42203b7b999d9dd5af94e709"
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
PUSH_COMMANDS = tuple(f"git push origin refs/tags/{tag}" for tag in TAGS)
FORBIDDEN = (
    "package tags are created by this record",
    "tags are pushed by this record",
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


class Patch012PackageTagApprovalDecisionTests(unittest.TestCase):
    def test_record_is_source_bound_and_indexed(self) -> None:
        record = normalized(RECORD)
        readme = normalized(VALIDATION_README)

        self.assertIn(RECORD.name, readme)
        self.assertIn("patch 0.1.2 package tag approval decision", readme.lower())
        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Patch 0.1.2 package tag approval decision source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Patch 0.1.2 package tag approval decision source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_decision_accepts_exact_request_packet(self) -> None:
        record = normalized(RECORD)

        self.assertIn(REQUEST.name, record)
        self.assertIn("Decision: accept exact patch `0.1.2` package tag creation decision packet.", record)
        self.assertIn("Decider approval supplied: Yes, I Approve exact patch 0.1.2.", record)
        self.assertIn(f"Package tag source commit accepted by this decision: `{PACKAGE_SOURCE_COMMIT}`", record)
        self.assertIn(f"Package tag source tree accepted by this decision: `{PACKAGE_SOURCE_TREE}`", record)
        self.assertEqual(PACKAGE_SOURCE_TREE, git("rev-parse", f"{PACKAGE_SOURCE_COMMIT}^{{tree}}"))
        for tag in TAGS:
            self.assertIn(tag, record)
        for command in TAG_COMMANDS + PUSH_COMMANDS:
            self.assertIn(command, record)

    def test_decision_authorizes_only_later_operator_tag_creation(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)
        lower = record.lower()

        for expected in (
            "This decision record does not create package tags.",
            "This decision record does not push package tags.",
            "Package tag creation remains a separate operator action after this decision is merged and validation passes on merged source.",
            "After this decision record is merged and validation passes on merged source, an operator may run only these tag commands:",
            "The operator must use annotated tags.",
            "The operator must stop if any requested tag already exists locally or on `origin`,",
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

    def test_status_docs_reference_decision_and_keep_operator_action_pending(self) -> None:
        for path in (EXECUTION_STATUS, PUBLIC_RELEASE_CHECKLIST):
            text = normalized(path)
            self.assertIn(RECORD.name, text, str(path))
            self.assertIn("Package tag creation remains a separate operator action", text, str(path))
            self.assertIn("hosted", text.lower(), str(path))
            self.assertIn("production", text.lower(), str(path))

    def test_release_candidate_prep_runs_after_request_before_artifact_checks(self) -> None:
        makefile = read(MAKEFILE)
        request_guard = "$(PYTHON) .github/scripts/test_patch_0_1_2_package_tag_approval_request.py"
        decision_guard = "$(PYTHON) .github/scripts/test_patch_0_1_2_package_tag_approval_decision.py"
        first_public_guard = "$(PYTHON) .github/scripts/test_first_public_release_artifact_evidence.py"
        block = target_block("release-candidate-prep")

        self.assertIn(decision_guard, block)
        self.assertEqual(1, makefile.count(decision_guard))
        self.assertLess(block.index(request_guard), block.index(decision_guard))
        self.assertLess(block.index(decision_guard), block.index(first_public_guard))


if __name__ == "__main__":
    unittest.main()
