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
RECORD = ROOT / "docs/validation/patch-0-1-2-npm-publication-approval-decision-validation-2026-06-24.md"
VALIDATION_README = ROOT / "docs/validation/README.md"

SOURCE_SHORT = "ef63161"
SOURCE_COMMIT = "ef631614f8c36b6ef080e968d8daac937a63a533"
SOURCE_TREE = "fc514355314347619e07122700b7d1b035302653"
PACKAGE = "@docushell/ethos-pdf@0.1.2"
NPM_SHASUM = "39b85d74f588666bfbf69e423a189c2039743de4"
TARBALL_SHA256 = "77cbc9c79dd60cc16073690a186e149ecbaabacce035fb0bd3603b267ce64112"
INTEGRITY = "sha512-3loga13tnAkUkjuOrjKjpA0D3Cm5lW6Al8OwTyRx7NGMt6EB4gMpZOoaSCPjZWchYv7as1uPaEnZyOqrmFOPxg=="
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


class Patch012NpmPublicationApprovalDecisionTests(unittest.TestCase):
    def test_decision_record_is_source_bound(self) -> None:
        record = normalized(RECORD)

        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"npm publication approval decision source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"npm publication approval decision source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_decision_accepts_exact_bounded_npm_candidate(self) -> None:
        record = normalized(RECORD)

        for expected in (
            PACKAGE,
            "docushell-ethos-pdf-0.1.2.tgz",
            NPM_SHASUM,
            TARBALL_SHA256,
            INTEGRITY,
            f"Node.js: `{NODE_VERSION}`",
            f"npm: `{NPM_VERSION}`",
            "per-file vendor SHA256 values are the durable cross-toolchain provenance binding",
            "vendor/ethos-darwin-arm64",
            "47c2f4aaac6cb6a1ca5cf1d9a0cc1f897ef00c48cdd8549455de70f0fbc6bcc1",
            "vendor/ethos-linux-x64",
            "e75122f2954efbde6b8c07a98601b8d4a3b7a06647891a9e60d6aef4046649c3",
            "vendor/manifest.json",
            "d557e081b946be0f839b17b8593027e31267b668498e202372026020f68a97a1",
            "ethos 0.1.2",
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
        self.assertIn("targets only `@docushell/ethos-pdf@0.1.2`", record)
        self.assertIn("Public installation wording remains blocked", read(RECORD))

    def test_decision_retains_unrelated_blockers_and_avoids_scope_expansion(self) -> None:
        raw = read(RECORD)
        lower = normalized(RECORD).lower()

        for blocker in (
            "Public installation wording remains blocked",
            "registry closeout remains blocked",
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
        self.assertIn("patch 0.1.2 npm publication approval decision", readme.lower())
        self.assertIn("leaves operator publish pending", readme)


if __name__ == "__main__":
    unittest.main()
