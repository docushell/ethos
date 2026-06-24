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
RECORD = ROOT / "docs/validation/patch-0-1-1-crates-publication-approval-decision-validation-2026-06-24.md"
REQUEST = ROOT / "docs/validation/patch-0-1-1-crates-publication-approval-request-validation-2026-06-24.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
MAKEFILE = ROOT / "Makefile"

SOURCE_SHORT = "5de6014"
SOURCE_COMMIT = "5de6014e0fe668bac306eb2c2f5b2963ab5baf96"
SOURCE_TREE = "6fc0207e61681da6ba868772e77bcbc808c98bfb"
PACKAGE_SOURCE_COMMIT = "a0851030e28c155c12f5f966af8fa0739a536ea9"
PACKAGE_SOURCE_TREE = "0238c3f6bfd264f8803708e4a828d8352320f08f"
CRATES = ("ethos-doc-core", "ethos-verify", "ethos-pdf")
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


class Patch011CratesPublicationApprovalDecisionTests(unittest.TestCase):
    def test_decision_record_is_source_bound_and_indexed(self) -> None:
        record = normalized(RECORD)
        readme = normalized(VALIDATION_README)

        self.assertIn(RECORD.name, readme)
        self.assertIn("patch 0.1.1 crates.io publication approval decision", readme.lower())
        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Patch 0.1.1 crates publication approval decision source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Patch 0.1.1 crates publication approval decision source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_decision_accepts_exact_request_packet(self) -> None:
        record = normalized(RECORD)

        self.assertIn(REQUEST.name, record)
        self.assertIn("Decision: accept exact patch `0.1.1` crates.io publication decision packet.", record)
        self.assertIn(f"Package source commit accepted by this decision: `{PACKAGE_SOURCE_COMMIT}`", record)
        self.assertIn(f"Package source tree accepted by this decision: `{PACKAGE_SOURCE_TREE}`", record)
        for crate in CRATES:
            self.assertIn(crate, record)
            self.assertIn(f"{crate} = 0.1.1", record)
            self.assertIn(f"cargo publish --locked -p {crate}", record)
        self.assertIn("ethos-package-ethos-doc-core-0.1.1", record)
        self.assertIn("ethos-package-ethos-verify-0.1.1", record)
        self.assertIn("ethos-package-ethos-pdf-0.1.1", record)

    def test_decision_allows_only_later_operator_actions_with_boundaries(self) -> None:
        raw = read(RECORD)
        lower = normalized(RECORD).lower()
        record = normalized(RECORD)

        for expected in (
            "This decision record does not run `cargo publish`.",
            "Publication remains a separate operator action.",
            "After this decision record is merged and validation passes on merged source, an operator may run only these commands:",
            "The operator must publish `ethos-doc-core` first.",
            "The operator must wait for crates.io to report `ethos-doc-core = 0.1.1` before publishing dependent crates.",
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
        request_guard = "$(PYTHON) .github/scripts/test_patch_0_1_1_crates_publication_approval_request.py"
        decision_guard = "$(PYTHON) .github/scripts/test_patch_0_1_1_crates_publication_approval_decision.py"

        self.assertIn(decision_guard, makefile)
        self.assertEqual(1, makefile.count(decision_guard))
        self.assertLess(makefile.index(request_guard), makefile.index(decision_guard))
        self.assertLess(
            makefile.index(decision_guard),
            makefile.index("$(PYTHON) .github/scripts/test_pdfium_manual_setup_contract.py"),
        )


if __name__ == "__main__":
    unittest.main()
