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
RECORD = ROOT / "docs/validation/patch-0-1-1-python-wheel-reproducibility-blocker-validation-2026-06-24.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
MAKEFILE = ROOT / "Makefile"

SOURCE_SHORT = "5be31dd"
SOURCE_COMMIT = "5be31dd292a0551caea457fd23db98045e110c00"
SOURCE_TREE = "590dc80d27beaa9950a21f7f188650d2f24dd036"
APPROVED_SHA256 = "faa6c4751341b603b986ad3cf65d3c0c2f574e5df1d7232f76c3afd0221dac14"
FRESH_SHA256 = "52cc738637a84aa084b776db8be866e7af7438d580f3d564801a2ce94492a950"
TIMESTAMP_PIN_SHA256 = "ab84782cd7b7e7db2628f36e5d34e636afcddb9798196305203380a49b36b964"
DETERMINISTIC_SHA256 = "e0292276e711e75d4f7e1bb8c2c6137c6e89d4c343dd308943eb9b22094ea451"
FORBIDDEN = (
    "pypi upload may proceed",
    "pypi upload approved",
    "wheel is published",
    "python package is published",
    "production-ready",
    "hosted surfaces approved",
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


class Patch011PythonWheelReproducibilityBlockerTests(unittest.TestCase):
    def test_blocker_record_is_source_bound_and_indexed(self) -> None:
        record = normalized(RECORD)
        readme = normalized(VALIDATION_README)

        self.assertIn(RECORD.name, readme)
        self.assertIn("patch 0.1.1 Python wheel reproducibility blocker", readme)
        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Patch 0.1.1 Python wheel reproducibility blocker source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Patch 0.1.1 Python wheel reproducibility blocker source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_blocker_records_hash_mismatch_and_root_cause(self) -> None:
        record = normalized(RECORD)

        for expected in (
            "ethos_pdf-0.1.1-py3-none-any.whl",
            APPROVED_SHA256,
            FRESH_SHA256,
            TIMESTAMP_PIN_SHA256,
            DETERMINISTIC_SHA256,
            "wheel member byte content was identical",
            "generated `dist-info` ZIP member timestamps differed",
            "Setting `SOURCE_DATE_EPOCH=0` produced the same wheel SHA256 twice",
        ):
            self.assertIn(expected, record)

    def test_blocker_keeps_upload_blocked_until_new_deterministic_decision(self) -> None:
        raw = read(RECORD)
        lower = normalized(RECORD).lower()
        record = normalized(RECORD)

        for expected in (
            "PyPI upload remains blocked.",
            "The prior merged approval decision remains useful as historical evidence but is not sufficient for upload because the required pre-upload rebuild produced a different wheel SHA256.",
            "A new deterministic wheel approval request and approval decision are required before any PyPI upload.",
            "The next candidate should be built with `SOURCE_DATE_EPOCH=0`",
            "This record does not approve PyPI upload.",
            "This record does not approve the deterministic wheel hash.",
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

    def test_release_candidate_prep_runs_blocker_after_decision_guard(self) -> None:
        makefile = read(MAKEFILE)
        decision_guard = "$(PYTHON) .github/scripts/test_patch_0_1_1_python_publication_approval_decision.py"
        blocker_guard = "$(PYTHON) .github/scripts/test_patch_0_1_1_python_wheel_reproducibility_blocker.py"
        npm_guard = "$(PYTHON) .github/scripts/test_npm_binary_package_scaffold.py"

        self.assertIn(blocker_guard, makefile)
        self.assertEqual(1, makefile.count(blocker_guard))
        self.assertLess(makefile.index(decision_guard), makefile.index(blocker_guard))
        self.assertLess(makefile.index(blocker_guard), makefile.index(npm_guard))


if __name__ == "__main__":
    unittest.main()
