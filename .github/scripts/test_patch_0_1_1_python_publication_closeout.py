#!/usr/bin/env python3
#
# Copyright 2026 The Ethos maintainers
#
# Licensed under the Apache License, Version 2.0 (the "License");
#

from __future__ import annotations

import json
import re
import subprocess
import unittest
import urllib.request
from pathlib import Path

from makefile_guard import target_block


ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "docs/validation/patch-0-1-1-python-publication-closeout-validation-2026-06-24.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
MAKEFILE = ROOT / "Makefile"

SOURCE_SHORT = "2cab87d"
SOURCE_COMMIT = "2cab87df30443cb8e1c32489adc9b3123cac455f"
SOURCE_TREE = "ae58f8fcdd7a3c60c68e96cb39259a2eb37350bc"
PACKAGE = "ethos-pdf"
VERSION = "0.1.1"
WHEEL = "ethos_pdf-0.1.1-py3-none-any.whl"
WHEEL_SHA256 = "e0292276e711e75d4f7e1bb8c2c6137c6e89d4c343dd308943eb9b22094ea451"
WHEEL_URL = "https://files.pythonhosted.org/packages/3d/c2/406c298e37fca7617c97ff9d74a30ab0a017a22f6025c8f2b74c25b5b39c/ethos_pdf-0.1.1-py3-none-any.whl"
WHEEL_SIZE = 11398
UPLOAD_TIME = "2026-06-24T06:15:17.128860Z"
FORBIDDEN = (
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


def pypi_release_json() -> dict:
    with urllib.request.urlopen(f"https://pypi.org/pypi/{PACKAGE}/{VERSION}/json", timeout=30) as response:
        return json.load(response)


class Patch011PythonPublicationCloseoutTests(unittest.TestCase):
    def test_closeout_record_is_source_bound_and_indexed(self) -> None:
        record = normalized(RECORD)
        readme = normalized(VALIDATION_README)

        self.assertIn(RECORD.name, readme)
        self.assertIn("patch 0.1.1 Python PyPI publication closeout", readme)
        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Patch 0.1.1 Python publication closeout source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Patch 0.1.1 Python publication closeout source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_closeout_records_upload_and_registry_evidence(self) -> None:
        record = normalized(RECORD)

        for expected in (
            "python3 -m twine upload <candidate-dir>/ethos_pdf-0.1.1-py3-none-any.whl",
            "Uploading distributions to https://upload.pypi.org/legacy/",
            "WARNING This environment is not supported for trusted publishing",
            "Uploading ethos_pdf-0.1.1-py3-none-any.whl",
            "View at: https://pypi.org/project/ethos-pdf/0.1.1/",
            "twine check",
            "PASSED",
            "SOURCE_DATE_EPOCH=0",
            PACKAGE,
            VERSION,
            WHEEL,
            WHEEL_SHA256,
            WHEEL_URL,
            UPLOAD_TIME,
            "bdist_wheel",
            "py3",
            "yanked: false",
            "ETHOS_PDFIUM_LIBRARY_PATH",
        ):
            self.assertIn(expected, record)

    def test_live_pypi_reports_published_candidate(self) -> None:
        data = pypi_release_json()

        self.assertEqual(PACKAGE, data["info"]["name"])
        self.assertEqual(VERSION, data["info"]["version"])
        self.assertEqual(">=3.8", data["info"]["requires_python"])
        self.assertEqual(1, len(data["urls"]))
        file = data["urls"][0]
        self.assertEqual(WHEEL, file["filename"])
        self.assertEqual("bdist_wheel", file["packagetype"])
        self.assertEqual("py3", file["python_version"])
        self.assertEqual(WHEEL_SHA256, file["digests"]["sha256"])
        self.assertEqual(WHEEL_URL, file["url"])
        self.assertEqual(WHEEL_SIZE, file["size"])
        self.assertEqual(UPLOAD_TIME, file["upload_time_iso_8601"])
        self.assertFalse(file["yanked"])

    def test_retained_blockers_and_public_path_hygiene(self) -> None:
        raw = read(RECORD)
        lower = normalized(RECORD).lower()

        for expected in (
            "Public installation wording may be updated only in a separate bounded docs lane.",
            "Hosted surfaces remain blocked.",
            "Production positioning remains blocked.",
            "Public benchmark reports remain blocked.",
            "Public benchmark claims remain blocked.",
            "Windows packaged artifacts remain blocked.",
            "Bundled project-maintained PDFium builds remain blocked.",
            "`ethos-doc` remains blocked.",
            "`ethos-rag` remains blocked.",
            "PDFium remains caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`.",
        ):
            self.assertIn(expected, raw)
        for forbidden in FORBIDDEN:
            self.assertNotIn(forbidden, lower)
        self.assertNotIn("/Users/", raw)
        self.assertNotIn("/tmp", raw)
        self.assertNotIn("/private/tmp", raw)
        self.assertNotIn("/private/var", raw)
        self.assertNotIn("/var/folders", raw)
        self.assertNotIn("saumildiwaker", raw)

    def test_release_candidate_prep_runs_closeout_after_decision_guard(self) -> None:
        makefile = read(MAKEFILE)
        decision_guard = "$(PYTHON) .github/scripts/test_patch_0_1_1_python_deterministic_wheel_approval_decision.py"
        closeout_guard = "$(PYTHON) .github/scripts/test_patch_0_1_1_python_publication_closeout.py"
        npm_guard = "$(PYTHON) .github/scripts/test_npm_binary_package_scaffold.py"
        block = target_block("release-candidate-prep")

        self.assertIn(closeout_guard, block)
        self.assertEqual(1, makefile.count(closeout_guard))
        self.assertLess(block.index(decision_guard), block.index(closeout_guard))
        self.assertLess(block.index(closeout_guard), block.index(npm_guard))


if __name__ == "__main__":
    unittest.main()
