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
RECORD = ROOT / "docs/validation/patch-0-1-1-python-deterministic-wheel-approval-decision-validation-2026-06-24.md"
REQUEST = ROOT / "docs/validation/patch-0-1-1-python-deterministic-wheel-approval-request-validation-2026-06-24.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
MAKEFILE = ROOT / "Makefile"

SOURCE_SHORT = "0c8ffe7"
SOURCE_COMMIT = "0c8ffe7db3b83896ab0be1c106bd1ec7de3cb278"
SOURCE_TREE = "44376507f98789401efae7b9cf0ab97ca3b78980"
PACKAGE_SOURCE_COMMIT = "d3e3953b99fbc74669f82ee56b753de7db6e63e4"
PACKAGE_SOURCE_TREE = "8920cbc9bc6ae05ec0c417533513637eda12658d"
PACKAGE = "ethos-pdf==0.1.1"
WHEEL = "ethos_pdf-0.1.1-py3-none-any.whl"
DETERMINISTIC_SHA256 = "e0292276e711e75d4f7e1bb8c2c6137c6e89d4c343dd308943eb9b22094ea451"
PRIOR_APPROVED_SHA256 = "faa6c4751341b603b986ad3cf65d3c0c2f574e5df1d7232f76c3afd0221dac14"
FRESH_STANDARD_SHA256 = "52cc738637a84aa084b776db8be866e7af7438d580f3d564801a2ce94492a950"
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


class Patch011PythonDeterministicWheelApprovalDecisionTests(unittest.TestCase):
    def test_decision_record_is_source_bound_and_indexed(self) -> None:
        record = normalized(RECORD)
        readme = normalized(VALIDATION_README)

        self.assertIn(RECORD.name, readme)
        self.assertIn("patch 0.1.1 Python deterministic wheel approval decision", readme)
        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Patch 0.1.1 Python deterministic wheel approval decision source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Patch 0.1.1 Python deterministic wheel approval decision source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_decision_accepts_exact_deterministic_request_packet(self) -> None:
        record = normalized(RECORD)

        self.assertIn(REQUEST.name, record)
        self.assertIn("Decision: accept exact patch `0.1.1` deterministic Python PyPI wheel publication decision packet.", record)
        self.assertIn(f"Deterministic package source commit accepted by this decision: `{PACKAGE_SOURCE_COMMIT}`", record)
        self.assertIn(f"Deterministic package source tree accepted by this decision: `{PACKAGE_SOURCE_TREE}`", record)
        for expected in (
            PACKAGE,
            WHEEL,
            DETERMINISTIC_SHA256,
            PRIOR_APPROVED_SHA256,
            FRESH_STANDARD_SHA256,
            "SOURCE_DATE_EPOCH=0",
            "Name: `ethos-pdf`",
            "Version: `0.1.1`",
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
            "After this decision record is merged and validation passes on merged source, an operator may upload only this deterministic wheel:",
            "The operator must set `SOURCE_DATE_EPOCH=0` before building the wheel for upload.",
            "The operator must use a PyPI-approved authentication path and must not record credentials in the repository.",
            "The operator must stop if the built wheel filename, SHA256, package version, source commit, source tree, deterministic build input, or retained blockers differ.",
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
        request_guard = "$(PYTHON) .github/scripts/test_patch_0_1_1_python_deterministic_wheel_approval_request.py"
        decision_guard = "$(PYTHON) .github/scripts/test_patch_0_1_1_python_deterministic_wheel_approval_decision.py"
        npm_guard = "$(PYTHON) .github/scripts/test_npm_binary_package_scaffold.py"
        block = target_block("release-candidate-prep")

        self.assertIn(decision_guard, block)
        self.assertEqual(1, makefile.count(decision_guard))
        self.assertLess(block.index(request_guard), block.index(decision_guard))
        self.assertLess(block.index(decision_guard), block.index(npm_guard))


if __name__ == "__main__":
    unittest.main()
