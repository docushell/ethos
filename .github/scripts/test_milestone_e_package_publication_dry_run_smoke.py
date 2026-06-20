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
    / "docs/validation/milestone-e-package-publication-dry-run-smoke-closeout-validation-2026-06-21.md"
)

LOCAL_SMOKE_COMMANDS = [
    "cargo package --locked --offline -p ethos-core --allow-dirty --no-verify",
    "cargo package --list --locked --offline -p ethos-core --allow-dirty",
    "cargo check --locked --offline -p ethos-verify",
    "cargo check --locked --offline -p ethos-pdf",
    "$(PYTHON) .github/scripts/test_milestone_e_package_publication_dry_run_smoke.py",
    "git diff --check",
]

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


class MilestoneEPackagePublicationDryRunSmokeTests(unittest.TestCase):
    def test_local_smoke_make_target_is_non_publishing(self) -> None:
        block = target_block("package-publication-dry-run-smoke")
        commands = [line.strip() for line in block.splitlines() if line.strip()]

        self.assertEqual(LOCAL_SMOKE_COMMANDS, commands)
        self.assertIn("cargo package --locked --offline -p ethos-core --allow-dirty --no-verify", block)
        self.assertIn("cargo package --list --locked --offline -p ethos-core --allow-dirty", block)
        self.assertIn("cargo check --locked --offline -p ethos-verify", block)
        self.assertIn("cargo check --locked --offline -p ethos-pdf", block)
        self.assertNotIn("cargo publish", block)
        self.assertNotIn("cargo install", block)
        self.assertNotIn("crates.io", block)

    def test_candidate_manifests_still_block_publication(self) -> None:
        for manifest in (
            ROOT / "crates/ethos-core/Cargo.toml",
            ROOT / "crates/ethos-verify/Cargo.toml",
            ROOT / "crates/ethos-pdf/Cargo.toml",
        ):
            text = read(manifest)
            self.assertIn("publish = false", text, str(manifest))
            self.assertIn("publication_status = \"blocked\"", text, str(manifest))
            self.assertIn("reserved_crates_io_version = \"0.0.0-reserved.0\"", text, str(manifest))

    def test_dependent_package_assembly_blocker_is_recorded(self) -> None:
        prep = load_json(PREP)
        follow_ups = prep["follow_up_records"]
        status = prep["evidence_review_status"]["install_build_smoke_path"]
        blocker_text = " ".join(prep["explicit_blockers"])

        self.assertEqual(
            "docs/validation/milestone-e-package-publication-dry-run-smoke-closeout-validation-2026-06-21.md",
            follow_ups["package_dry_run_smoke"],
        )
        self.assertIn("local source-tree smoke", status)
        self.assertIn("dependency-ordering follow-up recorded", status)
        self.assertIn("future dependent candidate ordering", status)
        self.assertIn("publication remains blocked", status)
        self.assertIn("registry-backed dependent package assembly", blocker_text)
        self.assertIn("package dependency manifest migration", blocker_text)
        self.assertIn("real package version selection", blocker_text)
        self.assertIn("package tag creation", blocker_text)
        self.assertIn("project-maintained PDFium builds remain blocked", blocker_text)

    def test_validation_record_is_indexed_and_names_smoke_results(self) -> None:
        readme = read(VALIDATION_README)
        record = normalized(RECORD)

        self.assertIn(RECORD.name, readme)
        self.assertIn("Validated source HEAD before this record: `d1c9384`", record)
        self.assertIn("Status: **pass for local dry-run smoke evidence with blockers retained**", record)
        self.assertIn("cargo package --locked --offline -p ethos-core --allow-dirty --no-verify", record)
        self.assertIn("cargo package --list --locked --offline -p ethos-core --allow-dirty", record)
        self.assertIn("cargo check --locked --offline -p ethos-verify", record)
        self.assertIn("cargo check --locked --offline -p ethos-pdf", record)
        self.assertIn("dependent package assembly remains blocked", record.lower())
        self.assertIn("no matching package named `ethos-core`", record)
        self.assertIn("Package publication remains blocked", record)
        self.assertIn("Public installation from crates.io remains blocked", record)
        self.assertIn("Real-version cargo publish remains blocked", record)
        self.assertIn("python3 .github/scripts/test_milestone_e_package_publication_dry_run_smoke.py", record)
        self.assertIn("make package-publication-dry-run-smoke PYTHON=<python>", record)
        self.assertIn("make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python", record)

    def test_make_and_ci_run_guards_in_expected_order(self) -> None:
        make_block = target_block("milestone-e-prep")
        ci = read(CI_WORKFLOW)
        metadata_guard = "test_milestone_e_package_publication_metadata_readiness.py"
        smoke_guard = "test_milestone_e_package_publication_dry_run_smoke.py"
        command_guard = "test_milestone_e_validation_command_index.py"

        for text, prefix in ((make_block, "$(PYTHON) .github/scripts/"), (ci, "python3 .github/scripts/")):
            self.assertIn(prefix + smoke_guard, text)
            self.assertLess(text.index(prefix + metadata_guard), text.index(prefix + smoke_guard))
            self.assertLess(text.index(prefix + smoke_guard), text.index(prefix + command_guard))

        self.assertIn("make package-publication-dry-run-smoke", ci)
        self.assertLess(
            ci.index("python3 .github/scripts/test_milestone_e_package_publication_metadata_readiness.py"),
            ci.index("make package-publication-dry-run-smoke"),
        )
        self.assertLess(
            ci.index("make package-publication-dry-run-smoke"),
            ci.index("python3 .github/scripts/test_milestone_e_package_publication_dry_run_smoke.py"),
        )

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
