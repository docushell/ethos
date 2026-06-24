#!/usr/bin/env python3
#
# Copyright 2026 The Ethos maintainers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path

from makefile_guard import target_block


ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "docs/validation/patch-0-1-1-python-publication-approval-request-validation-2026-06-24.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
PYPROJECT = ROOT / "pyproject.toml"
INIT = ROOT / "python/ethos_pdf/__init__.py"
MAKEFILE = ROOT / "Makefile"

SOURCE_SHORT = "16b2c18"
SOURCE_COMMIT = "16b2c189e1f23962dced921551cf6b4f9af4ba06"
SOURCE_TREE = "c76ba8525faaa63c53ac7f037d349a8ab4803fcb"
PACKAGE = "ethos-pdf==0.1.1"
WHEEL = "ethos_pdf-0.1.1-py3-none-any.whl"
WHEEL_SHA256 = "faa6c4751341b603b986ad3cf65d3c0c2f574e5df1d7232f76c3afd0221dac14"
WHEEL_FILES = (
    "ethos_pdf/__init__.py",
    "ethos_pdf/_cli.py",
    "ethos_pdf-0.1.1.dist-info/METADATA",
    "ethos_pdf-0.1.1.dist-info/WHEEL",
    "ethos_pdf-0.1.1.dist-info/licenses/LICENSE",
    "ethos_pdf-0.1.1.dist-info/licenses/NOTICE",
)
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


class Patch011PythonPublicationApprovalRequestTests(unittest.TestCase):
    def test_request_record_is_source_bound_and_indexed(self) -> None:
        record = normalized(RECORD)
        readme = normalized(VALIDATION_README)

        self.assertIn(RECORD.name, readme)
        self.assertIn("patch 0.1.1 Python PyPI publication approval request", readme)
        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Patch 0.1.1 Python publication approval request source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Patch 0.1.1 Python publication approval request source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_request_names_exact_wheel_candidate_and_metadata(self) -> None:
        record = normalized(RECORD)

        for expected in (
            PACKAGE,
            WHEEL,
            WHEEL_SHA256,
            "Name: `ethos-pdf`",
            "Version: `0.1.1`",
            "License-Expression: `Apache-2.0`",
            "Requires-Python: `>=3.8`",
            "Wheel-Version: `1.0`",
            "Root-Is-Purelib: `true`",
            "Tag: `py3-none-any`",
            "version `0.1.1`",
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
            "A decider must accept or reject this exact request packet.",
            "This request record does not approve PyPI upload.",
            "This request record does not upload any Python distribution.",
            "Only after that decision record passes may an operator upload the exact wheel named above",
            "Actual PyPI upload remains blocked pending explicit decider approval.",
            "Public installation wording remains blocked pending explicit decider approval.",
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
        self.assertNotIn("Desktop/Stuff", raw)

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

    def test_release_candidate_prep_runs_request_guard_after_python_surface_tests(self) -> None:
        makefile = read(MAKEFILE)
        block = target_block("release-candidate-prep")
        python_surface = "$(MAKE) python-surface-test PYTHON=$(PYTHON)"
        guard = "$(PYTHON) .github/scripts/test_patch_0_1_1_python_publication_approval_request.py"
        npm_guard = "$(PYTHON) .github/scripts/test_npm_binary_package_scaffold.py"

        self.assertIn(guard, block)
        self.assertEqual(1, makefile.count(guard))
        self.assertLess(block.index(python_surface), block.index(guard))
        self.assertLess(block.index(guard), block.index(npm_guard))


if __name__ == "__main__":
    unittest.main()
