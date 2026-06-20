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
    / "docs/validation/milestone-e-package-publication-metadata-readiness-closeout-validation-2026-06-21.md"
)

CANDIDATE_CRATES = {
    "ethos-core": {
        "path": ROOT / "crates/ethos-core",
        "reserved_name": "ethos-doc-core",
    },
    "ethos-verify": {
        "path": ROOT / "crates/ethos-verify",
        "reserved_name": "ethos-verify",
    },
    "ethos-pdf": {
        "path": ROOT / "crates/ethos-pdf",
        "reserved_name": "ethos-pdf",
    },
}

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


class MilestoneEPackagePublicationMetadataReadinessTests(unittest.TestCase):
    def test_in_tree_candidate_metadata_files_are_present_and_blocked(self) -> None:
        for crate, details in CANDIDATE_CRATES.items():
            root = details["path"]
            manifest = read(root / "Cargo.toml")
            readme = normalized(root / "README.md")
            notice = normalized(root / "NOTICE.md")

            self.assertIn("publish = false", manifest, crate)
            self.assertIn('readme = "README.md"', manifest, crate)
            self.assertIn('"README.md"', manifest, crate)
            self.assertIn('"NOTICE.md"', manifest, crate)
            self.assertIn('"src/**"', manifest, crate)
            self.assertIn("license.workspace = true", manifest, crate)
            self.assertIn("repository.workspace = true", manifest, crate)
            self.assertIn("authors.workspace = true", manifest, crate)
            self.assertIn("publication_status = \"blocked\"", manifest, crate)
            self.assertIn(
                f"reserved_crates_io_name = \"{details['reserved_name']}\"",
                manifest,
                crate,
            )
            self.assertIn("reserved_crates_io_version = \"0.0.0-reserved.0\"", manifest, crate)
            self.assertIn("Package publication remains blocked", readme, crate)
            self.assertIn("Public installation from crates.io remains blocked", readme, crate)
            self.assertIn("0.0.0-reserved.0", readme, crate)
            self.assertIn("no public API", readme, crate)
            self.assertIn("internal metadata readiness review only", readme, crate)
            self.assertIn("Package publication remains blocked", notice, crate)
            self.assertIn("internal metadata readiness review only", notice, crate)

    def test_reserved_placeholder_crates_without_manifests_stay_blocked(self) -> None:
        prep = load_json(PREP)
        joined_blockers = " ".join(prep["explicit_blockers"])

        self.assertFalse((ROOT / "crates/ethos-doc/Cargo.toml").exists())
        self.assertFalse((ROOT / "crates/ethos-rag/Cargo.toml").exists())
        self.assertIn("ethos-doc has no in-tree workspace member yet", " ".join(
            prep["approved_package_publication_prep"]["in_tree_reconciliation"]
        ))
        self.assertIn("ethos-rag has no in-tree workspace member yet", " ".join(
            prep["approved_package_publication_prep"]["in_tree_reconciliation"]
        ))
        self.assertIn("ethos-doc and ethos-rag package metadata remain blocked", joined_blockers)

    def test_core_public_name_split_is_explicit(self) -> None:
        readme = normalized(ROOT / "crates/ethos-core/README.md")
        manifest = read(ROOT / "crates/ethos-core/Cargo.toml")

        self.assertIn('name = "ethos-core"', manifest)
        self.assertIn('reserved_crates_io_name = "ethos-doc-core"', manifest)
        self.assertIn("in-tree crate name remains `ethos-core`", readme)
        self.assertIn("public crates.io identifier `ethos-doc-core`", readme)

    def test_pdfium_boundary_remains_explicit(self) -> None:
        readme = normalized(ROOT / "crates/ethos-pdf/README.md")
        notice = normalized(ROOT / "crates/ethos-pdf/NOTICE.md")
        manifest = read(ROOT / "crates/ethos-pdf/Cargo.toml")

        self.assertIn('"assets/**"', manifest)
        self.assertIn("No PDFium binary is bundled", readme)
        self.assertIn("ETHOS_PDFIUM_LIBRARY_PATH", readme)
        self.assertIn("Public schemas and APIs expose no PDFium types", readme)
        self.assertIn("caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`", notice)

    def test_package_prep_artifact_records_metadata_readiness_follow_up(self) -> None:
        prep = load_json(PREP)

        self.assertEqual(
            "docs/validation/"
            "milestone-e-package-publication-metadata-readiness-closeout-validation-2026-06-21.md",
            prep["follow_up_records"]["package_metadata_readiness"],
        )
        self.assertEqual(
            "metadata/readiness follow-up recorded for in-tree priority candidates; "
            "ethos-doc and ethos-rag remain reserved placeholders without in-tree manifests, "
            "and publication remains blocked",
            prep["evidence_review_status"]["package_metadata_license_readme_review"],
        )

    def test_validation_record_is_indexed_and_keeps_boundaries(self) -> None:
        readme = read(VALIDATION_README)
        record = normalized(RECORD)

        self.assertIn(RECORD.name, readme)
        self.assertIn("Validated source HEAD before this record: `5e216ff`", record)
        self.assertIn("Status: **pass for in-tree package metadata readiness with blockers retained**", record)
        self.assertIn("Package publication remains blocked", record)
        self.assertIn("Public installation from crates.io remains blocked", record)
        self.assertIn("Real-version cargo publish remains blocked", record)
        self.assertIn("`ethos-doc` and `ethos-rag` remain reserved placeholders", record)
        self.assertIn("python3 .github/scripts/test_milestone_e_package_publication_metadata_readiness.py", record)
        self.assertIn("python3 .github/scripts/test_public_surface_posture.py", record)
        self.assertIn("python3 .github/scripts/claims_gate.py", record)
        self.assertIn("cargo build --locked -p ethos-cli", record)
        self.assertIn("make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python", record)
        self.assertIn("git diff --check", record)

    def test_make_target_and_ci_run_metadata_guard_after_evidence_records(self) -> None:
        make_block = target_block("milestone-e-prep")
        ci = read(CI_WORKFLOW)
        evidence_guard = "test_milestone_e_package_publication_evidence_records.py"
        metadata_guard = "test_milestone_e_package_publication_metadata_readiness.py"
        command_guard = "test_milestone_e_validation_command_index.py"

        for text, prefix in ((make_block, "$(PYTHON) .github/scripts/"), (ci, "python3 .github/scripts/")):
            self.assertIn(prefix + metadata_guard, text)
            self.assertLess(text.index(prefix + evidence_guard), text.index(prefix + metadata_guard))
            self.assertLess(text.index(prefix + metadata_guard), text.index(prefix + command_guard))

    def test_no_scope_expansion_language_or_private_paths(self) -> None:
        paths = [RECORD]
        for details in CANDIDATE_CRATES.values():
            paths.extend([details["path"] / "README.md", details["path"] / "NOTICE.md"])

        for path in paths:
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
