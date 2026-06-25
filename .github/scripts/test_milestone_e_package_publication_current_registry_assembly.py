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

from cargo_manifest_guard import workspace_package_version
from makefile_guard import target_block


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / ".github/scripts/package_publication_candidate_activation.py"
RECORD = (
    ROOT
    / "docs/validation/"
    "milestone-e-package-publication-current-registry-assembly-validation-2026-06-22.md"
)
VALIDATION_README = ROOT / "docs/validation/README.md"
PREP_SCOPE = ROOT / "docs/milestone-e-prep-scope.md"
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"

SOURCE_COMMIT = "b48e2f2c7ff6f3507bbf84c6d603cf4a385b9875"
SOURCE_SHORT = "b48e2f2"
SOURCE_TREE = "4d660bd7c1de69259d0f8c59e6ac8d1c2cb6a3a3"
FORBIDDEN_SCOPE_EXPANSION = [
    "package publication approved",
    "package publication is approved",
    "public installation approved",
    "public installation is approved",
    "public installation wording is approved",
    "package tag creation approved",
    "release-ready",
    "release artifact approved",
    "package-ready",
    "packages are published",
    "published packages",
    "production-ready",
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


class MilestoneEPackagePublicationCurrentRegistryAssemblyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = run_candidate_activation()

    def test_current_registry_equivalent_assembly_passes_after_manifest_activation(self) -> None:
        result = self.result
        commands = [entry["command"] for entry in result["commands"]]

        self.assertEqual("pass", result["status"])
        self.assertEqual(workspace_package_version(read(ROOT / "Cargo.toml")), result["candidate_version"])
        self.assertEqual(["ethos-doc-core", "ethos-verify", "ethos-pdf"], result["candidate_packages"])
        self.assertEqual("pass", result["registry_equivalent_consumer_check"])
        self.assertTrue(result["source_manifest_activation_applied"])
        self.assertTrue(result["source_candidate_manifests_activated"])
        self.assertFalse(result["source_manifests_remain_blocked"])
        self.assertFalse(result["package_publication_approved"])
        self.assertFalse(result["public_installation_approved"])
        self.assertIn("cargo package --locked --offline -p ethos-doc-core --allow-dirty --no-verify", commands)
        self.assertIn("assemble candidate package artifact -p ethos-verify", commands)
        self.assertIn("assemble candidate package artifact -p ethos-pdf", commands)
        self.assertIn("cargo check --locked --offline", commands)

    def test_artifacts_and_manifest_shape_are_current(self) -> None:
        result = self.result
        activation = result["manifest_activation"]
        artifacts = {artifact["package"]: artifact for artifact in result["artifacts"]}

        self.assertEqual("ethos-doc-core", activation["core_package_name"])
        self.assertEqual("ethos_core", activation["core_library_name"])
        self.assertEqual("ethos-core", activation["dependency_key"])
        self.assertEqual(["grounding", "verify-types"], activation["verify_core_features"])
        self.assertEqual(["full"], activation["pdf_core_features"])
        self.assertEqual({"ethos-doc-core", "ethos-verify", "ethos-pdf"}, set(artifacts))
        candidate_version = self.result["candidate_version"]
        for artifact in artifacts.values():
            self.assertRegex(artifact["sha256"], r"^[0-9a-f]{64}$")
            self.assertTrue(artifact["crate_file"].endswith(f"-{candidate_version}.crate"))

    def test_source_candidate_manifests_are_activated_while_tags_and_registry_stay_absent(self) -> None:
        for manifest in (
            ROOT / "crates/ethos-core/Cargo.toml",
            ROOT / "crates/ethos-verify/Cargo.toml",
            ROOT / "crates/ethos-pdf/Cargo.toml",
        ):
            text = read(manifest)
            self.assertNotIn("publish = false", text, str(manifest))
            self.assertIn('publication_status = "approved_for_crates_io_publication"', text, str(manifest))

        for manifest in (
            ROOT / "crates/ethos-cli/Cargo.toml",
            ROOT / "crates/ethos-layout/Cargo.toml",
            ROOT / "crates/ethos-tables/Cargo.toml",
        ):
            self.assertIn("publish = false", read(manifest), str(manifest))

        self.assertFalse((ROOT / ".cargo/config.toml").exists())
        self.assertFalse((ROOT / "target/package-registry").exists())

    def test_record_is_indexed_and_source_bound(self) -> None:
        readme = normalized(VALIDATION_README)
        record = normalized(RECORD)

        self.assertIn(RECORD.name, readme)
        self.assertIn("package publication current registry-equivalent assembly validation", readme)
        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Current registry-equivalent assembly source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Current registry-equivalent assembly source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_docs_reference_current_assembly_and_retained_blockers(self) -> None:
        for path in (PREP_SCOPE, ROADMAP, EXECUTION_STATUS, VALIDATION_README):
            doc = normalized(path)

            self.assertIn(RECORD.name, doc, str(path))
            self.assertIn("current registry-equivalent assembly", doc.lower(), str(path))
            self.assertIn("package publication remains blocked", doc, str(path))
            self.assertIn("public installation remains blocked", doc, str(path))

    def test_make_and_ci_run_current_assembly_after_manifest_activation(self) -> None:
        make_block = target_block("milestone-e-prep")
        ci = read(CI_WORKFLOW)
        manifest_guard = "test_milestone_e_package_publication_manifest_activation_applied.py"
        assembly_guard = "test_milestone_e_package_publication_current_registry_assembly.py"
        readiness_guard = "test_milestone_e_public_facing_readiness_ledger.py"

        for text, prefix in ((make_block, "$(PYTHON) .github/scripts/"), (ci, "python3 .github/scripts/")):
            self.assertIn(prefix + assembly_guard, text)
            self.assertEqual(1, text.count(prefix + assembly_guard))
            self.assertLess(text.index(prefix + manifest_guard), text.index(prefix + assembly_guard))
            self.assertLess(text.index(prefix + assembly_guard), text.index(prefix + readiness_guard))

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
