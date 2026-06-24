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
LANE_BLOCKERS = ROOT / "docs/milestone-e-public-approval-lane-blockers.json"
VALIDATION_README = ROOT / "docs/validation/README.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"
RECORD = (
    ROOT
    / "docs/validation/milestone-e-package-publication-manifest-migration-prep-validation-2026-06-21.md"
)

FORBIDDEN_SCOPE_EXPANSION = [
    "public reports are approved",
    "public result wording approved",
    "release-ready",
    "release artifact approved",
    "package-ready",
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


class MilestoneEPackagePublicationManifestMigrationPrepTests(unittest.TestCase):
    def test_package_prep_artifact_records_manifest_migration_prep(self) -> None:
        prep = load_json(PREP)
        lane_blockers = load_json(LANE_BLOCKERS)
        status = prep["evidence_review_status"]["install_build_smoke_path"]
        blocker_text = " ".join(prep["explicit_blockers"])
        [package_lane] = [
            lane for lane in lane_blockers["approval_lanes"] if lane["lane_id"] == "package-publication"
        ]
        lane_blocker_text = " ".join(package_lane["explicit_blockers"])

        self.assertEqual(
            "docs/validation/"
            "milestone-e-package-publication-manifest-migration-prep-validation-2026-06-21.md",
            prep["follow_up_records"]["package_manifest_migration_prep"],
        )
        self.assertIn("manifest-migration prep recorded", status)
        self.assertIn("registry-assembly prep recorded", status)
        self.assertIn("manifest activation applied for source review", status)
        self.assertIn("publication remains blocked", status)
        self.assertIn("registry-backed dependent package assembly activation", blocker_text)
        self.assertIn("package dependency manifest activation", blocker_text)
        self.assertIn("real package version selection", blocker_text)
        self.assertIn("package tag creation", blocker_text)
        self.assertIn("registry-backed dependent package assembly activation", lane_blocker_text)
        self.assertIn("package dependency manifest activation", lane_blocker_text)

    def test_current_manifests_remain_unmigrated_source_tree_manifests(self) -> None:
        workspace = read(ROOT / "Cargo.toml")
        core = read(ROOT / "crates/ethos-core/Cargo.toml")
        verify = read(ROOT / "crates/ethos-verify/Cargo.toml")
        pdf = read(ROOT / "crates/ethos-pdf/Cargo.toml")

        self.assertIn('name = "ethos-doc-core"', core)
        self.assertIn('[lib]\nname = "ethos_core"', core)
        self.assertIn('reserved_crates_io_name = "ethos-doc-core"', core)
        self.assertNotIn("publish = false", core)
        self.assertNotIn("publish = false", verify)
        self.assertNotIn("publish = false", pdf)
        self.assertIn(
            'ethos-core = { package = "ethos-doc-core", path = "crates/ethos-core", version = "0.1.2", default-features = false }',
            workspace,
        )
        self.assertIn('ethos-core = { workspace = true, features = ["grounding", "verify-types"] }', verify)
        self.assertIn('ethos-core = { workspace = true, features = ["full"] }', pdf)
        for manifest in (verify, pdf):
            self.assertNotIn('package = "ethos-doc-core"', manifest)

    def test_manifest_migration_prep_record_names_future_shape_without_activation(self) -> None:
        record = normalized(RECORD)

        self.assertIn("Validated source HEAD before this record: `421fddd`", record)
        self.assertIn(
            "Status: **pass for package manifest-migration prep with publication blocked**",
            record,
        )
        self.assertIn("future core package-name migration", record)
        self.assertIn('name = "ethos-doc-core"', record)
        self.assertIn(
            'ethos-core = { package = "ethos-doc-core", path = "crates/ethos-core", '
            'version = "<approved-version>", default-features = false }',
            record,
        )
        self.assertIn('ethos-core = { workspace = true, features = ["grounding", "verify-types"] }', record)
        self.assertIn('ethos-core = { workspace = true, features = ["full"] }', record)
        self.assertIn("No Cargo manifest is changed by this record", record)
        self.assertIn("Package dependency manifest activation remains blocked", record)
        self.assertIn("Registry-backed dependent package assembly remains blocked", record)
        self.assertIn("Real package version selection and package tag creation remain blocked", record)

    def test_validation_record_is_indexed_and_names_commands(self) -> None:
        readme = read(VALIDATION_README)
        record = normalized(RECORD)

        self.assertIn(RECORD.name, readme)
        self.assertIn(
            "python3 .github/scripts/test_milestone_e_package_publication_manifest_migration_prep.py",
            record,
        )
        self.assertIn("python3 .github/scripts/test_public_surface_posture.py", record)
        self.assertIn("python3 .github/scripts/claims_gate.py", record)
        self.assertIn("cargo build --locked -p ethos-cli", record)
        self.assertIn("make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python", record)
        self.assertIn("git diff --check", record)

    def test_make_and_ci_run_guard_after_dependency_ordering(self) -> None:
        make_block = target_block("milestone-e-prep")
        ci = read(CI_WORKFLOW)
        dependency_guard = "test_milestone_e_package_publication_dependency_ordering.py"
        migration_guard = "test_milestone_e_package_publication_manifest_migration_prep.py"

        for text, prefix in ((make_block, "$(PYTHON) .github/scripts/"), (ci, "python3 .github/scripts/")):
            self.assertIn(prefix + migration_guard, text)
            self.assertLess(text.index(prefix + dependency_guard), text.index(prefix + migration_guard))

    def test_no_scope_expansion_language_or_private_paths(self) -> None:
        for path in (RECORD, ROOT / "docs/milestone-e-package-publication-approval-prep.json"):
            lower = normalized(path).lower()
            raw = read(path)

            for phrase in FORBIDDEN_SCOPE_EXPANSION:
                self.assertNotIn(phrase, lower, str(path))
            self.assertNotIn("/Users/", raw, str(path))
            self.assertNotIn("/private/tmp", raw, str(path))
            self.assertNotIn("/private/var", raw, str(path))
            self.assertNotIn("/var/folders", raw, str(path))
            self.assertNotIn("saumildiwaker", raw, str(path))
            self.assertNotIn("Desktop/Stuff", raw, str(path))
            self.assertNotIn("project/repo/ethos", raw, str(path))
            self.assertNotIn("docs/.roadmap.md.swp", raw, str(path))
            self.assertNotIn("web/", raw, str(path))


if __name__ == "__main__":
    unittest.main()
