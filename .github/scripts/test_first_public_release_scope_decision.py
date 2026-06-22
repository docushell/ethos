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
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "docs/validation/first-public-release-scope-decision-validation-2026-06-22.md"
VALIDATION_README = ROOT / "docs/validation/README.md"

SOURCE_SHORT = "d3bba4c"
SOURCE_COMMIT = "d3bba4c521ed1837977049bc6f687e795f40cca0"
SOURCE_TREE = "f62c1407658a3f7e67b217eeaebf4b5031c80d84"

IN_SCOPE = (
    "GitHub Release draft CLI artifacts for macOS arm64 and Linux x64",
    "Python package preparation for `ethos-pdf` / `ethos_pdf`",
    "npm package preparation for `@docushell/ethos-pdf`",
    "Caller-provided PDFium through `ETHOS_PDFIUM_LIBRARY_PATH`",
)
OUT_OF_SCOPE = (
    "Public artifact publication",
    "Hosted surfaces",
    "Production positioning",
    "Public benchmark reports",
    "Public benchmark claims",
    "Windows x64 packaged artifacts",
    "Bundled project-maintained PDFium builds",
    "`ethos-doc`",
    "`ethos-rag`",
)
REQUIRED_FOLLOW_UPS = (
    "Python public API policy",
    "npm binary package policy",
    "PDFium manual setup contract",
    "Release artifact workflow and inventory validation",
    "Release-candidate validation target",
    "Launch-copy claim audit",
    "Final release approval",
)
FORBIDDEN = (
    "public artifact publication approved",
    "hosted surfaces approved",
    "production positioning approved",
    "public benchmark claims approved",
    "public benchmark reports approved",
    "windows x64 approved",
    "bundled pdfium approved",
    "ethos-doc approved",
    "ethos-rag approved",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalized(path: Path) -> str:
    return re.sub(r"\s+", " ", read(path))


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args],
        cwd=ROOT,
        encoding="utf-8",
        stderr=subprocess.DEVNULL,
    ).strip()


class FirstPublicReleaseScopeDecisionTests(unittest.TestCase):
    def test_record_is_source_bound(self) -> None:
        record = normalized(RECORD)

        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Release-prep source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Release-prep source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_record_captures_scope_and_blockers(self) -> None:
        record = normalized(RECORD)

        self.assertIn("release preparation approved; public artifact publication remains blocked", record)
        for line in IN_SCOPE:
            self.assertIn(line, record)
        for line in OUT_OF_SCOPE:
            self.assertIn(line, record)
        for line in REQUIRED_FOLLOW_UPS:
            self.assertIn(line, record)

    def test_record_avoids_scope_expansion_language(self) -> None:
        lower = normalized(RECORD).lower()
        raw = read(RECORD)

        for phrase in FORBIDDEN:
            self.assertNotIn(phrase, lower)
        self.assertNotIn("/Users/", raw)
        self.assertNotIn("/private/tmp", raw)
        self.assertNotIn("/private/var", raw)
        self.assertNotIn("saumildiwaker", raw)

    def test_validation_readme_indexes_record(self) -> None:
        text = normalized(VALIDATION_README)

        self.assertIn(RECORD.name, text)
        self.assertIn("first public release scope decision validation", text)
        self.assertIn("public artifact publication remains blocked", text)


if __name__ == "__main__":
    unittest.main()
