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
RECORD = ROOT / "docs/validation/patch-0-1-2-package-tag-closeout-validation-2026-06-25.md"
DECISION = ROOT / "docs/validation/patch-0-1-2-package-tag-approval-decision-validation-2026-06-25.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"
MAKEFILE = ROOT / "Makefile"

SOURCE_SHORT = "8ab9e18"
SOURCE_COMMIT = "8ab9e180cfb96a1e6659dff97db7fb7a4288817b"
SOURCE_TREE = "1a40205d4d87614e14278ab7d0107fa58bbeeb46"
PACKAGE_SOURCE_COMMIT = "3bc3564e38c1168b2db72f38863d324b6b57bd4d"
PACKAGE_SOURCE_TREE = "eda8c7a605a4eb29c155ae3b9e6e9f0c35798f8c"
TAG_OBJECTS = {
    "ethos-package-ethos-doc-core-0.1.2": "4ced327565020277d7a1eb63b1d471e570b1f4a1",
    "ethos-package-ethos-verify-0.1.2": "57dd49a6b8a6cbb44dbff1fd70f221ee36c50819",
    "ethos-package-ethos-pdf-0.1.2": "024315d5a9735d6d6c68abe6f3aeb2e0f110dfe3",
}
TAG_OBJECT_PREFIXES = {
    "ethos-package-ethos-doc-core-0.1.2": "4ced-3275-6502",
    "ethos-package-ethos-verify-0.1.2": "57dd-49a6-b8a6",
    "ethos-package-ethos-pdf-0.1.2": "0243-15d5-a973",
}
FORBIDDEN = (
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


def remote_tag_refs() -> dict[str, str]:
    output = git("ls-remote", "--tags", "origin", "refs/tags/ethos-package-*-0.1.2*")
    refs: dict[str, str] = {}
    for line in output.splitlines():
        sha, ref = line.split("\t", 1)
        refs[ref] = sha
    return refs


class Patch012PackageTagCloseoutTests(unittest.TestCase):
    def test_record_is_source_bound_and_indexed(self) -> None:
        record = normalized(RECORD)
        readme = normalized(VALIDATION_README)

        self.assertIn(RECORD.name, readme)
        self.assertIn("patch 0.1.2 package tag closeout", readme.lower())
        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Patch 0.1.2 package tag closeout source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Patch 0.1.2 package tag closeout source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_closeout_records_exact_local_and_remote_tag_bindings(self) -> None:
        record = normalized(RECORD)
        refs = remote_tag_refs()

        self.assertIn(DECISION.name, record)
        self.assertIn(f"Package tag source commit: `{PACKAGE_SOURCE_COMMIT}`", record)
        self.assertIn(f"Package tag source tree: `{PACKAGE_SOURCE_TREE}`", record)
        self.assertEqual(PACKAGE_SOURCE_TREE, git("rev-parse", f"{PACKAGE_SOURCE_COMMIT}^{{tree}}"))

        for tag, tag_object in TAG_OBJECTS.items():
            self.assertIn(tag, record)
            self.assertIn(TAG_OBJECT_PREFIXES[tag], record)
            self.assertEqual(tag_object, git("rev-parse", tag))
            self.assertEqual(PACKAGE_SOURCE_COMMIT, git("rev-parse", f"{tag}^{{}}"))
            self.assertEqual(tag_object, refs[f"refs/tags/{tag}"])
            self.assertEqual(PACKAGE_SOURCE_COMMIT, refs[f"refs/tags/{tag}^{{}}"])

    def test_closeout_keeps_unrelated_surfaces_blocked(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)
        lower = record.lower()

        for expected in (
            "Package tag creation closeout is complete for the three patch `0.1.2` package tags.",
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

    def test_status_docs_reference_closeout(self) -> None:
        for path in (EXECUTION_STATUS, PUBLIC_RELEASE_CHECKLIST):
            text = normalized(path)
            self.assertIn(RECORD.name, text, str(path))
            self.assertIn("package tag creation closeout is complete", text.lower(), str(path))
            self.assertIn("hosted", text.lower(), str(path))
            self.assertIn("production", text.lower(), str(path))

    def test_release_candidate_prep_runs_after_decision_before_artifact_checks(self) -> None:
        makefile = read(MAKEFILE)
        decision_guard = "$(PYTHON) .github/scripts/test_patch_0_1_2_package_tag_approval_decision.py"
        closeout_guard = "$(PYTHON) .github/scripts/test_patch_0_1_2_package_tag_closeout.py"
        first_public_guard = "$(PYTHON) .github/scripts/test_first_public_release_artifact_evidence.py"
        block = target_block("release-candidate-prep")

        self.assertIn(closeout_guard, block)
        self.assertEqual(1, makefile.count(closeout_guard))
        self.assertLess(block.index(decision_guard), block.index(closeout_guard))
        self.assertLess(block.index(closeout_guard), block.index(first_public_guard))


if __name__ == "__main__":
    unittest.main()
