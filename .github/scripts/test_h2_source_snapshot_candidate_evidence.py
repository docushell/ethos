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
RECORD = ROOT / "docs/validation/h2-source-snapshot-candidate-evidence-660f268-2026-06-20.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"

EXPECTED_SHA256 = "58ec6fc1ec47a4c16f1294673ba9520b2fe9c2497e15ec96d78679db8517dd87"

BOUNDARY_PHRASES = (
    "does not close H2 for this candidate",
    "does not approve public beta",
    "does not approve binaries",
    "does not approve wheels",
    "does not approve npm packages",
    "does not approve crate publication",
    "does not approve hosted surfaces",
    "does not approve public benchmark reports",
    "does not approve wording beyond the exact approved pre-alpha sentence",
)

FORBIDDEN_SCOPE_EXPANSION = (
    "h2 closed for this candidate",
    "public beta approved",
    "binaries approved",
    "wheels approved",
    "npm packages approved",
    "crate publication approved",
    "hosted surfaces approved",
    "public benchmark reports approved",
    "first release approved",
    "release artifact approved",
)

def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalized(path: Path) -> str:
    return re.sub(r"\s+", " ", read(path))


class H2SourceSnapshotCandidateEvidenceTests(unittest.TestCase):
    def test_candidate_evidence_is_recorded_on_current_surfaces(self) -> None:
        for path in (EXECUTION_STATUS, PUBLIC_RELEASE_CHECKLIST, VALIDATION_README):
            text = normalized(path)
            self.assertIn("h2-source-snapshot-candidate-evidence-660f268-2026-06-20.md", text)

    def test_record_captures_candidate_identity_and_hash(self) -> None:
        text = normalized(RECORD)

        self.assertIn(
            "Status: **refreshed source-snapshot candidate evidence recorded; closeout recorded separately for this candidate**",
            text,
        )
        self.assertIn("Candidate source HEAD: `660f268`", text)
        self.assertIn("Candidate archive: `ethos-source-snapshot-660f268.tar.gz`", text)
        self.assertIn(EXPECTED_SHA256, text)
        self.assertIn("Candidate archive prefix: `ethos-source-snapshot-660f268/`", text)
        self.assertIn("Extracted file count: `501`", text)
        self.assertIn("Approved artifact class: `source-snapshot`", text)

    def test_record_captures_required_files_and_manual_validation(self) -> None:
        text = normalized(RECORD)

        for required in (
            "`LICENSE`",
            "`NOTICE`",
            "`README.md`",
            "`docs/gate-zero-evidence-runbook.md`",
            "`docs/public-release-checklist.md`",
            "`docs/release-artifact-notices.md`",
            "SOURCE_SNAPSHOT_EXTRACT_OK",
            "source-snapshot candidate audit: pass",
            "BLOCKED_ARTIFACT_SCAN_PASS",
            "UNTRACKED_OR_BUILD_PATH_SCAN_PASS",
            "public surface posture tests: pass",
            "public pre-alpha wording approval tests: pass",
            "claims gate green",
            "diff hygiene: pass",
        ):
            self.assertIn(required, text)

    def test_boundaries_remain_explicit_and_h2_open(self) -> None:
        text = normalized(RECORD)

        self.assertIn("Ethos remains source-only pre-alpha", text)
        self.assertIn("H2 closeout is recorded separately for this candidate", text)
        self.assertIn("source HEAD `60abfd4`", text)
        self.assertIn("h2-source-snapshot-closeout-660f268-2026-06-20.md", text)
        for phrase in BOUNDARY_PHRASES:
            self.assertIn(phrase, text, phrase)

    def test_current_docs_reference_candidate_and_closeout_records(self) -> None:
        docs = "\n".join(normalized(path) for path in (EXECUTION_STATUS, PUBLIC_RELEASE_CHECKLIST))

        self.assertIn("source-snapshot candidate evidence", docs)
        self.assertIn("h2-source-snapshot-closeout-660f268-2026-06-20.md", docs)
        self.assertIn("binaries, wheels, npm packages, crate publication, hosted surfaces", docs)

    def test_candidate_record_is_indexed_once(self) -> None:
        self.assertEqual(
            1,
            read(VALIDATION_README).count("h2-source-snapshot-candidate-evidence-660f268-2026-06-20.md"),
        )

    def test_make_target_runs_candidate_guard_after_snapshot_audit(self) -> None:
        block = target_block("milestone-e-prep")
        audit_guard = "$(PYTHON) .github/scripts/test_milestone_e_source_snapshot_candidate_audit.py"
        candidate_guard = "$(PYTHON) .github/scripts/test_h2_source_snapshot_candidate_evidence.py"
        closeout_guard = "$(PYTHON) .github/scripts/test_h2_source_snapshot_closeout.py"
        schema_validation = "$(PYTHON) schemas/validate_examples.py"

        self.assertIn(candidate_guard, block)
        self.assertIn(closeout_guard, block)
        self.assertLess(block.index(audit_guard), block.index(candidate_guard))
        self.assertLess(block.index(candidate_guard), block.index(closeout_guard))
        self.assertLess(block.index(closeout_guard), block.index(schema_validation))

    def test_ci_runs_candidate_guard_after_snapshot_audit(self) -> None:
        text = read(CI_WORKFLOW)
        audit_guard = "python3 .github/scripts/test_milestone_e_source_snapshot_candidate_audit.py"
        candidate_guard = "python3 .github/scripts/test_h2_source_snapshot_candidate_evidence.py"
        closeout_guard = "python3 .github/scripts/test_h2_source_snapshot_closeout.py"
        milestone_d = "python3 .github/scripts/test_milestone_d_internal_contracts.py"

        self.assertIn(candidate_guard, text)
        self.assertIn(closeout_guard, text)
        self.assertEqual(1, text.count(candidate_guard))
        self.assertLess(text.index(audit_guard), text.index(candidate_guard))
        self.assertLess(text.index(candidate_guard), text.index(closeout_guard))
        self.assertLess(text.index(closeout_guard), text.index(milestone_d))

    def test_scope_docs_avoid_scope_expansion_language(self) -> None:
        text = read(RECORD).lower()

        for phrase in FORBIDDEN_SCOPE_EXPANSION:
            self.assertNotIn(phrase, text)

    def test_record_avoids_local_private_paths(self) -> None:
        text = read(RECORD)

        for marker in PRIVATE_MARKERS:
            self.assertNotIn(marker, text, marker)


if __name__ == "__main__":
    unittest.main()
