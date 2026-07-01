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
RECORD = ROOT / "docs/validation/v0-3-0-publication-approval-decision-validation-2026-07-01.md"
REQUEST = ROOT / "docs/validation/v0-3-0-package-publication-approval-request-validation-2026-07-01.md"
EVIDENCE = ROOT / "docs/validation/v0-3-0-package-build-evidence-validation-2026-07-01.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"
MAKEFILE = ROOT / "Makefile"
NPM_PACKAGE = ROOT / "packages/npm/ethos-pdf/package.json"

SOURCE_SHORT = "1f6ab3c"
SOURCE_COMMIT = "1f6ab3c7294c390d87f70cde6514a02024cf964c"
SOURCE_TREE = "6541e73b597f39eea91d4d802b08823aa0bfa9a8"
REQUEST_SOURCE_COMMIT = "39cb548cf6cfe20fbcb47ee605ba51f1ebf71f6b"
EVIDENCE_SOURCE_COMMIT = "4b6d219df1757b6e4728c16c8023bee5c8cf8962"
VERSION = "0.3.0"
CRATES = ("ethos-doc-core", "ethos-verify", "ethos-pdf")
PACKAGE_TAGS = (
    "ethos-package-ethos-doc-core-0.3.0",
    "ethos-package-ethos-verify-0.3.0",
    "ethos-package-ethos-pdf-0.3.0",
)
CRATE_HASHES = (
    "7ba41a2ae299a53a4677153beaaec5ed486a07b5da08b2ef13974b9a0be141cb",
    "00f001455ca207e65aaf464551d3ba05945cda0b06e9e1036f49ac587accbb95",
    "c2f4f2ccb6de6e54cd3257597cd28e7f6dec2a6d22befbd230d2c4cf31931cfd",
)
WHEEL = "ethos_pdf-0.3.0-py3-none-any.whl"
WHEEL_SHA256 = "9eb106deafcd1d9717e5e7b67dc9413180421aba25a5257266352d09540b3265"
FORBIDDEN = (
    "crates are published",
    "published crates",
    "python package is published",
    "wheel is published",
    "github release artifacts are published",
    "npm package is published",
    "installable 0.3.0 wording approved",
    "public installation wording approved",
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


class V030PublicationApprovalDecisionTests(unittest.TestCase):
    def test_decision_record_is_source_bound_and_indexed(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)

        assert_record_source_binding(
            self,
            root=ROOT,
            raw_record=raw,
            normalized_record=record,
            validated_head=SOURCE_SHORT,
            source_label="v0.3.0 publication approval decision",
            source_commit=SOURCE_COMMIT,
            source_tree=SOURCE_TREE,
        )
        self.assertIn(REQUEST.name, record)
        self.assertIn(EVIDENCE.name, record)
        self.assertIn(REQUEST_SOURCE_COMMIT, record)
        self.assertIn(EVIDENCE_SOURCE_COMMIT, record)

        for path in (VALIDATION_README, EXECUTION_STATUS, PUBLIC_RELEASE_CHECKLIST):
            text = normalized(path)
            self.assertIn(RECORD.name, text, str(path))
            self.assertIn("v0.3.0 publication approval decision", text.lower(), str(path))
            self.assertIn("operator", text.lower(), str(path))

    def test_decision_accepts_exact_rust_and_python_package_inputs(self) -> None:
        record = normalized(RECORD)

        self.assertIn(
            "Status: **v0.3.0 publication approval decision recorded; operator publication remains pending**",
            record,
        )
        self.assertIn("Decision: accept exact v0.3.0 Rust crates.io and Python PyPI publication inputs.", record)
        for crate in CRATES:
            self.assertIn(f"`{crate} = {VERSION}`", record)
            self.assertIn(f"{crate}-0.3.0.crate", record)
            self.assertIn(f"cargo publish --locked -p {crate}", record)
        for tag in PACKAGE_TAGS:
            self.assertIn(tag, record)
        for digest in CRATE_HASHES:
            self.assertIn(digest, record)
        for expected in (
            WHEEL,
            WHEEL_SHA256,
            "SOURCE_DATE_EPOCH=0",
            "EthosCli",
            "proof_summary",
            "app_answer_release_decision",
            "Name: `ethos-pdf`",
            "Version: `0.3.0`",
            "Tag: `py3-none-any`",
        ):
            self.assertIn(expected, record)

    def test_operator_actions_are_later_bounded_and_artifact_npm_lanes_are_not_executed(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)
        lower = record.lower()

        for expected in (
            "This decision record does not run `cargo publish`.",
            "This decision record does not upload any Python distribution.",
            "Publication remains a separate operator action.",
            "After this decision record is merged and validation passes on merged source, an operator may run only these Rust commands:",
            "The operator must publish `ethos-doc-core` first.",
            "The operator must wait for crates.io to report `ethos-doc-core = 0.3.0` before publishing dependent crates.",
            "After this decision record is merged and validation passes on merged source, an operator may upload only this Python wheel:",
            "The operator must use a PyPI-approved authentication path and must not record credentials in the repository.",
            "CLI/GitHub Release artifact publication is approved only to start the v0.3.0 artifact evidence lane.",
            "npm publication is approved only to start the v0.3.0 npm alignment and vendor-refresh evidence lane.",
            "No GitHub Release artifact upload is authorized by this decision record.",
            "No `npm publish` command is authorized by this decision record.",
            "Installable `0.3.0` public wording remains blocked until registry and artifact availability closeout passes.",
            "DocuShell integration remains blocked pending closeout or explicit source-dependency integration approval.",
        ):
            self.assertIn(expected, record)
        for forbidden in FORBIDDEN:
            self.assertNotIn(forbidden, lower)
        for marker in PRIVATE_PATH_MARKERS:
            self.assertNotIn(marker, raw)

    def test_source_surface_remains_bounded_before_operator_publication(self) -> None:
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

    def test_v0_3_release_prep_runs_decision_guard_after_request_guard(self) -> None:
        makefile = read(MAKEFILE)
        block = target_block("v0-3-release-prep")
        request_guard = "$(PYTHON) .github/scripts/test_v0_3_0_package_publication_approval_request.py"
        decision_guard = "$(PYTHON) .github/scripts/test_v0_3_0_publication_approval_decision.py"
        public_surface_guard = "$(PYTHON) .github/scripts/test_public_surface_posture.py"

        self.assertIn(decision_guard, block)
        self.assertEqual(1, makefile.count(decision_guard))
        self.assertLess(block.index(request_guard), block.index(decision_guard))
        self.assertLess(block.index(decision_guard), block.index(public_surface_guard))


if __name__ == "__main__":
    unittest.main()
