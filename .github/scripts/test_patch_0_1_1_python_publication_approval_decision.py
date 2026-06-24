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


ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "docs/validation/patch-0-1-1-python-publication-approval-decision-validation-2026-06-24.md"
REQUEST = ROOT / "docs/validation/patch-0-1-1-python-publication-approval-request-validation-2026-06-24.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
MAKEFILE = ROOT / "Makefile"

SOURCE_SHORT = "d3c7db2"
SOURCE_COMMIT = "d3c7db24c8fac6cd9da627df76bde6df54dd46f9"
SOURCE_TREE = "90253df1cb04ef7c587138b3439bb1825d13a395"
PACKAGE_SOURCE_COMMIT = "16b2c189e1f23962dced921551cf6b4f9af4ba06"
PACKAGE_SOURCE_TREE = "c76ba8525faaa63c53ac7f037d349a8ab4803fcb"
PACKAGE = "ethos-pdf==0.1.1"
WHEEL = "ethos_pdf-0.1.1-py3-none-any.whl"
WHEEL_SHA256 = "faa6c4751341b603b986ad3cf65d3c0c2f574e5df1d7232f76c3afd0221dac14"
FORBIDDEN = (
    "python package is published",
    "wheel is published",
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


class Patch011PythonPublicationApprovalDecisionTests(unittest.TestCase):
    def test_decision_record_is_source_bound_and_indexed(self) -> None:
        record = normalized(RECORD)
        readme = normalized(VALIDATION_README)

        self.assertIn(RECORD.name, readme)
        self.assertIn("patch 0.1.1 Python PyPI publication approval decision", readme)
        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Patch 0.1.1 Python publication approval decision source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Patch 0.1.1 Python publication approval decision source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_decision_accepts_exact_request_packet(self) -> None:
        record = normalized(RECORD)

        self.assertIn(REQUEST.name, record)
        self.assertIn("Decision: accept exact patch `0.1.1` Python PyPI wheel publication decision packet.", record)
        self.assertIn(f"Package source commit accepted by this decision: `{PACKAGE_SOURCE_COMMIT}`", record)
        self.assertIn(f"Package source tree accepted by this decision: `{PACKAGE_SOURCE_TREE}`", record)
        for expected in (
            PACKAGE,
            WHEEL,
            WHEEL_SHA256,
            "Name: `ethos-pdf`",
            "Version: `0.1.1`",
            "License-Expression: `Apache-2.0`",
            "Requires-Python: `>=3.8`",
            "Tag: `py3-none-any`",
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
            "The operator must use a PyPI-approved authentication path and must not record credentials in the repository.",
            "The operator must stop if the built wheel filename, SHA256, package version, source commit, source tree, or retained blockers differ.",
            "Public installation wording remains blocked until PyPI availability is closed out.",
            "`ethos-doc` remains blocked.",
            "`ethos-rag` remains blocked.",
        ):
            self.assertIn(expected, record)
        for forbidden in FORBIDDEN:
            self.assertNotIn(forbidden, lower)
        self.assertNotIn("/Users/", raw)
        self.assertNotIn("/tmp", raw)
        self.assertNotIn("/private/tmp", raw)
        self.assertNotIn("/private/var", raw)
        self.assertNotIn("/var/folders", raw)
        self.assertNotIn("saumildiwaker", raw)

    def test_release_candidate_prep_runs_decision_guard_after_request_guard(self) -> None:
        makefile = read(MAKEFILE)
        request_guard = "$(PYTHON) .github/scripts/test_patch_0_1_1_python_publication_approval_request.py"
        decision_guard = "$(PYTHON) .github/scripts/test_patch_0_1_1_python_publication_approval_decision.py"
        npm_guard = "$(PYTHON) .github/scripts/test_npm_binary_package_scaffold.py"

        self.assertIn(decision_guard, makefile)
        self.assertEqual(1, makefile.count(decision_guard))
        self.assertLess(makefile.index(request_guard), makefile.index(decision_guard))
        self.assertLess(makefile.index(decision_guard), makefile.index(npm_guard))


if __name__ == "__main__":
    unittest.main()
