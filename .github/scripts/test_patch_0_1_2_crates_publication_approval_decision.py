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
RECORD = ROOT / "docs/validation/patch-0-1-2-crates-publication-approval-decision-validation-2026-06-25.md"
REQUEST = ROOT / "docs/validation/patch-0-1-2-crates-publication-approval-request-validation-2026-06-25.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
MAKEFILE = ROOT / "Makefile"

SOURCE_SHORT = "63f6533"
SOURCE_COMMIT = "63f6533d80918cd9304bfa6cb54e7dfdc10eebfc"
SOURCE_TREE = "adc6b379d1fa74e9124e59a7ffad4ff9d22b103c"
PACKAGE_SOURCE_COMMIT = "3bc3564e38c1168b2db72f38863d324b6b57bd4d"
PACKAGE_SOURCE_TREE = "eda8c7a605a4eb29c155ae3b9e6e9f0c35798f8c"
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
    "crates are published",
    "published crates",
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


class Patch012CratesPublicationApprovalDecisionTests(unittest.TestCase):
    def test_decision_record_is_source_bound_and_indexed(self) -> None:
        record = normalized(RECORD)
        readme = normalized(VALIDATION_README)

        self.assertIn(RECORD.name, readme)
        self.assertIn("patch 0.1.2 crates.io publication approval decision", readme.lower())
        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Patch 0.1.2 crates publication approval decision source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Patch 0.1.2 crates publication approval decision source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_decision_accepts_exact_request_packet(self) -> None:
        record = normalized(RECORD)

        self.assertIn(REQUEST.name, record)
        self.assertIn("Decision: accept exact patch `0.1.2` crates.io publication decision packet.", record)
        self.assertIn(f"Package source commit accepted by this decision: `{PACKAGE_SOURCE_COMMIT}`", record)
        self.assertIn(f"Package source tree accepted by this decision: `{PACKAGE_SOURCE_TREE}`", record)
        for crate in CRATES:
            self.assertIn(crate, record)
            self.assertIn(f"{crate} = {VERSION}", record)
            self.assertIn(f"cargo publish --locked -p {crate}", record)
        for tag in TAGS:
            self.assertIn(tag, record)
        for digest in CRATE_HASHES:
            self.assertIn(digest, record)

    def test_decision_allows_only_later_operator_actions_with_boundaries(self) -> None:
        raw = read(RECORD)
        lower = normalized(RECORD).lower()
        record = normalized(RECORD)

        for expected in (
            "This decision record does not run `cargo publish`.",
            "Publication remains a separate operator action.",
            "After this decision record is merged and validation passes on merged source, an operator may run only these commands:",
            "The operator must publish `ethos-doc-core` first.",
            "The operator must wait for crates.io to report `ethos-doc-core = 0.1.2` before publishing dependent crates.",
            "Public installation wording remains blocked until registry availability is closed out.",
            "`ethos-doc` remains blocked.",
            "`ethos-rag` remains blocked.",
        ):
            self.assertIn(expected, record)
        for forbidden in FORBIDDEN:
            self.assertNotIn(forbidden, lower)
        self.assertNotIn("/Users/", raw)
        self.assertNotIn("/private/tmp", raw)
        self.assertNotIn("/var/folders", raw)
        self.assertNotIn("saumildiwaker", raw)

    def test_publish_surface_remains_limited_in_manifests(self) -> None:
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

    def test_release_candidate_prep_runs_decision_guard_after_request_guard(self) -> None:
        makefile = read(MAKEFILE)
        request_guard = "$(PYTHON) .github/scripts/test_patch_0_1_2_crates_publication_approval_request.py"
        decision_guard = "$(PYTHON) .github/scripts/test_patch_0_1_2_crates_publication_approval_decision.py"
        first_public_guard = "$(PYTHON) .github/scripts/test_first_public_release_artifact_evidence.py"
        block = target_block("release-candidate-prep")

        self.assertIn(decision_guard, block)
        self.assertEqual(1, makefile.count(decision_guard))
        self.assertLess(block.index(request_guard), block.index(decision_guard))
        self.assertLess(block.index(decision_guard), block.index(first_public_guard))


if __name__ == "__main__":
    unittest.main()
