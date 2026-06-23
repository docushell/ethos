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

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SCRIPT = ROOT / "check_golden_change_rationale.py"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "check_golden_change_rationale_under_test",
        SCRIPT,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHECK = load_module()


class GoldenChangeRationaleTests(unittest.TestCase):
    def test_fixture_stage_goldens_are_golden_like(self) -> None:
        for name in [
            "extraction.json",
            "layout.json",
            "markdown.md",
            "tables.json",
            "text.txt",
        ]:
            with self.subTest(name=name):
                self.assertTrue(
                    CHECK.is_golden_like(f"fixtures/synthetic/simple-text/{name}")
                )

    def test_fixture_metadata_is_not_golden_like(self) -> None:
        self.assertFalse(
            CHECK.is_golden_like("fixtures/synthetic/simple-text/fixture.json")
        )
        self.assertFalse(CHECK.is_golden_like("fixtures/manifest.json"))

    def test_existing_golden_patterns_still_match(self) -> None:
        self.assertTrue(
            CHECK.is_golden_like("examples/verify/goldens/native_grounded_report.json")
        )
        self.assertTrue(
            CHECK.is_golden_like(
                "fixtures/foreign/opendataloader/real/expected.verification_report.json"
            )
        )


if __name__ == "__main__":
    unittest.main()
