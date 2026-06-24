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
RECORD = ROOT / "docs/validation/patch-0-1-2-npm-publication-blocker-validation-2026-06-24.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
MAKEFILE = ROOT / "Makefile"

SOURCE_SHORT = "5d04c71"
SOURCE_COMMIT = "5d04c71b3f229fc08f3cae3e094cb315da286ffd"
SOURCE_TREE = "828a57c1c4448f2dbb9e44c0c4afb9418d775567"
PACKAGE = "@docushell/ethos-pdf@0.1.2"
NPM_SHASUM = "39b85d74f588666bfbf69e423a189c2039743de4"
TARBALL_SHA256 = "77cbc9c79dd60cc16073690a186e149ecbaabacce035fb0bd3603b267ce64112"
INTEGRITY = "sha512-3loga13tnAkUkjuOrjKjpA0D3Cm5lW6Al8OwTyRx7NGMt6EB4gMpZOoaSCPjZWchYv7as1uPaEnZyOqrmFOPxg=="
FORBIDDEN = (
    "0.1.2 is published",
    "npm publication closeout complete",
    "public installation wording approved",
    "production-ready",
    "hosted surfaces approved",
    "public benchmark claims approved",
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


class Patch012NpmPublicationBlockerTests(unittest.TestCase):
    def test_blocker_record_is_source_bound_and_indexed(self) -> None:
        record = normalized(RECORD)
        readme = normalized(VALIDATION_README)

        self.assertIn(RECORD.name, readme)
        self.assertIn("patch 0.1.2 npm publication blocker", readme)
        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Patch 0.1.2 npm publication blocker source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Patch 0.1.2 npm publication blocker source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_blocker_records_failed_publish_and_absent_registry_version(self) -> None:
        record = normalized(RECORD)

        for expected in (
            PACKAGE,
            "docushell-ethos-pdf-0.1.2.tgz",
            NPM_SHASUM,
            TARBALL_SHA256,
            INTEGRITY,
            "npm error code E404",
            "Not Found - PUT https://registry.npmjs.org/@docushell%2fethos-pdf",
            "npm auto-corrected",
            '"bin[ethos]" script name was cleaned',
            "0.0.0-reserved.0",
            "0.1.0",
            "0.1.1",
            "latest registry version remains `0.1.1`",
            "`@docushell/ethos-pdf@0.1.2` returned E404",
        ):
            self.assertIn(expected, record)

    def test_blocker_keeps_publication_retry_and_wording_blocked(self) -> None:
        raw = read(RECORD)
        lower = normalized(RECORD).lower()
        record = normalized(RECORD)

        for expected in (
            "Retrying `npm publish` remains blocked.",
            "Resolve npm account, authentication, or `@docushell` scope permission before any retry.",
            "Record a new approval or unblocker lane before retrying publication.",
            "Registry closeout remains blocked until `@docushell/ethos-pdf@0.1.2` is visible on npm.",
            "Public installation wording remains blocked.",
            "This record does not approve another `npm publish` attempt.",
        ):
            self.assertIn(expected, record)
        for forbidden in FORBIDDEN:
            self.assertNotIn(forbidden, lower)
        self.assertNotIn("/Users/", raw)
        self.assertNotIn("/private/tmp", raw)
        self.assertNotIn("/private/var", raw)
        self.assertNotIn("/var/folders", raw)
        self.assertNotIn("saumildiwaker", raw)

    def test_release_candidate_prep_runs_blocker_after_decision_guard(self) -> None:
        makefile = read(MAKEFILE)
        decision_guard = "$(PYTHON) .github/scripts/test_patch_0_1_2_npm_publication_approval_decision.py"
        blocker_guard = "$(PYTHON) .github/scripts/test_patch_0_1_2_npm_publication_blocker.py"
        crates_guard = "$(PYTHON) .github/scripts/test_patch_0_1_1_crates_publication_approval_request.py"

        self.assertIn(blocker_guard, makefile)
        self.assertEqual(1, makefile.count(blocker_guard))
        self.assertLess(makefile.index(decision_guard), makefile.index(blocker_guard))
        self.assertLess(makefile.index(blocker_guard), makefile.index(crates_guard))


if __name__ == "__main__":
    unittest.main()
