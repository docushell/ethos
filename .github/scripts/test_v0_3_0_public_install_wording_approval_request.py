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
RECORD = ROOT / (
    "docs/validation/v0-3-0-public-install-wording-approval-request-validation-2026-07-02.md"
)
PUBLICATION_CLOSEOUT = ROOT / "docs/validation/v0-3-0-publication-closeout-validation-2026-07-01.md"
ARTIFACT_CLOSEOUT = ROOT / (
    "docs/validation/v0-3-0-artifact-publication-closeout-validation-2026-07-02.md"
)
NPM_CLOSEOUT = ROOT / (
    "docs/validation/v0-3-0-npm-publication-closeout-validation-2026-07-02.md"
)
VALIDATION_README = ROOT / "docs/validation/README.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"
RELEASE_PREP = ROOT / "docs/v0-3-0-release-prep.md"
README = ROOT / "README.md"
CLAIMS = ROOT / "docs/public-boundary-claims.json"
CHANGELOG = ROOT / "CHANGELOG.md"

SOURCE_SHORT = "7ad3521"
SOURCE_COMMIT = "7ad3521623764557edccbb563ef3bd279d046cc5"
SOURCE_TREE = "1471f4c7ecfc0aa84439042994be161bd97e1f4e"
PROPOSED_PUBLIC_SENTENCE = (
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
CURRENT_RUST_INSTALLS = (
    "cargo add ethos-doc-core@0.2.0",
    "cargo add ethos-verify@0.2.0",
    "cargo add ethos-pdf@0.2.0",
)
CURRENT_PYTHON_INSTALL = "python3 -m pip install ethos-pdf==0.2.0"
CURRENT_NPM_INSTALL = "npm install -g @docushell/ethos-pdf@0.2.1"
CURRENT_RELEASE = "GitHub Release `v0.2.0` also provides evaluation CLI archives"
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
    "public installation wording approved",
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


class V030PublicInstallWordingApprovalRequestTests(unittest.TestCase):
    def test_request_record_is_source_bound(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)

        assert_record_source_binding(
            self,
            root=ROOT,
            raw_record=raw,
            normalized_record=record,
            validated_head=SOURCE_SHORT,
            source_label="v0.3.0 public install wording approval request",
            source_commit=SOURCE_COMMIT,
            source_tree=SOURCE_TREE,
        )

    def test_request_captures_exact_proposed_wording_without_flipping_docs(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)

        for expected in (
            "Status: **v0.3.0 public install wording approval request recorded; wording remains blocked**",
            PROPOSED_PUBLIC_SENTENCE,
            *RUST_INSTALLS,
            PYTHON_INSTALL,
            NPM_INSTALL,
            GITHUB_RELEASE,
            PUBLICATION_CLOSEOUT.name,
            ARTIFACT_CLOSEOUT.name,
            NPM_CLOSEOUT.name,
            "The v0.3.0 Python wrapper includes JSON verification and evidence anchoring",
            "This request does not change `README.md`",
            "This request does not change `docs/public-boundary-claims.json`",
            "Public `0.3.0` install wording remains blocked until a separate approval decision and closeout pass.",
            "PDFium-backed commands use caller-provided PDFium through `ETHOS_PDFIUM_LIBRARY_PATH`.",
        ):
            self.assertIn(expected, record)

        for marker in PRIVATE_PATH_MARKERS:
            self.assertNotIn(marker, raw)
        for phrase in FORBIDDEN:
            self.assertNotIn(phrase, record.lower())

    def test_current_public_readme_and_claims_remain_on_0_2_baseline(self) -> None:
        readme = normalized(README)
        public_status = normalized_public_readme()
        claims = json.loads(read(CLAIMS))["surfaces"]["readme"]["claims"]

        self.assertIn("Rust library crates `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` at `0.2.0`", public_status)
        self.assertIn("the Python `ethos-pdf` wheel at `0.2.0`", public_status)
        self.assertIn("the npm `@docushell/ethos-pdf@0.2.1` package", public_status)
        self.assertIn("GitHub Release `v0.2.0` macOS arm64/Linux x64 CLI artifacts", public_status)

        for expected in (*CURRENT_RUST_INSTALLS, CURRENT_PYTHON_INSTALL, CURRENT_NPM_INSTALL, CURRENT_RELEASE):
            self.assertIn(expected, readme)
            self.assertTrue(any(expected in claim for claim in claims), expected)

        for proposed in (*RUST_INSTALLS, PYTHON_INSTALL, NPM_INSTALL, GITHUB_RELEASE):
            self.assertNotIn(proposed, readme)
            self.assertFalse(any(proposed in claim for claim in claims), proposed)

    def test_request_is_indexed_and_wired_into_status_docs(self) -> None:
        for path in (
            VALIDATION_README,
            EXECUTION_STATUS,
            PUBLIC_RELEASE_CHECKLIST,
            RELEASE_PREP,
        ):
            text = normalized(path)
            self.assertIn(RECORD.name, text)
            self.assertIn("v0.3.0 public install wording approval request", text.lower())
            self.assertIn("wording remains blocked", text.lower())
            self.assertIn("0.3.0", text)
            self.assertIn("DocuShell integration remain blocked", text)

        changelog = normalized(CHANGELOG)
        self.assertIn("request decider review for exact public `0.3.0` install wording", changelog)
        self.assertIn("blocked", changelog.lower())

    def test_release_prep_target_runs_request_guard_after_npm_closeout(self) -> None:
        block = target_block("v0-3-release-prep")
        npm_closeout_guard = "$(PYTHON) .github/scripts/test_v0_3_0_npm_publication_closeout.py"
        wording_request_guard = (
            "$(PYTHON) .github/scripts/test_v0_3_0_public_install_wording_approval_request.py"
        )
        public_surface_guard = "$(PYTHON) .github/scripts/test_public_surface_posture.py"

        self.assertIn(npm_closeout_guard, block)
        self.assertIn(wording_request_guard, block)
        self.assertEqual(1, block.count(wording_request_guard))
        self.assertLess(block.index(npm_closeout_guard), block.index(wording_request_guard))
        self.assertLess(block.index(wording_request_guard), block.index(public_surface_guard))


if __name__ == "__main__":
    unittest.main()
