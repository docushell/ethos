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

import tempfile
import unittest
from pathlib import Path

import font_policy_validation


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class FontPolicyValidationTests(unittest.TestCase):
    def with_repo(self):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        table = root / "crates/ethos-pdf/assets/font-substitution-table.json"
        write(table, '{"schema_version":"1.0.0"}\n')
        profile = {
            "font_policy": {
                "substitution_table": {
                    "path": "crates/ethos-pdf/assets/font-substitution-table.json",
                    "sha256": font_policy_validation.sha256_file(table),
                },
                "fallback_bundle": {
                    "name": "liberation",
                    "license": "OFL-1.1",
                    "sha256": None,
                },
            }
        }
        return temp, root, profile

    def test_current_null_fallback_contract_passes_when_bundle_is_absent(self) -> None:
        temp, root, profile = self.with_repo()
        with temp:
            self.assertEqual(font_policy_validation.diagnose_font_policy(root, profile), [])

    def test_substitution_table_hash_mismatch_fails_closed(self) -> None:
        temp, root, profile = self.with_repo()
        with temp:
            profile["font_policy"]["substitution_table"]["sha256"] = "0" * 64
            diagnostics = font_policy_validation.diagnose_font_policy(root, profile)
        self.assertEqual(len(diagnostics), 1)
        self.assertIn("substitution_table.sha256 mismatch", diagnostics[0])

    def test_unsafe_substitution_table_path_fails_closed(self) -> None:
        temp, root, profile = self.with_repo()
        with temp:
            profile["font_policy"]["substitution_table"]["path"] = "../font-table.json"
            diagnostics = font_policy_validation.diagnose_font_policy(root, profile)
        self.assertEqual(
            diagnostics,
            ["font_policy.substitution_table.path must be a safe relative path"],
        )

    def test_null_fallback_hash_fails_when_bundle_exists(self) -> None:
        temp, root, profile = self.with_repo()
        with temp:
            write(
                root / font_policy_validation.FALLBACK_BUNDLE_DIR / "LiberationSans-Regular.ttf",
                "font bytes",
            )
            diagnostics = font_policy_validation.diagnose_font_policy(root, profile)
        self.assertEqual(len(diagnostics), 1)
        self.assertIn("fallback_bundle.sha256 is null", diagnostics[0])

    def test_fallback_bundle_hash_can_pin_directory_payload(self) -> None:
        temp, root, profile = self.with_repo()
        with temp:
            bundle_dir = root / font_policy_validation.FALLBACK_BUNDLE_DIR
            write(bundle_dir / "LiberationSans-Regular.ttf", "font bytes")
            profile["font_policy"]["fallback_bundle"]["sha256"] = (
                font_policy_validation.sha256_directory(bundle_dir)
            )
            self.assertEqual(font_policy_validation.diagnose_font_policy(root, profile), [])

    def test_set_fallback_hash_requires_bundle_directory(self) -> None:
        temp, root, profile = self.with_repo()
        with temp:
            profile["font_policy"]["fallback_bundle"]["sha256"] = "1" * 64
            diagnostics = font_policy_validation.diagnose_font_policy(root, profile)
        self.assertEqual(len(diagnostics), 1)
        self.assertIn("fallback_bundle.sha256 is set", diagnostics[0])


if __name__ == "__main__":
    unittest.main()
