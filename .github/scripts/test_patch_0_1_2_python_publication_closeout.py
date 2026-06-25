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
RECORD = ROOT / "docs/validation/patch-0-1-2-python-publication-closeout-validation-2026-06-25.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
MAKEFILE = ROOT / "Makefile"

SOURCE_SHORT = "26012eb"
SOURCE_COMMIT = "26012ebfaf9a50e02c12515827f63c21e6a69ca6"
SOURCE_TREE = "a178affbdf5a0f46d52aa80c804b1142688f4a82"
PACKAGE_SOURCE_COMMIT = "e431982cca2922d4cc59ddc7cacb9e72538b1cd0"
PACKAGE_SOURCE_TREE = "f59ddd018d234eeee0ac77292b417f4acb892b4e"
PACKAGE = "ethos-pdf"
VERSION = "0.1.2"
WHEEL = "ethos_pdf-0.1.2-py3-none-any.whl"
WHEEL_SHA256 = "6f17240954f1257ece3c762c820ad771ccb114353bfb699fe87f418a5ceb663c"
WHEEL_URL = "https://files.pythonhosted.org/packages/32/0f/06fe9ab696ee596cc88f9b061b5c2b9f443fe7fcdc54ebb02a4189dda129/ethos_pdf-0.1.2-py3-none-any.whl"
WHEEL_SIZE = 11445
UPLOAD_TIME = "2026-06-25T05:06:17.574879Z"
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


class Patch012PythonPublicationCloseoutTests(unittest.TestCase):
    def test_closeout_record_is_source_bound_and_indexed(self) -> None:
        record = normalized(RECORD)
        readme = normalized(VALIDATION_README)

        self.assertIn(RECORD.name, readme)
        self.assertIn("patch 0.1.2 Python PyPI publication closeout", readme)
        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Patch 0.1.2 Python publication closeout source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Patch 0.1.2 Python publication closeout source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_closeout_records_upload_and_registry_evidence(self) -> None:
        record = normalized(RECORD)

        for expected in (
            "python3 -m twine upload target/python-pypi-0.1.2/ethos_pdf-0.1.2-py3-none-any.whl",
            "Uploading distributions to https://upload.pypi.org/legacy/",
            "WARNING This environment is not supported for trusted publishing",
            "Uploading ethos_pdf-0.1.2-py3-none-any.whl",
            "View at: https://pypi.org/project/ethos-pdf/0.1.2/",
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
            f"Package source commit: `{PACKAGE_SOURCE_COMMIT}`",
            f"Package source tree: `{PACKAGE_SOURCE_TREE}`",
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
            "Package tag creation remains blocked until a separate explicit approval or closeout record permits it.",
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

    def test_release_candidate_prep_runs_closeout_after_decision_guard(self) -> None:
        makefile = read(MAKEFILE)
        decision_guard = "$(PYTHON) .github/scripts/test_patch_0_1_2_python_publication_approval_decision.py"
        closeout_guard = "$(PYTHON) .github/scripts/test_patch_0_1_2_python_publication_closeout.py"
        first_public_guard = "$(PYTHON) .github/scripts/test_first_public_release_artifact_evidence.py"
        block = target_block("release-candidate-prep")

        self.assertIn(closeout_guard, block)
        self.assertEqual(1, makefile.count(closeout_guard))
        self.assertLess(block.index(decision_guard), block.index(closeout_guard))
        self.assertLess(block.index(closeout_guard), block.index(first_public_guard))


if __name__ == "__main__":
    unittest.main()
