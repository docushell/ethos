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
    "milestone-e-package-publication-manifest-activation-applied-validation-2026-06-22.md"
)
VALIDATION_README = ROOT / "docs/validation/README.md"
PREP_SCOPE = ROOT / "docs/milestone-e-prep-scope.md"
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"

SOURCE_COMMIT = "e517d76c7c5f34984f62181769809637e7123bbc"
SOURCE_SHORT = "e517d76"
SOURCE_TREE = "b0cdeca1387f2080a1f9dca4f075e3a4bd7a92ec"
PACKAGE_TAGS = (
    "ethos-package-ethos-doc-core-0.1.0",
    "ethos-package-ethos-verify-0.1.0",
    "ethos-package-ethos-pdf-0.1.0",
)
FORBIDDEN_SCOPE_EXPANSION = [
    "package publication approved",
    "package publication is approved",
    "public installation approved",
    "public installation is approved",
    "public installation wording is approved",
    "package tag creation approved",
    "registry creation approved",
    "registry-backed assembly activation approved",
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


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args],
        cwd=ROOT,
        encoding="utf-8",
        stderr=subprocess.DEVNULL,
    ).strip()


class MilestoneEPackagePublicationManifestActivationAppliedTests(unittest.TestCase):
    def test_record_is_indexed_and_source_bound(self) -> None:
        prep = load_json(PREP)
        readme = read(VALIDATION_README)
        record = normalized(RECORD)

        self.assertIn(RECORD.name, readme)
        self.assertIn("package publication manifest activation applied validation", readme)
        self.assertEqual(
            "docs/validation/"
            "milestone-e-package-publication-manifest-activation-applied-validation-2026-06-22.md",
            prep["follow_up_records"]["package_manifest_activation_applied"],
        )
        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Manifest activation source commit before this record: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Manifest activation source tree before this record: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_source_manifests_have_activated_but_blocked_shape(self) -> None:
        workspace = read(ROOT / "Cargo.toml")
        lockfile = read(ROOT / "Cargo.lock")
        core = read(ROOT / "crates/ethos-core/Cargo.toml")
        verify = read(ROOT / "crates/ethos-verify/Cargo.toml")
        pdf = read(ROOT / "crates/ethos-pdf/Cargo.toml")

        self.assertIn(
            'ethos-core = { package = "ethos-doc-core", path = "crates/ethos-core", '
            'version = "0.1.0", default-features = false }',
            workspace,
        )
        self.assertIn('name = "ethos-doc-core"', core)
        self.assertIn('[lib]\nname = "ethos_core"', core)
        self.assertIn('reserved_crates_io_name = "ethos-doc-core"', core)
        self.assertIn('name = "ethos-doc-core"', lockfile)
        self.assertNotIn('name = "ethos-core"', lockfile)
        self.assertIn('ethos-core = { workspace = true, features = ["grounding", "verify-types"] }', verify)
        self.assertIn('ethos-core = { workspace = true, features = ["full"] }', pdf)
        self.assertNotIn('package = "ethos-doc-core"', verify)
        self.assertNotIn('package = "ethos-doc-core"', pdf)
        for manifest in (core, verify, pdf):
            self.assertNotIn("publish = false", manifest)
            self.assertIn('publication_status = "approved_for_crates_io_publication"', manifest)

    def test_tags_registry_and_public_installation_remain_blocked(self) -> None:
        prep = load_json(PREP)

        for tag in PACKAGE_TAGS:
            self.assertIn(tag, str(prep))
        self.assertFalse((ROOT / ".cargo/config.toml").exists())
        self.assertFalse((ROOT / "target/package-registry").exists())
        self.assertIn(
            "public installation remains blocked",
            prep["package_publication_pre_approval_gap_ledger"]["retained_blockers"],
        )
        self.assertIn(
            "package publication remains blocked",
            prep["package_publication_pre_approval_gap_ledger"]["retained_blockers"],
        )

    def test_docs_reference_activation_and_retained_blockers(self) -> None:
        for path in (PREP_SCOPE, ROADMAP, EXECUTION_STATUS, VALIDATION_README):
            doc = normalized(path)

            self.assertIn(RECORD.name, doc, str(path))
            self.assertIn("manifest activation applied", doc.lower(), str(path))
            self.assertIn("package publication remains blocked", doc, str(path))
            self.assertIn("public installation remains blocked", doc, str(path))

    def test_make_and_ci_run_activation_guard_after_decision_refresh(self) -> None:
        make_block = target_block("milestone-e-prep")
        ci = read(CI_WORKFLOW)
        refresh_guard = "test_milestone_e_package_publication_approval_decision_refresh.py"
        activation_guard = "test_milestone_e_package_publication_manifest_activation_applied.py"
        public_facing_guard = "test_milestone_e_public_facing_readiness_ledger.py"

        for text, prefix in ((make_block, "$(PYTHON) .github/scripts/"), (ci, "python3 .github/scripts/")):
            self.assertIn(prefix + activation_guard, text)
            self.assertEqual(1, text.count(prefix + activation_guard))
            self.assertLess(text.index(prefix + refresh_guard), text.index(prefix + activation_guard))
            self.assertLess(text.index(prefix + activation_guard), text.index(prefix + public_facing_guard))

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
