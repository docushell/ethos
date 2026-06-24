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
RECORD = ROOT / "docs/validation/patch-0-1-1-crates-publication-approval-request-validation-2026-06-24.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
MAKEFILE = ROOT / "Makefile"

SOURCE_SHORT = "a085103"
SOURCE_COMMIT = "a0851030e28c155c12f5f966af8fa0739a536ea9"
SOURCE_TREE = "0238c3f6bfd264f8803708e4a828d8352320f08f"
VERSION = "0.1.1"
CRATES = ("ethos-doc-core", "ethos-verify", "ethos-pdf")
TAGS = (
    "ethos-package-ethos-doc-core-0.1.1",
    "ethos-package-ethos-verify-0.1.1",
    "ethos-package-ethos-pdf-0.1.1",
)
CRATE_HASHES = (
    "d845042c391d584a26dc3aa7ff367f118cfd94e8290a3caec81642186ed0de51",
    "27313b8decab66a3ea1b9e4c3e82dc47088e5c2f9d289a1450203cff1b9a7070",
    "a07e6436cceb64dddce1d5468fb25c44b745a26e4d044858b72bd570dcb84529",
)
FORBIDDEN = (
    "cargo publish approved",
    "crates are published",
    "published crates",
    "production-ready",
    "hosted surfaces approved",
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


class Patch011CratesPublicationApprovalRequestTests(unittest.TestCase):
    def test_request_record_is_source_bound_and_indexed(self) -> None:
        record = normalized(RECORD)
        readme = normalized(VALIDATION_README)

        self.assertIn(RECORD.name, readme)
        self.assertIn("patch 0.1.1 crates.io publication approval request", readme.lower())
        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Patch 0.1.1 crates publication approval request source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Patch 0.1.1 crates publication approval request source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_request_names_exact_crates_versions_tags_and_artifacts(self) -> None:
        record = normalized(RECORD)

        self.assertIn(
            "Status: **patch 0.1.1 crates.io publication approval request recorded; cargo publish remains blocked**",
            record,
        )
        for crate in CRATES:
            self.assertIn(crate, record)
            self.assertIn(f"{crate} = {VERSION}", record)
            self.assertIn(f"{crate}-0.1.1.crate", record)
        for tag in TAGS:
            self.assertIn(tag, record)
        for digest in CRATE_HASHES:
            self.assertIn(digest, record)
        self.assertIn("cargo publish --locked -p ethos-doc-core", record)
        self.assertIn("cargo publish --locked -p ethos-verify", record)
        self.assertIn("cargo publish --locked -p ethos-pdf", record)

    def test_request_retains_publication_and_surface_boundaries(self) -> None:
        raw = read(RECORD)
        lower = normalized(RECORD).lower()

        for expected in (
            "This request record does not approve `cargo publish`.",
            "Actual crates.io publication remains blocked pending explicit decider approval.",
            "Public installation wording remains blocked pending explicit decider approval.",
            "The `ethos-cli` package remains `publish = false`.",
            "`ethos-doc` remains blocked.",
            "`ethos-rag` remains blocked.",
            "PDFium remains caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`.",
        ):
            self.assertIn(expected, raw)
        for forbidden in FORBIDDEN:
            self.assertNotIn(forbidden, lower)
        self.assertNotIn("/Users/", raw)
        self.assertNotIn("/private/tmp", raw)
        self.assertNotIn("/private/var", raw)
        self.assertNotIn("/var/folders", raw)
        self.assertNotIn("saumildiwaker", raw)

    def test_source_manifests_keep_expected_publish_surface(self) -> None:
        for manifest in (
            ROOT / "crates/ethos-core/Cargo.toml",
            ROOT / "crates/ethos-verify/Cargo.toml",
            ROOT / "crates/ethos-pdf/Cargo.toml",
        ):
            text = read(manifest)
            self.assertNotIn("publish = false", text, str(manifest))
            self.assertIn('publication_status = "approved_for_crates_io_publication"', text, str(manifest))

        for manifest in (
            ROOT / "crates/ethos-cli/Cargo.toml",
            ROOT / "crates/ethos-layout/Cargo.toml",
            ROOT / "crates/ethos-tables/Cargo.toml",
        ):
            self.assertIn("publish = false", read(manifest), str(manifest))

    def test_release_candidate_prep_runs_request_guard(self) -> None:
        makefile = read(MAKEFILE)
        guard = "$(PYTHON) .github/scripts/test_patch_0_1_1_crates_publication_approval_request.py"

        self.assertIn(guard, makefile)
        self.assertEqual(1, makefile.count(guard))
        self.assertLess(
            makefile.index("$(PYTHON) .github/scripts/test_npm_publication_closeout.py"),
            makefile.index(guard),
        )
        self.assertLess(
            makefile.index(guard),
            makefile.index("$(PYTHON) .github/scripts/test_pdfium_manual_setup_contract.py"),
        )


if __name__ == "__main__":
    unittest.main()
