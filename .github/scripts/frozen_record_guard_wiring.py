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

"""Shared CI wiring assertion for manifest-driven frozen-record guards."""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Optional


MANIFEST = ".github/scripts/frozen_record_guards.json"
CI_WORKFLOW = ".github/workflows/ci.yml"
RUNNER_COMMAND = "python3 .github/scripts/run_frozen_record_guards.py"


def assert_frozen_guard_ci_wiring(
    test: unittest.TestCase,
    *,
    root: Path,
    guard_file: Optional[str] = None,
    guard_path: Optional[str] = None,
) -> None:
    """Require manifest membership and one indirect CI runner invocation."""

    if (guard_file is None) == (guard_path is None):
        raise ValueError("provide exactly one of guard_file or guard_path")
    if guard_file is not None:
        guard_path = Path(guard_file).resolve().relative_to(root.resolve()).as_posix()
    assert guard_path is not None

    manifest = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    guards = manifest["guards"]
    ci = (root / CI_WORKFLOW).read_text(encoding="utf-8")

    test.assertEqual(1, guards.count(guard_path), f"manifest membership for {guard_path}")
    test.assertEqual(1, ci.count(RUNNER_COMMAND), "frozen-record runner CI wiring")
    test.assertNotIn(guard_path, ci, f"{guard_path} must run only through the manifest")
