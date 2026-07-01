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
RECORD = ROOT / "docs/validation/v0-3-0-package-publication-approval-request-validation-2026-07-01.md"
EVIDENCE_RECORD = ROOT / "docs/validation/v0-3-0-package-build-evidence-validation-2026-07-01.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"
MAKEFILE = ROOT / "Makefile"
PYPROJECT = ROOT / "pyproject.toml"
PY_INIT = ROOT / "python/ethos_pdf/__init__.py"
NPM_PACKAGE = ROOT / "packages/npm/ethos-pdf/package.json"

SOURCE_SHORT = "39cb548"
SOURCE_COMMIT = "39cb548cf6cfe20fbcb47ee605ba51f1ebf71f6b"
SOURCE_TREE = "35076461b03ce8476cd8d73077c6f0bcaeae7dc3"
EVIDENCE_SOURCE_COMMIT = "4b6d219df1757b6e4728c16c8023bee5c8cf8962"
VERSION = "0.3.0"
CRATES = ("ethos-doc-core", "ethos-verify", "ethos-pdf")
PACKAGE_TAGS = (
    "ethos-package-ethos-doc-core-0.3.0",
    "ethos-package-ethos-verify-0.3.0",
    "ethos-package-ethos-pdf-0.3.0",
)
CRATE_HASHES = {
    "ethos-doc-core": (
        "ethos-doc-core-0.3.0.crate",
        "7ba41a2ae299a53a4677153beaaec5ed486a07b5da08b2ef13974b9a0be141cb",
    ),
    "ethos-verify": (
        "ethos-verify-0.3.0.crate",
        "00f001455ca207e65aaf464551d3ba05945cda0b06e9e1036f49ac587accbb95",
    ),
    "ethos-pdf": (
        "ethos-pdf-0.3.0.crate",
        "c2f4f2ccb6de6e54cd3257597cd28e7f6dec2a6d22befbd230d2c4cf31931cfd",
    ),
}
WHEEL = "ethos_pdf-0.3.0-py3-none-any.whl"
WHEEL_SHA256 = "9eb106deafcd1d9717e5e7b67dc9413180421aba25a5257266352d09540b3265"
FORBIDDEN = (
    "cargo publish approved",
    "crates.io publication approved",
    "pypi upload approved",
    "pypi publication approved",
    "python public installation wording approved",
    "rust crate public installation wording approved",
    "installable 0.3.0 wording approved",
    "npm publication approved",
    "github release publication approved",
    "docushell integration approved",
    "production-ready",
    "hosted surfaces approved",
    "windows packaged artifacts approved",
    "bundled pdfium approved",
    "public benchmark claims approved",
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


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalized(path: Path) -> str:
    return re.sub(r"\s+", " ", read(path))


class V030PackagePublicationApprovalRequestTests(unittest.TestCase):
    def test_request_record_is_source_bound_and_indexed(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)

        assert_record_source_binding(
            self,
            root=ROOT,
            raw_record=raw,
            normalized_record=record,
            validated_head=SOURCE_SHORT,
            source_label="v0.3.0 package publication approval request",
            source_commit=SOURCE_COMMIT,
            source_tree=SOURCE_TREE,
        )
        self.assertIn(EVIDENCE_RECORD.name, record)
        self.assertIn(EVIDENCE_SOURCE_COMMIT, record)

        for path in (VALIDATION_README, EXECUTION_STATUS, PUBLIC_RELEASE_CHECKLIST):
            text = normalized(path)
            self.assertIn(RECORD.name, text, str(path))
            self.assertIn("v0.3.0 package publication approval request", text.lower(), str(path))
            self.assertIn("remain blocked", text, str(path))

    def test_request_names_exact_crates_wheel_hashes_and_order(self) -> None:
        record = normalized(RECORD)

        self.assertIn(
            "Status: **v0.3.0 package publication approval request recorded; crates.io and PyPI publication remain blocked**",
            record,
        )
        for crate in CRATES:
            crate_file, digest = CRATE_HASHES[crate]
            self.assertIn(f"`{crate} = {VERSION}`", record)
            self.assertIn(crate_file, record)
            self.assertIn(digest, record)
        for tag in PACKAGE_TAGS:
            self.assertIn(tag, record)
        for expected in (
            WHEEL,
            WHEEL_SHA256,
            "SOURCE_DATE_EPOCH=0",
            "app_answer_release_decision",
            "proof_summary",
            "cargo publish --locked -p ethos-doc-core",
            "cargo publish --locked -p ethos-verify",
            "cargo publish --locked -p ethos-pdf",
            "Publish `ethos-doc-core` first.",
            "Publish `ethos-verify` after crates.io reports `ethos-doc-core = 0.3.0`.",
            "Publish `ethos-pdf` after crates.io reports `ethos-doc-core = 0.3.0`.",
        ):
            self.assertIn(expected, record)

    def test_request_does_not_publish_or_approve_public_wording(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)
        lower = record.lower()

        for expected in (
            "Manual action is required before any crates.io publication or PyPI upload.",
            "This request record does not approve `cargo publish`.",
            "This request record does not publish any crate.",
            "This request record does not approve PyPI upload.",
            "This request record does not upload any Python distribution.",
            "This request record does not approve installable `0.3.0` public wording.",
            "This request record does not approve `npm publish`.",
            "This request record does not approve GitHub Release artifact publication.",
            "This request record does not approve DocuShell integration.",
            "Actual crates.io publication remains blocked pending explicit decider approval.",
            "Actual PyPI upload remains blocked pending explicit decider approval.",
            "PDFium remains caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`.",
            "`ethos-doc` remains blocked.",
            "`ethos-rag` remains blocked.",
        ):
            self.assertIn(expected, record)
        for forbidden in FORBIDDEN:
            self.assertNotIn(forbidden, lower)
        for marker in PRIVATE_PATH_MARKERS:
            self.assertNotIn(marker, raw)

    def test_source_metadata_and_package_scope_remain_bounded(self) -> None:
        self.assertIn('version = "0.3.0"', read(PYPROJECT))
        self.assertIn('__version__ = "0.3.0"', read(PY_INIT))
        self.assertEqual("0.2.1", json.loads(read(NPM_PACKAGE))["version"])

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

    def test_v0_3_release_prep_runs_request_guard_after_package_evidence(self) -> None:
        makefile = read(MAKEFILE)
        block = target_block("v0-3-release-prep")
        evidence_guard = "$(PYTHON) .github/scripts/test_v0_3_0_package_build_evidence.py"
        request_guard = "$(PYTHON) .github/scripts/test_v0_3_0_package_publication_approval_request.py"
        public_surface_guard = "$(PYTHON) .github/scripts/test_public_surface_posture.py"
        claims_guard = "$(PYTHON) .github/scripts/claims_gate.py"

        self.assertIn(request_guard, block)
        self.assertEqual(1, makefile.count(request_guard))
        self.assertLess(block.index(evidence_guard), block.index(request_guard))
        self.assertLess(block.index(request_guard), block.index(public_surface_guard))
        self.assertLess(block.index(public_surface_guard), block.index(claims_guard))


if __name__ == "__main__":
    unittest.main()
