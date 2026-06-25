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
RECORD = ROOT / "docs/validation/patch-0-1-2-rust-public-install-wording-closeout-validation-2026-06-25.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
README = ROOT / "README.md"
PYTHON_README = ROOT / "python/README.md"
PYTHON_QUICKSTART = ROOT / "python/QUICKSTART.md"
CLAIMS = ROOT / "docs/public-boundary-claims.json"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"
MAKEFILE = ROOT / "Makefile"

SOURCE_SHORT = "5ca6e23"
SOURCE_COMMIT = "5ca6e237bd12656f894c7a1d70fe57c7385a7c95"
SOURCE_TREE = "9d0f629bdfb89ae191d971ee4ec9f323a61fba84"
RUST_INSTALLS = (
    "cargo add ethos-doc-core@0.1.2",
    "cargo add ethos-verify@0.1.2",
    "cargo add ethos-pdf@0.1.2",
)
OLD_RUST_INSTALLS = (
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
    "`ethos-verify`, and `ethos-pdf` at `0.1.2`, the Python `ethos-pdf` wheel at `0.1.1`, the "
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


def normalized_public_readme() -> str:
    return re.sub(
        r"\s+",
        " ",
        " ".join(line.removeprefix("> ").strip() for line in read(README).splitlines()),
    )


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args],
        cwd=ROOT,
        encoding="utf-8",
        stderr=subprocess.DEVNULL,
    ).strip()


class Patch012RustPublicInstallWordingCloseoutTests(unittest.TestCase):
    def test_record_is_source_bound_and_indexed(self) -> None:
        record = normalized(RECORD)
        validation_readme = normalized(VALIDATION_README)

        self.assertIn(RECORD.name, validation_readme)
        self.assertIn("patch 0.1.2 Rust public install wording closeout", normalized(VALIDATION_README))
        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Patch 0.1.2 Rust public install wording closeout source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Patch 0.1.2 Rust public install wording closeout source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_readme_exposes_published_rust_npm_and_cli_paths_only(self) -> None:
        readme = normalized(README)

        self.assertIn(CURRENT_PUBLIC_SENTENCE, normalized_public_readme())
        for expected in (*RUST_INSTALLS, NPM_INSTALL, GITHUB_RELEASE, PYTHON_INSTALL):
            self.assertIn(expected, readme)
        for old in OLD_RUST_INSTALLS:
            self.assertNotIn(old, readme)
        self.assertNotIn("python3 -m pip install ethos-pdf==0.1.2", readme)
        self.assertNotIn("npm install -g @docushell/ethos-pdf@0.1.1", readme)

    def test_python_package_docs_remain_on_published_pypi_baseline(self) -> None:
        for path in (PYTHON_README, PYTHON_QUICKSTART):
            text = normalized(path)
            self.assertIn(PYTHON_INSTALL, text)
            self.assertNotIn("ethos-pdf==0.1.2", text)
            self.assertIn("caller-provided local `ethos` CLI binary", text)
            self.assertIn("does not bundle", text)
            self.assertIn("ETHOS_PDFIUM_LIBRARY_PATH", text)

    def test_public_boundary_claims_track_current_install_wording(self) -> None:
        payload = json.loads(read(CLAIMS))
        claims = payload["surfaces"]["readme"]["claims"]

        for expected in (
            "Ethos is a deterministic document evidence layer for source-grounded verification and citation checking across native Ethos JSON and supported foreign parser outputs.",
            "The current beta includes the GitHub source repository, Rust library crates `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` at `0.1.2`, the Python `ethos-pdf` wheel at `0.1.1`, the npm `@docushell/ethos-pdf@0.1.2` package, and GitHub Release `v0.1.2` macOS arm64/Linux x64 CLI artifacts.",
            "PDFium-backed commands use caller-provided PDFium through `ETHOS_PDFIUM_LIBRARY_PATH`.",
            *RUST_INSTALLS,
            PYTHON_INSTALL,
            "The Python wheel is a thin wrapper around a caller-provided local `ethos` CLI binary.",
            "It does not bundle the CLI or PDFium.",
            NPM_INSTALL,
            "The npm package vendors only the approved macOS arm64 and Linux x64 CLI binaries.",
            GITHUB_RELEASE,
        ):
            self.assertIn(expected, claims)

    def test_status_docs_record_retained_python_and_surface_boundaries(self) -> None:
        for path in (EXECUTION_STATUS, PUBLIC_RELEASE_CHECKLIST):
            text = normalized(path)
            self.assertIn(RECORD.name, text, str(path))
            self.assertIn("ethos-doc-core", text, str(path))
            self.assertIn("0.1.2", text, str(path))
            self.assertIn("ethos-pdf==0.1.1", text, str(path))
            self.assertIn("PyPI", text, str(path))
            self.assertIn("hosted", text.lower(), str(path))
            self.assertIn("production", text.lower(), str(path))

        record = normalized(RECORD)
        self.assertIn("ethos-doc-core", record)
        self.assertIn("0.1.2", record)
        self.assertIn("ethos-pdf==0.1.1", record)
        self.assertIn("PyPI", record)
        self.assertIn("hosted", record.lower())
        self.assertIn("production", record.lower())

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

    def test_release_candidate_prep_runs_rust_wording_after_crates_closeout(self) -> None:
        makefile = read(MAKEFILE)
        crates_closeout_guard = "$(PYTHON) .github/scripts/test_patch_0_1_2_crates_publication_closeout.py"
        rust_wording_guard = "$(PYTHON) .github/scripts/test_patch_0_1_2_rust_public_install_wording_closeout.py"
        first_public_guard = "$(PYTHON) .github/scripts/test_first_public_release_artifact_evidence.py"
        block = target_block("release-candidate-prep")

        self.assertIn(rust_wording_guard, block)
        self.assertEqual(1, makefile.count(rust_wording_guard))
        self.assertLess(block.index(crates_closeout_guard), block.index(rust_wording_guard))
        self.assertLess(block.index(rust_wording_guard), block.index(first_public_guard))


if __name__ == "__main__":
    unittest.main()
