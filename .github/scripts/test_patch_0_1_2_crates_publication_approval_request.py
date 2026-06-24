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
RECORD = ROOT / "docs/validation/patch-0-1-2-crates-publication-approval-request-validation-2026-06-25.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"
MAKEFILE = ROOT / "Makefile"

SOURCE_SHORT = "3bc3564"
SOURCE_COMMIT = "3bc3564e38c1168b2db72f38863d324b6b57bd4d"
SOURCE_TREE = "eda8c7a605a4eb29c155ae3b9e6e9f0c35798f8c"
VERSION = "0.1.2"
CRATES = ("ethos-doc-core", "ethos-verify", "ethos-pdf")
TAGS = (
    "ethos-package-ethos-doc-core-0.1.2",
    "ethos-package-ethos-verify-0.1.2",
    "ethos-package-ethos-pdf-0.1.2",
)
CRATE_HASHES = (
    "471956cac567f2d328ab2538291462a0bf57e082ef40dd86d877ffaa363bb632",
    "cc4356aa24b304d2f18187d5c3a0c02f847031c1d74e2f6a902a742711d65bf4",
    "9245cf03c71802c385d65ac8539e678e513114fdbb359543ad0d1373af02b900",
)
FORBIDDEN = (
    "cargo publish approved",
    "crates are published",
    "published crates",
    "production-ready",
    "hosted surfaces approved",
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


class Patch012CratesPublicationApprovalRequestTests(unittest.TestCase):
    def test_request_record_is_source_bound_and_indexed(self) -> None:
        record = normalized(RECORD)
        validation_readme = normalized(VALIDATION_README)

        self.assertIn(RECORD.name, validation_readme)
        self.assertIn("patch 0.1.2 crates.io publication approval request", validation_readme.lower())
        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Patch 0.1.2 crates publication approval request source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Patch 0.1.2 crates publication approval request source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_request_names_exact_crates_versions_tags_and_artifacts(self) -> None:
        record = normalized(RECORD)

        self.assertIn(
            "Status: **patch 0.1.2 crates.io publication approval request recorded; cargo publish remains blocked**",
            record,
        )
        for crate in CRATES:
            self.assertIn(crate, record)
            self.assertIn(f"{crate} = {VERSION}", record)
            self.assertIn(f"{crate}-0.1.2.crate", record)
        for tag in TAGS:
            self.assertIn(tag, record)
        for digest in CRATE_HASHES:
            self.assertIn(digest, record)
        self.assertIn("cargo publish --locked -p ethos-doc-core", record)
        self.assertIn("cargo publish --locked -p ethos-verify", record)
        self.assertIn("cargo publish --locked -p ethos-pdf", record)

    def test_request_retains_publication_install_and_surface_boundaries(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)
        lower = record.lower()

        for expected in (
            "This request record does not approve `cargo publish`.",
            "Actual crates.io publication remains blocked pending explicit decider approval.",
            "Rust crate public installation wording remains blocked pending explicit decider approval, operator publication, and registry closeout.",
            "The `ethos-cli` package remains `publish = false`.",
            "`ethos-doc` remains blocked.",
            "`ethos-rag` remains blocked.",
            "PDFium remains caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`.",
        ):
            self.assertIn(expected, record)
        for forbidden in FORBIDDEN:
            self.assertNotIn(forbidden, lower)
        self.assertNotIn("/Users/", raw)
        self.assertNotIn("/private/tmp", raw)
        self.assertNotIn("/private/var", raw)
        self.assertNotIn("/var/folders", raw)
        self.assertNotIn("saumildiwaker", raw)

    def test_status_docs_reference_request_and_keep_install_baseline_split(self) -> None:
        for path in (EXECUTION_STATUS, PUBLIC_RELEASE_CHECKLIST):
            text = normalized(path)
            self.assertIn(RECORD.name, text, str(path))
            self.assertIn("0.1.2", text, str(path))
            self.assertIn("`cargo publish`", text, str(path))
            self.assertIn("remain blocked", text, str(path))
            self.assertIn("Rust crate public installation wording remains blocked", text, str(path))
            self.assertIn("Python installation remains at `ethos-pdf==0.1.1`", text, str(path))

    def test_source_manifests_keep_expected_publish_surface(self) -> None:
        for manifest in (
            ROOT / "crates/ethos-core/Cargo.toml",
            ROOT / "crates/ethos-verify/Cargo.toml",
            ROOT / "crates/ethos-pdf/Cargo.toml",
        ):
            text = read(manifest)
            self.assertNotIn("publish = false", text, str(manifest))
            self.assertIn('publication_status = "approved_for_crates_io_publication"', text, str(manifest))

        for manifest in (
            ROOT / "crates/ethos-cli/Cargo.toml",
            ROOT / "crates/ethos-layout/Cargo.toml",
            ROOT / "crates/ethos-tables/Cargo.toml",
        ):
            self.assertIn("publish = false", read(manifest), str(manifest))

    def test_release_candidate_prep_runs_request_guard_after_0_1_2_public_wording(self) -> None:
        makefile = read(MAKEFILE)
        wording_guard = "$(PYTHON) .github/scripts/test_patch_0_1_2_public_install_wording_closeout.py"
        guard = "$(PYTHON) .github/scripts/test_patch_0_1_2_crates_publication_approval_request.py"
        first_public_guard = "$(PYTHON) .github/scripts/test_first_public_release_artifact_evidence.py"
        block = target_block("release-candidate-prep")

        self.assertIn(guard, block)
        self.assertEqual(1, makefile.count(guard))
        self.assertLess(block.index(wording_guard), block.index(guard))
        self.assertLess(block.index(guard), block.index(first_public_guard))


if __name__ == "__main__":
    unittest.main()
