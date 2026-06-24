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
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class Patch012NpmVendorRefreshTests(unittest.TestCase):
    def test_current_npm_vendor_refresh_candidate_evidence_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, ".github/scripts/test_npm_tarball_candidate_evidence.py"],
            cwd=ROOT,
            check=False,
            encoding="utf-8",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("Ran 4 tests", result.stderr)
        self.assertIn("OK", result.stderr)


if __name__ == "__main__":
    unittest.main()
