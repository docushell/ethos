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
RECORD = ROOT / "docs/validation/milestone-d-contract-closeout-prep-2026-06-19.md"
VALIDATION_README = ROOT / "docs/validation/README.md"


def record_text() -> str:
    return RECORD.read_text(encoding="utf-8")


def normalized_record_text() -> str:
    return re.sub(r"\s+", " ", record_text())


class MilestoneDContractCloseoutPrepRecordTests(unittest.TestCase):
    def test_record_is_indexed(self) -> None:
        text = VALIDATION_README.read_text(encoding="utf-8")

        self.assertIn("milestone-d-contract-closeout-prep-2026-06-19.md", text)

    def test_record_names_internal_validation_command(self) -> None:
        text = record_text()

        self.assertIn("make milestone-d-internal-contracts PYTHON=<jsonschema-venv>/bin/python", text)
        self.assertIn(".github/scripts/test_milestone_d_closeout_prep_record.py", text)
        self.assertIn(".github/scripts/test_milestone_d_internal_contracts.py", text)
        for target in [
            "make milestone-d-verify-citations-contract",
            "make milestone-d-claim-kind-boundary-contract",
            "make milestone-d-grounding-source-contract",
            "make milestone-d-opendataloader-adapter-shape-contract",
            "make milestone-d-capability-downgrade-contract",
            "make milestone-d-crop-element-contract",
            "make milestone-d-crop-element-surface-shape-contract",
            "make milestone-d-sandbox-subprocess-contract",
        ]:
            self.assertIn(target, text)

    def test_record_keeps_closeout_prep_scope(self) -> None:
        text = normalized_record_text()

        self.assertIn("source-only contract closeout prep", text)
        self.assertIn("final D exit still pending review and a fresh validation run on `main`", text)
        self.assertIn(
            "Node, MCP, hosted, sandbox-backed, and foreign-adapter crop surfaces are explicitly "
            "out of Milestone D closeout scope and remain outside this prep record",
            text,
        )
        self.assertIn(
            "Cross-platform rendered-crop byte identity is not required for Milestone D closeout "
            "and remains outside this prep record",
            text,
        )
        self.assertIn("Sandbox hardening remains outside this prep record", text)
        self.assertIn(
            "Node beta and MCP experimental work remain outside this prep record and outside "
            "Milestone D closeout scope",
            text,
        )

    def test_record_keeps_public_boundaries_explicit(self) -> None:
        text = normalized_record_text()

        self.assertIn("does not approve public benchmark reports", text)
        self.assertIn("Release artifacts and package publication remain blocked", text)
        self.assertIn("Production positioning remains blocked", text)
        self.assertIn(
            "Performance, quality, footprint, table-quality, and parser-quality claims remain blocked",
            text,
        )

    def test_make_target_runs_closeout_prep_guard(self) -> None:
        block = target_block("milestone-d-internal-contracts")

        self.assertIn("$(PYTHON) .github/scripts/test_milestone_d_closeout_prep_record.py", block)
        self.assertLess(
            block.index("$(PYTHON) .github/scripts/test_milestone_d_closeout_prep_record.py"),
            block.index("$(PYTHON) .github/scripts/test_milestone_d_internal_contracts.py"),
        )

    def test_record_avoids_local_private_paths(self) -> None:
        text = record_text()

        self.assertNotIn("/Users/", text)
        self.assertNotIn("/private/tmp", text)
        self.assertNotIn("/private/var", text)


if __name__ == "__main__":
    unittest.main()
