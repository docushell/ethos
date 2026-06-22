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

import re
import subprocess
import unittest
from pathlib import Path

from makefile_guard import target_block


ROOT = Path(__file__).resolve().parents[2]
RECORD = (
    ROOT
    / "docs/validation/"
    "milestone-e-package-publication-activation-applied-validation-2026-06-22.md"
)
REQUEST_RECORD = (
    "docs/validation/"
    "milestone-e-package-publication-publish-flag-activation-request-validation-2026-06-22.md"
)
VALIDATION_README = ROOT / "docs/validation/README.md"
PREP_SCOPE = ROOT / "docs/milestone-e-prep-scope.md"
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"

SOURCE_COMMIT = "f50f2948b0536b3c75fe369558c94ce1155b73d1"
SOURCE_SHORT = "f50f294"
SOURCE_TREE = "00c3e4df7a7b3b368659650601a2df76b63a2ce8"
PACKAGE_TAGS = (
    "ethos-package-ethos-doc-core-0.1.0",
    "ethos-package-ethos-verify-0.1.0",
    "ethos-package-ethos-pdf-0.1.0",
)
FORBIDDEN_SCOPE_EXPANSION = [
    "public reports are approved",
    "public result wording approved",
    "release-ready",
    "release artifact approved",
    "package-ready",
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


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args],
        cwd=ROOT,
        encoding="utf-8",
        stderr=subprocess.DEVNULL,
    ).strip()


class MilestoneEPackagePublicationActivationAppliedTests(unittest.TestCase):
    def test_record_is_indexed_and_source_bound(self) -> None:
        readme = normalized(VALIDATION_README)
        record = normalized(RECORD)

        self.assertIn(RECORD.name, readme)
        self.assertIn("package publication activation applied validation", readme)
        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Activation applied source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Activation applied source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_candidate_manifests_are_activated_and_non_candidates_stay_blocked(self) -> None:
        expected_names = {
            ROOT / "crates/ethos-core/Cargo.toml": 'name = "ethos-doc-core"',
            ROOT / "crates/ethos-verify/Cargo.toml": 'name = "ethos-verify"',
            ROOT / "crates/ethos-pdf/Cargo.toml": 'name = "ethos-pdf"',
        }
        for manifest, package_name in expected_names.items():
            text = read(manifest)
            self.assertIn(package_name, text, str(manifest))
            self.assertNotIn("publish = false", text, str(manifest))
            self.assertIn(
                'publication_status = "approved_for_crates_io_publication"',
                text,
                str(manifest),
            )
            self.assertIn('reserved_crates_io_version = "0.0.0-reserved.0"', text, str(manifest))

        workspace = read(ROOT / "Cargo.toml")
        lockfile = read(ROOT / "Cargo.lock")
        verify = read(ROOT / "crates/ethos-verify/Cargo.toml")
        pdf = read(ROOT / "crates/ethos-pdf/Cargo.toml")
        self.assertIn(
            'ethos-core = { package = "ethos-doc-core", path = "crates/ethos-core", '
            'version = "0.1.0", default-features = false }',
            workspace,
        )
        self.assertIn('name = "ethos-doc-core"', lockfile)
        self.assertNotIn('name = "ethos-core"', lockfile)
        self.assertIn('ethos-core = { workspace = true, features = ["grounding", "verify-types"] }', verify)
        self.assertIn('ethos-core = { workspace = true, features = ["full"] }', pdf)

        for manifest in (
            ROOT / "crates/ethos-cli/Cargo.toml",
            ROOT / "crates/ethos-layout/Cargo.toml",
            ROOT / "crates/ethos-tables/Cargo.toml",
        ):
            self.assertIn("publish = false", read(manifest), str(manifest))

    def test_tags_registry_and_public_installation_remain_blocked(self) -> None:
        record = normalized(RECORD)

        self.assertIn(REQUEST_RECORD, record)
        self.assertIn("Package tag source binding must be refreshed", record)
        self.assertIn("No package tags are created by this record", record)
        self.assertIn("cargo publish` remains blocked", record)
        self.assertIn("Public installation instructions remain blocked", record)
        for tag in PACKAGE_TAGS:
            self.assertEqual("", git("tag", "--list", tag), tag)
        self.assertFalse((ROOT / ".cargo/config.toml").exists())
        self.assertFalse((ROOT / "target/package-registry").exists())

    def test_docs_reference_applied_activation_and_retained_blockers(self) -> None:
        for path in (PREP_SCOPE, ROADMAP, EXECUTION_STATUS, VALIDATION_README):
            doc = normalized(path).lower()

            self.assertIn(RECORD.name, doc, str(path))
            self.assertIn("activation applied", doc, str(path))
            self.assertIn("package tag source binding must be refreshed", doc, str(path))
            self.assertIn("public installation remains blocked", doc, str(path))

    def test_make_and_ci_run_applied_activation_after_request_before_readiness(self) -> None:
        make_block = target_block("milestone-e-prep")
        ci = read(CI_WORKFLOW)
        request_guard = "test_milestone_e_package_publication_activation_request.py"
        applied_guard = "test_milestone_e_package_publication_activation_applied.py"
        readiness_guard = "test_milestone_e_public_facing_readiness_ledger.py"

        for text, prefix in ((make_block, "$(PYTHON) .github/scripts/"), (ci, "python3 .github/scripts/")):
            self.assertIn(prefix + applied_guard, text)
            self.assertEqual(1, text.count(prefix + applied_guard))
            self.assertLess(text.index(prefix + request_guard), text.index(prefix + applied_guard))
            self.assertLess(text.index(prefix + applied_guard), text.index(prefix + readiness_guard))

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
