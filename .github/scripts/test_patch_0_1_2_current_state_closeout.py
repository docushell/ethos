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
RECORD = ROOT / "docs/validation/patch-0-1-2-current-state-closeout-validation-2026-06-25.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"
CHANGELOG = ROOT / "CHANGELOG.md"
MAKEFILE = ROOT / "Makefile"

SOURCE_SHORT = "aa4b5f2"
SOURCE_COMMIT = "aa4b5f2f3d58175e64572f42e9f4a8a88d9cede1"
SOURCE_TREE = "604b886cccfde24af3071a6babeda25f63230835"
APPROVED_SURFACES = (
    "GitHub source repository",
    "Rust library crates `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` at `0.1.2`",
    "Python `ethos-pdf` wheel at `0.1.2`",
    "npm `@docushell/ethos-pdf@0.1.2` package",
    "GitHub Release `v0.1.2` macOS arm64/Linux x64 CLI artifacts",
    "Annotated package tags `ethos-package-ethos-doc-core-0.1.2`, `ethos-package-ethos-verify-0.1.2`, and `ethos-package-ethos-pdf-0.1.2`",
)
RETAINED_BLOCKERS = (
    "Hosted surfaces remain blocked.",
    "Production positioning remains blocked.",
    "Windows packaged artifacts remain blocked.",
    "Bundled project-maintained PDFium builds remain blocked.",
    "`ethos-doc` remains blocked.",
    "`ethos-rag` remains blocked.",
    "Public benchmark reports remain blocked.",
    "Public benchmark claims remain blocked.",
    "Speed, footprint, parser-quality, table-quality, and production claims remain blocked.",
)
FORBIDDEN_CURRENT_STATUS = (
    "Patch `0.1.2` approved evaluation surfaces remain blocked",
    "Patch `0.1.2` package tag creation remains blocked",
    "Patch `0.1.2` is not package-release, artifact-release",
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


class Patch012CurrentStateCloseoutTests(unittest.TestCase):
    def test_record_is_source_bound_and_indexed(self) -> None:
        record = normalized(RECORD)
        readme = normalized(VALIDATION_README)

        self.assertIn(RECORD.name, readme)
        self.assertIn("patch `0.1.2` current-state closeout", readme.lower())
        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Patch 0.1.2 current-state closeout source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Patch 0.1.2 current-state closeout source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_record_closes_only_approved_patch_0_1_2_surfaces(self) -> None:
        record = normalized(RECORD)
        raw = read(RECORD)

        for surface in APPROVED_SURFACES:
            self.assertIn(surface, record)
        for blocker in RETAINED_BLOCKERS:
            self.assertIn(blocker, record)
        self.assertIn("This record does not approve any new public surface.", record)
        self.assertIn("This record does not approve production positioning.", record)
        self.assertNotIn("/Users/", raw)
        self.assertNotIn("/private/tmp", raw)
        self.assertNotIn("/private/var", raw)
        self.assertNotIn("/var/folders", raw)
        self.assertNotIn("saumildiwaker", raw)

    def test_current_status_docs_reference_final_patch_state(self) -> None:
        for path in (EXECUTION_STATUS, PUBLIC_RELEASE_CHECKLIST, VALIDATION_README):
            text = normalized(path)
            self.assertIn(RECORD.name, text, str(path))
            self.assertIn("patch `0.1.2` current-state closeout", text.lower(), str(path))
            self.assertIn("approved patch `0.1.2` evaluation surfaces are closed", text.lower(), str(path))
            self.assertIn("hosted surfaces remain blocked", text.lower(), str(path))
            self.assertIn("production positioning remains blocked", text.lower(), str(path))
            self.assertIn("public benchmark claims remain blocked", text.lower(), str(path))
            for forbidden in FORBIDDEN_CURRENT_STATUS:
                self.assertNotIn(forbidden, text, str(path))

    def test_changelog_records_narrow_boundary(self) -> None:
        text = normalized(CHANGELOG)
        self.assertIn(
            "boundary-exception: close patch `0.1.2` current status for the approved evaluation surfaces",
            text,
        )
        self.assertIn("no hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`, or `ethos-rag` boundary change", text)

    def test_release_candidate_prep_runs_current_state_after_package_tag_closeout(self) -> None:
        makefile = read(MAKEFILE)
        package_tag_guard = "$(PYTHON) .github/scripts/test_patch_0_1_2_package_tag_closeout.py"
        current_state_guard = "$(PYTHON) .github/scripts/test_patch_0_1_2_current_state_closeout.py"
        first_public_guard = "$(PYTHON) .github/scripts/test_first_public_release_artifact_evidence.py"
        block = target_block("release-candidate-prep")

        self.assertIn(current_state_guard, block)
        self.assertEqual(1, makefile.count(current_state_guard))
        self.assertLess(block.index(package_tag_guard), block.index(current_state_guard))
        self.assertLess(block.index(current_state_guard), block.index(first_public_guard))


if __name__ == "__main__":
    unittest.main()
