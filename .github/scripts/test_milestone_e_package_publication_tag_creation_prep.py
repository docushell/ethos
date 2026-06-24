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
    / "docs/validation/milestone-e-package-publication-tag-creation-prep-validation-2026-06-21.md"
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


class MilestoneEPackagePublicationTagCreationPrepTests(unittest.TestCase):
    def test_package_prep_artifact_records_tag_creation_prep(self) -> None:
        prep = load_json(PREP)
        lane_blockers = load_json(LANE_BLOCKERS)
        status = prep["evidence_review_status"]["version_tag_policy"]
        blocker_text = " ".join(prep["explicit_blockers"])
        [package_lane] = [
            lane for lane in lane_blockers["approval_lanes"] if lane["lane_id"] == "package-publication"
        ]
        lane_blocker_text = " ".join(package_lane["explicit_blockers"])

        self.assertEqual(
            "docs/validation/"
            "milestone-e-package-publication-tag-creation-prep-validation-2026-06-21.md",
            prep["follow_up_records"]["package_tag_creation_prep"],
        )
        self.assertIn("package tag-creation prep recorded", status)
        self.assertIn("no package publication version is selected", status)
        self.assertIn("no package tag is created", status)
        self.assertIn("real-version publication remains blocked", status)
        self.assertIn("real package version selection approval", blocker_text)
        self.assertIn("package tag creation", blocker_text)
        self.assertIn("package dependency manifest activation", blocker_text)
        self.assertIn("package tag creation", lane_blocker_text)

    def test_current_manifests_and_versions_stay_unchanged(self) -> None:
        workspace = read(ROOT / "Cargo.toml")
        core = read(ROOT / "crates/ethos-core/Cargo.toml")
        verify = read(ROOT / "crates/ethos-verify/Cargo.toml")
        pdf = read(ROOT / "crates/ethos-pdf/Cargo.toml")

        self.assertIn('version = "0.1.2"', workspace)
        self.assertIn('reserved_crates_io_version = "0.0.0-reserved.0"', core)
        self.assertIn('reserved_crates_io_version = "0.0.0-reserved.0"', verify)
        self.assertIn('reserved_crates_io_version = "0.0.0-reserved.0"', pdf)
        self.assertNotIn("publish = false", core)
        self.assertNotIn("publish = false", verify)
        self.assertNotIn("publish = false", pdf)

    def test_tag_creation_record_names_future_review_boundary(self) -> None:
        record = normalized(RECORD)

        self.assertIn("Validated source HEAD before this record: `8e1192d`", record)
        self.assertIn(
            "Status: **pass for package tag-creation prep with publication blocked**",
            record,
        )
        self.assertIn("No package tag is created by this record", record)
        self.assertIn("No package publication version is selected by this record", record)
        self.assertIn("future package tag creation review", record)
        self.assertIn("exact package name and exact SemVer candidate", record)
        self.assertIn("source commit and tree", record)
        self.assertIn("candidate package manifests", record)
        self.assertIn("public-surface posture and claims gates", record)
        self.assertIn("Package tag creation remains blocked", record)
        self.assertIn("Package publication remains blocked", record)

    def test_validation_record_is_indexed_and_names_commands(self) -> None:
        readme = read(VALIDATION_README)
        record = normalized(RECORD)

        self.assertIn(RECORD.name, readme)
        self.assertIn(
            "python3 .github/scripts/test_milestone_e_package_publication_tag_creation_prep.py",
            record,
        )
        self.assertIn("python3 .github/scripts/test_public_surface_posture.py", record)
        self.assertIn("python3 .github/scripts/claims_gate.py", record)
        self.assertIn("cargo build --locked -p ethos-cli", record)
        self.assertIn("make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python", record)
        self.assertIn("git diff --check", record)

    def test_make_and_ci_run_guard_after_real_version_selection_prep(self) -> None:
        make_block = target_block("milestone-e-prep")
        ci = read(CI_WORKFLOW)
        real_version_guard = "test_milestone_e_package_publication_real_version_selection_prep.py"
        tag_guard = "test_milestone_e_package_publication_tag_creation_prep.py"

        for text, prefix in ((make_block, "$(PYTHON) .github/scripts/"), (ci, "python3 .github/scripts/")):
            self.assertIn(prefix + tag_guard, text)
            self.assertLess(text.index(prefix + real_version_guard), text.index(prefix + tag_guard))

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
