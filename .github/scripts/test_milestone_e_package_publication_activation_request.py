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
    "milestone-e-package-publication-publish-flag-activation-request-validation-2026-06-22.md"
)
FINAL_DECISION_RECORD = (
    "docs/validation/"
    "milestone-e-package-publication-final-approval-decision-validation-2026-06-22.md"
)
VALIDATION_README = ROOT / "docs/validation/README.md"
PREP_SCOPE = ROOT / "docs/milestone-e-prep-scope.md"
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"

SOURCE_COMMIT = "cea20182e11271bf83675c12de43498df9c42c18"
SOURCE_SHORT = "cea2018"
SOURCE_TREE = "8c7076b0997fe925827bb81f859b74790a4d8b16"
EXACT_CRATES = ["ethos-doc-core", "ethos-verify", "ethos-pdf"]
EXACT_TAGS = [
    "ethos-package-ethos-doc-core-0.1.0",
    "ethos-package-ethos-verify-0.1.0",
    "ethos-package-ethos-pdf-0.1.0",
]
REQUIRED_REQUEST_FIELDS = [
    "Decision requested: approve exact publish-flag and package metadata activation diff.",
    "Approver requested: docushell-admin acting as decider.",
    "Date requested: 2026-06-22.",
    "Exact activation crate list requested: `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` only.",
    "Exact activation diff requested: remove `publish = false` from the three accepted candidate manifests only.",
    "Exact metadata diff requested: change `publication_status = \"blocked\"` to `publication_status = \"approved_for_crates_io_publication\"` in the three accepted candidate manifests only.",
    "Package tag source binding impact: the previous accepted source binding keeps `publish = false`; package tag source binding must be refreshed after the activation diff is applied and reviewed.",
]
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


class MilestoneEPackagePublicationPublishFlagActivationRequestTests(unittest.TestCase):
    def test_request_record_is_indexed_and_source_bound(self) -> None:
        readme = normalized(VALIDATION_README)
        record = normalized(RECORD)

        self.assertIn(RECORD.name, readme)
        self.assertIn("package publication publish-flag activation request validation", readme)
        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Activation request source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Activation request source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_request_names_exact_activation_diff_and_binding_impact(self) -> None:
        record = normalized(RECORD)

        self.assertIn(
            "Status: **pass for publish-flag activation request with activation blocked**",
            record,
        )
        for field in REQUIRED_REQUEST_FIELDS:
            self.assertIn(field, record)
        for crate in EXACT_CRATES:
            self.assertIn(crate, record)
        for tag in EXACT_TAGS:
            self.assertIn(tag, record)
        self.assertIn(FINAL_DECISION_RECORD, record)
        self.assertIn("`ethos-doc` remains excluded", record)
        self.assertIn("`ethos-rag` remains excluded", record)

    def test_request_does_not_mutate_current_source_or_tags(self) -> None:
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
        for tag in EXACT_TAGS:
            self.assertEqual("", git("tag", "--list", tag))
        self.assertFalse((ROOT / ".cargo/config.toml").exists())
        self.assertFalse((ROOT / "target/package-registry").exists())

    def test_docs_reference_request_and_retained_blockers(self) -> None:
        for path in (PREP_SCOPE, ROADMAP, EXECUTION_STATUS, VALIDATION_README):
            doc = normalized(path).lower()

            self.assertIn(RECORD.name, doc, str(path))
            self.assertIn("publish-flag activation request", doc, str(path))
            self.assertIn("activation remains blocked", doc, str(path))
            self.assertIn("package tag source binding must be refreshed", doc, str(path))
            self.assertIn("real-version cargo publish remains blocked", doc, str(path))

    def test_make_and_ci_run_request_after_final_decision_before_readiness(self) -> None:
        make_block = target_block("milestone-e-prep")
        ci = read(CI_WORKFLOW)
        decision_guard = "test_milestone_e_package_publication_final_approval_decision.py"
        activation_request_guard = (
            "test_milestone_e_package_publication_activation_request.py"
        )
        readiness_guard = "test_milestone_e_public_facing_readiness_ledger.py"

        for text, prefix in ((make_block, "$(PYTHON) .github/scripts/"), (ci, "python3 .github/scripts/")):
            self.assertIn(prefix + activation_request_guard, text)
            self.assertEqual(1, text.count(prefix + activation_request_guard))
            self.assertLess(text.index(prefix + decision_guard), text.index(prefix + activation_request_guard))
            self.assertLess(text.index(prefix + activation_request_guard), text.index(prefix + readiness_guard))

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
