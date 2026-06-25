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
RECORD = ROOT / "docs/validation/patch-0-1-2-python-publication-approval-request-validation-2026-06-25.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
PYPROJECT = ROOT / "pyproject.toml"
INIT = ROOT / "python/ethos_pdf/__init__.py"
MAKEFILE = ROOT / "Makefile"

SOURCE_SHORT = "e431982"
SOURCE_COMMIT = "e431982cca2922d4cc59ddc7cacb9e72538b1cd0"
SOURCE_TREE = "f59ddd018d234eeee0ac77292b417f4acb892b4e"
PACKAGE = "ethos-pdf==0.1.2"
WHEEL = "ethos_pdf-0.1.2-py3-none-any.whl"
DETERMINISTIC_SHA256 = "6f17240954f1257ece3c762c820ad771ccb114353bfb699fe87f418a5ceb663c"
WHEEL_FILES = (
    "ethos_pdf/__init__.py",
    "ethos_pdf/_cli.py",
    "ethos_pdf-0.1.2.dist-info/METADATA",
    "ethos_pdf-0.1.2.dist-info/RECORD",
    "ethos_pdf-0.1.2.dist-info/WHEEL",
    "ethos_pdf-0.1.2.dist-info/licenses/LICENSE",
    "ethos_pdf-0.1.2.dist-info/licenses/NOTICE",
    "ethos_pdf-0.1.2.dist-info/top_level.txt",
)
FORBIDDEN = (
    "pypi upload approved",
    "pypi publication approved",
    "python package is published",
    "wheel is published",
    "twine upload approved",
    "python installation wording approved",
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


class Patch012PythonPublicationApprovalRequestTests(unittest.TestCase):
    def test_request_record_is_source_bound_and_indexed(self) -> None:
        record = normalized(RECORD)
        readme = normalized(VALIDATION_README)

        self.assertIn(RECORD.name, readme)
        self.assertIn("patch 0.1.2 Python PyPI publication approval request", readme)
        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Patch 0.1.2 Python publication approval request source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Patch 0.1.2 Python publication approval request source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_request_names_exact_deterministic_wheel_candidate_and_metadata(self) -> None:
        record = normalized(RECORD)

        for expected in (
            PACKAGE,
            WHEEL,
            DETERMINISTIC_SHA256,
            "SOURCE_DATE_EPOCH=0",
            "Name: `ethos-pdf`",
            "Version: `0.1.2`",
            "License-Expression: `Apache-2.0`",
            "Requires-Python: `>=3.8`",
            "Wheel-Version: `1.0`",
            "Root-Is-Purelib: `true`",
            "Tag: `py3-none-any`",
            "member timestamps: `1980-01-01 00:00:00`",
            "version `0.1.2`",
            "EthosCli",
            "EthosCommandError",
            "Python `3.9.6`",
            "build `1.4.4`",
        ):
            self.assertIn(expected, record)
        for wheel_file in WHEEL_FILES:
            self.assertIn(wheel_file, record)

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
            "Python public installation wording remains blocked pending PyPI availability closeout.",
            "PDFium remains caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`.",
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

    def test_source_metadata_keeps_current_python_surface_shape(self) -> None:
        pyproject = read(PYPROJECT)
        init = read(INIT)

        self.assertIn('name = "ethos-pdf"', pyproject)
        self.assertIn('version = "0.1.2"', pyproject)
        self.assertIn('requires-python = ">=3.8"', pyproject)
        self.assertIn('license = "Apache-2.0"', pyproject)
        self.assertIn('readme = "python/README.md"', pyproject)
        self.assertIn('__version__ = "0.1.2"', init)
        self.assertIn('"EthosCli"', init)
        self.assertIn('"EthosCommandError"', init)

    def test_release_candidate_prep_runs_request_guard_after_rust_wording(self) -> None:
        makefile = read(MAKEFILE)
        rust_wording_guard = "$(PYTHON) .github/scripts/test_patch_0_1_2_rust_public_install_wording_closeout.py"
        guard = "$(PYTHON) .github/scripts/test_patch_0_1_2_python_publication_approval_request.py"
        first_public_guard = "$(PYTHON) .github/scripts/test_first_public_release_artifact_evidence.py"
        block = target_block("release-candidate-prep")

        self.assertIn(guard, block)
        self.assertEqual(1, makefile.count(guard))
        self.assertLess(block.index(rust_wording_guard), block.index(guard))
        self.assertLess(block.index(guard), block.index(first_public_guard))


if __name__ == "__main__":
    unittest.main()
