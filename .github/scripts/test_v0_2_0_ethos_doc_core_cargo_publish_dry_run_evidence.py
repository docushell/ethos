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
RECORD = ROOT / (
    "docs/validation/"
    "v0-2-0-ethos-doc-core-cargo-publish-dry-run-evidence-validation-2026-06-25.md"
)
VALIDATION_README = ROOT / "docs/validation/README.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"
MAKEFILE = ROOT / "Makefile"
GUARD_NAME = "test_v0_2_0_ethos_doc_core_cargo_publish_dry_run_evidence.py"
OLD_GUARD_NAME = "test_v0_2_0_ethos_doc_core_dry_run.py"

SOURCE_SHORT = "9ca0147"
SOURCE_COMMIT = "9ca01477a14b9addd542e7aa9c5217a1b1df6831"
SOURCE_TREE = "095ce634fa0a90e81fbc4805574d75fa4d06bb71"
CRATE_SHA256 = "de86ce74dd791b50d0722cddc878756cceabae2162f747e9e24902b88e5c7de1"
PACKAGE_FILES = (
    ".cargo_vcs_info.json",
    "Cargo.lock",
    "Cargo.toml",
    "Cargo.toml.orig",
    "NOTICE.md",
    "README.md",
    "src/c14n.rs",
    "src/codes.rs",
    "src/config.rs",
    "src/crop_element.rs",
    "src/error.rs",
    "src/evidence_anchor.rs",
    "src/fingerprint.rs",
    "src/geom.rs",
    "src/grounding.rs",
    "src/ids.rs",
    "src/lib.rs",
    "src/model.rs",
    "src/traits.rs",
    "src/verify_types.rs",
)
PRIVATE_PATH_MARKERS = (
    "/" + "Users/",
    "/" + "private/tmp",
    "/" + "private/var",
    "/" + "var/folders",
    "saumil" + "diwaker",
    "Desktop/" + "Stuff",
    "project/repo/" + "ethos",
)
FORBIDDEN_APPROVALS = (
    "cargo publish approved",
    "published crates",
    "crates are published",
    "installable 0.2.0 wording approved",
    "pypi upload approved",
    "npm publish approved",
    "github release approved",
    "tag creation approved",
    "hosted surfaces approved",
    "production-ready",
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


class V020EthosDocCoreDryRunTests(unittest.TestCase):
    def test_record_is_source_bound_and_indexed(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)

        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", raw)
        self.assertIn(f"v0.2.0 ethos-doc-core dry-run source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"v0.2.0 ethos-doc-core dry-run source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

        for path in (VALIDATION_README, EXECUTION_STATUS, PUBLIC_RELEASE_CHECKLIST):
            text = normalized(path)
            self.assertIn(RECORD.name, text, str(path))
            self.assertIn("ethos-doc-core", text, str(path))
            self.assertIn("dry-run", text.lower(), str(path))

    def test_record_captures_exact_dry_run_evidence(self) -> None:
        record = normalized(RECORD)

        self.assertIn("Status: **ethos-doc-core 0.2.0 cargo publish dry-run evidence recorded; cargo publish remains blocked**", record)
        self.assertIn("cargo publish --dry-run --locked -p ethos-doc-core", record)
        self.assertIn("Packaging ethos-doc-core v0.2.0", record)
        self.assertIn("Packaged 20 files, 162.1KiB (37.6KiB compressed)", record)
        self.assertIn("Verifying ethos-doc-core v0.2.0", record)
        self.assertIn("Compiling ethos-doc-core v0.2.0", record)
        self.assertIn("Uploading ethos-doc-core v0.2.0", record)
        self.assertIn("warning: aborting upload due to dry run", record)
        self.assertIn("RESULT: PASS (dry-run)", record)
        self.assertIn("The dry run exited `0`.", record)
        self.assertIn(CRATE_SHA256, record)
        self.assertIn(GUARD_NAME, record)
        self.assertNotIn(OLD_GUARD_NAME, record)

    def test_record_captures_package_file_list(self) -> None:
        record = read(RECORD)

        for file_name in PACKAGE_FILES:
            self.assertIn(file_name, record)
        self.assertEqual(20, len(PACKAGE_FILES))

    def test_boundaries_remain_closed_and_private_paths_absent(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)
        lower = record.lower()

        for expected in (
            "`cargo publish` remains blocked until an explicit operator publication decision is recorded.",
            "`ethos-verify` and `ethos-pdf` dry-runs remain blocked",
            "PyPI upload remains blocked.",
            "`npm publish` remains blocked.",
            "GitHub Release `v0.2.0` artifact upload remains blocked.",
            "Release tag creation remains blocked.",
            "Package tag creation remains blocked.",
            "Installable `0.2.0` public wording remains blocked.",
            "`ethos-doc` remains blocked.",
            "`ethos-rag` remains blocked.",
        ):
            self.assertIn(expected, record)
        for forbidden in FORBIDDEN_APPROVALS:
            self.assertNotIn(forbidden, lower)
        for private in PRIVATE_PATH_MARKERS:
            self.assertNotIn(private, raw)

    def test_v0_2_release_prep_runs_dry_run_guard_after_activation(self) -> None:
        makefile = read(MAKEFILE)
        activation_guard = "$(PYTHON) .github/scripts/test_v0_2_0_version_activation.py"
        dry_run_guard = f"$(PYTHON) .github/scripts/{GUARD_NAME}"
        claims = "$(PYTHON) .github/scripts/claims_gate.py"
        block = target_block("v0-2-release-prep")

        self.assertIn(dry_run_guard, block)
        self.assertEqual(1, makefile.count(dry_run_guard))
        self.assertLess(block.index(activation_guard), block.index(dry_run_guard))
        self.assertLess(block.index(dry_run_guard), block.index(claims))


if __name__ == "__main__":
    unittest.main()
