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
RECORD = ROOT / "docs/validation/v0-3-0-release-approval-decision-validation-2026-07-01.md"
REQUEST = ROOT / "docs/validation/app-answer-release-contract-release-prep-validation-2026-07-01.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"
MAKEFILE = ROOT / "Makefile"

SOURCE_SHORT = "57e3821"
SOURCE_COMMIT = "57e3821b63b119ee6ca8e52322ddde2fb05dde66"
SOURCE_TREE = "7fd3dd7bcd4d8b503483a06752fdc5e5cb587695"
REQUEST_SOURCE_COMMIT = "d386568ef680f36f4a395543b21d34d2b17baccb"
REQUEST_SOURCE_TREE = "5891ab9c1e2fb4a9094d3d52c59ec57630aa871f"
VERSION = "0.3.0"
CRATES = ("ethos-doc-core", "ethos-verify", "ethos-pdf")
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


class V030ReleaseApprovalDecisionTests(unittest.TestCase):
    def test_decision_record_is_source_bound_and_indexed(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)

        assert_record_source_binding(
            self,
            root=ROOT,
            raw_record=raw,
            normalized_record=record,
            validated_head=SOURCE_SHORT,
            source_label="v0.3.0 release approval decision",
            source_commit=SOURCE_COMMIT,
            source_tree=SOURCE_TREE,
        )

        for path in (VALIDATION_README, EXECUTION_STATUS, PUBLIC_RELEASE_CHECKLIST):
            text = normalized(path)
            self.assertIn(RECORD.name, text, str(path))
            self.assertIn("v0.3.0 release approval decision", text.lower(), str(path))
            self.assertIn("remain blocked", text, str(path))

    def test_decision_accepts_exact_app_answer_release_prep_packet(self) -> None:
        record = normalized(RECORD)

        self.assertIn(REQUEST.name, record)
        self.assertIn(
            "Decision: accept the exact app-answer-release contract release-prep packet for `0.3.0` "
            "release-candidate source activation.",
            record,
        )
        self.assertIn(
            f"Approval request source commit accepted by this decision: `{REQUEST_SOURCE_COMMIT}`",
            record,
        )
        self.assertIn(
            f"Approval request source tree accepted by this decision: `{REQUEST_SOURCE_TREE}`",
            record,
        )
        self.assertIn("continue on `dev/v0-3-approval-packet`", record)

    def test_decision_accepts_exact_scope_without_publication(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)
        lower = record.lower()

        self.assertIn(f"Exact target version accepted by this decision: `{VERSION}`", record)
        for crate in CRATES:
            self.assertIn(f"`{crate} = {VERSION}`", record)
        self.assertIn("VerificationReport::proof_summary()", record)
        self.assertIn("derive_app_answer_release_decision(...)", record)
        self.assertIn("`ethos-pdf==0.3.0`", record)
        self.assertIn("keep npm out of scope by default", record)
        self.assertIn("`@docushell/ethos-pdf@0.2.1` remains the current public CLI binary", record)
        self.assertIn("does not approve a Node API, Node SDK, N-API binding, WASM package", record)
        self.assertIn("keep GitHub Release CLI artifact publication out of scope by default", record)
        self.assertIn("release tag `v0.3.0` and package tags remain blocked", record)

        for forbidden in (
            "cargo publish approved",
            "crates are published",
            "pypi upload approved",
            "npm publish approved",
            "github release approved",
            "tag creation approved",
            "installable `0.3.0` public wording approved",
            "ethos verified the complete answer",
        ):
            self.assertNotIn(forbidden, lower)
        for private in PRIVATE_PATH_MARKERS:
            self.assertNotIn(private, raw)

    def test_approved_candidate_work_is_source_metadata_only(self) -> None:
        record = normalized(RECORD)

        for expected in (
            "bump Rust workspace/package dependency versions from `0.2.0` to `0.3.0`",
            "bump Python metadata and `ethos_pdf.__version__` from `0.2.0` to `0.3.0`",
            "leave npm `@docushell/ethos-pdf` metadata at `0.2.1`",
            "add `docs/v0-3-0-release-prep.md`",
            "keep public install commands on the current published `0.2.0` Rust/Python and `0.2.1` npm surfaces",
        ):
            self.assertIn(expected, record)
        self.assertIn("This decision record does not run `cargo publish`.", record)
        self.assertIn("This decision record does not approve installable `0.3.0` public wording.", record)
        self.assertIn("This decision record does not approve DocuShell integration.", record)

    def test_product_boundary_is_citation_grounding_not_answer_verification(self) -> None:
        record = normalized(RECORD)

        self.assertIn("Ethos owns citation grounding and derived proof summaries.", record)
        self.assertIn("Applications own question relevance labels.", record)
        self.assertIn("Applications own source-fact, synthesis, and unsupported-claim labels.", record)
        self.assertIn("Applications own final, review, and blocked answer-release policy.", record)
        self.assertIn("Ethos verified citation grounding.", record)
        self.assertIn("Answer relevance: direct, partial, or off-topic.", record)

    def test_v0_3_release_prep_runs_decision_guard_before_activation_guard(self) -> None:
        makefile = read(MAKEFILE)
        decision_guard = "$(PYTHON) .github/scripts/test_v0_3_0_release_approval_decision.py"
        activation_guard = "$(PYTHON) .github/scripts/test_v0_3_0_version_activation.py"
        claims = "$(PYTHON) .github/scripts/claims_gate.py"
        block = target_block("v0-3-release-prep")

        self.assertIn(decision_guard, block)
        self.assertEqual(1, makefile.count(decision_guard))
        self.assertLess(block.index(decision_guard), block.index(activation_guard))
        self.assertLess(block.index(activation_guard), block.index(claims))


if __name__ == "__main__":
    unittest.main()
