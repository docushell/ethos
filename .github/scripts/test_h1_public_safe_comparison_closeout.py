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
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"
RECORD = ROOT / "docs/validation/h1-public-safe-comparison-closeout-2026-06-20.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"

EXPECTED_HASHES = [
    "b50ad38527c6a13319601f6f8c7a7f45b4b982c8036552758dc72c1e1f1ba0eb",
    "0e56baaafd87204d39f081d1bbc2f0adcea9af3e7053868256bde1fb4dce862a",
    "0e1ec0e745f0fb62535890c8d4e33ed2c92c0a544e1e988265d05436e11963fb",
    "5dc7e55f5a8cdb9044a4dda5ffc1bd540d2c14aef6b20e54868c9bc118e35919",
    "27f2ed5927d3ec85722d558ef1c7c21876e2fc3f8cae3e38054bfa9a2ba5b0d0",
]

BOUNDARY_PHRASES = [
    "does not approve public benchmark claims",
    "does not approve public benchmark reports",
    "does not approve release artifacts",
    "does not approve package publication",
    "does not approve production positioning",
    "does not approve hosted surfaces",
    "does not approve wording beyond the exact approved pre-alpha sentence",
]

FORBIDDEN_SCOPE_EXPANSION = [
    "public beta approved",
    "public benchmark claims approved",
    "public benchmark reports approved",
    "comparison-report wording approved",
    "release artifacts approved",
    "package publication approved",
    "production positioning approved",
    "hosted surfaces approved",
    "first-release status approved",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalized(path: Path) -> str:
    return re.sub(r"\s+", " ", read(path))


class H1PublicSafeComparisonCloseoutTests(unittest.TestCase):
    def test_h1_closed_only_for_evidence_acceptance_in_current_docs(self) -> None:
        for path in (EXECUTION_STATUS, PUBLIC_RELEASE_CHECKLIST):
            text = normalized(path)
            self.assertIn("H1", text, str(path))
            self.assertIn("closed for public-safe evidence acceptance only", text, str(path))
            self.assertIn("h1-public-safe-comparison-closeout-2026-06-20.md", text, str(path))
            self.assertIn("public benchmark claims", text, str(path))
            self.assertIn("comparison-report wording remain blocked", text, str(path))

        status = normalized(EXECUTION_STATUS)
        self.assertIn("H2 | Complete public release/package checklist", status)
        self.assertIn("H2 remains open", normalized(RECORD))

    def test_h1_record_is_indexed_once(self) -> None:
        self.assertEqual(
            1,
            read(VALIDATION_README).count("h1-public-safe-comparison-closeout-2026-06-20.md"),
        )

    def test_record_captures_manual_validation_and_evidence_hashes(self) -> None:
        text = normalized(RECORD)

        self.assertIn("Sibling commit: `572bae915b915c5d4e329146007de869e6c56c7a`", text)
        self.assertIn("Validated source HEAD before this record: `85617c3`", text)
        self.assertIn("make benchmark-publication-preflight", text)
        self.assertIn("make test", text)
        self.assertIn("make smoke", text)
        self.assertIn("status: ready", text)
        self.assertIn("blockers_total: 0", text)
        self.assertIn("findings_total: 0", text)
        self.assertIn("files_scanned: 21", text)
        self.assertIn("claim_findings_total: 0", text)
        self.assertIn("evidence_bundles_total: 5", text)
        self.assertIn("public_safe_bundles_total: 5", text)

        for digest in EXPECTED_HASHES:
            self.assertIn(digest, text)

    def test_record_preserves_public_claim_boundaries(self) -> None:
        for path in (EXECUTION_STATUS, PUBLIC_RELEASE_CHECKLIST, RECORD):
            text = normalized(path)
            for phrase in BOUNDARY_PHRASES:
                self.assertIn(phrase, text, f"{phrase} missing from {path}")

    def test_make_target_runs_h1_guard_after_next_step_guard(self) -> None:
        block = target_block("milestone-e-prep")
        next_steps_guard = "$(PYTHON) .github/scripts/test_release_readiness_next_steps_approval.py"
        h1_guard = "$(PYTHON) .github/scripts/test_h1_public_safe_comparison_closeout.py"
        schema_validation = "$(PYTHON) schemas/validate_examples.py"

        self.assertIn(h1_guard, block)
        self.assertLess(block.index(next_steps_guard), block.index(h1_guard))
        self.assertLess(block.index(h1_guard), block.index(schema_validation))

    def test_ci_runs_h1_guard_after_next_step_guard(self) -> None:
        text = read(CI_WORKFLOW)
        next_steps_guard = "python3 .github/scripts/test_release_readiness_next_steps_approval.py"
        h1_guard = "python3 .github/scripts/test_h1_public_safe_comparison_closeout.py"
        milestone_d = "python3 .github/scripts/test_milestone_d_internal_contracts.py"

        self.assertIn(h1_guard, text)
        self.assertEqual(1, text.count(h1_guard))
        self.assertLess(text.index(next_steps_guard), text.index(h1_guard))
        self.assertLess(text.index(h1_guard), text.index(milestone_d))

    def test_h1_closeout_docs_avoid_scope_expansion_language(self) -> None:
        text = "\n".join(
            read(path).lower()
            for path in (EXECUTION_STATUS, PUBLIC_RELEASE_CHECKLIST, RECORD)
        )

        for phrase in FORBIDDEN_SCOPE_EXPANSION:
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
