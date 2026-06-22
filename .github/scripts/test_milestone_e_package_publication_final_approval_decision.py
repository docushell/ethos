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
import subprocess
import unittest
from pathlib import Path

from makefile_guard import target_block


ROOT = Path(__file__).resolve().parents[2]
RECORD = (
    ROOT
    / "docs/validation/"
    "milestone-e-package-publication-final-approval-decision-validation-2026-06-22.md"
)
REQUEST_RECORD = (
    "docs/validation/"
    "milestone-e-package-publication-final-approval-request-validation-2026-06-22.md"
)
REGISTRY_ASSEMBLY_RECORD = (
    "docs/validation/"
    "milestone-e-package-publication-current-registry-assembly-validation-2026-06-22.md"
)
DRY_RUN_RECORD = (
    "docs/validation/"
    "milestone-e-package-publication-current-dry-run-smoke-validation-2026-06-22.md"
)
MANIFEST_ACTIVATION_RECORD = (
    "docs/validation/"
    "milestone-e-package-publication-manifest-activation-applied-validation-2026-06-22.md"
)
VALIDATION_README = ROOT / "docs/validation/README.md"
PREP_SCOPE = ROOT / "docs/milestone-e-prep-scope.md"
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"

DECISION_SOURCE_COMMIT = "4fee88f005a9573de3c2f310ff824861768249c1"
DECISION_SOURCE_SHORT = "4fee88f"
DECISION_SOURCE_TREE = "7f801f0b5aeb51c7f79ecaac1ca19847f0cd1b61"
APPROVED_PACKAGE_SOURCE_COMMIT = "b48e2f2c7ff6f3507bbf84c6d603cf4a385b9875"
APPROVED_PACKAGE_SOURCE_TREE = "4d660bd7c1de69259d0f8c59e6ac8d1c2cb6a3a3"
EXACT_CRATES = ["ethos-doc-core", "ethos-verify", "ethos-pdf"]
EXACT_TAGS = [
    "ethos-package-ethos-doc-core-0.1.0",
    "ethos-package-ethos-verify-0.1.0",
    "ethos-package-ethos-pdf-0.1.0",
]
EXACT_PUBLIC_WORDING = (
    "Ethos Rust crates ethos-doc-core, ethos-verify, and ethos-pdf version 0.1.0 are proposed "
    "for crates.io installation only after explicit package-publication approval and package-tag "
    "creation. ethos-pdf requires caller-provided PDFium through ETHOS_PDFIUM_LIBRARY_PATH. "
    "Wheels, npm packages, binaries, hosted surfaces, production positioning, public benchmark "
    "reports, public benchmark claims, project-maintained PDFium builds, ethos-doc, and ethos-rag "
    "remain blocked."
)
REQUIRED_DECISION_FIELDS = [
    "Decision: accept exact package-publication decision packet for the bounded crates.io candidate surface.",
    "Approver: docushell-admin acting as decider.",
    "Date: 2026-06-22.",
    "Exact candidate crate list accepted by this decision: `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` only.",
    "Exact package version map accepted by this decision: `ethos-doc-core = 0.1.0`, `ethos-verify = 0.1.0`, and `ethos-pdf = 0.1.0`.",
    "Exact package tag source commit accepted by this decision: `b48e2f2c7ff6f3507bbf84c6d603cf4a385b9875`.",
    "Exact package tag source tree accepted by this decision: `4d660bd7c1de69259d0f8c59e6ac8d1c2cb6a3a3`.",
    "Exact public installation wording accepted by this decision:",
    "Publish-flag activation status: still pending a later activation change; `publish = false` remains in all three source manifests.",
    "Package tag creation status: still pending a later tag operation; no package tag is created by this decision record.",
]
FORBIDDEN_SCOPE_EXPANSION = [
    "public reports are approved",
    "public result wording approved",
    "release-ready",
    "release artifact approved",
    "package-ready",
    "packages are published",
    "published packages",
    "production-ready",
    "production positioning approved",
    "benchmark-validated",
    "public benchmark pass",
    "speed validated",
    "fastest",
    "launch-ready",
    "hosted surface approved",
    "hosted demo approved",
    "demo-ready",
    "performance validated",
    "quality validated",
    "footprint validated",
    "table-quality validated",
    "parser-quality validated",
]


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


class MilestoneEPackagePublicationFinalApprovalDecisionTests(unittest.TestCase):
    def test_decision_record_is_indexed_and_source_bound(self) -> None:
        readme = normalized(VALIDATION_README)
        record = normalized(RECORD)

        self.assertIn(RECORD.name, readme)
        self.assertIn("package publication final approval decision validation", readme)
        self.assertIn(
            f"Validated source HEAD before this record: `{DECISION_SOURCE_SHORT}`",
            read(RECORD),
        )
        self.assertIn(f"Approval decision record source commit: `{DECISION_SOURCE_COMMIT}`", record)
        self.assertIn(f"Approval decision record source tree: `{DECISION_SOURCE_TREE}`", record)
        self.assertEqual(DECISION_SOURCE_COMMIT, git("rev-parse", DECISION_SOURCE_SHORT))
        self.assertEqual(DECISION_SOURCE_TREE, git("rev-parse", f"{DECISION_SOURCE_SHORT}^{{tree}}"))

    def test_decision_accepts_exact_packet_fields(self) -> None:
        record = normalized(RECORD)

        self.assertIn(
            "Status: **pass for final package-publication approval decision with activation pending**",
            record,
        )
        for field in REQUIRED_DECISION_FIELDS:
            self.assertIn(field, record)
        for crate in EXACT_CRATES:
            self.assertIn(crate, record)
            self.assertIn(f"{crate} = 0.1.0", record)
        for tag in EXACT_TAGS:
            self.assertIn(tag, record)
        self.assertIn(EXACT_PUBLIC_WORDING, record)
        self.assertIn("`ethos-doc` remains excluded", record)
        self.assertIn("`ethos-rag` remains excluded", record)
        self.assertIn(REQUEST_RECORD, record)
        self.assertIn(REGISTRY_ASSEMBLY_RECORD, record)
        self.assertIn(DRY_RUN_RECORD, record)
        self.assertIn(MANIFEST_ACTIVATION_RECORD, record)

    def test_package_source_binding_is_real_and_unchanged(self) -> None:
        record = normalized(RECORD)

        self.assertIn(
            f"Approved package tag source commit: `{APPROVED_PACKAGE_SOURCE_COMMIT}`",
            record,
        )
        self.assertIn(
            f"Approved package tag source tree: `{APPROVED_PACKAGE_SOURCE_TREE}`",
            record,
        )
        self.assertEqual(APPROVED_PACKAGE_SOURCE_COMMIT, git("rev-parse", "b48e2f2"))
        self.assertEqual(APPROVED_PACKAGE_SOURCE_TREE, git("rev-parse", "b48e2f2^{tree}"))

    def test_decision_does_not_activate_publish_flags_tags_or_registry(self) -> None:
        for manifest in (
            ROOT / "crates/ethos-core/Cargo.toml",
            ROOT / "crates/ethos-verify/Cargo.toml",
            ROOT / "crates/ethos-pdf/Cargo.toml",
        ):
            text = read(manifest)
            self.assertNotIn("publish = false", text, str(manifest))
            self.assertIn('publication_status = "approved_for_crates_io_publication"', text, str(manifest))

        self.assertIn('name = "ethos-doc-core"', read(ROOT / "crates/ethos-core/Cargo.toml"))
        self.assertIn(
            'ethos-core = { package = "ethos-doc-core"',
            read(ROOT / "Cargo.toml"),
        )
        self.assertFalse((ROOT / ".cargo/config.toml").exists())
        self.assertFalse((ROOT / "target/package-registry").exists())

    def test_docs_reference_decision_and_retained_activation_blockers(self) -> None:
        for path in (PREP_SCOPE, ROADMAP, EXECUTION_STATUS, VALIDATION_README):
            doc = normalized(path)

            self.assertIn(RECORD.name, doc, str(path))
            self.assertIn("final approval decision", doc.lower(), str(path))
            self.assertIn("publish-flag activation remains blocked", doc.lower(), str(path))
            self.assertIn("package tag creation remains blocked", doc.lower(), str(path))
            self.assertIn("real-version cargo publish remains blocked", doc.lower(), str(path))

    def test_make_and_ci_run_decision_after_request_before_readiness(self) -> None:
        make_block = target_block("milestone-e-prep")
        ci = read(CI_WORKFLOW)
        request_guard = "test_milestone_e_package_publication_final_approval_request.py"
        decision_guard = "test_milestone_e_package_publication_final_approval_decision.py"
        readiness_guard = "test_milestone_e_public_facing_readiness_ledger.py"

        for text, prefix in ((make_block, "$(PYTHON) .github/scripts/"), (ci, "python3 .github/scripts/")):
            self.assertIn(prefix + decision_guard, text)
            self.assertEqual(1, text.count(prefix + decision_guard))
            self.assertLess(text.index(prefix + request_guard), text.index(prefix + decision_guard))
            self.assertLess(text.index(prefix + decision_guard), text.index(prefix + readiness_guard))

    def test_record_avoids_scope_expansion_language_or_private_paths(self) -> None:
        lower = normalized(RECORD).lower()
        raw = read(RECORD)

        for phrase in FORBIDDEN_SCOPE_EXPANSION:
            self.assertNotIn(phrase, lower)
        self.assertNotIn("/Users/", raw)
        self.assertNotIn("/private/tmp", raw)
        self.assertNotIn("/private/var", raw)
        self.assertNotIn("/var/folders", raw)
        self.assertNotIn("saumildiwaker", raw)
        self.assertNotIn("Desktop/Stuff", raw)
        self.assertNotIn("project/repo/ethos", raw)
        self.assertNotIn("docs/.roadmap.md.swp", raw)
        self.assertNotIn("web/", raw)


if __name__ == "__main__":
    unittest.main()
