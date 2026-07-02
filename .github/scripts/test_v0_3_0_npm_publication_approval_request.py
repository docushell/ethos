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
MAKEFILE = ROOT / "Makefile"

SOURCE_SHORT = "161645d"
SOURCE_COMMIT = "161645d7d3b5564cc4fafff411de07631616acca"
SOURCE_TREE = "3f872c9ff0685bcf6f95e8e05f9530f852b0bd98"
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
    "npm publish is approved",
    "npm publication approved",
    "operator publish approved",
    "package is published",
    "public installation wording approved",
    "hosted surfaces approved",
    "production-ready",
    "public benchmark claims approved",
    "windows packaged artifacts approved",
    "bundled pdfium approved",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalized(path: Path) -> str:
    return re.sub(r"\s+", " ", read(path))


class V030NpmPublicationApprovalRequestTests(unittest.TestCase):
    def test_request_record_is_source_bound(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)

        assert_record_source_binding(
            self,
            root=ROOT,
            raw_record=raw,
            normalized_record=record,
            validated_head=SOURCE_SHORT,
            source_label="v0.3.0 npm publication approval request",
            source_commit=SOURCE_COMMIT,
            source_tree=SOURCE_TREE,
        )

    def test_checked_in_candidate_matches_exact_request(self) -> None:
        self.assertEqual("0.3.0", json.loads(read(PACKAGE_JSON))["version"])

        for relative_path, expected in EXPECTED_VENDOR_SHA256.items():
            self.assertEqual(expected, sha256(PACKAGE_DIR / relative_path))

        manifest = json.loads(read(VENDOR_MANIFEST))
        self.assertEqual(MACOS_ARTIFACT_SHA256, manifest["targets"]["darwin:arm64"]["release_asset_sha256"])
        self.assertEqual(LINUX_ARTIFACT_SHA256, manifest["targets"]["linux:x64"]["release_asset_sha256"])

    def test_request_names_exact_candidate_and_boundaries(self) -> None:
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
            VENDOR_RECORD.name,
            ARTIFACT_CLOSEOUT.name,
            "per-file vendor SHA256 values are the durable cross-toolchain provenance binding",
            "Publication must use Node.js `v23.11.1` and npm `10.9.2`",
            "Exact installed CLI smoke accepted for request: `ethos 0.3.0`",
            "Exact missing-PDFium behavior accepted for request: exit code `12`",
            "ETHOS_PDFIUM_LIBRARY_PATH",
            "No `npm publish` command is approved by this request record.",
            "npm publication remains blocked pending explicit decider approval.",
            "Actual npm publish remains blocked pending explicit operator action",
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

    def test_request_is_indexed_and_wired_into_status_docs(self) -> None:
        for path in (
            VALIDATION_README,
            EXECUTION_STATUS,
            PUBLIC_RELEASE_CHECKLIST,
            RELEASE_PREP,
        ):
            text = normalized(path)
            self.assertIn(RECORD.name, text)
            self.assertIn("v0.3.0 npm publication approval request", text.lower())
            self.assertIn("npm publish", text)
            self.assertIn("blocked", text.lower())

        changelog = normalized(CHANGELOG)
        self.assertIn("request decider review for exact `@docushell/ethos-pdf@0.3.0`", changelog)
        self.assertIn("npm publication inputs", changelog)
        self.assertIn("blocked", changelog.lower())

    def test_release_prep_target_runs_request_guard_after_vendor_refresh(self) -> None:
        block = target_block("v0-3-release-prep")
        vendor_guard = "$(PYTHON) .github/scripts/test_v0_3_0_npm_vendor_refresh.py"
        request_guard = (
            "$(PYTHON) .github/scripts/test_v0_3_0_npm_publication_approval_request.py"
        )
        public_surface_guard = "$(PYTHON) .github/scripts/test_public_surface_posture.py"

        self.assertIn(vendor_guard, block)
        self.assertIn(request_guard, block)
        self.assertEqual(1, block.count(request_guard))
        self.assertLess(block.index(vendor_guard), block.index(request_guard))
        self.assertLess(block.index(request_guard), block.index(public_surface_guard))


if __name__ == "__main__":
    unittest.main()
