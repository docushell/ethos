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
PREP_SCOPE = ROOT / "docs/milestone-e-prep-scope.md"
FIXTURE_CANDIDATES = ROOT / "docs/milestone-e-fixture-candidates.json"
FIXTURE_CANDIDATES_SCHEMA = ROOT / "schemas/ethos-milestone-e-fixture-candidates.schema.json"
FIXTURE_PROMOTION_CRITERIA_SCHEMA = (
    ROOT / "schemas/ethos-milestone-e-fixture-promotion-criteria.schema.json"
)
TRUST_LOOP_WALKTHROUGH = ROOT / "docs/milestone-e-internal-trust-loop-walkthrough.json"
TRUST_LOOP_WALKTHROUGH_SCHEMA = (
    ROOT / "schemas/ethos-milestone-e-internal-trust-loop-walkthrough.schema.json"
)
TRUST_LOOP_USE_PROTOCOL = ROOT / "docs/milestone-e-internal-trust-loop-use-protocol.json"
TRUST_LOOP_USE_PROTOCOL_SCHEMA = (
    ROOT / "schemas/ethos-milestone-e-internal-trust-loop-use-protocol.schema.json"
)
TRUST_LOOP_REHEARSAL_EVIDENCE_MATRIX = (
    ROOT / "docs/milestone-e-internal-trust-loop-rehearsal-evidence-matrix.json"
)
TRUST_LOOP_REHEARSAL_EVIDENCE_MATRIX_SCHEMA = (
    ROOT
    / "schemas/ethos-milestone-e-internal-trust-loop-rehearsal-evidence-matrix.schema.json"
)
TRUST_LOOP_BLOCKER_LEDGER = ROOT / "docs/milestone-e-internal-trust-loop-blocker-ledger.json"
TRUST_LOOP_BLOCKER_LEDGER_SCHEMA = (
    ROOT / "schemas/ethos-milestone-e-internal-trust-loop-blocker-ledger.schema.json"
)
PUBLIC_APPROVAL_LANE_BLOCKERS = ROOT / "docs/milestone-e-public-approval-lane-blockers.json"
PUBLIC_APPROVAL_LANE_BLOCKERS_SCHEMA = (
    ROOT / "schemas/ethos-milestone-e-public-approval-lane-blockers.schema.json"
)
PUBLIC_BETA_APPROVAL_PREP = ROOT / "docs/milestone-e-public-beta-approval-prep.json"
PUBLIC_BETA_APPROVAL_PREP_SCHEMA = (
    ROOT / "schemas/ethos-milestone-e-public-beta-approval-prep.schema.json"
)
PACKAGE_PUBLICATION_APPROVAL_PREP = (
    ROOT / "docs/milestone-e-package-publication-approval-prep.json"
)
PACKAGE_PUBLICATION_APPROVAL_PREP_SCHEMA = (
    ROOT / "schemas/ethos-milestone-e-package-publication-approval-prep.schema.json"
)
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"
SCHEMAS_README = ROOT / "schemas/README.md"
VALIDATE_EXAMPLES = ROOT / "schemas/validate_examples.py"

EXPECTED_CANDIDATES = {
    "Native verification trust loop": [
        "examples/verify/cases.json",
        "examples/verify/goldens/native_grounded_report.json",
    ],
    "Split-quote and unsupported-claim diagnostics": [
        "examples/verify/native_split_quote_citations.json",
        "examples/verify/native_non_v1_claims_citations.json",
    ],
    "Capability downgrade diagnostics": [
        "examples/verify/capability_downgrade_v1_contract.json",
        "examples/verify/goldens/opendataloader_capability_limited_report.json",
    ],
    "OpenDataLoader-style adapter grounding": [
        "examples/verify/opendataloader_adapter_shape_v1_contract.json",
        "examples/verify/opendataloader.json",
    ],
    "Pinned real OpenDataLoader fixture path": [
        "fixtures/foreign/opendataloader/real/manifest.json",
        "fixtures/foreign/opendataloader/real/expected.verification_report.json",
        "fixtures/foreign/opendataloader/real/expected.ungrounded.verification_report.json",
    ],
    "Crop descriptor and source-bound crop shape": [
        "examples/crop/crop_element_v1_contract.json",
        "examples/crop/crop_element_surface_shape_v1_contract.json",
    ],
    "RAG chunk artifact loop": ["schemas/examples/chunks.example.jsonl"],
    "Security-report artifact loop": ["schemas/examples/security-report.example.json"],
    "Demo narrative index": ["docs/demos/verify-alpha.md"],
}

ALLOWED_COMMANDS = {
    "make milestone-d-capability-downgrade-contract",
    "make milestone-d-internal-contracts",
    "make milestone-d-opendataloader-adapter-shape-contract",
    "make rag-chunk-alpha",
    "make security-report-alpha",
    "make verify-alpha",
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalized(path: Path) -> str:
    return re.sub(r"\s+", " ", read(path))


def load_fixture_inventory() -> dict:
    return json.loads(FIXTURE_CANDIDATES.read_text(encoding="utf-8"))


class MilestoneEPrepScopeTests(unittest.TestCase):
    def assert_tracked_file(self, path: str) -> None:
        self.assertTrue((ROOT / path).is_file(), path)
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", path],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, path)

    def test_prep_scope_keeps_internal_source_only_status(self) -> None:
        text = normalized(PREP_SCOPE)

        self.assertIn("source-only pre-alpha prep for internal Milestone E continuation", text)
        self.assertIn("ADR-0005 remains an internal continuation decision only", text)
        self.assertIn("does not approve public benchmark reports", text)
        self.assertIn("release artifacts, package publication, production positioning", text)
        self.assertIn(
            "performance, quality, footprint, table-quality, or parser-quality claims",
            text,
        )
        self.assertIn("These are internal fixture candidates, not public proof points", text)

    def test_prep_scope_names_guarded_fixture_candidates(self) -> None:
        text = read(PREP_SCOPE)

        self.assertIn("`docs/milestone-e-fixture-candidates.json`", text)
        self.assertIn("`blockers_must_remain_explicit`", text)
        self.assertIn("structured blocker", text)
        self.assert_tracked_file("docs/milestone-e-fixture-candidates.json")
        self.assert_tracked_file("docs/milestone-e-internal-trust-loop-walkthrough.json")
        self.assert_tracked_file("schemas/ethos-milestone-e-fixture-candidates.schema.json")
        self.assert_tracked_file(
            "schemas/ethos-milestone-e-fixture-promotion-criteria.schema.json"
        )
        self.assert_tracked_file(
            "schemas/ethos-milestone-e-internal-trust-loop-walkthrough.schema.json"
        )
        self.assertIn("`docs/milestone-e-internal-trust-loop-use-protocol.json`", text)
        self.assertIn(
            "`docs/milestone-e-internal-trust-loop-rehearsal-evidence-matrix.json`",
            text,
        )
        self.assertTrue(TRUST_LOOP_REHEARSAL_EVIDENCE_MATRIX.is_file())
        self.assertTrue(TRUST_LOOP_REHEARSAL_EVIDENCE_MATRIX_SCHEMA.is_file())
        self.assertIn("`docs/milestone-e-internal-trust-loop-blocker-ledger.json`", text)
        self.assertIn("blocked-output alignment", text)
        self.assertIn("evidence-lane alignment", text)
        self.assertIn("diagnostic-boundary alignment", text)
        self.assertIn("promotion-status alignment", text)
        self.assertIn("source-status alignment", text)
        self.assertIn("applies-to binding alignment", text)
        self.assertIn("required-before alignment", text)
        self.assertIn("validation-record source-head alignment", text)
        self.assertTrue(TRUST_LOOP_BLOCKER_LEDGER.is_file())
        self.assertTrue(TRUST_LOOP_BLOCKER_LEDGER_SCHEMA.is_file())
        for label, paths in EXPECTED_CANDIDATES.items():
            self.assertIn(label, text)
            for path in paths:
                self.assertIn(f"`{path}`", text)
                self.assert_tracked_file(path)

    def test_fixture_inventory_is_exact_path_backed_and_internal(self) -> None:
        inventory = load_fixture_inventory()

        self.assertEqual(1, inventory["schema_version"])
        self.assertEqual(
            "source-only-pre-alpha-internal-milestone-e-prep",
            inventory["status"],
        )
        self.assertEqual("internal_fixture_candidate_inventory", inventory["scope"])
        self.assertEqual(
            "not_promoted_beyond_internal_fixture_planning",
            inventory["promotion_status"],
        )
        self.assertIn("public result wording remains blocked", inventory["public_boundary"])
        self.assertIn("hosted surfaces remain blocked", inventory["public_boundary"])

        by_label = {case["label"]: case for case in inventory["fixture_candidates"]}
        self.assertEqual(set(EXPECTED_CANDIDATES), set(by_label))
        for label, paths in EXPECTED_CANDIDATES.items():
            case = by_label[label]
            self.assertEqual("source-only-pre-alpha-internal-candidate", case["status"])
            self.assertIn(case["validated_command"], ALLOWED_COMMANDS)
            self.assertEqual(paths, case["input_fixtures"])
            self.assertTrue(case["expected_diagnostic_boundary"], label)
            self.assertIn("Internal fixture candidate only", case["blocker_status"])
            self.assertIn("blockers_must_remain_explicit", case)
            self.assertTrue(case["blockers_must_remain_explicit"], label)
            for path in paths:
                self.assert_tracked_file(path)

    def test_fixture_inventory_avoids_public_launch_posture(self) -> None:
        text = json.dumps(load_fixture_inventory(), sort_keys=True).lower()

        forbidden = [
            "public beta is approved",
            "release-ready",
            "package-ready",
            "production-ready",
            "benchmark-validated",
            "launch-ready",
            "public result wording approved",
            "hosted surface approved",
            "broad demo approved",
        ]
        for phrase in forbidden:
            self.assertNotIn(phrase, text)

    def test_status_and_roadmap_reference_prep_scope(self) -> None:
        roadmap = read(ROADMAP)
        status = read(EXECUTION_STATUS)
        normalized_roadmap = re.sub(r"\s+", " ", roadmap)
        normalized_status = re.sub(r"\s+", " ", status)

        self.assertIn("docs/milestone-e-prep-scope.md", roadmap)
        self.assertIn("docs/milestone-e-fixture-candidates.json", roadmap)
        self.assertIn("docs/milestone-e-prep-scope.md", status)
        self.assertIn("docs/milestone-e-fixture-candidates.json", status)
        self.assertIn("docs/milestone-e-internal-trust-loop-walkthrough.json", roadmap)
        self.assertIn("docs/milestone-e-internal-trust-loop-walkthrough.json", status)
        self.assertIn("docs/milestone-e-internal-trust-loop-use-protocol.json", roadmap)
        self.assertIn("docs/milestone-e-internal-trust-loop-use-protocol.json", status)
        self.assertIn(
            "docs/milestone-e-internal-trust-loop-rehearsal-evidence-matrix.json",
            roadmap,
        )
        self.assertIn(
            "docs/milestone-e-internal-trust-loop-rehearsal-evidence-matrix.json",
            status,
        )
        self.assertIn("docs/milestone-e-internal-trust-loop-blocker-ledger.json", roadmap)
        self.assertIn("docs/milestone-e-internal-trust-loop-blocker-ledger.json", status)
        self.assertIn("docs/milestone-e-public-approval-lane-blockers.json", roadmap)
        self.assertIn("docs/milestone-e-public-approval-lane-blockers.json", status)
        self.assertIn("docs/milestone-e-public-beta-approval-prep.json", roadmap)
        self.assertIn("docs/milestone-e-public-beta-approval-prep.json", status)
        self.assertIn("docs/milestone-e-package-publication-approval-prep.json", roadmap)
        self.assertIn("docs/milestone-e-package-publication-approval-prep.json", status)
        self.assertIn("public beta approval prep", normalized_roadmap)
        self.assertIn("public beta approval prep", normalized_status)
        self.assertIn("source-only public beta", normalized_roadmap)
        self.assertIn("source-only public beta", normalized_status)
        self.assertIn("package publication approval prep", normalized_roadmap)
        self.assertIn("package publication approval prep", normalized_status)
        self.assertIn("does not approve package publication", normalized_roadmap)
        self.assertIn("does not approve package publication", normalized_status)
        self.assertIn("make milestone-e-prep", status)
        self.assertIn("blocked-output alignment", normalized_roadmap)
        self.assertIn("blocked-output alignment", normalized_status)
        self.assertIn("evidence-lane alignment", normalized_roadmap)
        self.assertIn("evidence-lane alignment", normalized_status)
        self.assertIn("diagnostic-boundary alignment", normalized_roadmap)
        self.assertIn("diagnostic-boundary alignment", normalized_status)
        self.assertIn("promotion-status alignment", normalized_roadmap)
        self.assertIn("promotion-status alignment", normalized_status)
        self.assertIn("source-status alignment", normalized_roadmap)
        self.assertIn("source-status alignment", normalized_status)
        self.assertIn("applies-to binding alignment", normalized_roadmap)
        self.assertIn("applies-to binding alignment", normalized_status)
        self.assertIn("required-before alignment", normalized_roadmap)
        self.assertIn("required-before alignment", normalized_status)
        self.assertIn("validation-record source-head alignment", normalized_roadmap)
        self.assertIn("validation-record source-head alignment", normalized_status)
        self.assertIn("schemas/ethos-milestone-e-fixture-candidates.schema.json", roadmap)
        self.assertIn("schemas/ethos-milestone-e-fixture-promotion-criteria.schema.json", roadmap)
        self.assertIn(
            "schemas/ethos-milestone-e-internal-trust-loop-walkthrough.schema.json",
            roadmap,
        )
        self.assertIn(
            "schemas/ethos-milestone-e-internal-trust-loop-use-protocol.schema.json",
            roadmap,
        )
        self.assertIn(
            "schemas/ethos-milestone-e-internal-trust-loop-rehearsal-evidence-matrix.schema.json",
            roadmap,
        )
        self.assertIn(
            "schemas/ethos-milestone-e-internal-trust-loop-blocker-ledger.schema.json",
            roadmap,
        )
        self.assertIn("schema-validated by `schemas/validate_examples.py`", status)
        self.assertIn(
            "later public-report, project-maintained PDFium build, stable CLI/Python docs, and "
            "hosted demo work remain blocked on explicit claim-audit and release-scope decisions",
            roadmap,
        )
        self.assertIn("Still absent or not claimable:", status)
        self.assertIn("exact approved source-only public beta wording", status)
        self.assertIn("Broader public result language remains blocked", status)
        self.assertIn(
            "intentionally excludes public-report, release, package, hosted, and broad "
            "demo-generation workflows",
            status,
        )

    def test_make_target_is_narrow_and_guarded(self) -> None:
        block = target_block("milestone-e-prep")

        expected = [
            "$(PYTHON) .github/scripts/test_execution_status.py",
            "$(PYTHON) .github/scripts/test_roadmap_status.py",
            "$(PYTHON) .github/scripts/test_public_surface_posture.py",
            "$(PYTHON) .github/scripts/claims_gate.py",
            "$(PYTHON) .github/scripts/test_public_prealpha_wording_approval.py",
            "$(PYTHON) .github/scripts/test_release_readiness_next_steps_approval.py",
            "$(PYTHON) .github/scripts/test_h1_public_safe_comparison_closeout.py",
            "$(PYTHON) .github/scripts/test_h2_source_snapshot_scope_approval.py",
            "$(PYTHON) .github/scripts/test_milestone_e_source_snapshot_candidate_audit.py",
            "$(PYTHON) .github/scripts/test_h2_source_snapshot_candidate_evidence.py",
            "$(PYTHON) .github/scripts/test_h2_source_snapshot_closeout.py",
            "$(PYTHON) schemas/validate_examples.py",
            "$(PYTHON) .github/scripts/test_milestone_e_schema_registry_alignment.py",
            "$(PYTHON) .github/scripts/test_milestone_e_public_boundary_alignment.py",
            "$(PYTHON) .github/scripts/test_milestone_e_blocked_output_alignment.py",
            "$(PYTHON) .github/scripts/test_milestone_e_evidence_lane_alignment.py",
            "$(PYTHON) .github/scripts/test_milestone_e_diagnostic_boundary_alignment.py",
            "$(PYTHON) .github/scripts/test_milestone_e_promotion_status_alignment.py",
            "$(PYTHON) .github/scripts/test_milestone_e_source_status_alignment.py",
            "$(PYTHON) .github/scripts/test_milestone_e_applies_to_binding_alignment.py",
            "$(PYTHON) .github/scripts/test_milestone_e_required_before_alignment.py",
            "$(PYTHON) .github/scripts/test_milestone_e_prep_scope.py",
            "$(PYTHON) .github/scripts/test_milestone_e_fixture_promotion_criteria.py",
            "$(PYTHON) .github/scripts/test_milestone_e_fixture_candidate_blocker_alignment_validation_record.py",
            "$(PYTHON) .github/scripts/test_milestone_e_prep_scope_structured_blocker_validation_record.py",
            "$(PYTHON) .github/scripts/test_milestone_e_internal_trust_loop_walkthrough.py",
            "$(PYTHON) .github/scripts/test_milestone_e_internal_trust_loop_use_protocol.py",
            "$(PYTHON) .github/scripts/test_milestone_e_internal_trust_loop_rehearsal_evidence_matrix.py",
            "$(PYTHON) .github/scripts/test_milestone_e_internal_trust_loop_blocker_ledger.py",
            "$(PYTHON) .github/scripts/test_milestone_e_fixture_promotion_criteria_validation_record.py",
            "$(PYTHON) .github/scripts/test_milestone_e_internal_trust_loop_walkthrough_validation_record.py",
            "$(PYTHON) .github/scripts/test_milestone_e_internal_trust_loop_use_protocol_validation_record.py",
            "$(PYTHON) .github/scripts/test_milestone_e_internal_trust_loop_rehearsal_evidence_matrix_validation_record.py",
            "$(PYTHON) .github/scripts/test_milestone_e_internal_trust_loop_blocker_ledger_validation_record.py",
            "$(PYTHON) .github/scripts/test_milestone_e_native_grounding_baseline_rehearsal_validation_record.py",
            "$(PYTHON) .github/scripts/test_milestone_e_diagnostic_boundary_check_rehearsal_validation_record.py",
            "$(PYTHON) .github/scripts/test_milestone_e_capability_downgrade_boundary_rehearsal_validation_record.py",
            "$(PYTHON) .github/scripts/test_milestone_e_opendataloader_adapter_grounding_rehearsal_validation_record.py",
            "$(PYTHON) .github/scripts/test_milestone_e_pinned_opendataloader_fixture_path_rehearsal_validation_record.py",
            "$(PYTHON) .github/scripts/test_milestone_e_crop_descriptor_source_bound_shape_rehearsal_validation_record.py",
            "$(PYTHON) .github/scripts/test_milestone_e_rag_chunk_artifact_loop_rehearsal_validation_record.py",
            "$(PYTHON) .github/scripts/test_milestone_e_security_report_artifact_loop_rehearsal_validation_record.py",
            "$(PYTHON) .github/scripts/test_milestone_e_demo_narrative_index_rehearsal_validation_record.py",
            "$(PYTHON) .github/scripts/test_milestone_e_rehearsal_row_record_coverage_validation.py",
            "$(PYTHON) .github/scripts/test_milestone_e_schema_registry_alignment_validation_record.py",
            "$(PYTHON) .github/scripts/test_milestone_e_public_boundary_alignment_validation_record.py",
            "$(PYTHON) .github/scripts/test_milestone_e_blocked_output_alignment_validation_record.py",
            "$(PYTHON) .github/scripts/test_milestone_e_evidence_lane_alignment_validation_record.py",
            "$(PYTHON) .github/scripts/test_milestone_e_diagnostic_boundary_alignment_validation_record.py",
            "$(PYTHON) .github/scripts/test_milestone_e_promotion_status_alignment_validation_record.py",
            "$(PYTHON) .github/scripts/test_milestone_e_source_status_alignment_validation_record.py",
            "$(PYTHON) .github/scripts/test_milestone_e_applies_to_binding_alignment_validation_record.py",
            "$(PYTHON) .github/scripts/test_milestone_e_required_before_alignment_validation_record.py",
            "$(PYTHON) .github/scripts/test_milestone_e_public_approval_lane_blockers.py",
            "$(PYTHON) .github/scripts/test_milestone_e_public_approval_lane_blockers_validation_record.py",
            "$(PYTHON) .github/scripts/test_milestone_e_public_beta_approval_prep.py",
            "$(PYTHON) .github/scripts/test_milestone_e_public_beta_approval_prep_validation_record.py",
            "$(PYTHON) .github/scripts/test_milestone_e_public_beta_required_evidence_records.py",
            "$(PYTHON) .github/scripts/test_milestone_e_public_beta_source_only_approval.py",
            "$(PYTHON) .github/scripts/test_milestone_e_package_publication_approval_prep.py",
            "$(PYTHON) .github/scripts/test_milestone_e_package_publication_approval_prep_validation_record.py",
            "$(PYTHON) .github/scripts/test_milestone_e_package_publication_prep_approval_validation_record.py",
            "$(PYTHON) .github/scripts/test_milestone_e_package_publication_evidence_records.py",
            "$(PYTHON) .github/scripts/test_milestone_e_package_publication_metadata_readiness.py",
            "$(PYTHON) .github/scripts/test_milestone_e_package_publication_dry_run_smoke.py",
    "$(PYTHON) .github/scripts/test_milestone_e_package_publication_version_tag_policy.py",
    "$(PYTHON) .github/scripts/test_milestone_e_package_publication_pdfium_boundary.py",
    "$(PYTHON) .github/scripts/test_milestone_e_package_publication_dependency_ordering.py",
    "$(PYTHON) .github/scripts/test_milestone_e_package_publication_manifest_migration_prep.py",
    "$(PYTHON) .github/scripts/test_milestone_e_package_publication_registry_assembly_prep.py",
    "$(PYTHON) .github/scripts/test_milestone_e_package_publication_real_version_selection_prep.py",
    "$(PYTHON) .github/scripts/test_milestone_e_package_publication_tag_creation_prep.py",
    "$(PYTHON) .github/scripts/test_milestone_e_package_publication_manifest_activation_prep.py",
    "$(PYTHON) .github/scripts/test_milestone_e_validation_command_index.py",
            "$(PYTHON) .github/scripts/test_milestone_e_validation_command_index_validation_record.py",
            "$(PYTHON) .github/scripts/test_milestone_e_validation_record_index.py",
            "$(PYTHON) .github/scripts/test_milestone_e_validation_record_index_validation_record.py",
            "$(PYTHON) .github/scripts/test_milestone_e_validation_source_head_alignment.py",
            "$(PYTHON) .github/scripts/test_milestone_e_validation_source_head_alignment_validation_record.py",
            "$(PYTHON) .github/scripts/test_milestone_e_prep_guard_sequence_index.py",
            "$(PYTHON) .github/scripts/test_milestone_e_prep_guard_sequence_index_validation_record.py",
            "$(PYTHON) .github/scripts/test_milestone_e_prep_validation_record.py",
            "$(PYTHON) .github/scripts/test_milestone_e_final_closeout_record.py",
            "git diff --check",
        ]
        commands = [line.strip() for line in block.splitlines() if line.strip()]
        self.assertEqual(expected, commands)

        for excluded in [
            "release-",
            "third-party-license-manifest",
            "release-notice-draft",
            "deploy",
            "publish",
            "benchmark-report",
            "ethos-bench",
        ]:
            self.assertNotIn(excluded, block)

    def test_ci_runs_prep_scope_guard(self) -> None:
        text = read(CI_WORKFLOW)

        self.assertIn("python3 .github/scripts/test_milestone_e_prep_scope.py", text)
        self.assertEqual(1, text.count("python3 .github/scripts/test_milestone_e_prep_scope.py"))

    def test_schema_validation_covers_e_prep_json_artifacts(self) -> None:
        validate_examples = read(VALIDATE_EXAMPLES)
        schemas_readme = read(SCHEMAS_README)
        candidates_schema = json.loads(FIXTURE_CANDIDATES_SCHEMA.read_text(encoding="utf-8"))
        criteria_schema = json.loads(FIXTURE_PROMOTION_CRITERIA_SCHEMA.read_text(encoding="utf-8"))
        walkthrough_schema = json.loads(TRUST_LOOP_WALKTHROUGH_SCHEMA.read_text(encoding="utf-8"))
        walkthrough = json.loads(TRUST_LOOP_WALKTHROUGH.read_text(encoding="utf-8"))
        protocol_schema = json.loads(TRUST_LOOP_USE_PROTOCOL_SCHEMA.read_text(encoding="utf-8"))
        protocol = json.loads(TRUST_LOOP_USE_PROTOCOL.read_text(encoding="utf-8"))
        matrix_schema = json.loads(
            TRUST_LOOP_REHEARSAL_EVIDENCE_MATRIX_SCHEMA.read_text(encoding="utf-8")
        )
        matrix = json.loads(TRUST_LOOP_REHEARSAL_EVIDENCE_MATRIX.read_text(encoding="utf-8"))
        ledger_schema = json.loads(TRUST_LOOP_BLOCKER_LEDGER_SCHEMA.read_text(encoding="utf-8"))
        ledger = json.loads(TRUST_LOOP_BLOCKER_LEDGER.read_text(encoding="utf-8"))
        lane_schema = json.loads(PUBLIC_APPROVAL_LANE_BLOCKERS_SCHEMA.read_text(encoding="utf-8"))
        lane_ledger = json.loads(PUBLIC_APPROVAL_LANE_BLOCKERS.read_text(encoding="utf-8"))
        beta_schema = json.loads(PUBLIC_BETA_APPROVAL_PREP_SCHEMA.read_text(encoding="utf-8"))
        beta_prep = json.loads(PUBLIC_BETA_APPROVAL_PREP.read_text(encoding="utf-8"))
        package_schema = json.loads(
            PACKAGE_PUBLICATION_APPROVAL_PREP_SCHEMA.read_text(encoding="utf-8")
        )
        package_prep = json.loads(PACKAGE_PUBLICATION_APPROVAL_PREP.read_text(encoding="utf-8"))

        self.assertEqual(False, candidates_schema["additionalProperties"])
        self.assertEqual(False, criteria_schema["additionalProperties"])
        self.assertEqual(False, walkthrough_schema["additionalProperties"])
        self.assertEqual(False, protocol_schema["additionalProperties"])
        self.assertEqual(False, matrix_schema["additionalProperties"])
        self.assertEqual(False, ledger_schema["additionalProperties"])
        self.assertEqual(False, lane_schema["additionalProperties"])
        self.assertEqual(False, beta_schema["additionalProperties"])
        self.assertEqual(False, package_schema["additionalProperties"])
        self.assertEqual(
            "internal_trust_loop_walkthrough_plan",
            walkthrough["scope"],
        )
        self.assertEqual(
            "internal_trust_loop_use_protocol",
            protocol["scope"],
        )
        self.assertEqual(
            "internal_trust_loop_rehearsal_evidence_matrix",
            matrix["scope"],
        )
        self.assertEqual("internal_trust_loop_blocker_ledger", ledger["scope"])
        self.assertEqual("public_approval_lane_blocker_ledger", lane_ledger["scope"])
        self.assertEqual("public_beta_approval_prep", beta_prep["scope"])
        self.assertEqual("package_publication_approval_prep", package_prep["scope"])
        self.assertIn("ethos-milestone-e-fixture-candidates.schema.json", validate_examples)
        self.assertIn("docs\" / \"milestone-e-fixture-candidates.json", validate_examples)
        self.assertIn(
            "ethos-milestone-e-fixture-promotion-criteria.schema.json",
            validate_examples,
        )
        self.assertIn(
            "docs\" / \"milestone-e-fixture-promotion-criteria.json",
            validate_examples,
        )
        self.assertIn(
            "ethos-milestone-e-internal-trust-loop-walkthrough.schema.json",
            validate_examples,
        )
        self.assertIn(
            "docs\" / \"milestone-e-internal-trust-loop-walkthrough.json",
            validate_examples,
        )
        self.assertIn(
            "ethos-milestone-e-internal-trust-loop-use-protocol.schema.json",
            validate_examples,
        )
        self.assertIn(
            "docs\" / \"milestone-e-internal-trust-loop-use-protocol.json",
            validate_examples,
        )
        self.assertIn(
            "ethos-milestone-e-internal-trust-loop-rehearsal-evidence-matrix.schema.json",
            validate_examples,
        )
        self.assertIn(
            "docs\" / \"milestone-e-internal-trust-loop-rehearsal-evidence-matrix.json",
            validate_examples,
        )
        self.assertIn(
            "ethos-milestone-e-internal-trust-loop-blocker-ledger.schema.json",
            validate_examples,
        )
        self.assertIn(
            "docs\" / \"milestone-e-internal-trust-loop-blocker-ledger.json",
            validate_examples,
        )
        self.assertIn(
            "ethos-milestone-e-public-approval-lane-blockers.schema.json",
            validate_examples,
        )
        self.assertIn(
            "docs\" / \"milestone-e-public-approval-lane-blockers.json",
            validate_examples,
        )
        self.assertIn(
            "ethos-milestone-e-public-beta-approval-prep.schema.json",
            validate_examples,
        )
        self.assertIn(
            "docs\" / \"milestone-e-public-beta-approval-prep.json",
            validate_examples,
        )
        self.assertIn(
            "ethos-milestone-e-package-publication-approval-prep.schema.json",
            validate_examples,
        )
        self.assertIn(
            "docs\" / \"milestone-e-package-publication-approval-prep.json",
            validate_examples,
        )
        self.assertIn("ethos-milestone-e-fixture-candidates.schema.json", schemas_readme)
        self.assertIn(
            "ethos-milestone-e-fixture-promotion-criteria.schema.json",
            schemas_readme,
        )
        self.assertIn(
            "ethos-milestone-e-internal-trust-loop-walkthrough.schema.json",
            schemas_readme,
        )
        self.assertIn(
            "ethos-milestone-e-internal-trust-loop-use-protocol.schema.json",
            schemas_readme,
        )
        self.assertIn(
            "ethos-milestone-e-internal-trust-loop-rehearsal-evidence-matrix.schema.json",
            schemas_readme,
        )
        self.assertIn(
            "ethos-milestone-e-internal-trust-loop-blocker-ledger.schema.json",
            schemas_readme,
        )
        self.assertIn(
            "ethos-milestone-e-public-approval-lane-blockers.schema.json",
            schemas_readme,
        )
        self.assertIn(
            "ethos-milestone-e-public-beta-approval-prep.schema.json",
            schemas_readme,
        )
        self.assertIn(
            "ethos-milestone-e-package-publication-approval-prep.schema.json",
            schemas_readme,
        )

    def test_prep_scope_avoids_public_launch_posture(self) -> None:
        text = normalized(PREP_SCOPE).lower()

        forbidden = [
            "public beta is approved",
            "release-ready",
            "package-ready",
            "production-ready",
            "benchmark-validated",
            "launch-ready",
        ]
        for phrase in forbidden:
            self.assertNotIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
