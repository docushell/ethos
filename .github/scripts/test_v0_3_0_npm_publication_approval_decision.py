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
    "docs/validation/v0-3-0-npm-publication-approval-decision-validation-2026-07-02.md"
)
REQUEST_RECORD = ROOT / (
    "docs/validation/v0-3-0-npm-publication-approval-request-validation-2026-07-02.md"
)
VENDOR_RECORD = ROOT / "docs/validation/v0-3-0-npm-vendor-refresh-validation-2026-07-02.md"
ARTIFACT_CLOSEOUT = ROOT / (
    "docs/validation/v0-3-0-artifact-publication-closeout-validation-2026-07-02.md"
)
VALIDATION_README = ROOT / "docs/validation/README.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"
RELEASE_PREP = ROOT / "docs/v0-3-0-release-prep.md"
CHANGELOG = ROOT / "CHANGELOG.md"

SOURCE_SHORT = "5262d4f"
SOURCE_COMMIT = "5262d4f736f5fa52fd14990c11b535768085ede6"
SOURCE_TREE = "f942e215a6aa35cec96d8ff3958958d07b77b41f"
PACKAGE = "@docushell/ethos-pdf@0.3.0"
CURRENT_PUBLISHED = "@docushell/ethos-pdf@0.2.1"
NPM_TARBALL = "docushell-ethos-pdf-0.3.0.tgz"
NPM_SHASUM = "1a90cebd8d52011ea5c41629becdfb37dec73ee7"
TARBALL_SHA256 = "1b72ef2fd9415f9edff93319ee2763e8f67cd6168ea00cd64d89a3760101c5fa"
INTEGRITY = (
    "sha512-ZWoIY5BO7O8tzN88ICGvRasmOt7/RSN/xWFM2ONT8lavQqIOuCY/bQjvxnuK9vGpNeogh8X4UXHLLSRKqqHVOQ=="
)
NODE_VERSION = "v23.11.1"
NPM_VERSION = "10.9.2"
MACOS_ARTIFACT_SHA256 = "efb163f140bf4afffd1caeb396f79e42f484591c3e90a86810ca6c0f0c209c96"
LINUX_ARTIFACT_SHA256 = "b549ba5968e04b7679a8d3e879cd45d27f3e9a6fd226eee5c270a4e4f5c01405"
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
    "package is published",
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


class V030NpmPublicationApprovalDecisionTests(unittest.TestCase):
    def test_decision_record_is_source_bound(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)

        assert_record_source_binding(
            self,
            root=ROOT,
            raw_record=raw,
            normalized_record=record,
            validated_head=SOURCE_SHORT,
            source_label="v0.3.0 npm publication approval decision",
            source_commit=SOURCE_COMMIT,
            source_tree=SOURCE_TREE,
        )

    def test_checked_in_candidate_matches_exact_decision(self) -> None:
        self.assertEqual("0.3.0", json.loads(read(PACKAGE_JSON))["version"])

        for relative_path, expected in EXPECTED_VENDOR_SHA256.items():
            self.assertEqual(expected, sha256(PACKAGE_DIR / relative_path))

        manifest = json.loads(read(VENDOR_MANIFEST))
        self.assertEqual(MACOS_ARTIFACT_SHA256, manifest["targets"]["darwin:arm64"]["release_asset_sha256"])
        self.assertEqual(LINUX_ARTIFACT_SHA256, manifest["targets"]["linux:x64"]["release_asset_sha256"])

    def test_decision_accepts_exact_bounded_npm_candidate(self) -> None:
        record = normalized(RECORD)
        raw = read(RECORD)

        for expected in (
            PACKAGE,
            CURRENT_PUBLISHED,
            NPM_TARBALL,
            NPM_SHASUM,
            TARBALL_SHA256,
            INTEGRITY,
            f"Node.js: `{NODE_VERSION}`",
            f"npm: `{NPM_VERSION}`",
            REQUEST_RECORD.name,
            VENDOR_RECORD.name,
            ARTIFACT_CLOSEOUT.name,
            "Decider decision supplied: Approved",
            "per-file vendor SHA256 values are the durable cross-toolchain provenance binding",
            "Approved Operator Action",
            "operator may run `npm publish` for the exact `@docushell/ethos-pdf@0.3.0`",
            "This decision does not itself execute `npm publish`",
            "publication remains an explicit later operator action",
            "npm credentials authorized for the `@docushell` scope",
            "Exact installed CLI smoke accepted by this decision: `ethos 0.3.0`",
            "Exact missing-PDFium behavior accepted by this decision: exit code `12`",
            "ETHOS_PDFIUM_LIBRARY_PATH",
        ):
            self.assertIn(expected, record)

        for expected in (
            MACOS_ARTIFACT_SHA256,
            LINUX_ARTIFACT_SHA256,
            *EXPECTED_VENDOR_SHA256.values(),
        ):
            self.assertIn(expected, record)

        for marker in PRIVATE_PATH_MARKERS:
            self.assertNotIn(marker, raw)
        for phrase in FORBIDDEN:
            self.assertNotIn(phrase, record.lower())

    def test_decision_retains_post_publish_and_public_surface_blockers(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)

        for expected in (
            "Public `0.3.0` installation wording remains blocked",
            "registry closeout remains blocked until registry evidence is recorded after publication",
            "package tag creation remains blocked",
            "release tag creation remains blocked",
            "DocuShell integration remains blocked",
            "hosted surfaces remain blocked",
            "production positioning remains blocked",
            "public benchmark reports remain blocked",
            "public benchmark claims remain blocked",
            "Windows packaged artifacts remain blocked",
            "bundled project-maintained PDFium builds remain blocked",
            "`ethos-doc` remains blocked",
            "`ethos-rag` remains blocked",
        ):
            self.assertIn(expected, raw)
        self.assertIn("The operator must stop if", record)
        self.assertIn("the registry already reports `0.3.0` before publish", record)

    def test_decision_is_indexed_and_wired_into_status_docs(self) -> None:
        for path in (
            VALIDATION_README,
            EXECUTION_STATUS,
            PUBLIC_RELEASE_CHECKLIST,
            RELEASE_PREP,
        ):
            text = normalized(path)
            self.assertIn(RECORD.name, text)
            self.assertIn("v0.3.0 npm publication approval decision", text.lower())
            self.assertIn("operator publish remains pending", text)

        changelog = normalized(CHANGELOG)
        self.assertIn("approve exact `@docushell/ethos-pdf@0.3.0` npm publication", changelog)
        self.assertIn("operator action", changelog)
        self.assertIn("blocked", changelog.lower())

    def test_release_prep_target_runs_decision_guard_after_request_guard(self) -> None:
        block = target_block("v0-3-release-prep")
        request_guard = (
            "$(PYTHON) .github/scripts/test_v0_3_0_npm_publication_approval_request.py"
        )
        decision_guard = (
            "$(PYTHON) .github/scripts/test_v0_3_0_npm_publication_approval_decision.py"
        )
        public_surface_guard = "$(PYTHON) .github/scripts/test_public_surface_posture.py"

        self.assertIn(request_guard, block)
        self.assertIn(decision_guard, block)
        self.assertEqual(1, block.count(decision_guard))
        self.assertLess(block.index(request_guard), block.index(decision_guard))
        self.assertLess(block.index(decision_guard), block.index(public_surface_guard))


if __name__ == "__main__":
    unittest.main()
