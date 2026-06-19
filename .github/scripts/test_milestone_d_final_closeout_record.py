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
RECORD = ROOT / "docs/validation/milestone-d-final-closeout-validation-2026-06-19.md"
VALIDATION_README = ROOT / "docs/validation/README.md"


def record_text() -> str:
    return RECORD.read_text(encoding="utf-8")


def normalized_record_text() -> str:
    return re.sub(r"\s+", " ", record_text())


class MilestoneDFinalCloseoutRecordTests(unittest.TestCase):
    def test_record_is_indexed(self) -> None:
        text = VALIDATION_README.read_text(encoding="utf-8")

        self.assertIn("milestone-d-final-closeout-validation-2026-06-19.md", text)

    def test_record_names_final_validation_commands(self) -> None:
        text = record_text()

        self.assertIn("Validated source HEAD before this record: `792190e`", text)
        self.assertIn("make milestone-d-internal-contracts PYTHON=<jsonschema-venv>/bin/python", text)
        self.assertIn("cargo test --locked -p ethos-cli", text)
        self.assertIn(
            "cargo clippy --locked -p ethos-core -p ethos-cli --all-targets -- -D warnings",
            text,
        )
        self.assertIn("cargo fmt --all --check", text)
        self.assertIn("git diff --check", text)

    def test_record_closes_d_without_expanding_scope(self) -> None:
        text = normalized_record_text()

        self.assertIn("pass for internal Milestone D source-only closeout", text)
        self.assertIn(
            "Milestone D is internally complete for the current source-tree, source-only pre-alpha scope",
            text,
        )
        self.assertIn("Ethos remains source-only pre-alpha", text)
        self.assertIn("Node, MCP, hosted, sandbox-backed, and foreign-adapter crop surfaces are post-D blockers", text)
        self.assertIn("Cross-platform rendered-crop byte identity is not required for Milestone D closeout", text)
        self.assertIn("Sandbox hardening beyond the current worker-process contract remains future work", text)

    def test_record_keeps_public_boundaries_explicit(self) -> None:
        text = normalized_record_text()

        self.assertIn("does not approve public benchmark reports", text)
        self.assertIn("Release artifacts and package publication remain blocked", text)
        self.assertIn("Production positioning remains blocked", text)
        self.assertIn(
            "Performance, quality, footprint, table-quality, and parser-quality claims remain blocked",
            text,
        )

    def test_record_names_closed_contract_scope(self) -> None:
        text = normalized_record_text()

        for contract in [
            "verify_citations",
            "claim_kind_boundary",
            "grounding_source",
            "opendataloader_adapter_shape",
            "capability_downgrade",
            "crop_element",
            "crop_element_surface_shape",
            "sandbox_subprocess",
        ]:
            self.assertIn(contract, text)
        self.assertIn("Request-envelope identity is guarded", text)
        self.assertIn("Explicit blockers remain mirrored between contract docs and inventories", text)

    def test_make_target_runs_final_closeout_record_guard(self) -> None:
        block = target_block("milestone-d-internal-contracts")
        contract_guard = "$(PYTHON) .github/scripts/test_milestone_d_closeout_record.py"
        final_guard = "$(PYTHON) .github/scripts/test_milestone_d_final_closeout_record.py"
        registry_guard = "$(PYTHON) .github/scripts/test_milestone_d_internal_contracts.py"

        self.assertIn(final_guard, block)
        self.assertLess(block.index(contract_guard), block.index(final_guard))
        self.assertLess(block.index(final_guard), block.index(registry_guard))

    def test_record_avoids_local_private_paths(self) -> None:
        text = record_text()

        self.assertNotIn("/Users/", text)
        self.assertNotIn("/private/tmp", text)
        self.assertNotIn("/private/var", text)


if __name__ == "__main__":
    unittest.main()
