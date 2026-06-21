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
import unittest
from pathlib import Path
from typing import Any

from makefile_guard import target_block


ROOT = Path(__file__).resolve().parents[2]
PREP = ROOT / "docs/milestone-e-package-publication-approval-prep.json"
PREP_SCHEMA = ROOT / "schemas/ethos-milestone-e-package-publication-approval-prep.schema.json"
LANE_BLOCKERS = ROOT / "docs/milestone-e-public-approval-lane-blockers.json"
PREP_SCOPE = ROOT / "docs/milestone-e-prep-scope.md"
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
SCHEMAS_README = ROOT / "schemas/README.md"
VALIDATE_EXAMPLES = ROOT / "schemas/validate_examples.py"
VALIDATION_README = ROOT / "docs/validation/README.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"

EXPECTED_BOUNDARY = [
    "public reports remain blocked",
    "release artifacts remain blocked",
    "package publication remains blocked",
    "hosted surfaces remain blocked",
    "public result wording remains blocked",
    "performance claims remain blocked",
    "quality claims remain blocked",
    "footprint claims remain blocked",
    "table-quality claims remain blocked",
    "parser-quality claims remain blocked",
]

EXPECTED_APPROVED_SENTENCE = (
    "Ethos is pre-alpha. It verifies whether AI citations are grounded in document "
    "evidence across native Ethos JSON and supported foreign parser outputs."
)
EXPECTED_PACKAGE_PREP_WORDING = (
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
EXPECTED_GATE = ".github/scripts/test_milestone_e_package_publication_approval_prep.py"
EXPECTED_RECORD = (
    "docs/validation/milestone-e-package-publication-prep-approval-validation-2026-06-20.md"
)
EXPECTED_EVIDENCE_RECORDS = {
    "package_inventory": "docs/validation/milestone-e-package-publication-inventory-reconciliation-validation-2026-06-20.md",
    "package_metadata_license_readme": "docs/validation/milestone-e-package-publication-metadata-readiness-validation-2026-06-20.md",
    "dry_run_smoke_path": "docs/validation/milestone-e-package-publication-dry-run-smoke-plan-validation-2026-06-20.md",
    "version_tag_policy": "docs/validation/milestone-e-package-publication-version-tag-policy-validation-2026-06-20.md",
    "pdfium_boundary": "docs/validation/milestone-e-package-publication-pdfium-boundary-validation-2026-06-20.md",
}
EXPECTED_FOLLOW_UP_RECORDS = {
    "package_metadata_readiness": "docs/validation/milestone-e-package-publication-metadata-readiness-closeout-validation-2026-06-21.md",
    "package_dry_run_smoke": "docs/validation/milestone-e-package-publication-dry-run-smoke-closeout-validation-2026-06-21.md",
    "package_version_tag_policy": "docs/validation/milestone-e-package-publication-version-tag-policy-closeout-validation-2026-06-21.md",
    "package_pdfium_boundary": "docs/validation/milestone-e-package-publication-pdfium-boundary-closeout-validation-2026-06-21.md",
    "package_dependency_ordering": "docs/validation/milestone-e-package-publication-dependency-ordering-closeout-validation-2026-06-21.md",
    "package_manifest_migration_prep": "docs/validation/milestone-e-package-publication-manifest-migration-prep-validation-2026-06-21.md",
    "package_manifest_activation_prep": "docs/validation/milestone-e-package-publication-manifest-activation-prep-validation-2026-06-21.md",
    "package_registry_assembly_prep": "docs/validation/milestone-e-package-publication-registry-assembly-prep-validation-2026-06-21.md",
    "package_registry_assembly_activation_prep": "docs/validation/milestone-e-package-publication-registry-assembly-activation-prep-validation-2026-06-21.md",
    "package_real_version_selection_prep": "docs/validation/milestone-e-package-publication-real-version-selection-prep-validation-2026-06-21.md",
    "package_tag_creation_prep": "docs/validation/milestone-e-package-publication-tag-creation-prep-validation-2026-06-21.md",
    "package_decision_bundle_validation": "docs/validation/milestone-e-package-publication-decision-bundle-validation-2026-06-21.md",
    "package_pre_approval_gap_ledger": "docs/validation/milestone-e-package-publication-pre-approval-gap-ledger-validation-2026-06-21.md",
    "package_decision_input_packet": "docs/validation/milestone-e-package-publication-decision-input-packet-validation-2026-06-21.md",
    "package_approval_readiness_review": "docs/validation/milestone-e-package-publication-approval-readiness-review-validation-2026-06-21.md",
    "package_manifest_activation_diff_review": "docs/validation/milestone-e-package-publication-manifest-activation-diff-review-validation-2026-06-21.md",
    "package_registry_assembly_evidence_review": "docs/validation/milestone-e-package-publication-registry-assembly-evidence-review-validation-2026-06-21.md",
}
EXPECTED_PUBLICATION_DECISION_INPUTS = {
    "decision_status": "not_approved_pending_exact_decision",
    "candidate_surface": [
        "first candidate surface may include only ethos-doc-core, ethos-verify, and ethos-pdf after exact artifact evidence is reviewed",
        "ethos-doc and ethos-rag remain excluded until in-tree manifests, owners, metadata, README files, and support expectations exist",
    ],
    "required_exact_decision_fields": [
        "exact candidate crate list",
        "exact SemVer package version",
        "exact package tag name and source commit",
        "exact package dependency manifest activation diff",
        "exact registry-backed dependent package assembly evidence",
        "exact public installation wording",
        "exact exclusion list for wheels, npm packages, binaries, hosted surfaces, production positioning, public benchmark reports, public benchmark claims, and project-maintained PDFium builds",
    ],
    "required_pre_approval_commands": [
        "python3 .github/scripts/test_milestone_e_package_publication_approval_prep.py",
        "python3 .github/scripts/test_public_surface_posture.py",
        "python3 .github/scripts/claims_gate.py",
        "cargo build --locked -p ethos-cli",
        "make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python",
        "git diff --check",
    ],
    "retained_blockers": [
        "no package publication version is selected",
        "no package tag is created",
        "no package dependency manifest activation is approved",
        "no registry-backed dependent package assembly activation is approved",
        "public installation remains blocked",
        "package publication remains blocked",
    ],
}
EXPECTED_CANDIDATE_CRATE_SURFACE_REVIEW = {
    "review_state": "candidate_surface_review_recorded_publication_blocked",
    "included_candidate_crates": [
        "ethos-doc-core from crates/ethos-core; current manifest name ethos-core; publish=false; package-name migration remains pending",
        "ethos-verify from crates/ethos-verify; current manifest name ethos-verify; publish=false; dependency manifest activation remains pending",
        "ethos-pdf from crates/ethos-pdf; current manifest name ethos-pdf; publish=false; dependency manifest activation and PDFium boundary confirmation must remain current",
    ],
    "excluded_reserved_crates": [
        "ethos-doc remains excluded because no in-tree workspace member or package manifest exists",
        "ethos-rag remains excluded because no in-tree package manifest exists",
    ],
    "required_before_publication": [
        "exact SemVer package version selection",
        "exact package tag name and source commit",
        "exact package-name migration diff for ethos-doc-core",
        "exact dependency manifest activation diff for ethos-verify and ethos-pdf",
        "exact registry-backed dependent package assembly evidence",
        "exact public installation wording and explicit exclusions",
    ],
    "retained_blockers": [
        "candidate surface review does not approve package publication",
        "candidate surface review does not select a package publication version",
        "candidate surface review does not create a package tag",
        "candidate surface review does not change Cargo manifests",
        "candidate surface review does not approve public installation",
        "candidate surface review does not approve registry-backed dependent package assembly activation",
    ],
}
EXPECTED_SEMVER_PACKAGE_VERSION_DECISION_PREP = {
    "review_state": "semver_decision_inputs_recorded_version_unselected_publication_blocked",
    "current_version_context": [
        "workspace package version is 0.1.0 and remains source-tree only",
        "reserved crates.io placeholders remain 0.0.0-reserved.0",
        "candidate surface review includes ethos-doc-core, ethos-verify, and ethos-pdf only",
    ],
    "required_exact_decision_fields": [
        "exact SemVer package version for each included candidate crate",
        "exact confirmation that all included candidate crates share the same SemVer package version or an explicit per-crate version map",
        "exact source commit for the version decision",
        "exact package tag name that binds the selected version and source commit",
        "exact manifest diff showing package-name migration and dependency activation",
        "exact pre-publication dry-run and local install evidence for the selected version",
    ],
    "retained_blockers": [
        "no SemVer package version is selected",
        "workspace version 0.1.0 is not approved as a package publication version",
        "reserved placeholder version 0.0.0-reserved.0 remains a reservation only",
        "no package tag is created",
        "public installation remains blocked",
        "package publication remains blocked",
    ],
}
EXPECTED_PACKAGE_PUBLICATION_DECISION_PREP_BUNDLE = {
    "decision_state": "combined_decision_inputs_recorded_actions_blocked",
    "review_boundary": [
        "package tag and source-commit decision inputs are recorded while creating no package tag",
        "package dependency manifest activation inputs are recorded while changing no Cargo manifest",
        "registry-backed dependent package assembly inputs are recorded while creating no registry and activating no assembly",
        "public installation wording and exclusion inputs are recorded while inviting no public installation",
    ],
    "required_decision_inputs": [
        "exact package tag name",
        "exact source commit for package tag binding",
        "exact package-name migration diff for ethos-doc-core",
        "exact dependency manifest activation diff for ethos-verify and ethos-pdf",
        "exact registry-backed dependent package assembly evidence for ethos-doc-core before ethos-verify and ethos-pdf",
        "exact public installation wording limited to a later approved package surface",
        "exact exclusion list for wheels, npm packages, binaries, hosted surfaces, production positioning, public benchmark reports, public benchmark claims, and project-maintained PDFium builds",
        "posture and claims gates after exact public installation wording changes",
    ],
    "non_approvals": [
        "this bundle does not select a package publication version",
        "this bundle does not create a package tag",
        "this bundle does not change Cargo manifests",
        "this bundle does not activate package dependency manifests",
        "this bundle does not create a registry",
        "this bundle does not activate registry-backed dependent package assembly",
        "this bundle does not invite public installation",
        "this bundle does not approve package publication",
    ],
    "retained_blockers": [
        "no package publication version is selected",
        "no package tag is created",
        "no package dependency manifest activation is approved",
        "no registry-backed dependent package assembly activation is approved",
        "public installation remains blocked",
        "package publication remains blocked",
    ],
}
EXPECTED_PACKAGE_PUBLICATION_APPROVAL_REQUEST_PACKET = {
    "packet_state": "approval_request_packet_recorded_publication_blocked",
    "candidate_crates": [
        "ethos-doc-core mapped from crates/ethos-core; package-name migration remains pending",
        "ethos-verify mapped from crates/ethos-verify; dependency manifest activation remains pending",
        "ethos-pdf mapped from crates/ethos-pdf; dependency manifest activation and PDFium boundary confirmation must remain current",
    ],
    "package_version_map": [
        "ethos-doc-core has no selected package publication version",
        "ethos-verify has no selected package publication version",
        "ethos-pdf has no selected package publication version",
    ],
    "package_tag_name": "not selected; package tag creation remains blocked",
    "package_tag_source_commit": "not selected; package tag binding remains blocked",
    "package_tag_source_tree": "not selected; package source tree binding remains blocked",
    "manifest_activation_diff": "not prepared; current Cargo manifests remain unchanged",
    "registry_assembly_evidence": "not activated; registry-backed dependent package assembly remains blocked",
    "public_installation_wording": "No public installation wording is approved; public installation remains blocked.",
    "explicit_exclusions": [
        "wheels",
        "npm packages",
        "binaries",
        "hosted surfaces",
        "production positioning",
        "public benchmark reports",
        "public benchmark claims",
        "release artifacts",
        "project-maintained PDFium builds",
    ],
    "required_before_approval": [
        "exact package publication approval decision record",
        "exact candidate crate list",
        "exact SemVer package version or per-crate version map",
        "exact package tag name and package_tag_source_commit",
        "exact package-name migration diff for ethos-doc-core",
        "exact dependency manifest activation diff for ethos-verify and ethos-pdf",
        "exact registry-backed dependent package assembly evidence",
        "posture and claims gates after exact public installation wording changes",
    ],
    "non_approvals": [
        "this packet does not select a package publication version",
        "this packet does not create a package tag",
        "this packet does not change Cargo manifests",
        "this packet does not activate package dependency manifests",
        "this packet does not create a registry",
        "this packet does not activate registry-backed dependent package assembly",
        "this packet does not invite public installation",
        "this packet does not approve package publication",
    ],
    "retained_blockers": [
        "no package publication version is selected",
        "no package tag is created",
        "no package dependency manifest activation is approved",
        "no registry-backed dependent package assembly activation is approved",
        "public installation remains blocked",
        "package publication remains blocked",
        "real-version cargo publish remains blocked",
    ],
}
EXPECTED_PACKAGE_PUBLICATION_PRE_APPROVAL_GAP_LEDGER = {
    "ledger_state": "pre_approval_gaps_recorded_publication_blocked",
    "gap_rows": [
        "version map gap: no package publication version is selected; requires exact SemVer package version or per-crate version map",
        "tag name gap: no package tag is created; requires exact package tag name",
        "tag binding gap: no package_tag_source_commit or source tree is selected; requires exact source commit and tree binding",
        "manifest activation gap: current Cargo manifests remain unchanged; requires exact package-name migration and dependency activation diff",
        "registry assembly gap: no registry-backed dependent package assembly is activated; requires exact non-public assembly evidence",
        "public installation wording gap: no public installation wording is approved; requires exact wording and exclusions",
        "posture and claims gate gap: gates must rerun after exact public installation wording changes",
    ],
    "blocked_actions": [
        "selecting a package publication version remains blocked",
        "creating a package tag remains blocked",
        "changing Cargo manifests remains blocked",
        "activating package dependency manifests remains blocked",
        "creating a registry remains blocked",
        "activating registry-backed dependent package assembly remains blocked",
        "inviting public installation remains blocked",
        "approving package publication remains blocked",
    ],
    "required_resolution_inputs": [
        "exact package publication approval decision record",
        "exact candidate crate list",
        "exact SemVer package version or per-crate version map",
        "exact package tag name",
        "exact package_tag_source_commit and package source tree",
        "exact package-name migration diff for ethos-doc-core",
        "exact dependency manifest activation diff for ethos-verify and ethos-pdf",
        "exact registry-backed dependent package assembly evidence",
        "exact public installation wording and explicit exclusions",
        "posture and claims gates after exact public installation wording changes",
    ],
    "non_approvals": [
        "this ledger does not select a package publication version",
        "this ledger does not create a package tag",
        "this ledger does not change Cargo manifests",
        "this ledger does not activate package dependency manifests",
        "this ledger does not create a registry",
        "this ledger does not activate registry-backed dependent package assembly",
        "this ledger does not invite public installation",
        "this ledger does not approve package publication",
    ],
    "retained_blockers": [
        "no package publication version is selected",
        "no package tag is created",
        "no package dependency manifest activation is approved",
        "no registry-backed dependent package assembly activation is approved",
        "public installation remains blocked",
        "package publication remains blocked",
        "real-version cargo publish remains blocked",
    ],
}

FORBIDDEN_PREP_WORDING = [
    "public beta is approved",
    "public beta approved",
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


class MilestoneEPackagePublicationApprovalPrepTests(unittest.TestCase):
    def test_prep_is_approved_but_publication_stays_blocked(self) -> None:
        prep = load_json(PREP)

        self.assertEqual(1, prep["schema_version"])
        self.assertEqual("source-only-pre-alpha-internal-milestone-e-prep", prep["status"])
        self.assertEqual("package_publication_approval_prep", prep["scope"])
        self.assertEqual("package-publication", prep["lane_id"])
        self.assertEqual("Package publication", prep["lane_name"])
        self.assertEqual("prep_approved_publication_blocked", prep["approval_status"])
        self.assertEqual("approve_prep", prep["decision_status"])
        self.assertEqual("docushell-admin", prep["approval_owner"])
        self.assertEqual(EXPECTED_APPROVED_SENTENCE, prep["exact_approved_public_sentence"])
        self.assertEqual(
            EXPECTED_PACKAGE_PREP_WORDING,
            prep["exact_approved_package_publication_prep_wording"],
        )
        self.assertEqual(EXPECTED_BOUNDARY, prep["public_boundary"])
        self.assertEqual(EXPECTED_GATE, prep["gate_script"])
        self.assertEqual(EXPECTED_RECORD, prep["validation_record"])

    def test_prep_keeps_approved_snapshot_source_only(self) -> None:
        snapshot = load_json(PREP)["approved_source_snapshot"]

        self.assertEqual("660f268df400351347d5185ad36584faa0481c7f", snapshot["source_head"])
        self.assertEqual("ethos-source-snapshot-660f268", snapshot["tag"])
        self.assertEqual("ethos-source-snapshot-660f268.tar.gz", snapshot["archive"])
        self.assertEqual(
            "58ec6fc1ec47a4c16f1294673ba9520b2fe9c2497e15ec96d78679db8517dd87",
            snapshot["sha256"],
        )
        self.assertEqual("source-snapshot-only; no package publication approval", snapshot["boundary"])

    def test_package_lane_stays_aligned_with_global_lane_blocker(self) -> None:
        prep = load_json(PREP)
        lane_blockers = load_json(LANE_BLOCKERS)
        [package_lane] = [
            lane for lane in lane_blockers["approval_lanes"] if lane["lane_id"] == "package-publication"
        ]

        self.assertEqual(package_lane["lane_name"], prep["lane_name"])
        self.assertEqual(package_lane["approval_owner"], prep["approval_owner"])
        self.assertEqual("prep_approved_publication_blocked", package_lane["approval_status"])
        self.assertEqual(EXPECTED_PACKAGE_PREP_WORDING, package_lane["allowed_wording"][0])
        self.assertIn("package publication remains blocked", package_lane["explicit_blockers"])
        self.assertIn(
            "ADR-0005, H2 source-snapshot closeout, and source-only public beta approval do not approve package publication",
            package_lane["explicit_blockers"],
        )
        self.assertIn("package publication remains blocked", prep["explicit_blockers"])
        self.assertIn(
            "ADR-0005, H2 source-snapshot closeout, and source-only public beta approval do not approve package publication",
            prep["explicit_blockers"],
        )

    def test_required_evidence_and_blockers_are_explicit(self) -> None:
        prep = load_json(PREP)

        self.assertEqual(5, len(prep["approval_scope"]))
        self.assertEqual(9, len(prep["required_evidence"]))
        self.assertEqual(13, len(prep["explicit_blockers"]))
        self.assertIn("dedicated package publication prep approval decision record", prep["required_evidence"])
        self.assertIn(
            "package inventory reconciliation for the five ADR-0006 reserved crates.io identifiers",
            prep["required_evidence"],
        )
        self.assertIn("per-crate metadata, license, NOTICE, and README readiness review", prep["required_evidence"])
        self.assertIn("cargo publish --dry-run and smoke build path for each candidate crate", prep["required_evidence"])
        self.assertIn("publish version and tag policy reconciliation", prep["required_evidence"])
        self.assertIn("PDFium packaging boundary confirmation for ethos-pdf", prep["required_evidence"])
        self.assertIn("claims gate after exact wording changes", prep["required_evidence"])
        self.assertIn("package publication remains blocked", prep["explicit_blockers"])
        self.assertIn("real-version cargo publish remains blocked", prep["explicit_blockers"])
        self.assertIn("binaries remain blocked", prep["explicit_blockers"])
        self.assertIn("wheels remain blocked", prep["explicit_blockers"])
        self.assertIn("npm packages remain blocked", prep["explicit_blockers"])
        self.assertIn("crate publication remains blocked", prep["explicit_blockers"])
        self.assertIn("project-maintained PDFium builds remain blocked", prep["explicit_blockers"])

    def test_approved_prep_names_reserved_crates_and_current_workspace_mapping(self) -> None:
        prep = load_json(PREP)
        approved = prep["approved_package_publication_prep"]
        cargo = read(ROOT / "Cargo.toml")
        adr = read(ROOT / "docs/decisions/ADR-0006-package-identifiers.md")

        self.assertEqual(
            "Rust crate publication preparation only for the five ADR-0006 reserved priority crates.io identifiers",
            approved["surface"],
        )
        self.assertEqual("crates.io", approved["registry"])
        self.assertEqual("0.0.0-reserved.0", approved["reserved_version"])
        self.assertEqual(EXPECTED_RESERVED_CRATES, approved["reserved_identifiers"])
        for crate in EXPECTED_RESERVED_CRATES:
            self.assertIn(f"`{crate}`", adr)
            self.assertIn("`0.0.0-reserved.0`", adr)

        self.assertIn('"crates/ethos-core"', cargo)
        self.assertIn('"crates/ethos-pdf"', cargo)
        self.assertIn('"crates/ethos-verify"', cargo)
        self.assertNotIn('"crates/ethos-doc"', cargo)
        self.assertNotIn('"crates/ethos-rag"', cargo)
        self.assertIn("ethos-doc-core maps to the in-tree ethos-core crate", " ".join(approved["in_tree_reconciliation"]))
        self.assertIn("ethos-doc has no in-tree workspace member yet", " ".join(approved["in_tree_reconciliation"]))
        self.assertIn("ethos-rag has no in-tree workspace member yet", " ".join(approved["in_tree_reconciliation"]))

    def test_candidate_crates_remain_publish_false_until_later_approval(self) -> None:
        core = read(ROOT / "crates/ethos-core/Cargo.toml")
        verify = read(ROOT / "crates/ethos-verify/Cargo.toml")
        pdf = read(ROOT / "crates/ethos-pdf/Cargo.toml")

        self.assertIn('name = "ethos-core"', core)
        self.assertIn("publish = false", core)
        self.assertIn('name = "ethos-verify"', verify)
        self.assertIn("publish = false", verify)
        self.assertIn('name = "ethos-pdf"', pdf)
        self.assertIn("publish = false", pdf)
        self.assertIn('version = "0.1.0"', read(ROOT / "Cargo.toml"))

    def test_evidence_status_matches_decider_input(self) -> None:
        status = load_json(PREP)["evidence_review_status"]

        self.assertIn("evidence recorded", status["package_inventory"])
        self.assertIn("publication remains blocked", status["package_inventory"])
        self.assertIn("metadata/readiness follow-up recorded", status["package_metadata_license_readme_review"])
        self.assertIn("publication remains blocked", status["package_metadata_license_readme_review"])
        self.assertIn("local source-tree smoke", status["install_build_smoke_path"])
        self.assertIn("dependency-ordering follow-up recorded", status["install_build_smoke_path"])
        self.assertIn("manifest-migration prep recorded", status["install_build_smoke_path"])
        self.assertIn("manifest-activation prep recorded", status["install_build_smoke_path"])
        self.assertIn("registry-assembly prep recorded", status["install_build_smoke_path"])
        self.assertIn("registry-assembly activation prep recorded", status["install_build_smoke_path"])
        self.assertIn("current source-tree manifests remain unchanged", status["install_build_smoke_path"])
        self.assertIn("publication remains blocked", status["install_build_smoke_path"])
        self.assertIn("version/tag policy follow-up", status["version_tag_policy"])
        self.assertIn("real-version-selection prep recorded", status["version_tag_policy"])
        self.assertIn("package tag-creation prep recorded", status["version_tag_policy"])
        self.assertIn("workspace 0.1.0 remains source-tree only", status["version_tag_policy"])
        self.assertIn("reserved 0.0.0-reserved.0 names remain placeholders", status["version_tag_policy"])
        self.assertIn("no package publication version is selected", status["version_tag_policy"])
        self.assertIn("no package tag is created", status["version_tag_policy"])
        self.assertIn("real-version publication remains blocked", status["version_tag_policy"])
        self.assertIn("PDFium boundary follow-up recorded", status["pdfium_packaging_boundary"])
        self.assertIn("no bundled PDFium binary", status["pdfium_packaging_boundary"])
        self.assertIn("caller-provided ETHOS_PDFIUM_LIBRARY_PATH", status["pdfium_packaging_boundary"])
        self.assertIn("no raw PDFium types across public schemas/APIs", status["pdfium_packaging_boundary"])
        self.assertIn("publication remains blocked", status["pdfium_packaging_boundary"])
        self.assertEqual(
            "run after exact wording changes by the package evidence guard path",
            status["public_surface_posture_check"],
        )
        self.assertEqual(
            "run after exact wording changes by the package evidence guard path",
            status["claims_gate_after_wording_changes"],
        )
        self.assertEqual(
            "docushell-admin approved prep wording and prep surface on 2026-06-20",
            status["decider_signoff"],
        )
        self.assertEqual(EXPECTED_EVIDENCE_RECORDS, load_json(PREP)["evidence_records"])
        self.assertEqual(EXPECTED_FOLLOW_UP_RECORDS, load_json(PREP)["follow_up_records"])

    def test_publication_approval_decision_inputs_keep_next_decision_exact(self) -> None:
        inputs = load_json(PREP)["publication_approval_decision_inputs"]

        self.assertEqual(EXPECTED_PUBLICATION_DECISION_INPUTS, inputs)
        self.assertIn("not_approved_pending_exact_decision", inputs["decision_status"])
        self.assertIn("exact candidate crate list", inputs["required_exact_decision_fields"])
        self.assertIn("exact SemVer package version", inputs["required_exact_decision_fields"])
        self.assertIn("exact package tag name and source commit", inputs["required_exact_decision_fields"])
        self.assertIn(
            "exact package dependency manifest activation diff",
            inputs["required_exact_decision_fields"],
        )
        self.assertIn(
            "exact registry-backed dependent package assembly evidence",
            inputs["required_exact_decision_fields"],
        )
        self.assertIn("exact public installation wording", inputs["required_exact_decision_fields"])
        self.assertIn("no package publication version is selected", inputs["retained_blockers"])
        self.assertIn("no package tag is created", inputs["retained_blockers"])
        self.assertIn("public installation remains blocked", inputs["retained_blockers"])
        self.assertIn("package publication remains blocked", inputs["retained_blockers"])

    def test_candidate_crate_surface_review_keeps_publication_blocked(self) -> None:
        review = load_json(PREP)["candidate_crate_surface_review"]
        cargo = read(ROOT / "Cargo.toml")
        core_manifest = read(ROOT / "crates/ethos-core/Cargo.toml")
        verify_manifest = read(ROOT / "crates/ethos-verify/Cargo.toml")
        pdf_manifest = read(ROOT / "crates/ethos-pdf/Cargo.toml")

        self.assertEqual(EXPECTED_CANDIDATE_CRATE_SURFACE_REVIEW, review)
        self.assertIn("candidate_surface_review_recorded_publication_blocked", review["review_state"])
        self.assertEqual(3, len(review["included_candidate_crates"]))
        self.assertEqual(2, len(review["excluded_reserved_crates"]))
        self.assertIn('"crates/ethos-core"', cargo)
        self.assertIn('"crates/ethos-verify"', cargo)
        self.assertIn('"crates/ethos-pdf"', cargo)
        self.assertNotIn('"crates/ethos-doc"', cargo)
        self.assertNotIn('"crates/ethos-rag"', cargo)
        self.assertIn('name = "ethos-core"', core_manifest)
        self.assertIn('reserved_crates_io_name = "ethos-doc-core"', core_manifest)
        self.assertIn("publish = false", core_manifest)
        self.assertIn('name = "ethos-verify"', verify_manifest)
        self.assertIn('reserved_crates_io_name = "ethos-verify"', verify_manifest)
        self.assertIn("publish = false", verify_manifest)
        self.assertIn('name = "ethos-pdf"', pdf_manifest)
        self.assertIn('reserved_crates_io_name = "ethos-pdf"', pdf_manifest)
        self.assertIn("publish = false", pdf_manifest)
        self.assertIn(
            "candidate surface review does not approve package publication",
            review["retained_blockers"],
        )
        self.assertIn(
            "candidate surface review does not approve public installation",
            review["retained_blockers"],
        )

    def test_semver_package_version_decision_prep_keeps_version_unselected(self) -> None:
        prep = load_json(PREP)
        review = prep["semver_package_version_decision_prep"]
        cargo = read(ROOT / "Cargo.toml")
        core_manifest = read(ROOT / "crates/ethos-core/Cargo.toml")
        verify_manifest = read(ROOT / "crates/ethos-verify/Cargo.toml")
        pdf_manifest = read(ROOT / "crates/ethos-pdf/Cargo.toml")

        self.assertEqual(EXPECTED_SEMVER_PACKAGE_VERSION_DECISION_PREP, review)
        self.assertIn(
            "semver_decision_inputs_recorded_version_unselected_publication_blocked",
            review["review_state"],
        )
        self.assertIn('version = "0.1.0"', cargo)
        self.assertIn('reserved_crates_io_version = "0.0.0-reserved.0"', core_manifest)
        self.assertIn('reserved_crates_io_version = "0.0.0-reserved.0"', verify_manifest)
        self.assertIn('reserved_crates_io_version = "0.0.0-reserved.0"', pdf_manifest)
        self.assertIn(
            "no SemVer package version is selected",
            review["retained_blockers"],
        )
        self.assertIn(
            "workspace version 0.1.0 is not approved as a package publication version",
            review["retained_blockers"],
        )
        self.assertIn(
            "reserved placeholder version 0.0.0-reserved.0 remains a reservation only",
            review["retained_blockers"],
        )
        self.assertIn("public installation remains blocked", review["retained_blockers"])
        self.assertIn("package publication remains blocked", review["retained_blockers"])

    def test_combined_package_publication_decision_prep_bundle_blocks_all_actions(self) -> None:
        bundle = load_json(PREP)["package_publication_decision_prep_bundle"]
        cargo = read(ROOT / "Cargo.toml")
        core_manifest = read(ROOT / "crates/ethos-core/Cargo.toml")
        verify_manifest = read(ROOT / "crates/ethos-verify/Cargo.toml")
        pdf_manifest = read(ROOT / "crates/ethos-pdf/Cargo.toml")

        self.assertEqual(EXPECTED_PACKAGE_PUBLICATION_DECISION_PREP_BUNDLE, bundle)
        self.assertEqual("combined_decision_inputs_recorded_actions_blocked", bundle["decision_state"])
        self.assertIn("exact package tag name", bundle["required_decision_inputs"])
        self.assertIn("exact source commit for package tag binding", bundle["required_decision_inputs"])
        self.assertIn(
            "exact dependency manifest activation diff for ethos-verify and ethos-pdf",
            bundle["required_decision_inputs"],
        )
        self.assertIn(
            "exact registry-backed dependent package assembly evidence for ethos-doc-core before ethos-verify and ethos-pdf",
            bundle["required_decision_inputs"],
        )
        self.assertIn(
            "posture and claims gates after exact public installation wording changes",
            bundle["required_decision_inputs"],
        )
        self.assertIn("this bundle does not create a package tag", bundle["non_approvals"])
        self.assertIn("this bundle does not change Cargo manifests", bundle["non_approvals"])
        self.assertIn("this bundle does not create a registry", bundle["non_approvals"])
        self.assertIn("this bundle does not invite public installation", bundle["non_approvals"])
        self.assertIn("this bundle does not approve package publication", bundle["non_approvals"])
        self.assertIn("no package tag is created", bundle["retained_blockers"])
        self.assertIn("public installation remains blocked", bundle["retained_blockers"])
        self.assertIn("package publication remains blocked", bundle["retained_blockers"])
        self.assertIn("publish = false", core_manifest)
        self.assertIn("publish = false", verify_manifest)
        self.assertIn("publish = false", pdf_manifest)
        self.assertIn('name = "ethos-core"', core_manifest)
        self.assertIn('name = "ethos-verify"', verify_manifest)
        self.assertIn('name = "ethos-pdf"', pdf_manifest)
        self.assertIn('version = "0.1.0"', cargo)

    def test_package_publication_approval_request_packet_keeps_all_actions_blocked(self) -> None:
        packet = load_json(PREP)["package_publication_approval_request_packet"]
        cargo = read(ROOT / "Cargo.toml")
        core_manifest = read(ROOT / "crates/ethos-core/Cargo.toml")
        verify_manifest = read(ROOT / "crates/ethos-verify/Cargo.toml")
        pdf_manifest = read(ROOT / "crates/ethos-pdf/Cargo.toml")

        self.assertEqual(EXPECTED_PACKAGE_PUBLICATION_APPROVAL_REQUEST_PACKET, packet)
        self.assertEqual("approval_request_packet_recorded_publication_blocked", packet["packet_state"])
        self.assertEqual(3, len(packet["candidate_crates"]))
        self.assertIn("ethos-doc-core has no selected package publication version", packet["package_version_map"])
        self.assertEqual(
            "not selected; package tag creation remains blocked",
            packet["package_tag_name"],
        )
        self.assertEqual(
            "not selected; package tag binding remains blocked",
            packet["package_tag_source_commit"],
        )
        self.assertEqual(
            "not prepared; current Cargo manifests remain unchanged",
            packet["manifest_activation_diff"],
        )
        self.assertIn("public installation remains blocked", packet["public_installation_wording"])
        self.assertIn("release artifacts", packet["explicit_exclusions"])
        self.assertIn("project-maintained PDFium builds", packet["explicit_exclusions"])
        self.assertIn("exact package tag name and package_tag_source_commit", packet["required_before_approval"])
        self.assertIn("posture and claims gates after exact public installation wording changes", packet["required_before_approval"])
        self.assertIn("this packet does not change Cargo manifests", packet["non_approvals"])
        self.assertIn("this packet does not invite public installation", packet["non_approvals"])
        self.assertIn("this packet does not approve package publication", packet["non_approvals"])
        self.assertIn("real-version cargo publish remains blocked", packet["retained_blockers"])
        self.assertIn('"crates/ethos-core"', cargo)
        self.assertIn('"crates/ethos-verify"', cargo)
        self.assertIn('"crates/ethos-pdf"', cargo)
        self.assertIn("publish = false", core_manifest)
        self.assertIn("publish = false", verify_manifest)
        self.assertIn("publish = false", pdf_manifest)
        self.assertIn('name = "ethos-core"', core_manifest)
        self.assertIn('name = "ethos-verify"', verify_manifest)
        self.assertIn('name = "ethos-pdf"', pdf_manifest)

    def test_package_publication_pre_approval_gap_ledger_keeps_resolution_inputs_explicit(self) -> None:
        ledger = load_json(PREP)["package_publication_pre_approval_gap_ledger"]
        cargo = read(ROOT / "Cargo.toml")
        core_manifest = read(ROOT / "crates/ethos-core/Cargo.toml")
        verify_manifest = read(ROOT / "crates/ethos-verify/Cargo.toml")
        pdf_manifest = read(ROOT / "crates/ethos-pdf/Cargo.toml")

        self.assertEqual(EXPECTED_PACKAGE_PUBLICATION_PRE_APPROVAL_GAP_LEDGER, ledger)
        self.assertEqual("pre_approval_gaps_recorded_publication_blocked", ledger["ledger_state"])
        self.assertEqual(7, len(ledger["gap_rows"]))
        self.assertEqual(8, len(ledger["blocked_actions"]))
        self.assertIn("creating a package tag remains blocked", ledger["blocked_actions"])
        self.assertIn("changing Cargo manifests remains blocked", ledger["blocked_actions"])
        self.assertIn("inviting public installation remains blocked", ledger["blocked_actions"])
        self.assertIn(
            "exact package_tag_source_commit and package source tree",
            ledger["required_resolution_inputs"],
        )
        self.assertIn(
            "exact public installation wording and explicit exclusions",
            ledger["required_resolution_inputs"],
        )
        self.assertIn("this ledger does not approve package publication", ledger["non_approvals"])
        self.assertIn("real-version cargo publish remains blocked", ledger["retained_blockers"])
        self.assertIn("publish = false", core_manifest)
        self.assertIn("publish = false", verify_manifest)
        self.assertIn("publish = false", pdf_manifest)
        self.assertIn('name = "ethos-core"', core_manifest)
        self.assertIn('name = "ethos-verify"', verify_manifest)
        self.assertIn('name = "ethos-pdf"', pdf_manifest)
        self.assertIn('version = "0.1.0"', cargo)

    def test_pdfium_boundary_keeps_ethos_pdf_held_until_confirmed(self) -> None:
        approved = load_json(PREP)["approved_package_publication_prep"]
        pdfium_boundary = " ".join(approved["pdfium_boundary"])
        traits = read(ROOT / "crates/ethos-core/src/traits.rs")
        pdf_manifest = read(ROOT / "crates/ethos-pdf/Cargo.toml")

        self.assertIn("ethos-pdf prep must bundle no PDFium binary", pdfium_boundary)
        self.assertIn("ethos-pdf prep must expose no PDFium types in public API", pdfium_boundary)
        self.assertIn("ETHOS_PDFIUM_LIBRARY_PATH", pdfium_boundary)
        self.assertIn("held out of the first crate surface", pdfium_boundary)
        self.assertIn("public schemas and", traits)
        self.assertIn("APIs never expose PDFium types", traits)
        self.assertNotIn("pdfium-render", pdf_manifest)

    def test_allowed_and_forbidden_wording_stay_narrow(self) -> None:
        prep = load_json(PREP)

        self.assertEqual(
            [
                EXPECTED_PACKAGE_PREP_WORDING,
                "Package publication prep is limited to the five ADR-0006 reserved priority crates.io identifiers.",
                "No real-version cargo publish is approved; reservations stay at placeholder versions.",
                "ethos-pdf is held out of a first crate surface if the PDFium packaging boundary cannot be guaranteed.",
            ],
            prep["allowed_wording"],
        )
        self.assertIn(
            "any statement that presents real-version cargo publication as approved",
            prep["forbidden_wording"],
        )
        self.assertIn(
            "any statement that invites public installation from package registries",
            prep["forbidden_wording"],
        )

    def test_schema_validation_covers_package_publication_prep(self) -> None:
        schema = load_json(PREP_SCHEMA)
        validate_examples = read(VALIDATE_EXAMPLES)
        schemas_readme = read(SCHEMAS_README)

        self.assertEqual(False, schema["additionalProperties"])
        self.assertEqual(False, schema["$defs"]["approved_source_snapshot"]["additionalProperties"])
        self.assertEqual(False, schema["$defs"]["approved_package_publication_prep"]["additionalProperties"])
        self.assertEqual(False, schema["$defs"]["evidence_review_status"]["additionalProperties"])
        self.assertEqual(False, schema["$defs"]["evidence_records"]["additionalProperties"])
        self.assertEqual(
            False,
            schema["$defs"]["publication_approval_decision_inputs"]["additionalProperties"],
        )
        self.assertEqual(
            False,
            schema["$defs"]["candidate_crate_surface_review"]["additionalProperties"],
        )
        self.assertEqual(
            False,
            schema["$defs"]["semver_package_version_decision_prep"]["additionalProperties"],
        )
        self.assertEqual(
            False,
            schema["$defs"]["package_publication_decision_prep_bundle"]["additionalProperties"],
        )
        self.assertEqual(
            False,
            schema["$defs"]["package_publication_approval_request_packet"]["additionalProperties"],
        )
        self.assertEqual(
            False,
            schema["$defs"]["package_publication_decision_input_packet"]["additionalProperties"],
        )
        self.assertEqual(
            False,
            schema["$defs"]["package_publication_pre_approval_gap_ledger"]["additionalProperties"],
        )
        self.assertEqual(9, schema["properties"]["required_evidence"]["minItems"])
        self.assertEqual(13, schema["properties"]["explicit_blockers"]["minItems"])
        self.assertEqual(
            7,
            schema["$defs"]["publication_approval_decision_inputs"]["properties"][
                "required_exact_decision_fields"
            ]["minItems"],
        )
        self.assertEqual(
            3,
            schema["$defs"]["candidate_crate_surface_review"]["properties"][
                "included_candidate_crates"
            ]["minItems"],
        )
        self.assertEqual(
            6,
            schema["$defs"]["semver_package_version_decision_prep"]["properties"][
                "required_exact_decision_fields"
            ]["minItems"],
        )
        self.assertEqual(
            8,
            schema["$defs"]["package_publication_decision_prep_bundle"]["properties"][
                "required_decision_inputs"
            ]["minItems"],
        )
        self.assertEqual(
            8,
            schema["$defs"]["package_publication_approval_request_packet"]["properties"][
                "required_before_approval"
            ]["minItems"],
        )
        self.assertEqual(
            9,
            schema["$defs"]["package_publication_approval_request_packet"]["properties"][
                "explicit_exclusions"
            ]["minItems"],
        )
        self.assertEqual(
            8,
            schema["$defs"]["package_publication_decision_input_packet"]["properties"][
                "required_before_approval"
            ]["minItems"],
        )
        self.assertEqual(
            7,
            schema["$defs"]["package_publication_pre_approval_gap_ledger"]["properties"][
                "gap_rows"
            ]["minItems"],
        )
        self.assertEqual(
            10,
            schema["$defs"]["package_publication_pre_approval_gap_ledger"]["properties"][
                "required_resolution_inputs"
            ]["minItems"],
        )
        self.assertIn("ethos-milestone-e-package-publication-approval-prep.schema.json", validate_examples)
        self.assertIn("docs\" / \"milestone-e-package-publication-approval-prep.json", validate_examples)
        self.assertIn("ethos-milestone-e-package-publication-approval-prep.schema.json", schemas_readme)
        self.assertIn("docs/milestone-e-package-publication-approval-prep.json", schemas_readme)

    def test_docs_reference_package_publication_prep_boundary(self) -> None:
        for path in (PREP_SCOPE, ROADMAP, EXECUTION_STATUS, VALIDATION_README):
            normalized = " ".join(read(path).split())

            self.assertIn(
                "docs/milestone-e-package-publication-approval-prep.json",
                normalized,
                str(path),
            )
            self.assertIn("package publication approval prep", normalized, str(path))
            self.assertIn("does not approve package publication", normalized, str(path))

    def test_make_target_runs_package_prep_after_public_beta_prep(self) -> None:
        block = target_block("milestone-e-prep")

        beta_record = (
            "$(PYTHON) .github/scripts/test_milestone_e_public_beta_approval_prep_validation_record.py"
        )
        package_guard = "$(PYTHON) .github/scripts/test_milestone_e_package_publication_approval_prep.py"
        package_record = (
            "$(PYTHON) .github/scripts/test_milestone_e_package_publication_approval_prep_validation_record.py"
        )
        package_prep_approval_record = (
            "$(PYTHON) .github/scripts/test_milestone_e_package_publication_prep_approval_validation_record.py"
        )
        index_guard = "$(PYTHON) .github/scripts/test_milestone_e_validation_record_index.py"

        self.assertIn(package_guard, block)
        self.assertIn(package_record, block)
        self.assertIn(package_prep_approval_record, block)
        self.assertLess(block.index(beta_record), block.index(package_guard))
        self.assertLess(block.index(package_guard), block.index(package_record))
        self.assertLess(block.index(package_record), block.index(package_prep_approval_record))
        self.assertLess(block.index(package_prep_approval_record), block.index(index_guard))
        self.assertLess(block.index(package_prep_approval_record), block.index("git diff --check"))

    def test_ci_runs_package_prep_once_in_order(self) -> None:
        text = read(CI_WORKFLOW)
        beta_record = (
            "python3 .github/scripts/test_milestone_e_public_beta_approval_prep_validation_record.py"
        )
        package_guard = "python3 .github/scripts/test_milestone_e_package_publication_approval_prep.py"
        package_record = (
            "python3 .github/scripts/test_milestone_e_package_publication_approval_prep_validation_record.py"
        )
        package_prep_approval_record = (
            "python3 .github/scripts/test_milestone_e_package_publication_prep_approval_validation_record.py"
        )
        index_guard = "python3 .github/scripts/test_milestone_e_validation_record_index.py"

        self.assertIn(package_guard, text)
        self.assertIn(package_record, text)
        self.assertIn(package_prep_approval_record, text)
        self.assertEqual(1, text.count(package_guard))
        self.assertEqual(1, text.count(package_record))
        self.assertEqual(1, text.count(package_prep_approval_record))
        self.assertLess(text.index(beta_record), text.index(package_guard))
        self.assertLess(text.index(package_guard), text.index(package_record))
        self.assertLess(text.index(package_record), text.index(package_prep_approval_record))
        self.assertLess(text.index(package_prep_approval_record), text.index(index_guard))

    def test_prep_avoids_scope_expansion_language(self) -> None:
        text = json.dumps(load_json(PREP), sort_keys=True).lower()

        for phrase in FORBIDDEN_PREP_WORDING:
            self.assertNotIn(phrase, text)

    def test_prep_avoids_local_private_paths(self) -> None:
        text = read(PREP)

        self.assertNotIn("/Users/", text)
        self.assertNotIn("/private/tmp", text)
        self.assertNotIn("/private/var", text)
        self.assertNotIn("/var/folders", text)
        self.assertNotIn("saumildiwaker", text)
        self.assertNotIn("Desktop/Stuff", text)
        self.assertNotIn("project/repo/ethos", text)
        self.assertNotIn("docs/.roadmap.md.swp", text)
        self.assertNotIn("web/", text)


if __name__ == "__main__":
    unittest.main()
