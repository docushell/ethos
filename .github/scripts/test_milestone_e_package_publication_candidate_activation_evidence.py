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
SCRIPT = ROOT / ".github/scripts/package_publication_candidate_activation.py"
PREP = ROOT / "docs/milestone-e-package-publication-approval-prep.json"
RECORD = (
    ROOT
    / "docs/validation/"
    "milestone-e-package-publication-candidate-activation-evidence-validation-2026-06-22.md"
)
VALIDATION_README = ROOT / "docs/validation/README.md"
PREP_SCOPE = ROOT / "docs/milestone-e-prep-scope.md"
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"
ROOT_PROFILE = ROOT / "profiles/ethos-deterministic-v1.json"
PDF_PROFILE = ROOT / "crates/ethos-pdf/assets/ethos-deterministic-v1.json"

SOURCE_COMMIT = "6cf211cfae82c8ba7d6454a71e0922bd95a01f28"
SOURCE_SHORT = "6cf211c"
SOURCE_TREE = "ae76bc588b64dc1e8087d9096d52545a3560c2c0"
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


def run_candidate_activation() -> dict:
    result = subprocess.run(
        ["python3", str(SCRIPT), "--json"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise AssertionError(
            "candidate activation script failed\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return json.loads(result.stdout)


class MilestoneEPackagePublicationCandidateActivationEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = run_candidate_activation()

    def test_candidate_activation_script_passes_with_registry_equivalent_consumer(self) -> None:
        result = self.result
        commands = [entry["command"] for entry in result["commands"]]

        self.assertEqual("pass", result["status"])
        self.assertEqual("0.1.0", result["candidate_version"])
        self.assertEqual(["ethos-doc-core", "ethos-verify", "ethos-pdf"], result["candidate_packages"])
        self.assertEqual("pass", result["registry_equivalent_consumer_check"])
        self.assertTrue(result["source_manifests_remain_blocked"])
        self.assertFalse(result["package_publication_approved"])
        self.assertFalse(result["public_installation_approved"])
        self.assertNotIn("cargo generate-lockfile --offline", commands)
        self.assertNotIn("cargo vendor --locked --offline target/package-candidate-vendor", commands)
        self.assertIn("cargo package --locked --offline -p ethos-doc-core --allow-dirty --no-verify", commands)
        self.assertIn("cargo package --list --locked --offline -p ethos-verify --allow-dirty", commands)
        self.assertIn("cargo package --list --locked --offline -p ethos-pdf --allow-dirty", commands)
        self.assertIn("assemble candidate package artifact -p ethos-verify", commands)
        self.assertIn("assemble candidate package artifact -p ethos-pdf", commands)
        self.assertIn("cargo check --locked --offline", commands)

    def test_candidate_activation_preserves_import_and_dependency_shape(self) -> None:
        activation = self.result["manifest_activation"]
        checks = self.result["packaged_manifest_checks"]
        artifacts = {artifact["package"]: artifact for artifact in self.result["artifacts"]}

        self.assertEqual("ethos-doc-core", activation["core_package_name"])
        self.assertEqual("ethos_core", activation["core_library_name"])
        self.assertEqual("ethos-core", activation["dependency_key"])
        self.assertEqual(["grounding", "verify-types"], activation["verify_core_features"])
        self.assertEqual(["full"], activation["pdf_core_features"])
        self.assertTrue(all(checks.values()))
        self.assertEqual({"ethos-doc-core", "ethos-verify", "ethos-pdf"}, set(artifacts))
        for artifact in artifacts.values():
            self.assertRegex(artifact["sha256"], r"^[0-9a-f]{64}$")
            self.assertTrue(artifact["crate_file"].endswith("-0.1.0.crate"))

    def test_source_manifests_remain_blocked_and_profile_copy_is_in_sync(self) -> None:
        core_manifest = read(ROOT / "crates/ethos-core/Cargo.toml")
        verify_manifest = read(ROOT / "crates/ethos-verify/Cargo.toml")
        pdf_manifest = read(ROOT / "crates/ethos-pdf/Cargo.toml")
        pdf_lib = read(ROOT / "crates/ethos-pdf/src/lib.rs")

        self.assertEqual(read(ROOT_PROFILE), read(PDF_PROFILE))
        self.assertIn('include_str!("../assets/ethos-deterministic-v1.json")', pdf_lib)
        self.assertIn('name = "ethos-doc-core"', core_manifest)
        self.assertIn("publish = false", core_manifest)
        self.assertIn("publish = false", verify_manifest)
        self.assertIn("publish = false", pdf_manifest)
        self.assertNotIn('package = "ethos-doc-core"', verify_manifest)
        self.assertNotIn('package = "ethos-doc-core"', pdf_manifest)
        self.assertFalse((ROOT / ".cargo/config.toml").exists())
        self.assertFalse((ROOT / "target/package-registry").exists())

    def test_record_is_indexed_and_source_bound(self) -> None:
        prep = load_json(PREP)
        readme = read(VALIDATION_README)
        record = normalized(RECORD)

        self.assertIn(RECORD.name, readme)
        self.assertIn("package publication candidate activation evidence validation", readme)
        self.assertEqual(
            "docs/validation/"
            "milestone-e-package-publication-candidate-activation-evidence-validation-2026-06-22.md",
            prep["follow_up_records"]["package_candidate_activation_evidence"],
        )
        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Candidate activation evidence source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Candidate activation evidence source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_docs_reference_candidate_evidence_and_retained_blockers(self) -> None:
        for path in (PREP_SCOPE, ROADMAP, EXECUTION_STATUS, VALIDATION_README):
            doc = normalized(path)

            self.assertIn(RECORD.name, doc, str(path))
            self.assertIn("candidate activation evidence", doc.lower(), str(path))
            self.assertIn("package publication remains blocked", doc, str(path))
            self.assertIn("public installation remains blocked", doc, str(path))

    def test_make_and_ci_run_evidence_after_decision_record(self) -> None:
        make_block = target_block("milestone-e-prep")
        ci = read(CI_WORKFLOW)
        decision_guard = "test_milestone_e_package_publication_approval_decision_record.py"
        evidence_guard = "test_milestone_e_package_publication_candidate_activation_evidence.py"
        public_facing_guard = "test_milestone_e_public_facing_readiness_ledger.py"

        for text, prefix in ((make_block, "$(PYTHON) .github/scripts/"), (ci, "python3 .github/scripts/")):
            self.assertIn(prefix + evidence_guard, text)
            self.assertEqual(1, text.count(prefix + evidence_guard))
            self.assertLess(text.index(prefix + decision_guard), text.index(prefix + evidence_guard))
            self.assertLess(text.index(prefix + evidence_guard), text.index(prefix + public_facing_guard))

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
