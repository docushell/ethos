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
RECORD = ROOT / "docs/validation/patch-0-1-1-crates-publication-closeout-validation-2026-06-24.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
MAKEFILE = ROOT / "Makefile"

SOURCE_SHORT = "7bc50f0"
SOURCE_COMMIT = "7bc50f09f6ce0385737e9b978dcb249f161195b0"
SOURCE_TREE = "88bc7969652d56c534c5a101824926a8e9bbb4d0"
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


def cargo_search(crate: str) -> str:
    return subprocess.check_output(
        ["cargo", "search", crate, "--limit", "1"],
        cwd=ROOT,
        encoding="utf-8",
        stderr=subprocess.DEVNULL,
    ).strip()


class Patch011CratesPublicationCloseoutTests(unittest.TestCase):
    def test_closeout_record_is_source_bound_and_indexed(self) -> None:
        record = normalized(RECORD)
        readme = normalized(VALIDATION_README)

        self.assertIn(RECORD.name, readme)
        self.assertIn("patch 0.1.1 crates.io publication closeout", readme.lower())
        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Patch 0.1.1 crates publication closeout source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Patch 0.1.1 crates publication closeout source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_closeout_records_all_published_crates_and_commands(self) -> None:
        record = normalized(RECORD)

        for crate in CRATES:
            self.assertIn(f"{crate} = 0.1.1", record)
            self.assertIn(f"cargo publish --locked -p {crate}", record)
            self.assertIn(f"Published {crate} v0.1.1 at registry `crates-io`", record)
        self.assertIn("`ethos-doc-core` was published before dependent crates", record)
        self.assertIn("`ethos-verify` was published after ethos-doc-core was visible", record)
        self.assertIn("`ethos-pdf` was published after ethos-doc-core was visible", record)

    def test_live_crates_io_reports_patch_versions(self) -> None:
        for crate in CRATES:
            self.assertIn(f'{crate} = "0.1.1"', cargo_search(crate))

    def test_closeout_keeps_other_surfaces_blocked(self) -> None:
        raw = read(RECORD)
        lower = normalized(RECORD).lower()

        for expected in (
            "Public installation wording remains blocked until a separate wording and availability record.",
            "Hosted surfaces remain blocked.",
            "Production positioning remains blocked.",
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
        self.assertNotIn("/private/tmp", raw)
        self.assertNotIn("/var/folders", raw)
        self.assertNotIn("saumildiwaker", raw)

    def test_release_candidate_prep_runs_closeout_after_decision_guard(self) -> None:
        makefile = read(MAKEFILE)
        decision_guard = "$(PYTHON) .github/scripts/test_patch_0_1_1_crates_publication_approval_decision.py"
        closeout_guard = "$(PYTHON) .github/scripts/test_patch_0_1_1_crates_publication_closeout.py"

        self.assertIn(closeout_guard, makefile)
        self.assertEqual(1, makefile.count(closeout_guard))
        self.assertLess(makefile.index(decision_guard), makefile.index(closeout_guard))
        self.assertLess(
            makefile.index(closeout_guard),
            makefile.index("$(PYTHON) .github/scripts/test_pdfium_manual_setup_contract.py"),
        )


if __name__ == "__main__":
    unittest.main()
