#!/usr/bin/env python3
#
# Copyright 2026 The Ethos maintainers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#

from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path

from makefile_guard import target_block


ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "docs/validation/v0-2-0-release-approval-decision-validation-2026-06-25.md"
REQUEST = ROOT / "docs/validation/v0-2-0-release-approval-request-validation-2026-06-25.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"
MAKEFILE = ROOT / "Makefile"

SOURCE_SHORT = "bebc3b0"
SOURCE_COMMIT = "bebc3b0a2a20fd762ad70351291222c162631eb6"
SOURCE_TREE = "90b19b657df2df50a957a991dcde7b9474e1f758"
REQUEST_SOURCE_COMMIT = "fa15fa6f60993e30aa90540526903e4eb72c8252"
REQUEST_SOURCE_TREE = "983f484ff1249ee3ea88da79ebafa9d2cd2410f5"
VERSION = "0.2.0"
CRATES = ("ethos-doc-core", "ethos-verify", "ethos-pdf")
PACKAGE_TAGS = (
    "ethos-package-ethos-doc-core-0.2.0",
    "ethos-package-ethos-verify-0.2.0",
    "ethos-package-ethos-pdf-0.2.0",
)
FORBIDDEN_APPROVALS = (
    "cargo publish approved",
    "crates are published",
    "published crates",
    "pypi upload approved",
    "npm publish approved",
    "github release approved",
    "tag creation approved",
    "installable 0.2.0 wording approved",
    "hosted surfaces approved",
    "production-ready",
    "windows packaged artifacts approved",
    "bundled pdfium approved",
    "public benchmark claims approved",
    "ethos-doc approved",
    "ethos-rag approved",
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


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args],
        cwd=ROOT,
        encoding="utf-8",
        stderr=subprocess.DEVNULL,
    ).strip()


class V020ReleaseApprovalDecisionTests(unittest.TestCase):
    def test_decision_record_is_source_bound_and_indexed(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)

        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", raw)
        self.assertIn(f"v0.2.0 release approval decision source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"v0.2.0 release approval decision source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

        for path in (VALIDATION_README, EXECUTION_STATUS, PUBLIC_RELEASE_CHECKLIST):
            text = normalized(path)
            self.assertIn(RECORD.name, text, str(path))
            self.assertIn("v0.2.0 release approval decision", text.lower(), str(path))
            self.assertIn("remain blocked", text, str(path))

    def test_decision_accepts_exact_request_packet_and_branch_instruction(self) -> None:
        record = normalized(RECORD)

        self.assertIn(REQUEST.name, record)
        self.assertIn("Decision: accept the exact `v0.2.0` release approval request packet.", record)
        self.assertIn(
            f"Approval request source commit accepted by this decision: `{REQUEST_SOURCE_COMMIT}`",
            record,
        )
        self.assertIn(
            f"Approval request source tree accepted by this decision: `{REQUEST_SOURCE_TREE}`",
            record,
        )
        self.assertIn("continue on `dev/v0-2-approval-packet` as the release-candidate working branch", record)
        self.assertIn("do not create a separate branch for this lane", record)

    def test_decision_accepts_exact_scope_without_publication(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)
        lower = record.lower()

        self.assertIn(f"Exact target version accepted by this decision: `{VERSION}`", record)
        for crate in CRATES:
            self.assertIn(f"`{crate} = {VERSION}`", record)
        for tag in PACKAGE_TAGS:
            self.assertIn(tag, record)
        self.assertIn("Python is public in `v0.2.0` only as `ethos-pdf==0.2.0`", record)
        self.assertIn("PyPI wheel", record)
        self.assertIn("caller-provided `ethos` CLI binary", record)
        self.assertIn("`@docushell/ethos-pdf@0.2.0` may remain in scope only as a CLI binary distribution package", record)
        self.assertIn("does not approve a Node API, Node SDK, N-API binding, or WASM package", record)
        self.assertIn('`reserved_crates_io_version = "0.0.0-reserved.0"`', record)
        self.assertIn("A bad publish can only be yanked", record)

        for forbidden in FORBIDDEN_APPROVALS:
            self.assertNotIn(forbidden, lower)
        for private in PRIVATE_PATH_MARKERS:
            self.assertNotIn(private, raw)

    def test_approved_candidate_work_is_version_activation_only(self) -> None:
        record = normalized(RECORD)

        for expected in (
            "bump Rust workspace/package dependency versions from `0.1.2` to `0.2.0`",
            "bump Python metadata and `ethos_pdf.__version__` from `0.1.2` to `0.2.0`",
            "bump npm `@docushell/ethos-pdf` from `0.1.2` to `0.2.0`",
            "finalize `CHANGELOG.md`",
            "update version-pinned docs to release-candidate wording, not installable wording",
        ):
            self.assertIn(expected, record)
        self.assertIn("This decision record does not run `cargo publish`.", record)
        self.assertIn("Installable `0.2.0` public wording remains blocked", record)

    def test_docushell_pilot_boundary_is_internal_only(self) -> None:
        record = normalized(RECORD)

        self.assertIn("Evidence-Checked Answers", record)
        self.assertIn("internal/design-partner", record)
        self.assertIn("claim extraction quality", record)
        self.assertIn("non-PDF ingestion", record)
        self.assertIn("does not approve hosted DocuShell surfaces", record)

    def test_v0_2_release_prep_runs_decision_guard_after_request_guard(self) -> None:
        makefile = read(MAKEFILE)
        request_guard = "$(PYTHON) .github/scripts/test_v0_2_0_release_approval_request.py"
        decision_guard = "$(PYTHON) .github/scripts/test_v0_2_0_release_approval_decision.py"
        claims = "$(PYTHON) .github/scripts/claims_gate.py"
        block = target_block("v0-2-release-prep")

        self.assertIn(decision_guard, block)
        self.assertEqual(1, makefile.count(decision_guard))
        self.assertLess(block.index(request_guard), block.index(decision_guard))
        self.assertLess(block.index(decision_guard), block.index(claims))


if __name__ == "__main__":
    unittest.main()
