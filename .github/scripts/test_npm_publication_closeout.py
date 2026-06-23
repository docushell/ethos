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

import json
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "docs/validation/patch-0-1-1-npm-publication-closeout-validation-2026-06-24.md"
VALIDATION_README = ROOT / "docs/validation/README.md"

SOURCE_SHORT = "65360a9"
SOURCE_COMMIT = "65360a9012104227ba939f6d30f2ec7b82b2ac4d"
SOURCE_TREE = "85465e6eb1918155088e4d4cb4f5608f5ea65589"
PACKAGE = "@docushell/ethos-pdf"
VERSION = "0.1.1"
SHASUM = "a150d08395724aa186d077074782413249a48689"
INTEGRITY = "sha512-wVF4Ew6836sRncPZkvVieyQuo8FFbbBsIQ/vdupleUQZVX4YHgXb+lFZzZNcVB54Hh7srbbY17El4Z5sV7odhA=="


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalized(path: Path) -> str:
    return re.sub(r"\s+", " ", read(path))


def npm_view(*args: str) -> str:
    with tempfile.TemporaryDirectory(prefix="ethos-npm-view-") as temp:
        return subprocess.check_output(
            ["npm", "view", *args, "--registry=https://registry.npmjs.org/"],
            cwd=ROOT,
            encoding="utf-8",
            env={**os.environ, "npm_config_cache": str(Path(temp) / "npm-cache")},
            stderr=subprocess.DEVNULL,
        ).strip()


class NpmPublicationCloseoutTests(unittest.TestCase):
    def test_record_is_source_bound_and_indexed(self) -> None:
        record = normalized(RECORD)
        readme = normalized(VALIDATION_README)

        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"npm publication closeout source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"npm publication closeout source tree: `{SOURCE_TREE}`", record)
        self.assertIn(RECORD.name, readme)
        self.assertIn("npm publication closeout validation", readme)

    def test_record_captures_publish_and_registry_evidence(self) -> None:
        record = normalized(RECORD)

        for expected in (
            "+ @docushell/ethos-pdf@0.1.1",
            "npm auto-corrected",
            '"bin[ethos]" script name was cleaned',
            SHASUM,
            INTEGRITY,
            "fileCount",
            "3811617",
            "v23.11.1",
            "10.9.2",
            "ETHOS_PDFIUM_LIBRARY_PATH",
        ):
            self.assertIn(expected, record)

    def test_registry_reports_published_candidate(self) -> None:
        self.assertEqual(VERSION, npm_view(f"{PACKAGE}", "version"))
        versions = json.loads(npm_view(f"{PACKAGE}", "versions", "--json"))
        self.assertIn("0.0.0-reserved.0", versions)
        self.assertIn("0.1.0", versions)
        self.assertIn(VERSION, versions)
        dist = json.loads(npm_view(f"{PACKAGE}", "dist", "--json"))
        self.assertEqual(SHASUM, dist["shasum"])
        self.assertEqual(INTEGRITY, dist["integrity"])
        self.assertEqual(11, dist["fileCount"])
        self.assertEqual(3811617, dist["unpackedSize"])
        self.assertEqual(
            "https://registry.npmjs.org/@docushell/ethos-pdf/-/ethos-pdf-0.1.1.tgz",
            dist["tarball"],
        )

    def test_retained_blockers_and_public_path_hygiene(self) -> None:
        raw = read(RECORD)
        lower = normalized(RECORD).lower()

        for blocker in (
            "Hosted surfaces remain blocked.",
            "Production positioning remains blocked.",
            "Public benchmark reports remain blocked.",
            "Public benchmark claims remain blocked.",
            "Windows packaged artifacts remain blocked.",
            "Bundled project-maintained PDFium builds remain blocked.",
            "`ethos-doc` remains blocked.",
            "`ethos-rag` remains blocked.",
        ):
            self.assertIn(blocker, raw)
        for forbidden in (
            "production-ready",
            "hosted surfaces approved",
            "public benchmark claims approved",
            "windows packaged artifacts approved",
            "bundled pdfium approved",
        ):
            self.assertNotIn(forbidden, lower)
        self.assertNotIn("/Users/", raw)
        self.assertNotIn("/private/tmp", raw)
        self.assertNotIn("saumildiwaker", raw)


if __name__ == "__main__":
    unittest.main()
