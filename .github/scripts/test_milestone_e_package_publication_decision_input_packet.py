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
    "milestone-e-package-publication-decision-input-packet-validation-2026-06-21.md"
)
VALIDATION_README = ROOT / "docs/validation/README.md"
PREP_SCOPE = ROOT / "docs/milestone-e-prep-scope.md"
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"

SOURCE_COMMIT = "54bf70f57b8c357ec76059e31d203b80ade7c0e4"
SOURCE_SHORT = "54bf70f"
SOURCE_TREE = "5a197bee718e3b31399563340169e9efd4f1317c"
HISTORICAL_CANDIDATE_CRATES = [
    "ethos-doc-core mapped from crates/ethos-core; package-name migration remains pending",
    "ethos-verify mapped from crates/ethos-verify; dependency manifest activation remains pending",
    "ethos-pdf mapped from crates/ethos-pdf; dependency manifest activation and PDFium boundary confirmation must remain current",
]
HISTORICAL_CANDIDATE_MANIFEST_DIFF = [
    "crates/ethos-core/Cargo.toml candidate package-name migration: package.name ethos-core -> ethos-doc-core; current manifest remains unchanged",
    "crates/ethos-verify/Cargo.toml candidate dependency activation: ethos_core package alias points at ethos-doc-core; current manifest remains unchanged",
    "crates/ethos-pdf/Cargo.toml candidate dependency activation: ethos_core package alias points at ethos-doc-core; current manifest remains unchanged",
    "included candidate crates require later publish-flag activation only after dedicated approval; current manifests remain publish=false",
]
HISTORICAL_NON_APPROVALS = [
    "this exact decision input packet does not select a package publication version",
    "this exact decision input packet does not create a package tag",
    "this exact decision input packet does not change Cargo manifests",
    "this exact decision input packet does not activate package dependency manifests",
    "this exact decision input packet does not create a registry",
    "this exact decision input packet does not activate registry-backed dependent package assembly",
    "this exact decision input packet does not invite public installation",
    "this exact decision input packet does not approve package publication",
]
HISTORICAL_RETAINED_BLOCKERS = [
    "candidate package version map is recorded but no package publication version is selected",
    "candidate package tag names are recorded but no package tag is created",
    "candidate manifest activation diff is recorded but no Cargo manifest is changed",
    "registry-backed dependent package assembly evidence remains required",
    "public installation remains blocked",
    "package publication remains blocked",
    "real-version cargo publish remains blocked",
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


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args],
        cwd=ROOT,
        encoding="utf-8",
        stderr=subprocess.DEVNULL,
    ).strip()


class MilestoneEPackagePublicationDecisionInputPacketTests(unittest.TestCase):
    def test_packet_is_schema_bound_indexed_and_source_bound(self) -> None:
        prep = load_json(PREP)
        readme = read(VALIDATION_README)
        record = normalized(RECORD)
        packet = prep["package_publication_decision_input_packet"]

        self.assertIn(RECORD.name, readme)
        self.assertIn("package publication decision-input packet validation", re.sub(r"\s+", " ", readme))
        self.assertEqual(
            "docs/validation/milestone-e-package-publication-decision-input-packet-validation-2026-06-21.md",
            prep["follow_up_records"]["package_decision_input_packet"],
        )
        self.assertEqual("decision_input_packet_recorded_publication_blocked", packet["packet_state"])
        self.assertEqual(SOURCE_COMMIT, packet["source_binding"]["candidate_source_commit"])
        self.assertEqual(SOURCE_TREE, packet["source_binding"]["candidate_source_tree"])
        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Candidate source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Candidate source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_packet_records_exact_inputs_without_approval(self) -> None:
        packet = load_json(PREP)["package_publication_decision_input_packet"]
        record = normalized(RECORD)

        self.assertEqual(3, len(packet["candidate_crates"]))
        self.assertIn("ethos-doc-core mapped from crates/ethos-core", " ".join(packet["candidate_crates"]))
        self.assertIn("ethos-verify mapped from crates/ethos-verify", " ".join(packet["candidate_crates"]))
        self.assertIn("ethos-pdf mapped from crates/ethos-pdf", " ".join(packet["candidate_crates"]))
        self.assertEqual(3, len(packet["candidate_version_map"]))
        self.assertEqual(3, len(packet["candidate_package_tag_names"]))
        self.assertEqual(4, len(packet["candidate_manifest_activation_diff"]))
        self.assertIn("0.1.0; not selected or approved", " ".join(packet["candidate_version_map"]))
        self.assertIn("tag is not created", " ".join(packet["candidate_package_tag_names"]))
        self.assertIn("source package-name activation", " ".join(packet["candidate_manifest_activation_diff"]))
        self.assertIn("publish=false remains", " ".join(packet["candidate_manifest_activation_diff"]))
        self.assertIn("no registry is created and no assembly is activated", packet["registry_backed_assembly_input"])
        self.assertIn("public installation remains blocked", packet["candidate_public_installation_wording"])
        self.assertIn("this exact decision input packet does not approve package publication", packet["non_approvals"])
        self.assertIn("this exact decision input packet does not invite public installation", packet["non_approvals"])
        self.assertIn("package publication remains blocked", packet["retained_blockers"])
        self.assertIn("public installation remains blocked", packet["retained_blockers"])
        for values in (
            HISTORICAL_CANDIDATE_CRATES,
            packet["candidate_version_map"],
            packet["candidate_package_tag_names"],
            HISTORICAL_CANDIDATE_MANIFEST_DIFF,
            packet["required_before_approval"],
            HISTORICAL_NON_APPROVALS,
            HISTORICAL_RETAINED_BLOCKERS,
        ):
            for value in values:
                self.assertIn(value, record)

    def test_candidate_tags_do_not_exist_and_manifests_remain_inactive(self) -> None:
        packet = load_json(PREP)["package_publication_decision_input_packet"]
        core_manifest = read(ROOT / "crates/ethos-core/Cargo.toml")
        verify_manifest = read(ROOT / "crates/ethos-verify/Cargo.toml")
        pdf_manifest = read(ROOT / "crates/ethos-pdf/Cargo.toml")

        for value in packet["candidate_package_tag_names"]:
            tag = value.split(": ", maxsplit=1)[1].split(";", maxsplit=1)[0]
            self.assertEqual("", git("tag", "--list", tag))
        self.assertIn('name = "ethos-doc-core"', core_manifest)
        self.assertIn("publish = false", core_manifest)
        self.assertIn('reserved_crates_io_name = "ethos-doc-core"', core_manifest)
        self.assertIn('name = "ethos-verify"', verify_manifest)
        self.assertIn("publish = false", verify_manifest)
        self.assertIn('name = "ethos-pdf"', pdf_manifest)
        self.assertIn("publish = false", pdf_manifest)
        self.assertNotIn('package = "ethos-doc-core"', verify_manifest)
        self.assertNotIn('package = "ethos-doc-core"', pdf_manifest)

    def test_docs_reference_decision_input_packet_and_blockers(self) -> None:
        for path in (PREP_SCOPE, ROADMAP, EXECUTION_STATUS, VALIDATION_README):
            doc = normalized(path)

            self.assertIn(RECORD.name, doc, str(path))
            self.assertIn("package publication decision input packet", doc.lower(), str(path))
            self.assertIn("package publication remains blocked", doc, str(path))
            self.assertIn("public installation remains blocked", doc, str(path))

    def test_make_and_ci_run_packet_after_resolution_plan(self) -> None:
        make_block = target_block("milestone-e-prep")
        ci = read(CI_WORKFLOW)
        resolution_guard = "test_milestone_e_package_publication_approval_resolution_plan.py"
        packet_guard = "test_milestone_e_package_publication_decision_input_packet.py"
        public_facing_guard = "test_milestone_e_public_facing_readiness_ledger.py"

        for text, prefix in ((make_block, "$(PYTHON) .github/scripts/"), (ci, "python3 .github/scripts/")):
            self.assertIn(prefix + packet_guard, text)
            self.assertEqual(1, text.count(prefix + packet_guard))
            self.assertLess(text.index(prefix + resolution_guard), text.index(prefix + packet_guard))
            self.assertLess(text.index(prefix + packet_guard), text.index(prefix + public_facing_guard))

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
