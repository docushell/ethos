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
RECORD = ROOT / "docs/validation/patch-0-1-1-readiness-prep-validation-2026-06-23.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"

SOURCE_SHORT = "dd155e4"
SOURCE_COMMIT = "dd155e4f5e999da82043e2f53fa1ac8e84929118"
SOURCE_TREE = "ba0291a1c084f19d04935dc4af16fb7603388a19"

CANDIDATE_CONTENTS = (
    "ethos doctor",
    "Synthetic fixture golden-change rationale guard",
    "2-minute PDF parse quickstart",
    "fixtures/synthetic/simple-text/document.pdf",
    "ethos doctor --require-pdfium",
    "docs/pdfium-manual-setup.md",
)

RETAINED_BLOCKERS = (
    "does not approve a release",
    "version bump",
    "npm publish",
    "PyPI publish",
    "crates.io publish",
    "hosted surface",
    "production positioning",
    "Windows packaged artifact",
    "bundled project-maintained PDFium build",
    "public benchmark report",
    "public benchmark claim",
    "`ethos-doc`",
    "`ethos-rag`",
)

FORBIDDEN_APPROVALS = (
    "0.1.1 is approved",
    "v0.1.1 is approved",
    "publish 0.1.1",
    "tag v0.1.1",
    "production positioning approved",
    "hosted surface approved",
    "public benchmark claim approved",
    "bundled pdfium approved",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalized(path: Path) -> str:
    return re.sub(r"\s+", " ", read(path))


class Patch011ReadinessPrepTests(unittest.TestCase):
    def test_record_binds_source_and_candidate_contents(self) -> None:
        text = normalized(RECORD)
        raw = read(RECORD)

        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", raw)
        self.assertIn(f"Patch-prep source commit: `{SOURCE_COMMIT}`", text)
        self.assertIn(f"Patch-prep source tree: `{SOURCE_TREE}`", text)
        for item in CANDIDATE_CONTENTS:
            self.assertIn(item, text)

    def test_record_keeps_release_and_surface_boundaries_closed(self) -> None:
        text = normalized(RECORD)
        lower = text.lower()

        for blocker in RETAINED_BLOCKERS:
            self.assertIn(blocker, text)
        for phrase in FORBIDDEN_APPROVALS:
            self.assertNotIn(phrase, lower)
        self.assertIn("current public baseline remains `v0.1.0`", text)
        self.assertIn("PDFium remains caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`", text)
        self.assertIn("do not vet untrusted dynamic libraries", text)

    def test_record_lists_required_gates_before_patch_action(self) -> None:
        text = normalized(RECORD)

        for phrase in (
            "Decide the exact patch version and surfaces",
            "Update package and CLI versions only after that decision",
            "Build and smoke any proposed artifacts from the exact candidate commit",
            "public posture, claims, source snapshot, license/NOTICE, and private-path checks",
            "manual operator evidence",
        ):
            self.assertIn(phrase, text)

    def test_record_is_indexed_and_status_docs_reference_it(self) -> None:
        record_name = RECORD.name

        self.assertIn(record_name, read(VALIDATION_README))
        self.assertIn(record_name, read(EXECUTION_STATUS))
        self.assertIn(record_name, read(PUBLIC_RELEASE_CHECKLIST))

    def test_record_avoids_local_private_paths(self) -> None:
        text = read(RECORD)

        for private in (
            "/" + "Users/",
            "/" + "private/tmp",
            "/" + "private/var",
            "/" + "var/folders",
            "saumil" + "diwaker",
            "Desktop/" + "Stuff",
            "project/repo/" + "ethos",
        ):
            self.assertNotIn(private, text)


if __name__ == "__main__":
    unittest.main()
