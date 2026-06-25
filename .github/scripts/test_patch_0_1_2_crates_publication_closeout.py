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
RECORD = ROOT / "docs/validation/patch-0-1-2-crates-publication-closeout-validation-2026-06-25.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"
MAKEFILE = ROOT / "Makefile"

SOURCE_SHORT = "35d0cca"
SOURCE_COMMIT = "35d0cca87669217f079793ce0553c9ac1121884b"
SOURCE_TREE = "3fcad87f2fc67c59c2f102f4f2c73d9e5c382724"
VERSION = "0.1.2"
CRATES = ("ethos-doc-core", "ethos-verify", "ethos-pdf")
FORBIDDEN = (
    "hosted surfaces approved",
    "production-ready",
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


def crates_io_version(crate: str, version: str) -> str:
    request = urllib.request.Request(
        f"https://crates.io/api/v1/crates/{crate}/{version}",
        headers={"User-Agent": "ethos-release-validation"},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        payload = json.load(response)
    return payload["version"]["num"]


class Patch012CratesPublicationCloseoutTests(unittest.TestCase):
    def test_closeout_record_is_source_bound_and_indexed(self) -> None:
        record = normalized(RECORD)
        readme = normalized(VALIDATION_README)

        self.assertIn(RECORD.name, readme)
        self.assertIn("patch 0.1.2 crates.io publication closeout", readme.lower())
        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Patch 0.1.2 crates publication closeout source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Patch 0.1.2 crates publication closeout source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_closeout_records_all_published_crates_and_commands(self) -> None:
        record = normalized(RECORD)

        for crate in CRATES:
            self.assertIn(f"{crate} = {VERSION}", record)
            self.assertIn(f"cargo publish --locked -p {crate}", record)
            self.assertIn(f"Published {crate} v{VERSION} at registry `crates-io`", record)
            self.assertIn(f'{crate} = "{VERSION}"', record)
        self.assertIn("`ethos-doc-core` was published before dependent crates", record)
        self.assertIn("`ethos-verify` was published after ethos-doc-core was visible", record)
        self.assertIn("`ethos-pdf` was published after ethos-verify was visible", record)

    def test_live_crates_io_reports_patch_versions(self) -> None:
        for crate in CRATES:
            self.assertEqual(VERSION, crates_io_version(crate, VERSION))

    def test_status_docs_reference_closeout_and_keep_remaining_boundaries(self) -> None:
        for path in (EXECUTION_STATUS, PUBLIC_RELEASE_CHECKLIST):
            text = normalized(path)
            self.assertIn(RECORD.name, text, str(path))
            self.assertIn("Rust crate public installation wording remains blocked", text, str(path))
            self.assertIn("Python installation remains at `ethos-pdf==0.1.1`", text, str(path))
            self.assertIn("hosted", text.lower(), str(path))
            self.assertIn("production", text.lower(), str(path))

    def test_closeout_keeps_other_surfaces_blocked(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)
        lower = record.lower()

        for expected in (
            "Rust crate public installation wording remains blocked until a separate wording and availability record.",
            "Python installation remains at `ethos-pdf==0.1.1` until separate PyPI `0.1.2` publication records pass.",
            "Hosted surfaces remain blocked.",
            "Production positioning remains blocked.",
            "Windows packaged artifacts remain blocked.",
            "Bundled project-maintained PDFium builds remain blocked.",
            "`ethos-doc` remains blocked.",
            "`ethos-rag` remains blocked.",
            "PDFium remains caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`.",
        ):
            self.assertIn(expected, record)
        for forbidden in FORBIDDEN:
            self.assertNotIn(forbidden, lower)
        self.assertNotIn("/Users/", raw)
        self.assertNotIn("/private/tmp", raw)
        self.assertNotIn("/var/folders", raw)
        self.assertNotIn("saumildiwaker", raw)

    def test_release_candidate_prep_runs_closeout_after_decision_guard(self) -> None:
        makefile = read(MAKEFILE)
        decision_guard = "$(PYTHON) .github/scripts/test_patch_0_1_2_crates_publication_approval_decision.py"
        closeout_guard = "$(PYTHON) .github/scripts/test_patch_0_1_2_crates_publication_closeout.py"
        first_public_guard = "$(PYTHON) .github/scripts/test_first_public_release_artifact_evidence.py"
        block = target_block("release-candidate-prep")

        self.assertIn(closeout_guard, block)
        self.assertEqual(1, makefile.count(closeout_guard))
        self.assertLess(block.index(decision_guard), block.index(closeout_guard))
        self.assertLess(block.index(closeout_guard), block.index(first_public_guard))


if __name__ == "__main__":
    unittest.main()
