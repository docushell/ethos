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
import unittest
from pathlib import Path
from typing import Any

from cargo_manifest_guard import assert_workspace_version_is_semver
from makefile_guard import target_block


ROOT = Path(__file__).resolve().parents[2]
PREP = ROOT / "docs/milestone-e-package-publication-approval-prep.json"
VALIDATION_README = ROOT / "docs/validation/README.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"

RECORDS = {
    "package_inventory": "milestone-e-package-publication-inventory-reconciliation-validation-2026-06-20.md",
    "package_metadata_license_readme": "milestone-e-package-publication-metadata-readiness-validation-2026-06-20.md",
    "dry_run_smoke_path": "milestone-e-package-publication-dry-run-smoke-plan-validation-2026-06-20.md",
    "version_tag_policy": "milestone-e-package-publication-version-tag-policy-validation-2026-06-20.md",
    "pdfium_boundary": "milestone-e-package-publication-pdfium-boundary-validation-2026-06-20.md",
}

RESERVED_CRATES = [
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


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def record_path(name: str) -> Path:
    return ROOT / "docs/validation" / name


def normalized(path: Path) -> str:
    return re.sub(r"\s+", " ", read(path))


class MilestoneEPackagePublicationEvidenceRecordTests(unittest.TestCase):
    def test_records_are_indexed_and_referenced_by_prep_artifact(self) -> None:
        readme = read(VALIDATION_README)
        prep = load_json(PREP)

        self.assertEqual(
            {
                key: f"docs/validation/{name}"
                for key, name in RECORDS.items()
            },
            prep["evidence_records"],
        )
        for name in RECORDS.values():
            self.assertIn(name, readme)
        self.assertIn("package publication evidence", readme)

    def test_records_keep_standard_blocked_boundaries(self) -> None:
        for name in RECORDS.values():
            text = normalized(record_path(name))
            lower = text.lower()

            self.assertIn("Validated source HEAD before this record: `e792f03`", text, name)
            self.assertIn("Ethos remains source-only pre-alpha", text, name)
            self.assertIn("Package publication remains blocked", text, name)
            self.assertIn("Public reports remain blocked", text, name)
            self.assertIn("Public result wording remains blocked", text, name)
            self.assertIn("Real-version cargo publish remains blocked", text, name)
            self.assertIn("Public installation from crates.io remains blocked", text, name)
            self.assertIn("does not resolve or soften blockers", lower, name)
            self.assertIn("python3 .github/scripts/test_milestone_e_package_publication_evidence_records.py", text, name)
            self.assertIn("python3 .github/scripts/test_public_surface_posture.py", text, name)
            self.assertIn("python3 .github/scripts/claims_gate.py", text, name)
            self.assertIn("cargo build --locked -p ethos-cli", text, name)
            self.assertIn("make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python", text, name)
            self.assertIn("git diff --check", text, name)

    def test_package_inventory_record_matches_workspace_and_adr(self) -> None:
        record = normalized(record_path(RECORDS["package_inventory"]))
        root_manifest = read(ROOT / "Cargo.toml")
        adr = read(ROOT / "docs/decisions/ADR-0006-package-identifiers.md")

        for crate in RESERVED_CRATES:
            self.assertIn(f"`{crate}`", record)
            self.assertIn(f"`{crate}`", adr)
        self.assertIn("`0.0.0-reserved.0`", record)
        self.assertIn('"crates/ethos-core"', root_manifest)
        self.assertIn('"crates/ethos-verify"', root_manifest)
        self.assertIn('"crates/ethos-pdf"', root_manifest)
        self.assertNotIn('"crates/ethos-doc"', root_manifest)
        self.assertNotIn('"crates/ethos-rag"', root_manifest)
        self.assertFalse((ROOT / "crates/ethos-doc/Cargo.toml").exists())
        self.assertFalse((ROOT / "crates/ethos-rag/Cargo.toml").exists())

    def test_metadata_record_matches_license_notice_and_manifest_state(self) -> None:
        record = normalized(record_path(RECORDS["package_metadata_license_readme"]))

        self.assertIn("Apache License", read(ROOT / "LICENSE"))
        self.assertIn("Ethos", read(ROOT / "NOTICE"))
        self.assertIn("license.workspace = true", read(ROOT / "crates/ethos-core/Cargo.toml"))
        self.assertIn("license.workspace = true", read(ROOT / "crates/ethos-verify/Cargo.toml"))
        self.assertIn("license.workspace = true", read(ROOT / "crates/ethos-pdf/Cargo.toml"))
        self.assertIn("`crates/ethos-core` has no crate README ready", record)
        self.assertIn("`crates/ethos-verify` has no crate README ready", record)
        self.assertIn("`crates/ethos-pdf` has no crate README ready", record)
        self.assertIn("Per-crate README content remains incomplete", record)
        self.assertIn("Per-crate NOTICE packaging remains undefined", record)

    def test_dry_run_plan_keeps_publish_false_and_does_not_run_publication(self) -> None:
        record = normalized(record_path(RECORDS["dry_run_smoke_path"]))

        for manifest in (
            ROOT / "crates/ethos-core/Cargo.toml",
            ROOT / "crates/ethos-verify/Cargo.toml",
            ROOT / "crates/ethos-pdf/Cargo.toml",
        ):
            self.assertNotIn("publish = false", read(manifest), str(manifest))
        self.assertIn("cargo build --locked -p ethos-cli", record)
        self.assertIn("cargo publish --dry-run -p ethos-verify", record)
        self.assertIn("These commands are not approved as current publication evidence", record)
        self.assertIn("No registry-install smoke test has been run", record)

    def test_version_tag_policy_record_keeps_placeholder_and_workspace_versions_separate(self) -> None:
        record = normalized(record_path(RECORDS["version_tag_policy"]))
        root_manifest = read(ROOT / "Cargo.toml")

        assert_workspace_version_is_semver(self, root_manifest)
        self.assertIn("Workspace package version is `0.1.0`", record)
        self.assertIn("`0.0.0-reserved.0` placeholders", record)
        self.assertIn("`ethos-source-snapshot-660f268`", record)
        self.assertIn("No package release tag policy exists", record)

    def test_pdfium_boundary_record_matches_source_boundaries(self) -> None:
        record = normalized(record_path(RECORDS["pdfium_boundary"]))
        traits = read(ROOT / "crates/ethos-core/src/traits.rs")
        verify_manifest = read(ROOT / "crates/ethos-verify/Cargo.toml")
        pdf_manifest = read(ROOT / "crates/ethos-pdf/Cargo.toml")

        self.assertNotIn("publish = false", pdf_manifest)
        self.assertIn("ETHOS_PDFIUM_LIBRARY_PATH", record)
        self.assertIn("expose no PDFium types in public API", record)
        self.assertIn("public schemas and", traits)
        self.assertIn("APIs never expose PDFium types", traits)
        self.assertIn("never ethos-pdf", verify_manifest)
        self.assertIn("ethos-verify` remains the recommended first candidate", record)

    def test_make_target_and_ci_run_evidence_guard_after_prep_approval(self) -> None:
        make_block = target_block("milestone-e-prep")
        ci = read(CI_WORKFLOW)
        prep_approval_guard = "test_milestone_e_package_publication_prep_approval_validation_record.py"
        evidence_guard = "test_milestone_e_package_publication_evidence_records.py"

        for text, prefix in ((make_block, "$(PYTHON) .github/scripts/"), (ci, "python3 .github/scripts/")):
            self.assertIn(prefix + evidence_guard, text)
            self.assertLess(text.index(prefix + prep_approval_guard), text.index(prefix + evidence_guard))

    def test_records_avoid_scope_expansion_language_and_private_paths(self) -> None:
        for name in RECORDS.values():
            lower = normalized(record_path(name)).lower()
            raw = read(record_path(name))

            for phrase in FORBIDDEN_RECORD_WORDING:
                self.assertNotIn(phrase, lower, name)
            self.assertNotIn("/Users/", raw, name)
            self.assertNotIn("/private/tmp", raw, name)
            self.assertNotIn("/private/var", raw, name)
            self.assertNotIn("/var/folders", raw, name)
            self.assertNotIn("saumildiwaker", raw, name)
            self.assertNotIn("Desktop/Stuff", raw, name)
            self.assertNotIn("project/repo/ethos", raw, name)
            self.assertNotIn("docs/.roadmap.md.swp", raw, name)
            self.assertNotIn("web/", raw, name)


if __name__ == "__main__":
    unittest.main()
