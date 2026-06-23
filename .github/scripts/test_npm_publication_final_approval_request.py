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
RECORD = ROOT / "docs/validation/patch-0-1-1-npm-publication-approval-request-validation-2026-06-23.md"
VALIDATION_README = ROOT / "docs/validation/README.md"

SOURCE_SHORT = "af1851c"
SOURCE_COMMIT = "af1851c88b2b7c17f706a902ca64987c2af082be"
SOURCE_TREE = "7d501ab7fa5a585352918f65fbd2de1756a184b9"
PACKAGE = "@docushell/ethos-pdf@0.1.1"
NPM_SHASUM = "a150d08395724aa186d077074782413249a48689"
TARBALL_SHA256 = "4b227d37bd125c6db1ffe40534f6cb5223a60073f26e3c4dbf60709561671d3d"
INTEGRITY = "sha512-wVF4Ew6836sRncPZkvVieyQuo8FFbbBsIQ/vdupleUQZVX4YHgXb+lFZzZNcVB54Hh7srbbY17El4Z5sV7odhA=="
NODE_VERSION = "v23.11.1"
NPM_VERSION = "10.9.2"
FORBIDDEN = (
    "npm publish is approved",
    "npm publication approved",
    "package is published",
    "production-ready",
    "hosted surfaces approved",
    "public benchmark claims approved",
    "windows packaged artifacts approved",
    "bundled pdfium approved",
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


class NpmPublicationFinalApprovalRequestTests(unittest.TestCase):
    def test_request_record_is_source_bound(self) -> None:
        record = normalized(RECORD)

        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"npm publication approval request source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"npm publication approval request source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_request_names_exact_candidate_and_evidence(self) -> None:
        record = normalized(RECORD)

        for expected in (
            PACKAGE,
            "docushell-ethos-pdf-0.1.1.tgz",
            NPM_SHASUM,
            TARBALL_SHA256,
            INTEGRITY,
            f"Node.js: `{NODE_VERSION}`",
            f"npm: `{NPM_VERSION}`",
            "per-file vendor SHA256 values are the durable cross-toolchain provenance binding",
            "vendor/ethos-darwin-arm64",
            "vendor/ethos-linux-x64",
            "vendor/manifest.json",
            "ethos 0.1.1",
            "exit code `12`",
            "ETHOS_PDFIUM_LIBRARY_PATH",
            "patch-0-1-1-npm-vendor-refresh-validation-2026-06-23.md",
            "npm-vendor-binary-payload-strategy-validation-2026-06-23.md",
        ):
            self.assertIn(expected, record)

    def test_request_requires_manual_decider_and_keeps_publish_blocked(self) -> None:
        record = normalized(RECORD)
        raw = read(RECORD)

        self.assertIn("Manual action is required before any publish operation", record)
        self.assertIn("A decider must accept or reject this exact request packet.", record)
        self.assertIn("Publication must use Node.js `v23.11.1` and npm `10.9.2`", record)
        self.assertIn("Only after that decision record passes may an operator run `npm publish`", record)
        self.assertIn("No `npm publish` command is approved by this request record.", record)
        self.assertIn("npm publication remains blocked pending explicit decider approval.", raw)
        self.assertIn("Actual npm publish remains blocked pending explicit operator action", raw)

    def test_request_retains_blockers_and_avoids_scope_expansion(self) -> None:
        lower = normalized(RECORD).lower()
        raw = read(RECORD)

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
        for phrase in FORBIDDEN:
            self.assertNotIn(phrase, lower)
        self.assertNotIn("/Users/", raw)
        self.assertNotIn("/private/tmp", raw)
        self.assertNotIn("/private/var", raw)
        self.assertNotIn("/var/folders", raw)
        self.assertNotIn("saumildiwaker", raw)
        self.assertNotIn("Desktop/Stuff", raw)
        self.assertNotIn("project/repo/ethos", raw)

    def test_record_is_indexed(self) -> None:
        readme = normalized(VALIDATION_README)

        self.assertIn(RECORD.name, readme)
        self.assertIn("patch 0.1.1 npm publication approval request", readme.lower())
        self.assertIn("npm publish remains blocked", readme)


if __name__ == "__main__":
    unittest.main()
