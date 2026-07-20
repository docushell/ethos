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

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from check_release_boundary_paths import is_heavy
from run_frozen_record_guards import (
    DEFAULT_MANIFEST,
    ROOT,
    ManifestError,
    load_manifest,
    run_guards,
)


EXPECTED_DEFAULT_GUARD_COUNT = 1
EXPECTED_DEFAULT_INVENTORY_SHA256 = (
    "7ae1331b5b464b812be1c9e18d589fb13ef350f16d24ae367dca8511b6af6857"
)


class FrozenRecordGuardRunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.scripts = self.root / ".github/scripts"
        self.scripts.mkdir(parents=True)
        self.manifest = self.root / "manifest.json"

    def write_script(self, name: str, source: str = "raise SystemExit(0)\n") -> str:
        relative = f".github/scripts/{name}"
        (self.root / relative).write_text(source, encoding="utf-8")
        return relative

    def write_manifest(self, guards: object) -> None:
        self.manifest.write_text(
            json.dumps({"schema_version": 1, "guards": guards}),
            encoding="utf-8",
        )

    def test_repository_manifest_inventory_is_pinned_and_boundary_guarded(self) -> None:
        guards = load_manifest(ROOT, DEFAULT_MANIFEST)
        labels = [label for label, _ in guards]
        inventory_sha256 = hashlib.sha256(
            "\n".join(labels).encode("utf-8")
        ).hexdigest()

        self.assertEqual(EXPECTED_DEFAULT_GUARD_COUNT, len(labels))
        self.assertEqual(EXPECTED_DEFAULT_INVENTORY_SHA256, inventory_sha256)
        self.assertTrue(
            is_heavy(DEFAULT_MANIFEST.relative_to(ROOT).as_posix()),
            "the frozen guard inventory must require a boundary-exception review",
        )

    def test_empty_manifest_is_rejected(self) -> None:
        self.write_manifest([])

        with self.assertRaisesRegex(ManifestError, "non-empty array"):
            load_manifest(self.root, self.manifest)

    def test_duplicate_guard_is_rejected(self) -> None:
        guard = self.write_script("test_example.py")
        self.write_manifest([guard, guard])

        with self.assertRaisesRegex(ManifestError, "duplicate guard path"):
            load_manifest(self.root, self.manifest)

    def test_path_escape_is_rejected(self) -> None:
        self.write_manifest([".github/scripts/../test_escape.py"])

        with self.assertRaisesRegex(ManifestError, "escapes the repository"):
            load_manifest(self.root, self.manifest)

    def test_missing_script_is_rejected(self) -> None:
        self.write_manifest([".github/scripts/test_missing.py"])

        with self.assertRaisesRegex(ManifestError, "does not exist"):
            load_manifest(self.root, self.manifest)

    def test_python_interpreter_is_forwarded(self) -> None:
        guard = self.write_script("test_example.py")
        self.write_manifest([guard])
        guards = load_manifest(self.root, self.manifest)
        completed = mock.Mock(returncode=0)

        with mock.patch(
            "run_frozen_record_guards.subprocess.run", return_value=completed
        ) as run:
            result = run_guards(self.root, guards, python="chosen-python")

        self.assertEqual(0, result)
        run.assert_called_once_with(
            ["chosen-python", str(self.root / guard)],
            cwd=self.root,
            check=False,
        )

    def test_nonzero_exit_is_propagated_and_stops_the_run(self) -> None:
        first = self.write_script("test_first.py", "raise SystemExit(7)\n")
        marker = self.root / "second-ran"
        second = self.write_script(
            "test_second.py",
            "from pathlib import Path\nPath('second-ran').write_text('ran')\n",
        )
        self.write_manifest([first, second])

        result = run_guards(
            self.root,
            load_manifest(self.root, self.manifest),
            python=sys.executable,
        )

        self.assertEqual(7, result)
        self.assertFalse(marker.exists())


if __name__ == "__main__":
    unittest.main()
