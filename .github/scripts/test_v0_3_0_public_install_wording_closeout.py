#!/usr/bin/env python3
#
# Copyright 2026 The Ethos maintainers
#
# Licensed under the Apache License, Version 2.0 (the "License");
#

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from makefile_guard import target_block
from validation_record_source import assert_record_source_binding


ROOT = Path(__file__).resolve().parents[2]
DECISION_RECORD = ROOT / (
    "docs/validation/v0-3-0-public-install-wording-approval-decision-validation-2026-07-02.md"
)
CLOSEOUT_RECORD = ROOT / (
    "docs/validation/v0-3-0-public-install-wording-closeout-validation-2026-07-02.md"
)
REQUEST_RECORD = ROOT / (
    "docs/validation/v0-3-0-public-install-wording-approval-request-validation-2026-07-02.md"
)
VALIDATION_README = ROOT / "docs/validation/README.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"
RELEASE_PREP = ROOT / "docs/v0-3-0-release-prep.md"
README = ROOT / "README.md"
CLAIMS = ROOT / "docs/public-boundary-claims.json"
CHANGELOG = ROOT / "CHANGELOG.md"

SOURCE_SHORT = "7502658"
SOURCE_COMMIT = "750265856f352b32378ab62c72a74dd6ca72646f"
SOURCE_TREE = "0c458a91f49267aadc4240e2981305338d4793ca"
PUBLIC_SENTENCE = (
    "Ethos is a deterministic document evidence layer for source-grounded verification and "
    "citation checking across native Ethos JSON and supported foreign parser outputs. The current "
    "beta includes the GitHub source repository, Rust library crates `ethos-doc-core`, "
    "`ethos-verify`, and `ethos-pdf` at `0.3.0`, the Python `ethos-pdf` wheel at `0.3.0`, the "
    "npm `@docushell/ethos-pdf@0.3.0` package, and GitHub Release `v0.3.0` macOS arm64/Linux x64 "
    "CLI artifacts. PDFium-backed commands use caller-provided PDFium through "
    "`ETHOS_PDFIUM_LIBRARY_PATH`."
)
RUST_INSTALLS = (
    "cargo add ethos-doc-core@0.3.0",
    "cargo add ethos-verify@0.3.0",
    "cargo add ethos-pdf@0.3.0",
)
PYTHON_INSTALL = "python3 -m pip install ethos-pdf==0.3.0"
NPM_INSTALL = "npm install -g @docushell/ethos-pdf@0.3.0"
GITHUB_RELEASE = (
    "GitHub Release `v0.3.0` also provides evaluation CLI archives for macOS arm64 and Linux x64."
)
PYTHON_WRAPPER = (
    "The v0.3.0 Python wrapper includes JSON verification and evidence anchoring through that "
    "caller-provided CLI"
)
OLD_INSTALLS = (
    "cargo add ethos-doc-core@0.2.0",
    "python3 -m pip install ethos-pdf==0.2.0",
    "npm install -g @docushell/ethos-pdf@0.2.1",
    "GitHub Release `v0.2.0` also provides evaluation CLI archives",
    "npm `@docushell/ethos-pdf@0.2.0` is deprecated",
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
FORBIDDEN = (
    "hosted surfaces approved",
    "production-ready",
    "public benchmark claims approved",
    "windows packaged artifacts approved",
    "bundled pdfium approved",
    "docushell integration approved",
    "package tag creation approved",
    "release tag creation approved",
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


def claims() -> list[str]:
    return json.loads(read(CLAIMS))["surfaces"]["readme"]["claims"]


class V030PublicInstallWordingCloseoutTests(unittest.TestCase):
    def test_decision_and_closeout_records_are_source_bound(self) -> None:
        for path, label in (
            (DECISION_RECORD, "v0.3.0 public install wording approval decision"),
            (CLOSEOUT_RECORD, "v0.3.0 public install wording closeout"),
        ):
            raw = read(path)
            record = normalized(path)
            assert_record_source_binding(
                self,
                root=ROOT,
                raw_record=raw,
                normalized_record=record,
                validated_head=SOURCE_SHORT,
                source_label=label,
                source_commit=SOURCE_COMMIT,
                source_tree=SOURCE_TREE,
            )

    def test_decision_accepts_exact_wording_without_broadening_scope(self) -> None:
        raw = read(DECISION_RECORD)
        record = normalized(DECISION_RECORD)

        for expected in (
            "Decider decision supplied: **Approved**.",
            REQUEST_RECORD.name,
            PUBLIC_SENTENCE,
            *RUST_INSTALLS,
            PYTHON_INSTALL,
            NPM_INSTALL,
            GITHUB_RELEASE,
            PYTHON_WRAPPER,
            "This decision does not create package tags.",
            "This decision does not create release tags.",
            "This decision does not approve DocuShell integration.",
            "This decision does not approve hosted surfaces.",
            "This decision does not approve production positioning.",
            "This decision does not approve public benchmark claims.",
        ):
            self.assertIn(expected, record)

        for marker in PRIVATE_PATH_MARKERS:
            self.assertNotIn(marker, raw)
        for phrase in FORBIDDEN:
            self.assertNotIn(phrase, record.lower())

    def test_closeout_updates_readme_and_claim_inventory_to_exact_0_3_wording(self) -> None:
        readme = normalized_public_readme()
        claim_text = " ".join(claims())

        self.assertIn(PUBLIC_SENTENCE, readme)
        for expected in (*RUST_INSTALLS, PYTHON_INSTALL, NPM_INSTALL, GITHUB_RELEASE, PYTHON_WRAPPER):
            self.assertIn(expected, readme)
        for expected in (*RUST_INSTALLS, PYTHON_INSTALL, NPM_INSTALL, GITHUB_RELEASE):
            self.assertTrue(any(expected in claim for claim in claims()), expected)
        self.assertIn("@docushell/ethos-pdf@0.3.0", claim_text)
        self.assertIn("GitHub Release `v0.3.0` macOS arm64/Linux x64 CLI artifacts", claim_text)

        for old in OLD_INSTALLS:
            self.assertNotIn(old, readme)
            self.assertFalse(any(old in claim for claim in claims()), old)

    def test_closeout_record_is_indexed_and_status_docs_are_current(self) -> None:
        for path in (VALIDATION_README, EXECUTION_STATUS, PUBLIC_RELEASE_CHECKLIST, RELEASE_PREP):
            text = normalized(path)
            self.assertIn(DECISION_RECORD.name, text, str(path))
            self.assertIn(CLOSEOUT_RECORD.name, text, str(path))
            self.assertIn("v0.3.0 public install wording closeout", text.lower(), str(path))
            self.assertIn("approved and closed out", text.lower(), str(path))
            self.assertIn("@docushell/ethos-pdf@0.3.0", text, str(path))
            self.assertIn("GitHub Release `v0.3.0`", text, str(path))
            self.assertIn("DocuShell integration remain blocked", text, str(path))

        changelog = normalized(CHANGELOG)
        self.assertIn("close exact public `0.3.0` install wording", changelog)
        self.assertIn("approve exact public `0.3.0` install wording", changelog)

    def test_closeout_record_retains_blockers_and_path_hygiene(self) -> None:
        raw = read(CLOSEOUT_RECORD)
        record = normalized(CLOSEOUT_RECORD)

        for expected in (
            PUBLIC_SENTENCE,
            *RUST_INSTALLS,
            PYTHON_INSTALL,
            NPM_INSTALL,
            GITHUB_RELEASE,
            PYTHON_WRAPPER,
            "Package tag creation remains blocked.",
            "Release tag creation remains blocked.",
            "DocuShell integration remains blocked.",
            "Hosted surfaces remain blocked.",
            "Production positioning remains blocked.",
            "Windows packaged artifacts remain blocked.",
            "Bundled project-maintained PDFium builds remain blocked.",
            "Public benchmark claims remain blocked.",
            "`ethos-doc` remains blocked.",
            "`ethos-rag` remains blocked.",
        ):
            self.assertIn(expected, record)

        for marker in PRIVATE_PATH_MARKERS:
            self.assertNotIn(marker, raw)
        for phrase in FORBIDDEN:
            self.assertNotIn(phrase, record.lower())

    def test_release_prep_target_runs_closeout_guard_after_request_before_public_surface(self) -> None:
        block = target_block("v0-3-release-prep")
        request_guard = (
            "$(PYTHON) .github/scripts/test_v0_3_0_public_install_wording_approval_request.py"
        )
        closeout_guard = "$(PYTHON) .github/scripts/test_v0_3_0_public_install_wording_closeout.py"
        public_surface_guard = "$(PYTHON) .github/scripts/test_public_surface_posture.py"

        self.assertIn(request_guard, block)
        self.assertIn(closeout_guard, block)
        self.assertEqual(1, block.count(closeout_guard))
        self.assertLess(block.index(request_guard), block.index(closeout_guard))
        self.assertLess(block.index(closeout_guard), block.index(public_surface_guard))


if __name__ == "__main__":
    unittest.main()
