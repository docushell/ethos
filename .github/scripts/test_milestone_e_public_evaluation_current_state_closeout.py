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
    "milestone-e-public-evaluation-current-state-closeout-validation-2026-06-22.md"
)
README = ROOT / "README.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
PREP_SCOPE = ROOT / "docs/milestone-e-prep-scope.md"
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"

SOURCE_COMMIT = "034881e46b243549b76b477adeb55c0d6f1992aa"
SOURCE_SHORT = "034881e"
SOURCE_TREE = "fb089e027641a7d2152d7d1ebd499f45bb1f6a1c"
EXACT_PUBLIC_WORDING = (
    "Ethos is public beta for source and Rust crate evaluation. It verifies whether AI citations "
    "are grounded in document evidence across native Ethos JSON and supported foreign parser "
    "outputs. Rust library crates `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` are available "
    "on crates.io at `0.1.0` for evaluation. Hosted surfaces, production positioning, and public "
    "benchmark claims remain blocked."
)
CURRENT_README_WORDING = (
    "Ethos is public beta for source, Rust crate, Python wheel, macOS arm64 CLI artifact, "
    "Linux x64 CLI artifact, and npm `@docushell/ethos-pdf` evaluation. It verifies whether "
    "AI citations are grounded in document evidence across native Ethos JSON and supported foreign "
    "parser outputs. Rust library crates `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` are "
    "available on crates.io at `0.1.0` for evaluation. The Python `ethos-pdf` wheel, npm "
    "`@docushell/ethos-pdf@0.1.0` package, and macOS arm64/Linux x64 CLI artifacts are available "
    "for evaluation with caller-provided PDFium. Hosted surfaces, production positioning, Windows "
    "packaged artifacts, bundled project-maintained PDFium builds, `ethos-doc`, `ethos-rag`, "
    "public benchmark reports, public benchmark claims, and speed, footprint, parser-quality, "
    "table-quality, or production claims remain blocked."
)
APPROVED_SURFACE_LINES = (
    "GitHub source repository",
    "`ethos-doc-core`",
    "`ethos-verify`",
    "`ethos-pdf`",
    "`0.1.0`",
)
RETAINED_BLOCKERS = (
    "CLI distribution remains blocked",
    "Wheels remain blocked",
    "npm packages remain blocked",
    "Binaries remain blocked",
    "Hosted surfaces remain blocked",
    "Production positioning remains blocked",
    "Public benchmark reports remain blocked",
    "Public benchmark claims remain blocked",
    "Project-maintained PDFium builds remain blocked",
    "`ethos-doc` remains blocked",
    "`ethos-rag` remains blocked",
    "Broader public wording outside the exact approved wording remains blocked",
)
FORBIDDEN_SCOPE_EXPANSION = [
    "generally released",
    "first public release",
    "release-ready",
    "release artifact approved",
    "package-complete",
    "package-ready",
    "production-ready",
    "production positioning approved",
    "benchmark-validated",
    "public benchmark pass",
    "hosted surface approved",
    "hosted demo approved",
    "demo-ready",
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


class MilestoneEPublicEvaluationCurrentStateCloseoutTests(unittest.TestCase):
    def test_record_is_indexed_and_source_bound(self) -> None:
        readme = normalized(VALIDATION_README)
        record = normalized(RECORD)

        self.assertIn(RECORD.name, readme)
        self.assertIn("public evaluation current-state closeout validation", readme)
        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Current-state source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Current-state source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_record_captures_approved_surface_and_exact_wording(self) -> None:
        record = normalized(RECORD)

        self.assertIn(EXACT_PUBLIC_WORDING, record)
        for line in APPROVED_SURFACE_LINES:
            self.assertIn(line, record)
        for blocker in RETAINED_BLOCKERS:
            self.assertIn(blocker, record)

    def test_readme_and_status_docs_match_exact_public_wording(self) -> None:
        readme_text = re.sub(
            r"\s+",
            " ",
            " ".join(line.removeprefix("> ").strip() for line in read(README).splitlines()),
        )
        self.assertIn(CURRENT_README_WORDING, readme_text, str(README))
        self.assertIn(EXACT_PUBLIC_WORDING, normalized(EXECUTION_STATUS), str(EXECUTION_STATUS))

    def test_docs_reference_current_state_and_retained_blockers(self) -> None:
        for path in (PREP_SCOPE, ROADMAP, EXECUTION_STATUS, VALIDATION_README):
            doc = normalized(path).lower()

            self.assertIn(RECORD.name, doc, str(path))
            self.assertIn("public evaluation current-state closeout", doc, str(path))
            self.assertIn("github source repository", doc, str(path))
            self.assertIn("rust crate evaluation", doc, str(path))
            self.assertIn("hosted surfaces", doc, str(path))
            self.assertIn("public benchmark claims", doc, str(path))

    def test_make_and_ci_run_closeout_after_current_main_source_approval_before_indexes(self) -> None:
        make_block = target_block("milestone-e-prep")
        ci = read(CI_WORKFLOW)
        source_approval_guard = "test_milestone_e_public_beta_current_main_source_only_approval.py"
        closeout_guard = "test_milestone_e_public_evaluation_current_state_closeout.py"

        for text, prefix in ((make_block, "$(PYTHON) .github/scripts/"), (ci, "python3 .github/scripts/")):
            self.assertIn(prefix + closeout_guard, text)
            self.assertEqual(1, text.count(prefix + closeout_guard))
            self.assertLess(text.index(prefix + source_approval_guard), text.index(prefix + closeout_guard))

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
