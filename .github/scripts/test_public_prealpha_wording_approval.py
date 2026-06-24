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
import unittest
from pathlib import Path

from makefile_guard import target_block


ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"
RECORD = ROOT / "docs/validation/public-prealpha-wording-approval-2026-06-20.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"

APPROVED_SENTENCE = (
    "Ethos is pre-alpha. It verifies whether AI citations are grounded in document evidence "
    "across native Ethos JSON and supported foreign parser outputs."
)
APPROVED_PUBLIC_BETA_SENTENCE = (
    "Ethos is a deterministic document evidence layer for source-grounded verification and "
    "citation checking across native Ethos JSON and supported foreign parser outputs. The current "
    "beta includes the GitHub source repository, Rust library crates `ethos-doc-core`, "
    "`ethos-verify`, and `ethos-pdf` at `0.1.1`, the Python `ethos-pdf` wheel at `0.1.1`, the "
    "npm `@docushell/ethos-pdf@0.1.2` package, and GitHub Release `v0.1.2` macOS arm64/Linux x64 "
    "CLI artifacts. PDFium-backed commands use caller-provided PDFium through "
    "`ETHOS_PDFIUM_LIBRARY_PATH`."
)

FORBIDDEN_APPROVAL_WORDING = [
    "public beta is approved",
    "public reports are approved",
    "public result wording approved",
    "release-ready",
    "release artifact approved",
    "package-ready",
    "package publication approved",
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
    "complete demo plan",
    "broad demo approved",
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


def normalized_public_readme() -> str:
    return re.sub(
        r"\s+",
        " ",
        " ".join(line.removeprefix("> ").strip() for line in read(README).splitlines()),
    )


class PublicPreAlphaWordingApprovalTests(unittest.TestCase):
    def test_exact_approved_sentence_is_present_on_controlled_surfaces(self) -> None:
        self.assertIn(APPROVED_PUBLIC_BETA_SENTENCE, normalized_public_readme())

        for path in (EXECUTION_STATUS, PUBLIC_RELEASE_CHECKLIST, RECORD):
            self.assertIn(APPROVED_SENTENCE, normalized(path), str(path))

    def test_approval_record_is_indexed(self) -> None:
        text = read(VALIDATION_README)

        self.assertEqual(
            1,
            text.count("public-prealpha-wording-approval-2026-06-20.md"),
        )

    def test_execution_status_closes_only_exact_sentence(self) -> None:
        text = normalized(EXECUTION_STATUS)

        self.assertIn("H3", text)
        self.assertIn("Closed for the exact approved pre-alpha sentence only", text)
        self.assertIn("Broader public result language remains blocked", text)
        self.assertIn("Public benchmark reports", text)
        self.assertIn("Public releases, packages, and production positioning", text)

    def test_release_checklist_keeps_release_and_benchmark_blockers(self) -> None:
        text = normalized(PUBLIC_RELEASE_CHECKLIST)

        self.assertIn("Approved exact public source wording until the checklist is complete", text)
        self.assertIn("does not approve public benchmark reports", text)
        self.assertIn("does not approve release artifacts", text)
        self.assertIn("does not approve package publication", text)
        self.assertIn("does not approve production positioning", text)
        self.assertIn("does not approve altered public wording", text)

    def test_record_captures_manual_verification_and_boundaries(self) -> None:
        text = normalized(RECORD)

        self.assertIn("Validated source HEAD before this record: `a1d2cfc`", text)
        self.assertIn("ethos-bench commit: `572bae9`", text)
        self.assertIn("make benchmark-publication-preflight", text)
        self.assertIn("python3 .github/scripts/test_public_surface_posture.py", text)
        self.assertIn("python3 .github/scripts/claims_gate.py", text)
        self.assertIn("git diff --check", text)
        self.assertIn("does not approve public benchmark reports", text)
        self.assertIn("does not approve release artifacts", text)
        self.assertIn("does not approve package publication", text)
        self.assertIn("does not approve production positioning", text)
        self.assertIn("does not approve hosted surfaces", text)

    def test_make_target_runs_approval_guard_after_claims_gate(self) -> None:
        block = target_block("milestone-e-prep")

        claims_gate = "$(PYTHON) .github/scripts/claims_gate.py"
        approval_guard = "$(PYTHON) .github/scripts/test_public_prealpha_wording_approval.py"
        schema_validation = "$(PYTHON) schemas/validate_examples.py"

        self.assertIn(approval_guard, block)
        self.assertLess(block.index(claims_gate), block.index(approval_guard))
        self.assertLess(block.index(approval_guard), block.index(schema_validation))

    def test_ci_runs_approval_guard(self) -> None:
        text = read(CI_WORKFLOW)
        public_surface = "python3 .github/scripts/test_public_surface_posture.py"
        approval_guard = "python3 .github/scripts/test_public_prealpha_wording_approval.py"
        milestone_d = "python3 .github/scripts/test_milestone_d_internal_contracts.py"

        self.assertIn(approval_guard, text)
        self.assertEqual(1, text.count(approval_guard))
        self.assertLess(text.index(public_surface), text.index(approval_guard))
        self.assertLess(text.index(approval_guard), text.index(milestone_d))

    def test_approval_surfaces_avoid_scope_expansion_language(self) -> None:
        text = "\n".join(
            read(path).lower()
            for path in (README, EXECUTION_STATUS, PUBLIC_RELEASE_CHECKLIST, RECORD)
        )

        for phrase in FORBIDDEN_APPROVAL_WORDING:
            self.assertNotIn(phrase, text)

    def test_record_avoids_local_private_paths(self) -> None:
        text = read(RECORD)

        self.assertNotIn("/Users/", text)
        self.assertNotIn("/private/tmp", text)
        self.assertNotIn("/private/var", text)
        self.assertNotIn("/var/folders", text)
        self.assertNotIn("saumildiwaker", text)
        self.assertNotIn("Desktop/Stuff", text)
        self.assertNotIn("project/repo/ethos", text)
        self.assertNotIn("docs/.roadmap.md.swp", text)
        self.assertNotIn("web/", text)


if __name__ == "__main__":
    unittest.main()
