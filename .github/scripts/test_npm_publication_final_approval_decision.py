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
RECORD = ROOT / "docs/validation/npm-publication-final-approval-decision-validation-2026-06-23.md"
VALIDATION_README = ROOT / "docs/validation/README.md"

SOURCE_SHORT = "aab7a97"
SOURCE_COMMIT = "aab7a97dabc17fa1f90e085e8934e1582827dcda"
SOURCE_TREE = "b842f2aaedf51275cebf25c9ecadc37f56120106"
PACKAGE = "@docushell/ethos-pdf@0.1.0"
NPM_SHASUM = "17a053c5ccb802bca2a295e1b1d0e6106c6a3ca6"
TARBALL_SHA256 = "8d0483d69a6de471dee52c8ef06d46712c06861682a0d7319ca573fdb1fe6376"
INTEGRITY = "sha512-uWTHYd9Hfkm3nkahK2UchCMOVvYWe82z03jffZnX6aYPqYGd6LkuiEoTH5DjrXl+oA817EjlE88fIKBxZbhjMw=="
NODE_VERSION = "v23.11.1"
NPM_VERSION = "10.9.2"
FORBIDDEN = (
    "production-ready",
    "hosted surfaces approved",
    "public benchmark claims approved",
    "windows packaged artifacts approved",
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


class NpmPublicationFinalApprovalDecisionTests(unittest.TestCase):
    def test_decision_record_is_source_bound(self) -> None:
        record = normalized(RECORD)

        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"npm publication final approval decision source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"npm publication final approval decision source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_decision_accepts_exact_bounded_npm_candidate(self) -> None:
        record = normalized(RECORD)

        for expected in (
            PACKAGE,
            "docushell-ethos-pdf-0.1.0.tgz",
            NPM_SHASUM,
            TARBALL_SHA256,
            INTEGRITY,
            f"Node.js: `{NODE_VERSION}`",
            f"npm: `{NPM_VERSION}`",
            "per-file SHA256 values are the durable cross-toolchain provenance binding",
            "vendor/ethos-darwin-arm64",
            "vendor/ethos-linux-x64",
            "vendor/manifest.json",
            "ethos 0.1.0",
            "exit code `12`",
            "ETHOS_PDFIUM_LIBRARY_PATH",
            "Approved Operator Action",
        ):
            self.assertIn(expected, record)

    def test_decision_permits_only_later_operator_publish_with_boundaries(self) -> None:
        record = normalized(RECORD)

        self.assertIn("This decision does not itself execute `npm publish`", record)
        self.assertIn("publication remains an explicit later operator action", record)
        self.assertIn("the operator uses Node.js `v23.11.1` and npm `10.9.2`", record)
        self.assertIn("npm credentials authorized for the `@docushell` scope", record)
        self.assertIn("targets only `@docushell/ethos-pdf@0.1.0`", record)

    def test_decision_retains_unrelated_blockers_and_avoids_scope_expansion(self) -> None:
        raw = read(RECORD)
        lower = normalized(RECORD).lower()

        for blocker in (
            "hosted surfaces remain blocked",
            "production positioning remains blocked",
            "public benchmark reports remain blocked",
            "public benchmark claims remain blocked",
            "Windows packaged artifacts remain blocked",
            "bundled project-maintained PDFium builds remain blocked",
            "`ethos-doc` remains blocked",
            "`ethos-rag` remains blocked",
        ):
            self.assertIn(blocker, raw)
        for phrase in FORBIDDEN:
            self.assertNotIn(phrase, lower)
        self.assertNotIn("/Users/", raw)
        self.assertNotIn("/private/tmp", raw)
        self.assertNotIn("/private/var", raw)
        self.assertNotIn("/var/folders", raw)
        self.assertNotIn("saumildiwaker", raw)
        self.assertNotIn("Desktop/Stuff", raw)
        self.assertNotIn("project/repo/ethos", raw)

    def test_decision_is_indexed(self) -> None:
        readme = normalized(VALIDATION_README)

        self.assertIn(RECORD.name, readme)
        self.assertIn("npm publication final approval decision validation", readme)
        self.assertIn("leaves operator publish pending", readme)


if __name__ == "__main__":
    unittest.main()
