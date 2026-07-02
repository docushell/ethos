#!/usr/bin/env python3
#
# Copyright 2026 The Ethos maintainers
#
# Licensed under the Apache License, Version 2.0 (the "License");
#

from __future__ import annotations

import re
import unittest
from pathlib import Path

from makefile_guard import target_block
from validation_record_source import assert_record_source_binding


ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "docs/validation/v0-3-0-npm-vendor-refresh-validation-2026-07-02.md"
ARTIFACT_CLOSEOUT = ROOT / (
    "docs/validation/v0-3-0-artifact-publication-closeout-validation-2026-07-02.md"
)
VALIDATION_README = ROOT / "docs/validation/README.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"
RELEASE_PREP = ROOT / "docs/v0-3-0-release-prep.md"
MAKEFILE = ROOT / "Makefile"

SOURCE_SHORT = "8e20db3"
SOURCE_COMMIT = "8e20db3c796f051925b059f62c294f41f981bcfa"
SOURCE_TREE = "7f528ace4993e21e457aefb5a0aa65ed40297c6c"
MACOS_ARTIFACT_SHA256 = "efb163f140bf4afffd1caeb396f79e42f484591c3e90a86810ca6c0f0c209c96"
LINUX_ARTIFACT_SHA256 = "b549ba5968e04b7679a8d3e879cd45d27f3e9a6fd226eee5c270a4e4f5c01405"
EXPECTED_FILES = {
    "LICENSE",
    "NOTICE",
    "QUICKSTART.md",
    "README.md",
    "bin/ethos-pdf.js",
    "package.json",
    "scripts/postinstall.js",
    "scripts/prepare-vendor.js",
    "vendor/ethos-darwin-arm64",
    "vendor/ethos-linux-x64",
    "vendor/manifest.json",
}
EXPECTED_VENDOR_SHA256 = {
    "vendor/ethos-darwin-arm64": "777e1fb243425a46b83b63ed92fbf7cb810f59cfedd81cfe671cf791410c20dc",
    "vendor/ethos-linux-x64": "b416993fc38e6f794611b8b71789ed85af18eb6aa63fef380d9ae7738661f154",
    "vendor/manifest.json": "e313b42e49b258171611935455fd9e70bad7ce61c409df63ab90aaa2732a46af",
}
EXPECTED_PACK_SHASUM = "1a90cebd8d52011ea5c41629becdfb37dec73ee7"
EXPECTED_PACK_SHA256 = "1b72ef2fd9415f9edff93319ee2763e8f67cd6168ea00cd64d89a3760101c5fa"
EXPECTED_PACK_INTEGRITY = (
    "sha512-ZWoIY5BO7O8tzN88ICGvRasmOt7/RSN/xWFM2ONT8lavQqIOuCY/bQjvxnuK9vGpNeogh8X4UXHLLSRKqqHVOQ=="
)
EXPECTED_NODE_VERSION = "v23.11.1"
EXPECTED_NPM_VERSION = "10.9.2"
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
    "npm publication approved",
    "npm publish approved",
    "github release artifact publication approved",
    "registry publication approved",
    "release tag creation approved",
    "package tag creation approved",
    "public installation wording approved",
    "installable 0.3.0 wording approved",
    "production-ready",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalized(path: Path) -> str:
    return re.sub(r"\s+", " ", read(path))


class V030NpmVendorRefreshTests(unittest.TestCase):
    def test_historical_record_binds_release_assets_and_vendor_payload(self) -> None:
        record = normalized(RECORD)

        for expected in (
            MACOS_ARTIFACT_SHA256,
            LINUX_ARTIFACT_SHA256,
            *EXPECTED_VENDOR_SHA256.values(),
        ):
            self.assertIn(expected, record)

    def test_historical_record_binds_pack_contents_and_checksums(self) -> None:
        record = normalized(RECORD)

        for expected in (
            "@docushell/ethos-pdf@0.3.0",
            "docushell-ethos-pdf-0.3.0.tgz",
            EXPECTED_PACK_SHASUM,
            EXPECTED_PACK_SHA256,
            EXPECTED_PACK_INTEGRITY,
            "entry count: `11`",
            "executable mode `493`",
        ):
            self.assertIn(expected, record)
        for relative_path in EXPECTED_FILES:
            self.assertIn(f"- `{relative_path}`", read(RECORD))

    def test_historical_record_retains_install_and_pdfium_smoke_evidence(self) -> None:
        record = normalized(RECORD)

        for expected in (
            "added 1 package",
            "ethos 0.3.0",
            "exit code 12",
            "darwin:arm64",
            "approved npm vendor manifest",
            "ETHOS_PDFIUM_LIBRARY_PATH is unset",
        ):
            self.assertIn(expected, record)

    def test_evidence_record_is_source_bound_indexed_and_blocked(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)
        readme = normalized(VALIDATION_README)
        execution = normalized(EXECUTION_STATUS)
        checklist = normalized(PUBLIC_RELEASE_CHECKLIST)
        release_prep = normalized(RELEASE_PREP)
        block = target_block("v0-3-release-prep")
        artifact_closeout_guard = (
            "$(PYTHON) .github/scripts/test_v0_3_0_artifact_publication_closeout.py"
        )
        scaffold_guard = "$(PYTHON) .github/scripts/test_npm_binary_package_scaffold.py"
        vendor_guard = "$(PYTHON) .github/scripts/test_v0_3_0_npm_vendor_refresh.py"
        public_surface_guard = "$(PYTHON) .github/scripts/test_public_surface_posture.py"

        assert_record_source_binding(
            self,
            root=ROOT,
            raw_record=raw,
            normalized_record=record,
            validated_head=SOURCE_SHORT,
            source_label="v0.3.0 npm vendor refresh",
            source_commit=SOURCE_COMMIT,
            source_tree=SOURCE_TREE,
        )
        for expected in (
            ARTIFACT_CLOSEOUT.name,
            MACOS_ARTIFACT_SHA256,
            LINUX_ARTIFACT_SHA256,
            EXPECTED_PACK_SHASUM,
            EXPECTED_PACK_SHA256,
            EXPECTED_PACK_INTEGRITY,
            *EXPECTED_VENDOR_SHA256.values(),
            f"Node.js: `{EXPECTED_NODE_VERSION}`",
            f"npm: `{EXPECTED_NPM_VERSION}`",
            "durable package-content provenance",
            "per-file vendor SHA256 values as the durable content binding",
            "@docushell/ethos-pdf@0.3.0",
            "ethos 0.3.0",
            "exit code 12",
            "npm publication remains blocked",
            "Public `0.3.0` install wording remains blocked",
            "current published npm package remains `@docushell/ethos-pdf@0.2.1`",
        ):
            self.assertIn(expected, record)
        for text in (readme, execution, checklist, release_prep):
            self.assertIn(RECORD.name, text)
            self.assertIn("v0.3.0 npm vendor refresh", text.lower())
            self.assertIn("npm publication", text)
            self.assertIn("blocked", text.lower())
        for forbidden in FORBIDDEN_APPROVALS:
            self.assertNotIn(forbidden, record.lower())
        for marker in PRIVATE_PATH_MARKERS:
            self.assertNotIn(marker, raw)
        self.assertIn(scaffold_guard, block)
        self.assertIn(vendor_guard, block)
        self.assertEqual(1, block.count(vendor_guard))
        self.assertLess(block.index(artifact_closeout_guard), block.index(scaffold_guard))
        self.assertLess(block.index(scaffold_guard), block.index(vendor_guard))
        self.assertLess(block.index(vendor_guard), block.index(public_surface_guard))


if __name__ == "__main__":
    unittest.main()
