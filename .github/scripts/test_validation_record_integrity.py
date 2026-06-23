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
SCRIPT = ROOT / "validation_record_integrity.py"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "validation_record_integrity_under_test",
        SCRIPT,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


INTEGRITY = load_module()


class ValidationRecordIntegrityTests(unittest.TestCase):
    def test_hex_ref_matcher_ignores_decimal_workflow_run_ids(self) -> None:
        text = "workflow run `28004938177`, commit `dd155e4`, tree `ba0291a`"

        self.assertEqual(
            sorted(set(INTEGRITY.HEX_REF.findall(text))),
            ["ba0291a", "dd155e4"],
        )


if __name__ == "__main__":
    unittest.main()
