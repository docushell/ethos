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
RECORD = ROOT / "docs/validation/patch-0-1-2-public-install-wording-closeout-validation-2026-06-24.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
MAKEFILE = ROOT / "Makefile"

SOURCE_SHORT = "37c294a"
SOURCE_COMMIT = "37c294a2175bd4713df6a93464b90e6372a176d9"
SOURCE_TREE = "648cd0cca2f04461fb3d6e04db6004590b75ede4"
RUST_INSTALLS = (
    "cargo add ethos-doc-core@0.1.1",
    "cargo add ethos-verify@0.1.1",
    "cargo add ethos-pdf@0.1.1",
)
PYTHON_INSTALL = "python3 -m pip install ethos-pdf==0.1.1"
NPM_INSTALL = "npm install -g @docushell/ethos-pdf@0.1.2"
GITHUB_RELEASE = "GitHub Release `v0.1.2` also provides evaluation CLI archives for macOS arm64 and Linux x64."
CURRENT_PUBLIC_SENTENCE = (
    "Ethos is a deterministic document evidence layer for source-grounded verification and "
    "citation checking across native Ethos JSON and supported foreign parser outputs. The current "
    "beta includes the GitHub source repository, Rust library crates `ethos-doc-core`, "
    "`ethos-verify`, and `ethos-pdf` at `0.1.1`, the Python `ethos-pdf` wheel at `0.1.1`, the "
    "npm `@docushell/ethos-pdf@0.1.2` package, and GitHub Release `v0.1.2` macOS arm64/Linux x64 "
    "CLI artifacts. PDFium-backed commands use caller-provided PDFium through "
    "`ETHOS_PDFIUM_LIBRARY_PATH`."
)
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


class Patch012PublicInstallWordingCloseoutTests(unittest.TestCase):
    def test_record_is_source_bound_and_indexed(self) -> None:
        record = normalized(RECORD)
        validation_readme = normalized(VALIDATION_README)

        self.assertIn(RECORD.name, validation_readme)
        self.assertIn("patch 0.1.2 public install wording closeout", validation_readme)
        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Patch 0.1.2 public install wording closeout source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Patch 0.1.2 public install wording closeout source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_record_exposes_bounded_npm_cli_wording_at_time_of_closeout(self) -> None:
        record = normalized(RECORD)

        self.assertIn("The current public README status sentence is:", record)
        self.assertIn("Rust library crates `ethos-doc-core`, `ethos-verify`, and", record)
        self.assertIn("`ethos-pdf` at `0.1.1`", record)
        self.assertIn("the Python `ethos-pdf` wheel at `0.1.1`", record)
        self.assertIn("the npm > `@docushell/ethos-pdf@0.1.2` package", record)
        self.assertIn(NPM_INSTALL, record)
        self.assertIn(
            "GitHub Release `v0.1.2` evaluation CLI archives for macOS arm64 and Linux x64 are also the current public CLI artifact references.",
            record,
        )
        for expected in (*RUST_INSTALLS, PYTHON_INSTALL):
            self.assertIn(expected, record)

        self.assertNotIn("npm install -g @docushell/ethos-pdf@0.1.1", record)
        self.assertNotIn("python3 -m pip install ethos-pdf==0.1.2", record)

    def test_record_preserves_python_baseline_at_time_of_closeout(self) -> None:
        record = normalized(RECORD)

        self.assertIn(PYTHON_INSTALL, record)
        self.assertNotIn("python3 -m pip install ethos-pdf==0.1.2", record)

    def test_status_docs_record_retained_rust_python_boundaries(self) -> None:
        for path in (RECORD,):
            text = normalized(path)
            self.assertIn("@docushell/ethos-pdf@0.1.2", text)
            self.assertIn("v0.1.2", text)
            self.assertIn("Rust", text)
            self.assertIn("0.1.1", text)
            self.assertIn("ethos-pdf==0.1.1", text)
            self.assertIn("crates.io/PyPI `0.1.2` publication closeout records", text)

    def test_boundaries_and_public_path_hygiene(self) -> None:
        raw = read(RECORD)
        lower = re.sub(r"\s+", " ", raw).lower()
        for forbidden in FORBIDDEN:
            self.assertNotIn(forbidden, lower)
        self.assertNotIn("/Users/", raw)
        self.assertNotIn("/private/tmp", raw)
        self.assertNotIn("/private/var", raw)
        self.assertNotIn("/var/folders", raw)
        self.assertNotIn("saumildiwaker", raw)

    def test_release_candidate_prep_runs_wording_guard_after_0_1_2_publication_closeouts(self) -> None:
        makefile = read(MAKEFILE)
        artifact_guard = "$(PYTHON) .github/scripts/test_patch_0_1_2_artifact_publication_closeout.py"
        npm_guard = "$(PYTHON) .github/scripts/test_patch_0_1_2_npm_publication_closeout.py"
        wording_guard = "$(PYTHON) .github/scripts/test_patch_0_1_2_public_install_wording_closeout.py"
        first_public_guard = "$(PYTHON) .github/scripts/test_first_public_release_artifact_evidence.py"
        block = target_block("release-candidate-prep")

        self.assertIn(wording_guard, block)
        self.assertEqual(1, makefile.count(wording_guard))
        self.assertLess(block.index(artifact_guard), block.index(wording_guard))
        self.assertLess(block.index(npm_guard), block.index(wording_guard))
        self.assertLess(block.index(wording_guard), block.index(first_public_guard))


if __name__ == "__main__":
    unittest.main()
