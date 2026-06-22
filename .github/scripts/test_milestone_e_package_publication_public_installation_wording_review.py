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

import json
import re
import subprocess
import unittest
from pathlib import Path

from makefile_guard import target_block


ROOT = Path(__file__).resolve().parents[2]
PREP = ROOT / "docs/milestone-e-package-publication-approval-prep.json"
RECORD = (
    ROOT
    / "docs/validation/"
    "milestone-e-package-publication-public-installation-wording-review-validation-2026-06-21.md"
)
VALIDATION_README = ROOT / "docs/validation/README.md"
PREP_SCOPE = ROOT / "docs/milestone-e-prep-scope.md"
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"

SOURCE_COMMIT = "8b446e3554c9b4b223e43ee46d218c47a7931c76"
SOURCE_SHORT = "8b446e3"
SOURCE_TREE = "385dd7799cf898fc850555ce13d6d74e8ee15196"
EXPECTED_CANDIDATE_WORDING = (
    "Ethos Rust crates are proposed for crates.io installation after dedicated package-publication "
    "approval. The first candidate crate surface is limited to ethos-doc-core, ethos-verify, and "
    "ethos-pdf. Wheels, npm packages, binaries, hosted surfaces, production positioning, public "
    "benchmark reports, public benchmark claims, release artifacts, project-maintained PDFium "
    "builds, ethos-doc, and ethos-rag remain excluded."
)
FORBIDDEN_SCOPE_EXPANSION = [
    "public reports are approved",
    "public result wording approved",
    "release-ready",
    "release artifact approved",
    "package-ready",
    "package publication is approved",
    "package publication approved",
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


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args],
        cwd=ROOT,
        encoding="utf-8",
        stderr=subprocess.DEVNULL,
    ).strip()


class MilestoneEPackagePublicationPublicInstallationWordingReviewTests(unittest.TestCase):
    def test_wording_review_record_is_indexed_and_source_bound(self) -> None:
        prep = load_json(PREP)
        readme = read(VALIDATION_README)
        record = normalized(RECORD)

        self.assertIn(RECORD.name, readme)
        self.assertIn("package publication public installation wording review validation", readme)
        self.assertEqual(
            "docs/validation/"
            "milestone-e-package-publication-public-installation-wording-review-validation-2026-06-21.md",
            prep["follow_up_records"]["package_public_installation_wording_review"],
        )
        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Public installation wording review source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Public installation wording review source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_candidate_wording_is_review_only_and_exclusion_bound(self) -> None:
        record = normalized(RECORD)
        lower_record = record.lower()

        self.assertIn(EXPECTED_CANDIDATE_WORDING, record)
        self.assertIn("This candidate wording is not approved public wording", record)
        self.assertIn("No public installation wording is approved by this record", record)
        self.assertIn("Public installation remains blocked", record)
        self.assertIn("Package publication remains blocked", record)
        for included in ("ethos-doc-core", "ethos-verify", "ethos-pdf"):
            self.assertIn(included, record)
        for excluded in (
            "wheels",
            "npm packages",
            "binaries",
            "hosted surfaces",
            "production positioning",
            "public benchmark reports",
            "public benchmark claims",
            "release artifacts",
            "project-maintained PDFium builds",
            "ethos-doc",
            "ethos-rag",
        ):
            self.assertIn(excluded.lower(), lower_record)
        self.assertIn("public-surface posture check after exact public installation wording changes remains required", record)
        self.assertIn("claims gate after exact public installation wording changes remains required", record)

    def test_current_manifests_tags_and_registry_state_stay_unactivated(self) -> None:
        packet = load_json(PREP)["package_publication_decision_input_packet"]
        core_manifest = read(ROOT / "crates/ethos-core/Cargo.toml")
        verify_manifest = read(ROOT / "crates/ethos-verify/Cargo.toml")
        pdf_manifest = read(ROOT / "crates/ethos-pdf/Cargo.toml")

        for value in packet["candidate_package_tag_names"]:
            tag = value.split(": ", maxsplit=1)[1].split(";", maxsplit=1)[0]
            self.assertEqual("", git("tag", "--list", tag))
        self.assertIn('name = "ethos-doc-core"', core_manifest)
        self.assertNotIn("publish = false", core_manifest)
        self.assertNotIn("publish = false", verify_manifest)
        self.assertNotIn("publish = false", pdf_manifest)
        self.assertNotIn('package = "ethos-doc-core"', verify_manifest)
        self.assertNotIn('package = "ethos-doc-core"', pdf_manifest)
        self.assertFalse((ROOT / ".cargo/config.toml").exists())
        self.assertFalse((ROOT / "target/package-registry").exists())

    def test_docs_reference_wording_review_and_retained_blockers(self) -> None:
        for path in (PREP_SCOPE, ROADMAP, EXECUTION_STATUS, VALIDATION_README):
            doc = normalized(path)

            self.assertIn(RECORD.name, doc, str(path))
            self.assertIn("public installation wording review", doc.lower(), str(path))
            self.assertIn("package publication remains blocked", doc, str(path))
            self.assertIn("public installation remains blocked", doc, str(path))

    def test_make_and_ci_run_wording_review_after_registry_evidence_review(self) -> None:
        make_block = target_block("milestone-e-prep")
        ci = read(CI_WORKFLOW)
        evidence_guard = "test_milestone_e_package_publication_registry_assembly_evidence_review.py"
        wording_guard = "test_milestone_e_package_publication_public_installation_wording_review.py"
        public_facing_guard = "test_milestone_e_public_facing_readiness_ledger.py"

        for text, prefix in ((make_block, "$(PYTHON) .github/scripts/"), (ci, "python3 .github/scripts/")):
            self.assertIn(prefix + wording_guard, text)
            self.assertEqual(1, text.count(prefix + wording_guard))
            self.assertLess(text.index(prefix + evidence_guard), text.index(prefix + wording_guard))
            self.assertLess(text.index(prefix + wording_guard), text.index(prefix + public_facing_guard))

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
