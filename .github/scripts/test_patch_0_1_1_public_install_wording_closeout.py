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
from pathlib import Path

from makefile_guard import target_block


ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "docs/validation/patch-0-1-1-public-install-wording-closeout-validation-2026-06-24.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
README = ROOT / "README.md"
PYTHON_README = ROOT / "python/README.md"
PYTHON_QUICKSTART = ROOT / "python/QUICKSTART.md"
CLAIMS = ROOT / "docs/public-boundary-claims.json"
MAKEFILE = ROOT / "Makefile"

SOURCE_SHORT = "4a573dc"
SOURCE_COMMIT = "4a573dc96175cf10b90b8e6928e2c2408cb763e3"
SOURCE_TREE = "71c874291b17d92d641470f01d2dedaf8a48d8ea"
PYPI_PACKAGE = "ethos-pdf==0.1.1"
NPM_PACKAGE = "@docushell/ethos-pdf@0.1.1"
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


class Patch011PublicInstallWordingCloseoutTests(unittest.TestCase):
    def test_record_is_source_bound_and_indexed(self) -> None:
        record = normalized(RECORD)
        readme = normalized(VALIDATION_README)

        self.assertIn(RECORD.name, readme)
        self.assertIn("patch 0.1.1 public installation wording closeout", readme)
        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Patch 0.1.1 public install wording closeout source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Patch 0.1.1 public install wording closeout source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_readme_exposes_bounded_public_install_paths(self) -> None:
        record = normalized(RECORD)

        for expected in (
            "cargo add ethos-doc-core@0.1.1",
            "cargo add ethos-verify@0.1.1",
            "cargo add ethos-pdf@0.1.1",
            "python3 -m pip install ethos-pdf==0.1.1",
            "The Python wheel is a thin wrapper around a caller-provided local ethos CLI binary.",
            "It does not bundle the CLI or PDFium.",
            "ETHOS_PDFIUM_LIBRARY_PATH",
        ):
            self.assertIn(expected, record)

        for expected in (
            "npm install -g @docushell/ethos-pdf@0.1.1",
            "GitHub Release v0.1.1 evaluation CLI archives for macOS arm64 and Linux x64",
        ):
            self.assertIn(expected, record)

    def test_python_package_docs_keep_cli_and_pdfium_boundaries(self) -> None:
        for path in (PYTHON_README, PYTHON_QUICKSTART):
            text = normalized(path)
            self.assertIn("python3 -m pip install ethos-pdf==0.1.1", text)
            self.assertIn("caller-provided local `ethos` CLI binary", text)
            self.assertIn("does not bundle", text)
            self.assertIn("PDFium", text)
            self.assertIn("ETHOS_PDFIUM_LIBRARY_PATH", text)

    def test_public_boundary_claims_track_install_wording(self) -> None:
        payload = json.loads(read(CLAIMS))
        claims = payload["surfaces"]["readme"]["claims"]

        for expected in (
            "python3 -m pip install ethos-pdf==0.1.1",
            "The Python wheel is a thin wrapper around a caller-provided local `ethos` CLI binary.",
            "It does not bundle the CLI or PDFium.",
        ):
            self.assertIn(expected, claims)

    def test_boundaries_and_public_path_hygiene(self) -> None:
        for path in (RECORD, README, PYTHON_README, PYTHON_QUICKSTART):
            raw = read(path)
            lower = re.sub(r"\s+", " ", raw).lower()
            for forbidden in FORBIDDEN:
                self.assertNotIn(forbidden, lower, str(path))
            self.assertNotIn("/Users/", raw, str(path))
            self.assertNotIn("/private/tmp", raw, str(path))
            self.assertNotIn("/private/var", raw, str(path))
            self.assertNotIn("/var/folders", raw, str(path))
            self.assertNotIn("saumildiwaker", raw, str(path))

    def test_release_candidate_prep_runs_wording_guard_after_publication_closeout(self) -> None:
        makefile = read(MAKEFILE)
        closeout_guard = "$(PYTHON) .github/scripts/test_patch_0_1_1_python_publication_closeout.py"
        wording_guard = "$(PYTHON) .github/scripts/test_patch_0_1_1_public_install_wording_closeout.py"
        npm_guard = "$(PYTHON) .github/scripts/test_npm_binary_package_scaffold.py"
        block = target_block("release-candidate-prep")

        self.assertIn(wording_guard, block)
        self.assertEqual(1, makefile.count(wording_guard))
        self.assertLess(block.index(closeout_guard), block.index(wording_guard))
        self.assertLess(block.index(wording_guard), block.index(npm_guard))


if __name__ == "__main__":
    unittest.main()
