#!/usr/bin/env python3
#
# Copyright 2026 The Ethos maintainers
#
# Licensed under the Apache License, Version 2.0 (the "License");
#

from __future__ import annotations

import hashlib
import json
import re
import unittest
from pathlib import Path

from makefile_guard import target_block
from validation_record_source import assert_record_source_binding


ROOT = Path(__file__).resolve().parents[2]
PACKAGE_DIR = ROOT / "packages/npm/ethos-pdf"
PACKAGE_JSON = PACKAGE_DIR / "package.json"
VENDOR_MANIFEST = PACKAGE_DIR / "vendor/manifest.json"
RECORD = ROOT / (
    "docs/validation/v0-3-0-npm-publication-closeout-validation-2026-07-02.md"
)
APPROVAL_DECISION = ROOT / (
    "docs/validation/v0-3-0-npm-publication-approval-decision-validation-2026-07-02.md"
)
APPROVAL_REQUEST = ROOT / (
    "docs/validation/v0-3-0-npm-publication-approval-request-validation-2026-07-02.md"
)
VENDOR_RECORD = ROOT / "docs/validation/v0-3-0-npm-vendor-refresh-validation-2026-07-02.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"
RELEASE_PREP = ROOT / "docs/v0-3-0-release-prep.md"
CHANGELOG = ROOT / "CHANGELOG.md"

SOURCE_SHORT = "bb93a30"
SOURCE_COMMIT = "bb93a30140ba4d3a64faacfb3ac0bed1e4fc59b2"
SOURCE_TREE = "1e562c9604cb8e1105ff51145f8f8a9ff984c0a8"
PACKAGE = "@docushell/ethos-pdf"
VERSION = "0.3.0"
PACKAGE_VERSION = f"{PACKAGE}@{VERSION}"
PRIOR_PUBLISHED = "@docushell/ethos-pdf@0.2.1"
NPM_TARBALL = "docushell-ethos-pdf-0.3.0.tgz"
NPM_SHASUM = "1a90cebd8d52011ea5c41629becdfb37dec73ee7"
INTEGRITY = (
    "sha512-ZWoIY5BO7O8tzN88ICGvRasmOt7/RSN/xWFM2ONT8lavQqIOuCY/bQjvxnuK9vGpNeogh8X4UXHLLSRKqqHVOQ=="
)
TARBALL_URL = "https://registry.npmjs.org/@docushell/ethos-pdf/-/ethos-pdf-0.3.0.tgz"
NODE_VERSION = "v23.11.1"
NPM_VERSION = "10.9.2"
PUBLISHED_AT = "2026-07-02T12:01:02.015Z"
SIGNATURE_KEYID = "SHA256:DhQ8wR5APBvFHLF/+Tc+AYvPOdTpcIDqOhxsBHRwC7U"
SIGNATURE_SIG = (
    "MEUCIQDba2Q4kRW068MuweRo5a5Hz+vLTtgV0S02cU3xp5POtwIgWUf5YaUD1fv0dCAcRlijDgNVl+P2AjBPVG36DmZ7WDI="
)
EXPECTED_VENDOR_SHA256 = {
    "vendor/ethos-darwin-arm64": "777e1fb243425a46b83b63ed92fbf7cb810f59cfedd81cfe671cf791410c20dc",
    "vendor/ethos-linux-x64": "b416993fc38e6f794611b8b71789ed85af18eb6aa63fef380d9ae7738661f154",
    "vendor/manifest.json": "e313b42e49b258171611935455fd9e70bad7ce61c409df63ab90aaa2732a46af",
}
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
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalized(path: Path) -> str:
    return re.sub(r"\s+", " ", read(path))


class V030NpmPublicationCloseoutTests(unittest.TestCase):
    def test_closeout_record_is_source_bound(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)

        assert_record_source_binding(
            self,
            root=ROOT,
            raw_record=raw,
            normalized_record=record,
            validated_head=SOURCE_SHORT,
            source_label="v0.3.0 npm publication closeout",
            source_commit=SOURCE_COMMIT,
            source_tree=SOURCE_TREE,
        )

    def test_checked_in_candidate_matches_published_payload(self) -> None:
        self.assertEqual(VERSION, json.loads(read(PACKAGE_JSON))["version"])

        for relative_path, expected in EXPECTED_VENDOR_SHA256.items():
            self.assertEqual(expected, sha256(PACKAGE_DIR / relative_path))

        manifest = json.loads(read(VENDOR_MANIFEST))
        self.assertEqual(1, manifest["version"])
        self.assertEqual(PACKAGE, manifest["package"])
        self.assertEqual("ethos-darwin-arm64", manifest["targets"]["darwin:arm64"]["binary"])
        self.assertEqual("ethos-linux-x64", manifest["targets"]["linux:x64"]["binary"])

    def test_record_captures_publish_and_registry_evidence(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)

        for expected in (
            PACKAGE_VERSION,
            PRIOR_PUBLISHED,
            APPROVAL_DECISION.name,
            APPROVAL_REQUEST.name,
            VENDOR_RECORD.name,
            "+ @docushell/ethos-pdf@0.3.0",
            "npm auto-corrected",
            '"bin[ethos]" script name was cleaned',
            NPM_TARBALL,
            NPM_SHASUM,
            INTEGRITY,
            TARBALL_URL,
            SOURCE_COMMIT,
            f"Node.js: `{NODE_VERSION}`",
            f"npm: `{NPM_VERSION}`",
            PUBLISHED_AT,
            "Registry latest is now `0.3.0`",
            '"latest": "0.3.0"',
            '"fileCount": 11',
            '"unpackedSize": 4005888',
            SIGNATURE_KEYID,
            SIGNATURE_SIG,
            "This closeout supersedes the npm publication blocker only for the exact package and version",
            "This closeout does not run `npm pkg fix`",
            "ETHOS_PDFIUM_LIBRARY_PATH",
        ):
            self.assertIn(expected, record)

        for expected in EXPECTED_VENDOR_SHA256.values():
            self.assertIn(expected, record)
        for marker in PRIVATE_PATH_MARKERS:
            self.assertNotIn(marker, raw)
        for phrase in FORBIDDEN:
            self.assertNotIn(phrase, record.lower())

    def test_closeout_retains_public_surface_blockers(self) -> None:
        raw = read(RECORD)

        for blocker in (
            "Public `0.3.0` install wording remains blocked.",
            "package tag creation remains blocked.",
            "release tag creation remains blocked.",
            "DocuShell integration remains blocked.",
            "hosted surfaces remain blocked.",
            "production positioning remains blocked.",
            "public benchmark reports remain blocked.",
            "public benchmark claims remain blocked.",
            "Windows packaged artifacts remain blocked.",
            "bundled project-maintained PDFium builds remain blocked.",
            "`ethos-doc` remains blocked.",
            "`ethos-rag` remains blocked.",
        ):
            self.assertIn(blocker, raw)

    def test_closeout_is_indexed_and_wired_into_status_docs(self) -> None:
        for path in (
            VALIDATION_README,
            EXECUTION_STATUS,
            PUBLIC_RELEASE_CHECKLIST,
            RELEASE_PREP,
        ):
            text = normalized(path)
            self.assertIn(RECORD.name, text)
            self.assertIn("v0.3.0 npm publication closeout", text.lower())
            self.assertIn(PACKAGE_VERSION, text)
            self.assertIn("Public `0.3.0` install wording", text)
            self.assertIn("DocuShell integration remain blocked", text)

        changelog = normalized(CHANGELOG)
        self.assertIn("close exact `@docushell/ethos-pdf@0.3.0` npm publication", changelog)
        self.assertIn("live registry evidence", changelog)
        self.assertIn("blocked", changelog.lower())

    def test_release_prep_target_runs_closeout_guard_after_decision_guard(self) -> None:
        block = target_block("v0-3-release-prep")
        decision_guard = (
            "$(PYTHON) .github/scripts/test_v0_3_0_npm_publication_approval_decision.py"
        )
        closeout_guard = "$(PYTHON) .github/scripts/test_v0_3_0_npm_publication_closeout.py"
        public_surface_guard = "$(PYTHON) .github/scripts/test_public_surface_posture.py"

        self.assertIn(decision_guard, block)
        self.assertIn(closeout_guard, block)
        self.assertEqual(1, block.count(closeout_guard))
        self.assertLess(block.index(decision_guard), block.index(closeout_guard))
        self.assertLess(block.index(closeout_guard), block.index(public_surface_guard))


if __name__ == "__main__":
    unittest.main()
