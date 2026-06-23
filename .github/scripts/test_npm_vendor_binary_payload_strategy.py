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


ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "docs/validation/npm-vendor-binary-payload-strategy-validation-2026-06-23.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
PACKAGE_README = ROOT / "packages/npm/ethos-pdf/README.md"
QUICKSTART = ROOT / "packages/npm/ethos-pdf/QUICKSTART.md"

SOURCE_SHORT = "e705962"
SOURCE_COMMIT = "e705962eb08224c2c397126adb40ec2110020f95"
SOURCE_TREE = "3741717e6b5d9bbb7c8f46e5aa4a81c05147fd0c"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalized(path: Path) -> str:
    return re.sub(r"\s+", " ", read(path))


class NpmVendorBinaryPayloadStrategyTests(unittest.TestCase):
    def test_record_is_source_bound_and_scoped(self) -> None:
        record = normalized(RECORD)

        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"npm vendor payload strategy source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"npm vendor payload strategy source tree: `{SOURCE_TREE}`", record)
        self.assertIn("npm publication remains blocked", record)
        self.assertNotIn("npm publication approved", record.lower())

    def test_record_captures_vendor_payload_contract(self) -> None:
        record = normalized(RECORD)

        for expected in (
            "vendor/manifest.json",
            "ethos-darwin-arm64",
            "ethos-linux-x64",
            "ethos-macos-arm64.tar.gz",
            "ethos-linux-x64.tar.gz",
            "prepare-vendor.js",
            "npm pack --json --dry-run",
            "Checksum mismatch",
            "Missing release asset",
        ):
            self.assertIn(expected, record)

    def test_package_docs_explain_local_vendor_assembly(self) -> None:
        docs = normalized(PACKAGE_README) + " " + normalized(QUICKSTART)

        self.assertIn("npm run prepare:vendor -- <release-artifact-dir>", docs)
        self.assertIn("vendor/manifest.json", docs)
        self.assertIn("ethos-macos-arm64.tar.gz", docs)
        self.assertIn("ethos-linux-x64.tar.gz", docs)
        self.assertIn("does not bundle PDFium", docs)

    def test_record_is_indexed(self) -> None:
        readme = normalized(VALIDATION_README)

        self.assertIn(RECORD.name, readme)
        self.assertIn("npm vendor binary payload strategy validation", readme)
        self.assertIn("npm publication remains blocked", readme)


if __name__ == "__main__":
    unittest.main()
