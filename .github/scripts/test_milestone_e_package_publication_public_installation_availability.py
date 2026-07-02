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
    "milestone-e-package-publication-public-installation-availability-validation-2026-06-22.md"
)
DEPENDENT_EVIDENCE_RECORD = (
    "docs/validation/"
    "milestone-e-package-publication-dependent-registry-action-evidence-validation-2026-06-22.md"
)
README = ROOT / "README.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
PREP_SCOPE = ROOT / "docs/milestone-e-prep-scope.md"
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"

SOURCE_COMMIT = "25073a1b9cf1d691e8b2496b3622cb6349e96a98"
SOURCE_SHORT = "25073a1"
SOURCE_TREE = "46a0e8a7bf11c3b30ee5c32512fb57a1f3677aeb"
TAG_SOURCE_COMMIT = "421bed8c6e04fa3d2299c6a1d9c99ccfd508122e"
TAG_SOURCE_TREE = "aa0d5d31d879540fd0044052dfeb747f12b64204"
EXACT_PUBLIC_WORDING = (
    "Ethos is public beta for source and Rust crate evaluation. It verifies whether AI citations "
    "are grounded in document evidence across native Ethos JSON and supported foreign parser "
    "outputs. Rust library crates `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` are available "
    "on crates.io at `0.1.0` for evaluation. Hosted surfaces, production positioning, and public "
    "benchmark claims remain blocked."
)
CURRENT_README_WORDING = (
    "Ethos is a deterministic document evidence layer for source-grounded verification and "
    "citation checking across native Ethos JSON and supported foreign parser outputs. The current "
    "beta includes the GitHub source repository, Rust library crates `ethos-doc-core`, "
    "`ethos-verify`, and `ethos-pdf` at `0.3.0`, the Python `ethos-pdf` wheel at `0.3.0`, the "
    "npm `@docushell/ethos-pdf@0.3.0` package, and GitHub Release `v0.3.0` macOS arm64/Linux x64 "
    "CLI artifacts. PDFium-backed commands use caller-provided PDFium through "
    "`ETHOS_PDFIUM_LIBRARY_PATH`."
)
BOUNDED_INSTALLATION_WORDING = (
    "Rust library crates `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` are available on "
    "crates.io at `0.1.0` for evaluation. The Ethos CLI, wheels, npm packages, binaries, hosted "
    "surfaces, production positioning, public benchmark reports, public benchmark claims, "
    "project-maintained PDFium builds, `ethos-doc`, and `ethos-rag` remain blocked."
)
CRATE_LINES = (
    'ethos-doc-core = "0.1.0"',
    'ethos-verify = "0.1.0"',
    'ethos-pdf = "0.1.0"',
)
API_LINES = (
    "ethos-doc-core: num=0.1.0; yanked=false; license=Apache-2.0; rust_version=1.87; "
    "published_by=docushell-dev; checksum=97a1c7b508988d2aa20d386dc29985a2db2308dca337fce9ba2b8ee219953a4d",
    "ethos-verify: num=0.1.0; yanked=false; license=Apache-2.0; rust_version=1.87; "
    "published_by=docushell-dev; checksum=101629eb2cd67f6ced6efab766c3c4c83e2e33f1adddc57937e84b18c78a113c",
    "ethos-pdf: num=0.1.0; yanked=false; license=Apache-2.0; rust_version=1.87; "
    "published_by=docushell-dev; checksum=54194a3e90defb78aadbb03cc17e7ab817338c57c2fc9a5d47795e6365b741b9",
)
INSTALL_COMMANDS = (
    "cargo add ethos-doc-core@0.1.0",
    "cargo add ethos-verify@0.1.0",
    "cargo add ethos-pdf@0.1.0",
)
CURRENT_INSTALL_COMMANDS = (
    "cargo add ethos-doc-core@0.3.0",
    "cargo add ethos-verify@0.3.0",
    "cargo add ethos-pdf@0.3.0",
)
FORBIDDEN_SCOPE_EXPANSION = [
    "public reports are approved",
    "public result wording approved",
    "release-ready",
    "release artifact approved",
    "package-ready",
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


class MilestoneEPackagePublicationPublicInstallationAvailabilityTests(unittest.TestCase):
    def test_record_is_indexed_and_source_bound(self) -> None:
        readme = normalized(VALIDATION_README)
        record = normalized(RECORD)

        self.assertIn(RECORD.name, readme)
        self.assertIn("package publication public installation availability validation", readme)
        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Availability source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Availability source tree: `{SOURCE_TREE}`", record)
        self.assertIn(f"Accepted package tag source commit: `{TAG_SOURCE_COMMIT}`", record)
        self.assertIn(f"Accepted package tag source tree: `{TAG_SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))
        self.assertEqual(TAG_SOURCE_TREE, git("rev-parse", f"{TAG_SOURCE_COMMIT}^{{tree}}"))

    def test_record_captures_availability_evidence_and_exact_wording(self) -> None:
        record = normalized(RECORD)

        self.assertIn(DEPENDENT_EVIDENCE_RECORD, record)
        self.assertIn(EXACT_PUBLIC_WORDING, record)
        self.assertIn(BOUNDED_INSTALLATION_WORDING, record)
        for line in CRATE_LINES:
            self.assertIn(line, record)
        for line in API_LINES:
            self.assertIn(line, record)
        for command in INSTALL_COMMANDS:
            self.assertIn(command, record)

    def test_readme_matches_bounded_public_wording(self) -> None:
        readme = re.sub(
            r"\s+",
            " ",
            " ".join(line.removeprefix("> ").strip() for line in read(README).splitlines()),
        )

        self.assertIn(CURRENT_README_WORDING, readme)
        for command in CURRENT_INSTALL_COMMANDS:
            self.assertIn(command, readme)
        self.assertIn("npm install -g @docushell/ethos-pdf@0.3.0", readme)
        self.assertIn("python3 -m pip install ethos-pdf==0.3.0", readme)
        self.assertIn("GitHub Release `v0.3.0`", readme)
        self.assertIn("macOS arm64/Linux x64 CLI artifacts", readme)
        self.assertIn("Windows packaged artifacts", readme)
        self.assertIn("bundled project-maintained PDFium builds", readme)
        self.assertIn("ethos-doc", readme)
        self.assertIn("ethos-rag", readme)
        self.assertIn("public benchmark reports", readme)
        self.assertIn("release-scope work", readme)

    def test_docs_reference_availability_and_retained_blockers(self) -> None:
        for path in (PREP_SCOPE, ROADMAP, EXECUTION_STATUS, VALIDATION_README):
            doc = normalized(path).lower()

            self.assertIn(RECORD.name, doc, str(path))
            self.assertIn("public installation availability", doc, str(path))
            self.assertIn("rust crate installation wording", doc, str(path))
            self.assertIn("hosted surfaces", doc, str(path))
            self.assertIn("public benchmark claims", doc, str(path))

    def test_make_and_ci_run_availability_after_dependent_evidence_before_readiness(self) -> None:
        make_block = target_block("milestone-e-prep")
        ci = read(CI_WORKFLOW)
        dependent_evidence_guard = (
            "test_milestone_e_package_publication_dependent_registry_action_evidence.py"
        )
        availability_guard = "test_milestone_e_package_publication_public_installation_availability.py"
        readiness_guard = "test_milestone_e_public_facing_readiness_ledger.py"

        for text, prefix in ((make_block, "$(PYTHON) .github/scripts/"), (ci, "python3 .github/scripts/")):
            self.assertIn(prefix + availability_guard, text)
            self.assertEqual(1, text.count(prefix + availability_guard))
            self.assertLess(text.index(prefix + dependent_evidence_guard), text.index(prefix + availability_guard))
            self.assertLess(text.index(prefix + availability_guard), text.index(prefix + readiness_guard))

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
