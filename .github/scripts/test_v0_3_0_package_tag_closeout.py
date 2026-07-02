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
RECORD = ROOT / "docs/validation/v0-3-0-package-tag-closeout-validation-2026-07-02.md"
DECISION = ROOT / "docs/validation/v0-3-0-package-tag-approval-decision-validation-2026-07-02.md"
REQUEST = ROOT / "docs/validation/v0-3-0-package-tag-approval-request-validation-2026-07-02.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"
RELEASE_PREP = ROOT / "docs/v0-3-0-release-prep.md"
CHANGELOG = ROOT / "CHANGELOG.md"
MAKEFILE = ROOT / "Makefile"

SOURCE_SHORT = "068d843"
SOURCE_COMMIT = "068d843e28ff1ce4e45182665245e08e222d8f17"
SOURCE_TREE = "7e50368c8d59756b467a4e257b23ecf64cab2eca"
PACKAGE_SOURCE_COMMIT = "39cb548cf6cfe20fbcb47ee605ba51f1ebf71f6b"
PACKAGE_SOURCE_TREE = "35076461b03ce8476cd8d73077c6f0bcaeae7dc3"
TAG_OBJECTS = {
    "ethos-package-ethos-doc-core-0.3.0": "c772f2ca0c57e854121a1b3ae21a4ab7e5b1b356",
    "ethos-package-ethos-verify-0.3.0": "a9cf6df0a7a7e0e263c725971cc98bfa77bcc5ef",
    "ethos-package-ethos-pdf-0.3.0": "6489829d5f7d54a62fed8356c7e1c862be06df3f",
}
TAG_OBJECT_PREFIXES = {
    "ethos-package-ethos-doc-core-0.3.0": "c772-f2ca-0c57",
    "ethos-package-ethos-verify-0.3.0": "a9cf-6df0-a7a7",
    "ethos-package-ethos-pdf-0.3.0": "6489-829d-5f7d",
}
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
    output = git("ls-remote", "--tags", "origin", "refs/tags/ethos-package-*-0.3.0*")
    refs: dict[str, str] = {}
    for line in output.splitlines():
        sha, ref = line.split("\t", 1)
        refs[ref] = sha
    return refs


class V030PackageTagCloseoutTests(unittest.TestCase):
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
            source_label="v0.3.0 package tag closeout",
            source_commit=SOURCE_COMMIT,
            source_tree=SOURCE_TREE,
        )
        self.assertIn(RECORD.name, readme)
        self.assertIn("v0.3.0 package tag closeout", readme.lower())

    def test_closeout_records_exact_local_and_remote_tag_bindings(self) -> None:
        record = normalized(RECORD)
        refs = remote_tag_refs()

        self.assertIn(DECISION.name, record)
        self.assertIn(REQUEST.name, record)
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
            "Package tag creation closeout is complete for the three v0.3.0 package tags.",
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

    def test_status_docs_reference_closeout(self) -> None:
        for path in (EXECUTION_STATUS, PUBLIC_RELEASE_CHECKLIST, RELEASE_PREP):
            text = normalized(path)
            self.assertIn(RECORD.name, text, str(path))
            self.assertIn("v0.3.0 package tag closeout", text.lower(), str(path))
            self.assertIn("package tag creation closeout is complete", text.lower(), str(path))
            self.assertIn("DocuShell integration remain blocked", text, str(path))
            self.assertIn("hosted", text.lower(), str(path))
            self.assertIn("production", text.lower(), str(path))

        changelog = normalized(CHANGELOG)
        self.assertIn("close exact v0.3.0 package tag creation", changelog)
        self.assertIn("DocuShell integration blocked", changelog)

    def test_release_prep_runs_closeout_after_decision_before_public_surface(self) -> None:
        makefile = read(MAKEFILE)
        block = target_block("v0-3-release-prep")
        decision_guard = "$(PYTHON) .github/scripts/test_v0_3_0_package_tag_approval_decision.py"
        closeout_guard = "$(PYTHON) .github/scripts/test_v0_3_0_package_tag_closeout.py"
        public_surface_guard = "$(PYTHON) .github/scripts/test_public_surface_posture.py"

        self.assertIn(closeout_guard, block)
        self.assertEqual(1, makefile.count(closeout_guard))
        self.assertLess(block.index(decision_guard), block.index(closeout_guard))
        self.assertLess(block.index(closeout_guard), block.index(public_surface_guard))


if __name__ == "__main__":
    unittest.main()
