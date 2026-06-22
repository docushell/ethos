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

from makefile_guard import target_block


ROOT = Path(__file__).resolve().parents[2]
PREP = ROOT / "docs/milestone-e-package-publication-approval-prep.json"
RECORD = (
    ROOT
    / "docs/validation/"
    "milestone-e-package-publication-decision-bundle-validation-2026-06-21.md"
)
VALIDATION_README = ROOT / "docs/validation/README.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"
HISTORICAL_REVIEW_BOUNDARY = [
    "package tag and source-commit decision inputs are recorded while creating no package tag",
    "package dependency manifest activation inputs are recorded while changing no Cargo manifest",
    "registry-backed dependent package assembly inputs are recorded while creating no registry and activating no assembly",
    "public installation wording and exclusion inputs are recorded while inviting no public installation",
]
HISTORICAL_CANDIDATE_CRATES = [
    "ethos-doc-core mapped from crates/ethos-core; package-name migration remains pending",
    "ethos-verify mapped from crates/ethos-verify; dependency manifest activation remains pending",
    "ethos-pdf mapped from crates/ethos-pdf; dependency manifest activation and PDFium boundary confirmation must remain current",
]
HISTORICAL_MANIFEST_ACTIVATION_DIFF = "not prepared; current Cargo manifests remain unchanged"
HISTORICAL_BUNDLE_NON_APPROVALS = [
    "this bundle does not select a package publication version",
    "this bundle does not create a package tag",
    "this bundle does not change Cargo manifests",
    "this bundle does not activate package dependency manifests",
    "this bundle does not create a registry",
    "this bundle does not activate registry-backed dependent package assembly",
    "this bundle does not invite public installation",
    "this bundle does not approve package publication",
]
HISTORICAL_PACKET_NON_APPROVALS = [
    "this packet does not select a package publication version",
    "this packet does not create a package tag",
    "this packet does not change Cargo manifests",
    "this packet does not activate package dependency manifests",
    "this packet does not create a registry",
    "this packet does not activate registry-backed dependent package assembly",
    "this packet does not invite public installation",
    "this packet does not approve package publication",
]

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


class MilestoneEPackagePublicationDecisionBundleValidationRecordTests(unittest.TestCase):
    def test_decision_bundle_record_is_indexed(self) -> None:
        readme = read(VALIDATION_README)
        normalized_readme = re.sub(r"\s+", " ", readme)

        self.assertIn(RECORD.name, readme)
        self.assertIn(
            "package publication decision-bundle validation for the combined decision inputs",
            normalized_readme,
        )

    def test_record_names_validation_commands(self) -> None:
        text = read(RECORD)

        self.assertIn("Validated source HEAD before this record: `63d8647`", text)
        self.assertIn(
            "python3 .github/scripts/test_milestone_e_package_publication_approval_prep.py",
            text,
        )
        self.assertIn(
            "python3 .github/scripts/"
            "test_milestone_e_package_publication_decision_bundle_validation_record.py",
            text,
        )
        self.assertIn("python3 .github/scripts/test_public_surface_posture.py", text)
        self.assertIn("python3 .github/scripts/claims_gate.py", text)
        self.assertIn("cargo build --locked -p ethos-cli", text)
        self.assertIn("make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python", text)
        self.assertIn("git diff --check", text)

    def test_record_matches_combined_decision_bundle_scope(self) -> None:
        prep = load_json(PREP)
        bundle = prep["package_publication_decision_prep_bundle"]
        record = normalized(RECORD)

        self.assertEqual("combined_decision_inputs_recorded_actions_blocked", bundle["decision_state"])
        for boundary in HISTORICAL_REVIEW_BOUNDARY:
            self.assertIn(boundary, record)
        for decision_input in bundle["required_decision_inputs"]:
            self.assertIn(decision_input, record)
        for non_approval in HISTORICAL_BUNDLE_NON_APPROVALS:
            self.assertIn(non_approval, record)
        for blocker in bundle["retained_blockers"]:
            self.assertIn(blocker, record)
        self.assertIn("Ethos remains source-only pre-alpha", record)
        self.assertIn("Package publication remains blocked", record)
        self.assertIn("Public installation remains blocked", record)

    def test_record_matches_non_activating_approval_request_packet(self) -> None:
        prep = load_json(PREP)
        packet = prep["package_publication_approval_request_packet"]
        record = normalized(RECORD)

        self.assertEqual("approval_request_packet_recorded_publication_blocked", packet["packet_state"])
        self.assertIn(packet["packet_state"], record)
        for candidate in HISTORICAL_CANDIDATE_CRATES:
            self.assertIn(candidate, record)
        for version in packet["package_version_map"]:
            self.assertIn(version, record)
        self.assertIn(packet["package_tag_name"], record)
        self.assertIn(packet["package_tag_source_commit"], record)
        self.assertIn(packet["package_tag_source_tree"], record)
        self.assertIn(HISTORICAL_MANIFEST_ACTIVATION_DIFF, record)
        self.assertIn(packet["registry_assembly_evidence"], record)
        self.assertIn(packet["public_installation_wording"], record)
        for exclusion in packet["explicit_exclusions"]:
            self.assertIn(exclusion, record)
        for required in packet["required_before_approval"]:
            self.assertIn(required, record)
        for non_approval in HISTORICAL_PACKET_NON_APPROVALS:
            self.assertIn(non_approval, record)
        for blocker in packet["retained_blockers"]:
            self.assertIn(blocker, record)

    def test_record_keeps_public_boundaries_explicit(self) -> None:
        record = normalized(RECORD)

        self.assertIn("Public reports remain blocked", record)
        self.assertIn("Public result wording remains blocked", record)
        self.assertIn("Release artifacts remain blocked", record)
        self.assertIn("Binaries remain blocked", record)
        self.assertIn("Wheels remain blocked", record)
        self.assertIn("Npm packages remain blocked", record)
        self.assertIn("Hosted surfaces remain blocked", record)
        self.assertIn("Production positioning remains blocked", record)
        self.assertIn("Public benchmark reports remain blocked", record)
        self.assertIn("Public benchmark claims remain blocked", record)
        self.assertIn("Project-maintained PDFium builds remain blocked", record)

    def test_make_and_ci_run_record_guard_after_combined_prep(self) -> None:
        make_block = target_block("milestone-e-prep")
        ci = read(CI_WORKFLOW)
        registry_activation_guard = (
            "test_milestone_e_package_publication_registry_assembly_activation_prep.py"
        )
        record_guard = "test_milestone_e_package_publication_decision_bundle_validation_record.py"
        command_guard = "test_milestone_e_validation_command_index.py"

        for text, prefix in ((make_block, "$(PYTHON) .github/scripts/"), (ci, "python3 .github/scripts/")):
            self.assertIn(prefix + record_guard, text)
            self.assertEqual(1, text.count(prefix + record_guard))
            self.assertLess(text.index(prefix + registry_activation_guard), text.index(prefix + record_guard))
            self.assertLess(text.index(prefix + record_guard), text.index(prefix + command_guard))

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
