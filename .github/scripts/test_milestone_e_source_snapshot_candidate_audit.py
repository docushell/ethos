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

import subprocess
import unittest
from dataclasses import dataclass
from pathlib import Path

from makefile_guard import target_block


ROOT = Path(__file__).resolve().parents[2]
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"
GATE_ZERO_RUNBOOK = ROOT / "docs/gate-zero-evidence-runbook.md"

PRIVATE_MARKERS = (
    "/Users/",
    "/private/tmp",
    "/private/var",
    "/var/folders",
    "saumildiwaker",
    "Desktop/Stuff",
    "project/repo/ethos",
    "docs/.roadmap.md.swp",
    "web/",
)

BLOCKED_ARTIFACT_SUFFIXES = (
    ".whl",
    ".crate",
    ".dmg",
    ".pkg",
    ".deb",
    ".rpm",
    ".exe",
    ".msi",
)

BLOCKED_ARTIFACT_FILENAMES = {"npm-debug.log"}


@dataclass(frozen=True)
class PrivateMarkerHit:
    path: str
    line_number: int
    marker: str
    line: str


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    return [line for line in result.stdout.splitlines() if line]


def private_marker_hits() -> list[PrivateMarkerHit]:
    hits: list[PrivateMarkerHit] = []
    for relative_path in tracked_files():
        path = ROOT / relative_path
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        for line_number, line in enumerate(text.splitlines(), start=1):
            for marker in PRIVATE_MARKERS:
                if marker in line:
                    hits.append(
                        PrivateMarkerHit(
                            path=relative_path,
                            line_number=line_number,
                            marker=marker,
                            line=line.strip(),
                        )
                    )
    return hits


def is_allowed_sentinel_hit(hit: PrivateMarkerHit) -> bool:
    if hit.path.startswith(".github/scripts/test_") and hit.path.endswith(".py"):
        return (
            "assertNotIn(" in hit.line
            or hit.path == ".github/scripts/test_milestone_e_source_snapshot_candidate_audit.py"
        )

    if hit.path == "docs/validation/public-source-push-preflight-2026-06-15.md":
        return "git ls-files" in hit.line and "<private-user-or-host-pattern>" in hit.line

    return False


def blocked_artifact_paths() -> list[str]:
    blocked: list[str] = []
    for relative_path in tracked_files():
        name = Path(relative_path).name
        if name in BLOCKED_ARTIFACT_FILENAMES or name.endswith(BLOCKED_ARTIFACT_SUFFIXES):
            blocked.append(relative_path)
    return blocked


class MilestoneESourceSnapshotCandidateAuditTests(unittest.TestCase):
    def test_private_path_scan_classifies_only_intentional_sentinel_literals(self) -> None:
        unexpected = [
            hit
            for hit in private_marker_hits()
            if not is_allowed_sentinel_hit(hit)
        ]

        self.assertEqual(
            [],
            [
                f"{hit.path}:{hit.line_number}: {hit.marker}: {hit.line}"
                for hit in unexpected
            ],
        )

    def test_gate_zero_runbook_uses_portable_python_placeholder(self) -> None:
        text = read(GATE_ZERO_RUNBOOK)

        self.assertIn("make verify-alpha PYTHON=<jsonschema-venv>/bin/python", text)
        self.assertNotIn("/private/tmp", text)

    def test_source_snapshot_scope_has_no_tracked_blocked_artifact_payloads(self) -> None:
        self.assertEqual([], blocked_artifact_paths())

    def test_make_target_runs_audit_after_h2_scope_guard(self) -> None:
        block = target_block("milestone-e-prep")
        h2_guard = "$(PYTHON) .github/scripts/test_h2_source_snapshot_scope_approval.py"
        audit_guard = "$(PYTHON) .github/scripts/test_milestone_e_source_snapshot_candidate_audit.py"
        schema_validation = "$(PYTHON) schemas/validate_examples.py"

        self.assertIn(audit_guard, block)
        self.assertLess(block.index(h2_guard), block.index(audit_guard))
        self.assertLess(block.index(audit_guard), block.index(schema_validation))

    def test_ci_runs_audit_after_h2_scope_guard(self) -> None:
        text = read(CI_WORKFLOW)
        h2_guard = "python3 .github/scripts/test_h2_source_snapshot_scope_approval.py"
        audit_guard = "python3 .github/scripts/test_milestone_e_source_snapshot_candidate_audit.py"
        milestone_d = "python3 .github/scripts/test_milestone_d_internal_contracts.py"

        self.assertIn(audit_guard, text)
        self.assertEqual(1, text.count(audit_guard))
        self.assertLess(text.index(h2_guard), text.index(audit_guard))
        self.assertLess(text.index(audit_guard), text.index(milestone_d))


if __name__ == "__main__":
    unittest.main()
