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
RECORD = ROOT / "docs/validation/patch-0-1-1-python-deterministic-wheel-approval-request-validation-2026-06-24.md"
BLOCKER = ROOT / "docs/validation/patch-0-1-1-python-wheel-reproducibility-blocker-validation-2026-06-24.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
MAKEFILE = ROOT / "Makefile"

SOURCE_SHORT = "d3e3953"
SOURCE_COMMIT = "d3e3953b99fbc74669f82ee56b753de7db6e63e4"
SOURCE_TREE = "8920cbc9bc6ae05ec0c417533513637eda12658d"
PACKAGE = "ethos-pdf==0.1.1"
WHEEL = "ethos_pdf-0.1.1-py3-none-any.whl"
DETERMINISTIC_SHA256 = "e0292276e711e75d4f7e1bb8c2c6137c6e89d4c343dd308943eb9b22094ea451"
PRIOR_APPROVED_SHA256 = "faa6c4751341b603b986ad3cf65d3c0c2f574e5df1d7232f76c3afd0221dac14"
FRESH_STANDARD_SHA256 = "52cc738637a84aa084b776db8be866e7af7438d580f3d564801a2ce94492a950"
FORBIDDEN = (
    "pypi upload approved",
    "pypi publication approved",
    "python package is published",
    "wheel is published",
    "twine upload approved",
    "production-ready",
    "hosted surfaces approved",
    "windows packaged artifacts approved",
    "bundled pdfium approved",
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


class Patch011PythonDeterministicWheelApprovalRequestTests(unittest.TestCase):
    def test_request_record_is_source_bound_and_indexed(self) -> None:
        record = normalized(RECORD)
        readme = normalized(VALIDATION_README)

        self.assertIn(RECORD.name, readme)
        self.assertIn("patch 0.1.1 Python deterministic wheel approval request", readme)
        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Patch 0.1.1 Python deterministic wheel approval request source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Patch 0.1.1 Python deterministic wheel approval request source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_request_names_exact_deterministic_candidate_and_metadata(self) -> None:
        record = normalized(RECORD)

        for expected in (
            BLOCKER.name,
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
            "version `0.1.1`",
            "EthosCli",
            "EthosCommandError",
        ):
            self.assertIn(expected, record)

    def test_request_requires_decision_and_keeps_upload_blocked(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)
        lower = record.lower()

        for expected in (
            "Manual action is required before any PyPI upload.",
            "A decider must accept or reject this exact deterministic request packet.",
            "This request record does not approve PyPI upload.",
            "This request record does not upload any Python distribution.",
            "This request record does not approve the deterministic wheel hash.",
            "Actual PyPI upload remains blocked pending explicit decider approval.",
            "Public installation wording remains blocked pending PyPI availability closeout.",
            "PDFium remains caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`.",
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

    def test_release_candidate_prep_runs_request_guard_after_blocker_guard(self) -> None:
        makefile = read(MAKEFILE)
        blocker_guard = "$(PYTHON) .github/scripts/test_patch_0_1_1_python_wheel_reproducibility_blocker.py"
        guard = "$(PYTHON) .github/scripts/test_patch_0_1_1_python_deterministic_wheel_approval_request.py"
        npm_guard = "$(PYTHON) .github/scripts/test_npm_binary_package_scaffold.py"
        block = target_block("release-candidate-prep")

        self.assertIn(guard, block)
        self.assertEqual(1, makefile.count(guard))
        self.assertLess(block.index(blocker_guard), block.index(guard))
        self.assertLess(block.index(guard), block.index(npm_guard))


if __name__ == "__main__":
    unittest.main()
