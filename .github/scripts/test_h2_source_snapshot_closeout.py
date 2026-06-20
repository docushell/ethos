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
from test_milestone_e_source_snapshot_candidate_audit import PRIVATE_MARKERS


ROOT = Path(__file__).resolve().parents[2]
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"
RECORD = ROOT / "docs/validation/h2-source-snapshot-closeout-660f268-2026-06-20.md"
HISTORICAL_CLOSEOUT_RECORD = ROOT / "docs/validation/h2-source-snapshot-closeout-2026-06-20.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"

EXPECTED_APPROVAL = (
    "H2 approved for closeout: the exact source-snapshot candidate at source HEAD 660f268, "
    "archive ethos-source-snapshot-660f268.tar.gz, SHA256 "
    "58ec6fc1ec47a4c16f1294673ba9520b2fe9c2497e15ec96d78679db8517dd87, and "
    "source-snapshot-only surface is accepted for closeout. This does not approve binaries, "
    "wheels, npm packages, crate publication, hosted surfaces, public benchmark reports, "
    "public beta, production positioning, or wording beyond the exact approved pre-alpha sentence."
)
EXPECTED_SHA256 = "58ec6fc1ec47a4c16f1294673ba9520b2fe9c2497e15ec96d78679db8517dd87"

REQUIRED_BOUNDARIES = (
    "Binaries remain blocked.",
    "Wheels remain blocked.",
    "npm packages remain blocked.",
    "Crate publication remains blocked.",
    "Hosted surfaces remain blocked.",
    "Public benchmark reports remain blocked.",
    "Public beta remains blocked.",
    "Production positioning remains blocked.",
    "Public wording remains limited to the exact approved pre-alpha sentence.",
)

FORBIDDEN_SCOPE_EXPANSION = (
    "public beta approved",
    "binaries approved",
    "wheels approved",
    "npm packages approved",
    "crate publication approved",
    "hosted surfaces approved",
    "public benchmark reports approved",
    "first release approved",
    "release artifact approved",
    "production positioning approved",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalized(path: Path) -> str:
    return re.sub(r"\s+", " ", read(path))


class H2SourceSnapshotCloseoutTests(unittest.TestCase):
    def test_closeout_is_recorded_on_current_surfaces(self) -> None:
        for path in (EXECUTION_STATUS, PUBLIC_RELEASE_CHECKLIST, VALIDATION_README):
            text = normalized(path)
            self.assertIn("h2-source-snapshot-closeout-660f268-2026-06-20.md", text, str(path))
            self.assertIn("H2", text, str(path))

    def test_record_captures_exact_decider_approval(self) -> None:
        text = normalized(RECORD)

        self.assertIn(EXPECTED_APPROVAL, text)
        self.assertIn("Status: **H2 closed for exact source-snapshot candidate", text)
        self.assertIn("source-snapshot-only surface**", text)
        self.assertIn("Ethos remains source-only pre-alpha", text)

    def test_record_captures_candidate_identity_and_validation_basis(self) -> None:
        text = normalized(RECORD)

        self.assertIn("Candidate source HEAD: `660f268`", text)
        self.assertIn("Candidate archive: `ethos-source-snapshot-660f268.tar.gz`", text)
        self.assertIn(EXPECTED_SHA256, text)
        self.assertIn("Candidate archive prefix: `ethos-source-snapshot-660f268/`", text)
        self.assertIn("Approved artifact class: `source-snapshot`", text)
        self.assertIn("Approved surface: `source-snapshot-only`", text)
        self.assertIn("extraction check over `501` files", text)
        self.assertIn("source-snapshot candidate audit pass", text)
        self.assertIn("blocked-artifact scan pass", text)
        self.assertIn("untracked/build-path scan pass", text)
        self.assertIn("claims gate green", text)

    def test_non_source_snapshot_artifacts_remain_blocked(self) -> None:
        text = read(RECORD)

        for boundary in REQUIRED_BOUNDARIES:
            self.assertIn(boundary, text)

    def test_current_docs_show_h2_closed_only_for_exact_candidate(self) -> None:
        docs = "\n".join(normalized(path) for path in (EXECUTION_STATUS, PUBLIC_RELEASE_CHECKLIST))

        self.assertIn("H2 is closed for the exact source-snapshot candidate at source HEAD `660f268`", docs)
        self.assertIn("source-snapshot-only surface", docs)
        self.assertIn("binaries, wheels, npm packages, crate publication, hosted surfaces", docs)
        self.assertIn("public benchmark reports remain blocked", docs)

    def test_closeout_record_is_indexed_once(self) -> None:
        self.assertEqual(
            1,
            read(VALIDATION_README).count("h2-source-snapshot-closeout-660f268-2026-06-20.md"),
        )
        self.assertEqual(1, read(VALIDATION_README).count("h2-source-snapshot-closeout-2026-06-20.md"))
        self.assertTrue(HISTORICAL_CLOSEOUT_RECORD.is_file())

    def test_make_target_runs_closeout_guard_after_candidate_guard(self) -> None:
        block = target_block("milestone-e-prep")
        candidate_guard = "$(PYTHON) .github/scripts/test_h2_source_snapshot_candidate_evidence.py"
        closeout_guard = "$(PYTHON) .github/scripts/test_h2_source_snapshot_closeout.py"
        schema_validation = "$(PYTHON) schemas/validate_examples.py"

        self.assertIn(closeout_guard, block)
        self.assertLess(block.index(candidate_guard), block.index(closeout_guard))
        self.assertLess(block.index(closeout_guard), block.index(schema_validation))

    def test_ci_runs_closeout_guard_after_candidate_guard(self) -> None:
        text = read(CI_WORKFLOW)
        candidate_guard = "python3 .github/scripts/test_h2_source_snapshot_candidate_evidence.py"
        closeout_guard = "python3 .github/scripts/test_h2_source_snapshot_closeout.py"
        milestone_d = "python3 .github/scripts/test_milestone_d_internal_contracts.py"

        self.assertIn(closeout_guard, text)
        self.assertEqual(1, text.count(closeout_guard))
        self.assertLess(text.index(candidate_guard), text.index(closeout_guard))
        self.assertLess(text.index(closeout_guard), text.index(milestone_d))

    def test_scope_docs_avoid_unapproved_expansion_language(self) -> None:
        text = "\n".join(read(path).lower() for path in (EXECUTION_STATUS, PUBLIC_RELEASE_CHECKLIST, RECORD))

        for phrase in FORBIDDEN_SCOPE_EXPANSION:
            self.assertNotIn(phrase, text)

    def test_record_avoids_local_private_paths(self) -> None:
        text = read(RECORD)

        for marker in PRIVATE_MARKERS:
            self.assertNotIn(marker, text, marker)


if __name__ == "__main__":
    unittest.main()
