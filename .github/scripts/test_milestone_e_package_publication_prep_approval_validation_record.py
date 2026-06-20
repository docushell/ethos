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


ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "docs/validation/milestone-e-package-publication-prep-approval-validation-2026-06-20.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"

EXPECTED_WORDING = (
    "Ethos crate publication is in internal preparation only and remains blocked for public "
    "installation. No Ethos crates are published; the reserved crates.io names remain "
    "0.0.0-reserved.0 placeholders with no public API. Wheels, npm packages, binaries, hosted "
    "surfaces, production positioning, and public benchmark claims remain blocked."
)
EXPECTED_RESERVED_CRATES = [
    "ethos-doc-core",
    "ethos-doc",
    "ethos-verify",
    "ethos-rag",
    "ethos-pdf",
]
FORBIDDEN_RECORD_WORDING = [
    "public reports are approved",
    "public result wording approved",
    "release-ready",
    "release artifact approved",
    "package-ready",
    "package publication approved",
    "packages are published",
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
    "complete demo plan",
    "broad demo approved",
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


class MilestoneEPackagePublicationPrepApprovalValidationRecordTests(unittest.TestCase):
    def test_record_is_indexed(self) -> None:
        text = read(VALIDATION_README)
        normalized_readme = re.sub(r"\s+", " ", text)

        self.assertIn(RECORD.name, text)
        self.assertIn("package publication prep approval validation", normalized_readme)

    def test_record_names_decision_and_exact_wording(self) -> None:
        text = normalized(RECORD)

        self.assertIn("Validated source HEAD before this record: `f93508e`", text)
        self.assertIn("Status: **pass for package publication prep approval validation**", text)
        self.assertIn("Decision: approve package publication prep only", text)
        self.assertIn(EXPECTED_WORDING, text)
        self.assertIn("Package publication remains blocked", text)
        self.assertIn("No real-version cargo publish is approved", text)

    def test_record_names_exact_reserved_crate_surface(self) -> None:
        text = read(RECORD)
        normalized_record = re.sub(r"\s+", " ", text)

        for crate in EXPECTED_RESERVED_CRATES:
            self.assertIn(f"`{crate}`", text)
        self.assertIn("Reserved version: `0.0.0-reserved.0`", text)
        self.assertIn("ethos-doc-core` maps to the in-tree `ethos-core` crate", normalized_record)
        self.assertIn("ethos-doc` has no in-tree workspace member yet", normalized_record)
        self.assertIn("ethos-verify` maps to `crates/ethos-verify`", normalized_record)
        self.assertIn("ethos-rag` has no in-tree workspace member yet", normalized_record)
        self.assertIn("ethos-pdf` maps to `crates/ethos-pdf`", normalized_record)

    def test_record_names_evidence_review_status(self) -> None:
        text = normalized(RECORD)

        self.assertIn("Package inventory: reviewed", text)
        self.assertIn("Package metadata/license/README review: not reviewed", text)
        self.assertIn("Install/build smoke path: not reviewed for packaged publication", text)
        self.assertIn("Version/tag policy: not ratified", text)
        self.assertIn("PDFium packaging boundary: reviewed as caller-provided PDFium only", text)
        self.assertIn("Public-surface posture check: required after exact wording changes", text)
        self.assertIn("Claims gate after exact wording changes: required after exact wording changes", text)
        self.assertIn("Decider signoff: docushell-admin approved the exact prep wording", text)

    def test_record_names_pdfium_and_blocked_boundaries(self) -> None:
        text = normalized(RECORD)

        self.assertIn("ethos-pdf` prep must bundle no PDFium binary", text)
        self.assertIn("ethos-pdf` prep must expose no PDFium types in public API", text)
        self.assertIn("ETHOS_PDFIUM_LIBRARY_PATH", text)
        self.assertIn("ethos-pdf` remains held out of the first crate surface", text)
        self.assertIn("Real-version cargo publish remains blocked", text)
        self.assertIn("Public installation from crates.io remains blocked", text)
        self.assertIn("Release artifacts remain blocked", text)
        self.assertIn("Binaries remain blocked", text)
        self.assertIn("Wheels remain blocked", text)
        self.assertIn("npm packages remain blocked", text)
        self.assertIn("Hosted surfaces remain blocked", text)
        self.assertIn("Production positioning remains blocked", text)
        self.assertIn("Public benchmark reports remain blocked", text)
        self.assertIn("Public benchmark claims remain blocked", text)
        self.assertIn("Project-maintained PDFium builds remain blocked", text)

    def test_record_names_validation_commands(self) -> None:
        text = read(RECORD)

        self.assertIn("python3 .github/scripts/test_milestone_e_package_publication_approval_prep.py", text)
        self.assertIn(
            "python3 .github/scripts/test_milestone_e_package_publication_prep_approval_validation_record.py",
            text,
        )
        self.assertIn("python3 .github/scripts/test_milestone_e_public_approval_lane_blockers.py", text)
        self.assertIn("python3 .github/scripts/test_public_surface_posture.py", text)
        self.assertIn("python3 .github/scripts/claims_gate.py", text)
        self.assertIn("cargo build --locked -p ethos-cli", text)
        self.assertIn("make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python", text)
        self.assertIn("git diff --check", text)

    def test_make_target_and_ci_run_record_guard_in_order(self) -> None:
        make_block = target_block("milestone-e-prep")
        ci = read(CI_WORKFLOW)
        package_guard = "test_milestone_e_package_publication_approval_prep.py"
        old_record_guard = "test_milestone_e_package_publication_approval_prep_validation_record.py"
        approval_record_guard = (
            "test_milestone_e_package_publication_prep_approval_validation_record.py"
        )
        index_guard = "test_milestone_e_validation_record_index.py"

        for text, prefix in ((make_block, "$(PYTHON) .github/scripts/"), (ci, "python3 .github/scripts/")):
            self.assertIn(prefix + approval_record_guard, text)
            self.assertLess(text.index(prefix + package_guard), text.index(prefix + old_record_guard))
            self.assertLess(text.index(prefix + old_record_guard), text.index(prefix + approval_record_guard))
            self.assertLess(text.index(prefix + approval_record_guard), text.index(prefix + index_guard))

    def test_record_avoids_scope_expansion_language_and_private_paths(self) -> None:
        lower = normalized(RECORD).lower()
        raw = read(RECORD)

        for phrase in FORBIDDEN_RECORD_WORDING:
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
