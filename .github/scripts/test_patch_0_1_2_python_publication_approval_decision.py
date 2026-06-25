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
RECORD = ROOT / "docs/validation/patch-0-1-2-python-publication-approval-decision-validation-2026-06-25.md"
REQUEST = ROOT / "docs/validation/patch-0-1-2-python-publication-approval-request-validation-2026-06-25.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
MAKEFILE = ROOT / "Makefile"

SOURCE_SHORT = "a35ff66"
SOURCE_COMMIT = "a35ff66cbb7d04f4df4d7ac478edcd1f11ecbcdc"
SOURCE_TREE = "2deb30a01223fd9afc4291460cfd5578a3c3242c"
PACKAGE_SOURCE_COMMIT = "e431982cca2922d4cc59ddc7cacb9e72538b1cd0"
PACKAGE_SOURCE_TREE = "f59ddd018d234eeee0ac77292b417f4acb892b4e"
PACKAGE = "ethos-pdf==0.1.2"
WHEEL = "ethos_pdf-0.1.2-py3-none-any.whl"
WHEEL_SHA256 = "6f17240954f1257ece3c762c820ad771ccb114353bfb699fe87f418a5ceb663c"
FORBIDDEN = (
    "python package is published",
    "wheel is published",
    "python installation wording approved",
    "package tags approved",
    "production-ready",
    "hosted surfaces approved",
    "windows packaged artifacts approved",
    "bundled pdfium approved",
    "public benchmark claims approved",
    "ethos-doc approved",
    "ethos-rag approved",
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


class Patch012PythonPublicationApprovalDecisionTests(unittest.TestCase):
    def test_decision_record_is_source_bound_and_indexed(self) -> None:
        record = normalized(RECORD)
        readme = normalized(VALIDATION_README)

        self.assertIn(RECORD.name, readme)
        self.assertIn("patch 0.1.2 Python PyPI publication approval decision", readme)
        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Patch 0.1.2 Python publication approval decision source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Patch 0.1.2 Python publication approval decision source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_decision_accepts_exact_deterministic_request_packet(self) -> None:
        record = normalized(RECORD)

        self.assertIn(REQUEST.name, record)
        self.assertIn("Decision: accept exact deterministic patch `0.1.2` Python PyPI wheel publication decision packet.", record)
        self.assertIn(f"Package source commit accepted by this decision: `{PACKAGE_SOURCE_COMMIT}`", record)
        self.assertIn(f"Package source tree accepted by this decision: `{PACKAGE_SOURCE_TREE}`", record)
        for expected in (
            PACKAGE,
            WHEEL,
            WHEEL_SHA256,
            "SOURCE_DATE_EPOCH=0",
            "Name: `ethos-pdf`",
            "Version: `0.1.2`",
            "License-Expression: `Apache-2.0`",
            "Requires-Python: `>=3.8`",
            "Wheel-Version: `1.0`",
            "Root-Is-Purelib: `true`",
            "Tag: `py3-none-any`",
            "member timestamps: `1980-01-01 00:00:00`",
            "EthosCli",
            "EthosCommandError",
            "ETHOS_PDFIUM_LIBRARY_PATH",
        ):
            self.assertIn(expected, record)

    def test_decision_allows_only_later_operator_upload_with_boundaries(self) -> None:
        raw = read(RECORD)
        lower = normalized(RECORD).lower()
        record = normalized(RECORD)

        for expected in (
            "This decision record does not upload any Python distribution.",
            "PyPI upload remains a separate operator action.",
            "After this decision record is merged and validation passes on merged source, an operator may upload only this wheel:",
            "The operator must build with `SOURCE_DATE_EPOCH=0`.",
            "The operator must use a PyPI-approved authentication path and must not record credentials in the repository.",
            "The operator must stop if the built wheel filename, SHA256, package version, source commit, source tree, deterministic build input, or retained blockers differ.",
            "Python public installation wording remains blocked until PyPI availability is closed out.",
            "Package tag creation remains blocked until a separate explicit approval or closeout record permits it.",
            "`ethos-doc` remains blocked.",
            "`ethos-rag` remains blocked.",
        ):
            self.assertIn(expected, record)
        for forbidden in FORBIDDEN:
            self.assertNotIn(forbidden, lower)
        for private in (
            "/" + "Users/",
            "/" + "tmp",
            "/" + "private/tmp",
            "/" + "private/var",
            "/" + "var/folders",
            "saumil" + "diwaker",
            "Desktop/" + "Stuff",
            "project/repo/" + "ethos",
        ):
            self.assertNotIn(private, raw)

    def test_release_candidate_prep_runs_decision_guard_after_request_guard(self) -> None:
        makefile = read(MAKEFILE)
        request_guard = "$(PYTHON) .github/scripts/test_patch_0_1_2_python_publication_approval_request.py"
        decision_guard = "$(PYTHON) .github/scripts/test_patch_0_1_2_python_publication_approval_decision.py"
        first_public_guard = "$(PYTHON) .github/scripts/test_first_public_release_artifact_evidence.py"
        block = target_block("release-candidate-prep")

        self.assertIn(decision_guard, block)
        self.assertEqual(1, makefile.count(decision_guard))
        self.assertLess(block.index(request_guard), block.index(decision_guard))
        self.assertLess(block.index(decision_guard), block.index(first_public_guard))


if __name__ == "__main__":
    unittest.main()
