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
"""Structural guard: governance that nobody executes is not governance.

Two failure modes had gone unnoticed for months before this gate existed:

- 15 gate scripts were unreachable from CI. They ran only from a `make` target, so when
  `docs/roadmap.md` was deleted as a completed historical record, the eight contract gates
  asserting it still existed simply went red and stayed red.
- Seven `make` targets referenced roughly 280 scripts that had been deleted, including
  `test_roadmap_status.py` in eleven places. Those targets could not run at all, which is
  precisely why nobody noticed the gates behind them were broken.

A red gate nobody runs is worse than no gate: it costs real time whenever someone finally
runs it, and it trains readers to ignore failures. This file makes both states impossible.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / ".github/scripts"
WORKFLOWS = ROOT / ".github/workflows"
MAKEFILE = ROOT / "Makefile"
SCRIPT_REF = re.compile(r"\.github/scripts/([a-z0-9_]+\.py)")

# This module is itself invoked by name from the governance-gates job.
SELF = "test_gate_reachability.py"


def workflow_text() -> str:
    return "\n".join(p.read_text(encoding="utf-8") for p in sorted(WORKFLOWS.glob("*.yml")))


def makefile_blocks() -> dict[str, list[str]]:
    blocks: dict[str, list[str]] = {}
    current: str | None = None
    for line in MAKEFILE.read_text(encoding="utf-8").splitlines():
        header = re.match(r"^([a-zA-Z][a-zA-Z0-9._-]*):", line)
        if header:
            current = header.group(1)
            blocks[current] = []
        elif current and line.startswith("\t"):
            blocks[current].append(line)
    return blocks


def gates() -> set[str]:
    return {p.name for p in SCRIPTS.glob("test_*.py")}


def ci_reachable() -> set[str]:
    """Gate scripts CI executes, named directly or via a `make` target CI runs."""
    text = workflow_text()
    reachable = set(re.findall(r"(test_[a-z0-9_]+)\.py", text))
    reachable = {f"{name}.py" for name in reachable}
    blocks = makefile_blocks()
    for target in set(re.findall(r"make ([a-z0-9][a-z0-9-]*)", text)):
        for line in blocks.get(target, []):
            reachable.update(SCRIPT_REF.findall(line))
    return reachable


class GateReachabilityTests(unittest.TestCase):
    def test_every_gate_script_is_reachable_from_ci(self) -> None:
        orphans = sorted(gates() - ci_reachable() - {SELF})

        self.assertEqual(
            [],
            orphans,
            "these gate scripts are never executed by CI. Either wire each into a workflow "
            "(directly or through a `make` target CI runs) or delete it. An unrun gate rots "
            f"silently and blocks whoever runs it next: {orphans}",
        )

    def test_makefile_only_references_scripts_that_exist(self) -> None:
        missing: dict[str, set[str]] = {}
        for target, lines in makefile_blocks().items():
            for line in lines:
                for script in SCRIPT_REF.findall(line):
                    if not (SCRIPTS / script).is_file():
                        missing.setdefault(target, set()).add(script)

        self.assertEqual(
            {},
            {t: sorted(s) for t, s in missing.items()},
            "these `make` targets invoke scripts that do not exist, so the target cannot run. "
            "Remove the target if its release or milestone has shipped.",
        )

    def test_workflows_only_reference_scripts_that_exist(self) -> None:
        missing = sorted(
            {s for s in SCRIPT_REF.findall(workflow_text()) if not (SCRIPTS / s).is_file()}
        )

        self.assertEqual([], missing, f"workflows reference missing gate scripts: {missing}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
