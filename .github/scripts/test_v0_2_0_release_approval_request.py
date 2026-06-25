#!/usr/bin/env python3
#
# Copyright 2026 The Ethos maintainers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from __future__ import annotations

import re
import unittest
from pathlib import Path

from makefile_guard import target_block
from validation_record_source import assert_record_source_binding


ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "docs/validation/v0-2-0-release-approval-request-validation-2026-06-25.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"
RELEASE_PREP = ROOT / "docs/v0-2-0-release-prep.md"
MAKEFILE = ROOT / "Makefile"

SOURCE_SHORT = "fa15fa6"
SOURCE_COMMIT = "fa15fa6f60993e30aa90540526903e4eb72c8252"
SOURCE_TREE = "983f484ff1249ee3ea88da79ebafa9d2cd2410f5"
CURRENT_VERSION = "0.1.2"
TARGET_VERSION = "0.2.0"
CRATES = ("ethos-doc-core", "ethos-verify", "ethos-pdf")
PACKAGE_TAGS = (
    "ethos-package-ethos-doc-core-0.2.0",
    "ethos-package-ethos-verify-0.2.0",
    "ethos-package-ethos-pdf-0.2.0",
)
REQUIRED_REQUEST_FIELDS = (
    "exact source commit requested",
    "version-bump plan requested",
    "explicit `ethos-pdf` continuity decision requested",
    "Python decision requested",
    "npm `@docushell/ethos-pdf` fate requested",
    "CLI artifact decision requested",
    "Tag and package-tag approval requested",
    "ADR-0006/name ownership confirmation requested",
    "`reserved_crates_io_version` handling requested",
    "crates.io append-only risk accepted for review",
    "Operator requested",
    "Closeout owner requested",
    "Retained Blockers",
)
FORBIDDEN_APPROVALS = (
    "version bump approved",
    "release-candidate branch approved",
    "cargo publish approved",
    "pypi upload approved",
    "npm publish approved",
    "github release approved",
    "tag creation approved",
    "installable 0.2.0 wording approved",
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


class V020ReleaseApprovalRequestTests(unittest.TestCase):
    def test_request_record_is_source_bound_and_indexed(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)

        assert_record_source_binding(
            self,
            root=ROOT,
            raw_record=raw,
            normalized_record=record,
            validated_head=SOURCE_SHORT,
            source_label="v0.2.0 release approval request",
            source_commit=SOURCE_COMMIT,
            source_tree=SOURCE_TREE,
        )

        for path in (VALIDATION_README, EXECUTION_STATUS, PUBLIC_RELEASE_CHECKLIST):
            text = normalized(path)
            self.assertIn(RECORD.name, text, str(path))
            self.assertIn("v0.2.0 release approval request", text.lower(), str(path))
            self.assertIn("remain blocked", text, str(path))

    def test_request_names_every_required_decision_field(self) -> None:
        record = normalized(RECORD)
        record_lower = record.lower()

        self.assertIn(
            "Status: **v0.2.0 release approval request recorded; version bump, package publication, "
            "tag creation, artifact publication, and installable wording remain blocked**",
            record,
        )
        self.assertIn(f"Current source version baseline before approval: `{CURRENT_VERSION}`", record)
        self.assertIn(f"Requested target version after approval: `{TARGET_VERSION}`", record)
        for required in REQUIRED_REQUEST_FIELDS:
            self.assertIn(required.lower(), record_lower)
        for crate in CRATES:
            self.assertIn(f"`{crate} = {TARGET_VERSION}`", record)
        for tag in PACKAGE_TAGS:
            self.assertIn(tag, record)
        self.assertIn("release tag candidate: `v0.2.0`", record)

    def test_python_npm_cli_and_name_decisions_are_bounded(self) -> None:
        record = normalized(RECORD)

        self.assertIn("include Python `ethos-pdf==0.2.0` in public `v0.2.0` only if", record)
        self.assertIn("PyPI wheel for `ethos-pdf==0.2.0`", record)
        self.assertIn("caller-provided `ethos` CLI binary", record)
        self.assertIn("include `@docushell/ethos-pdf@0.2.0` only as a CLI binary distribution package", record)
        self.assertIn("does not approve a Node API, Node SDK, N-API binding, or WASM package", record)
        self.assertIn("prepare macOS arm64 and Linux x64 GitHub Release CLI artifacts", record)
        self.assertIn("Windows packaged artifacts remain blocked", record)
        self.assertIn("retain `docushell/ethos` as the canonical source repository", record)
        self.assertIn("`ethos-pdf` as the PyPI package/import surface `ethos_pdf`", record)

    def test_reserved_version_append_only_risk_operator_and_blockers_are_explicit(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)
        lower = record.lower()

        self.assertIn('`reserved_crates_io_version = "0.0.0-reserved.0"`', record)
        self.assertIn("keep `reserved_crates_io_version = \"0.0.0-reserved.0\"` as historical reservation metadata", record)
        self.assertIn("The real package version comes from the workspace/package version", record)
        self.assertIn("once `0.2.0` is published to crates.io, the exact version cannot be deleted or overwritten", record)
        self.assertIn("A bad publish can only be yanked", record)
        self.assertIn("Operator requested: `docushell-admin`", record)
        self.assertIn("Closeout owner requested: `docushell-admin`", record)
        self.assertIn("Explicit decider approval remains required before a release-candidate branch", record)
        self.assertIn("Installable `0.2.0` public wording remains blocked", record)

        for forbidden in FORBIDDEN_APPROVALS:
            self.assertNotIn(forbidden, lower)
        for private in PRIVATE_PATH_MARKERS:
            self.assertNotIn(private, raw)

    def test_doc_pilot_boundary_and_release_sequence_match_request(self) -> None:
        record = normalized(RECORD)
        prep = normalized(RELEASE_PREP)

        for text in (record, prep):
            self.assertIn("Evidence-Checked Answers", text)
            self.assertIn("internal/design-partner", text)
            self.assertIn("claim extraction quality", text)
            self.assertIn("non-PDF ingestion", text)
        self.assertIn("Only after registry/artifact availability and smoke evidence", prep)
        self.assertIn("Only after publication and smoke evidence", record)

    def test_request_packet_does_not_itself_perform_release_actions(self) -> None:
        record = normalized(RECORD)

        self.assertIn("This request record does not approve a version bump.", record)
        self.assertIn("This request record does not create a release-candidate branch.", record)
        self.assertIn("This request record does not approve `cargo publish`.", record)
        self.assertIn("This request record does not approve PyPI upload.", record)
        self.assertIn("This request record does not approve `npm publish`.", record)
        self.assertIn("This request record does not upload CLI artifacts.", record)
        self.assertIn("This request record does not approve installable `0.2.0` public wording.", record)

    def test_v0_2_release_prep_runs_request_guard_once_before_claims(self) -> None:
        makefile = read(MAKEFILE)
        guard = "$(PYTHON) .github/scripts/test_v0_2_0_release_approval_request.py"
        claims = "$(PYTHON) .github/scripts/claims_gate.py"
        public_claims = "$(PYTHON) .github/scripts/public_boundary_claims_gate.py"
        block = target_block("v0-2-release-prep")

        self.assertIn(guard, block)
        self.assertEqual(1, makefile.count(guard))
        self.assertLess(block.index(guard), block.index(claims))
        self.assertLess(block.index(claims), block.index(public_claims))


if __name__ == "__main__":
    unittest.main()
