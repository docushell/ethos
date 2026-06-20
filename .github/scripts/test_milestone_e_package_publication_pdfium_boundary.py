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
    / "docs/validation/milestone-e-package-publication-pdfium-boundary-closeout-validation-2026-06-21.md"
)
PDF_CRATE = ROOT / "crates/ethos-pdf"

BINARY_SUFFIXES = {
    ".a",
    ".dll",
    ".dylib",
    ".gz",
    ".lib",
    ".so",
    ".tar",
    ".tgz",
    ".wasm",
    ".zip",
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


class MilestoneEPackagePublicationPdfiumBoundaryTests(unittest.TestCase):
    def test_package_prep_artifact_records_pdfium_boundary_follow_up(self) -> None:
        prep = load_json(PREP)
        lane_blockers = load_json(LANE_BLOCKERS)
        status = prep["evidence_review_status"]["pdfium_packaging_boundary"]
        blocker_text = " ".join(prep["explicit_blockers"])
        [package_lane] = [
            lane for lane in lane_blockers["approval_lanes"] if lane["lane_id"] == "package-publication"
        ]
        lane_blocker_text = " ".join(package_lane["explicit_blockers"])

        self.assertEqual(
            "docs/validation/"
            "milestone-e-package-publication-pdfium-boundary-closeout-validation-2026-06-21.md",
            prep["follow_up_records"]["package_pdfium_boundary"],
        )
        self.assertIn("PDFium boundary follow-up recorded", status)
        self.assertIn("no bundled PDFium binary", status)
        self.assertIn("caller-provided ETHOS_PDFIUM_LIBRARY_PATH", status)
        self.assertIn("no raw PDFium types across public schemas/APIs", status)
        self.assertIn("publication remains blocked", status)
        self.assertIn("project-maintained PDFium builds remain blocked", blocker_text)
        self.assertIn("real package version selection", blocker_text)
        self.assertIn("package tag creation", blocker_text)
        self.assertIn("project-maintained PDFium builds remain blocked", lane_blocker_text)
        self.assertIn("dependent package assembly", lane_blocker_text)
        self.assertIn("real package version selection", lane_blocker_text)
        self.assertIn("package tag creation", lane_blocker_text)
        self.assertNotIn("PDFium-boundary evidence remains incomplete", lane_blocker_text)

    def test_ethos_pdf_manifest_and_docs_keep_current_boundary(self) -> None:
        manifest = read(PDF_CRATE / "Cargo.toml")
        readme = normalized(PDF_CRATE / "README.md")
        notice = normalized(PDF_CRATE / "NOTICE.md")

        self.assertIn("publish = false", manifest)
        self.assertIn("publication_status = \"blocked\"", manifest)
        self.assertIn("reserved_crates_io_version = \"0.0.0-reserved.0\"", manifest)
        self.assertIn('"assets/**"', manifest)
        self.assertNotIn("build.rs", manifest)
        self.assertNotIn("[build-dependencies]", manifest)
        self.assertIn("No PDFium binary is bundled in this crate", readme)
        self.assertIn("PDFium remains caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`", readme)
        self.assertIn("Public schemas and APIs expose no PDFium types", readme)
        self.assertIn("bundles no PDFium binary", notice)
        self.assertIn("caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`", notice)

    def test_ethos_pdf_package_inputs_do_not_bundle_pdfium_binaries(self) -> None:
        tracked_files = [path.relative_to(PDF_CRATE).as_posix() for path in PDF_CRATE.rglob("*") if path.is_file()]

        self.assertEqual(
            [
                "Cargo.toml",
                "NOTICE.md",
                "README.md",
                "assets/README.md",
                "assets/font-substitution-table.json",
                "src/lib.rs",
            ],
            sorted(tracked_files),
        )
        for path in PDF_CRATE.rglob("*"):
            if path.is_file():
                suffixes = {suffix.lower() for suffix in path.suffixes}
                self.assertTrue(BINARY_SUFFIXES.isdisjoint(suffixes), str(path))

    def test_public_boundary_uses_normalized_core_types_not_raw_pdfium_types(self) -> None:
        traits = read(ROOT / "crates/ethos-core/src/traits.rs")
        pdf_source = read(PDF_CRATE / "src/lib.rs")
        verify_manifest = read(ROOT / "crates/ethos-verify/Cargo.toml")

        self.assertIn("public schemas and", traits)
        self.assertIn("APIs never expose PDFium types", traits)
        self.assertIn("fn manifest(&self) -> BackendManifest;", traits)
        self.assertIn("fn extract(&self, pdf_bytes: &[u8], config: &ParseConfig) -> Result<Extraction, EthosError>;", traits)
        self.assertNotRegex(traits, r"pub\s+.*\b(FPDF|c_void|c_char|c_int|c_ulong)\b")
        self.assertNotRegex(pdf_source, r"pub\s+.*\b(FPDF|c_void|c_char|c_int|c_ulong)\b")
        self.assertIn("never ethos-pdf", verify_manifest)

    def test_validation_record_is_indexed_and_keeps_publication_blocked(self) -> None:
        readme = read(VALIDATION_README)
        record = normalized(RECORD)

        self.assertIn(RECORD.name, readme)
        self.assertIn("Validated source HEAD before this record: `6ec51e3`", record)
        self.assertIn(
            "Status: **pass for PDFium packaging boundary follow-up with publication blocked**",
            record,
        )
        self.assertIn("Package publication remains blocked", record)
        self.assertIn("Public installation from crates.io remains blocked", record)
        self.assertIn("Real-version cargo publish remains blocked", record)
        self.assertIn("No PDFium binary is bundled", record)
        self.assertIn("ETHOS_PDFIUM_LIBRARY_PATH", record)
        self.assertIn("no raw PDFium FFI types", record)
        self.assertIn("Project-maintained PDFium builds remain blocked", record)
        self.assertIn(
            "python3 .github/scripts/test_milestone_e_package_publication_pdfium_boundary.py",
            record,
        )
        self.assertIn("python3 .github/scripts/test_public_surface_posture.py", record)
        self.assertIn("python3 .github/scripts/claims_gate.py", record)
        self.assertIn("cargo build --locked -p ethos-cli", record)
        self.assertIn("make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python", record)
        self.assertIn("git diff --check", record)

    def test_make_and_ci_run_guard_after_version_tag_policy(self) -> None:
        make_block = target_block("milestone-e-prep")
        ci = read(CI_WORKFLOW)
        version_tag_guard = "test_milestone_e_package_publication_version_tag_policy.py"
        pdfium_guard = "test_milestone_e_package_publication_pdfium_boundary.py"
        command_guard = "test_milestone_e_validation_command_index.py"

        for text, prefix in ((make_block, "$(PYTHON) .github/scripts/"), (ci, "python3 .github/scripts/")):
            self.assertIn(prefix + pdfium_guard, text)
            self.assertLess(text.index(prefix + version_tag_guard), text.index(prefix + pdfium_guard))
            self.assertLess(text.index(prefix + pdfium_guard), text.index(prefix + command_guard))

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
