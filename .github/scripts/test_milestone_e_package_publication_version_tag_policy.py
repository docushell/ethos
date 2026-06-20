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
VALIDATION_README = ROOT / "docs/validation/README.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"
RECORD = (
    ROOT
    / "docs/validation/milestone-e-package-publication-version-tag-policy-closeout-validation-2026-06-21.md"
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


class MilestoneEPackagePublicationVersionTagPolicyTests(unittest.TestCase):
    def test_package_prep_artifact_records_version_tag_follow_up(self) -> None:
        prep = load_json(PREP)
        status = prep["evidence_review_status"]["version_tag_policy"]
        blocker_text = " ".join(prep["explicit_blockers"])

        self.assertEqual(
            "docs/validation/"
            "milestone-e-package-publication-version-tag-policy-closeout-validation-2026-06-21.md",
            prep["follow_up_records"]["package_version_tag_policy"],
        )
        self.assertIn("version/tag policy follow-up recorded", status)
        self.assertIn("workspace 0.1.0 remains source-tree only", status)
        self.assertIn("reserved 0.0.0-reserved.0 names remain placeholders", status)
        self.assertIn("real-version publication remains blocked", status)
        self.assertIn("real package version selection", blocker_text)
        self.assertIn("package tag creation", blocker_text)
        self.assertIn("project-maintained PDFium builds remain blocked", blocker_text)

    def test_workspace_and_reserved_versions_stay_separate(self) -> None:
        root_manifest = read(ROOT / "Cargo.toml")
        adr = normalized(ROOT / "docs/decisions/ADR-0006-package-identifiers.md")
        record = normalized(RECORD)

        self.assertIn('version = "0.1.0"', root_manifest)
        self.assertIn("0.0.0-reserved.0", adr)
        self.assertIn("Workspace package version `0.1.0` remains a source-tree version", record)
        self.assertIn("ADR-0006 crates.io reservations remain `0.0.0-reserved.0` placeholders", record)
        self.assertIn("Placeholder reservations are not installable packages", record)
        self.assertIn("No package tag is created by this record", record)

    def test_validation_record_is_indexed_and_keeps_publication_blocked(self) -> None:
        readme = read(VALIDATION_README)
        record = normalized(RECORD)

        self.assertIn(RECORD.name, readme)
        self.assertIn("Validated source HEAD before this record: `fb869c6`", record)
        self.assertIn(
            "Status: **pass for version/tag policy follow-up with publication blocked**",
            record,
        )
        self.assertIn("Package publication remains blocked", record)
        self.assertIn("Public installation from crates.io remains blocked", record)
        self.assertIn("Real-version cargo publish remains blocked", record)
        self.assertIn("Real package version selection remains blocked", record)
        self.assertIn("Package tag creation remains blocked", record)
        self.assertIn("ethos-source-snapshot-660f268", record)
        self.assertIn("ethos-package-<crate-name>-<version>", record)
        self.assertIn(
            "python3 .github/scripts/test_milestone_e_package_publication_version_tag_policy.py",
            record,
        )
        self.assertIn("python3 .github/scripts/test_public_surface_posture.py", record)
        self.assertIn("python3 .github/scripts/claims_gate.py", record)
        self.assertIn("cargo build --locked -p ethos-cli", record)
        self.assertIn("make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python", record)
        self.assertIn("git diff --check", record)

    def test_make_and_ci_run_guard_after_dry_run_smoke(self) -> None:
        make_block = target_block("milestone-e-prep")
        ci = read(CI_WORKFLOW)
        dry_run_guard = "test_milestone_e_package_publication_dry_run_smoke.py"
        version_tag_guard = "test_milestone_e_package_publication_version_tag_policy.py"
        command_guard = "test_milestone_e_validation_command_index.py"

        for text, prefix in ((make_block, "$(PYTHON) .github/scripts/"), (ci, "python3 .github/scripts/")):
            self.assertIn(prefix + version_tag_guard, text)
            self.assertLess(text.index(prefix + dry_run_guard), text.index(prefix + version_tag_guard))
            self.assertLess(text.index(prefix + version_tag_guard), text.index(prefix + command_guard))

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
