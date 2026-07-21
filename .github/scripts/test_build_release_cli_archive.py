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

from __future__ import annotations

import importlib.util
import tarfile
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / ".github/scripts/build_release_cli_archive.py"
DOCTOR = ROOT / "crates/ethos-cli/src/cmd/doctor.rs"
SPEC = importlib.util.spec_from_file_location("build_release_cli_archive", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class BuildReleaseCliArchiveTests(unittest.TestCase):
    def test_cli_does_not_embed_the_npm_vendor_manifest(self) -> None:
        doctor = DOCTOR.read_text(encoding="utf-8")
        self.assertNotIn('include_str!("../../../../packages/npm/ethos-pdf/vendor/manifest.json")', doctor)

    def test_two_archives_are_byte_identical_and_normalize_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            artifact_dir = Path(temp) / "ethos-linux-x64"
            artifact_dir.mkdir()
            for name, content in {
                "ethos": b"#!/bin/sh\necho ethos\n",
                "LICENSE": b"license\n",
                "NOTICE": b"notice\n",
                "pdfium-manual-setup.md": b"manual\n",
            }.items():
                (artifact_dir / name).write_bytes(content)

            first = Path(temp) / "first.tar.gz"
            second = Path(temp) / "second.tar.gz"
            MODULE.build_archive(artifact_dir, first)
            MODULE.build_archive(artifact_dir, second)

            self.assertEqual(first.read_bytes(), second.read_bytes())
            with tarfile.open(first, "r:gz") as archive:
                members = archive.getmembers()
                self.assertEqual(
                    [
                        "ethos-linux-x64",
                        "ethos-linux-x64/ethos",
                        "ethos-linux-x64/LICENSE",
                        "ethos-linux-x64/NOTICE",
                        "ethos-linux-x64/pdfium-manual-setup.md",
                    ],
                    [member.name for member in members],
                )
                self.assertTrue(all(member.mtime == 0 for member in members))
                self.assertTrue(all(member.uid == 0 and member.gid == 0 for member in members))

    def test_missing_required_file_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            artifact_dir = Path(temp) / "ethos-linux-x64"
            artifact_dir.mkdir()
            with self.assertRaisesRegex(ValueError, "missing required files: ethos"):
                MODULE.build_archive(artifact_dir, Path(temp) / "archive.tar.gz")


if __name__ == "__main__":
    unittest.main()
