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
RECORD = ROOT / "docs/validation/patch-0-1-2-readiness-prep-validation-2026-06-24.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"
README = ROOT / "README.md"
WORKSPACE_CARGO = ROOT / "Cargo.toml"
PYPROJECT = ROOT / "pyproject.toml"
NPM_PACKAGE = ROOT / "packages/npm/ethos-pdf/package.json"
PYTHON_INIT = ROOT / "python/ethos_pdf/__init__.py"

SOURCE_SHORT = "8926217"
SOURCE_COMMIT = "89262171ee9fdd342c5bcc808d8c12d40a126337"
SOURCE_TREE = "3e41ef063d7746de2a59486a2bacc2fdecb187f2"

PREP_CONTENTS = (
    "0.1.2",
    "narrow beta patch",
    "ethos evidence anchor",
    "`evidence_anchor` v1 guard",
    "Professional public README status wording",
    "caller-provided PDFium",
)

FORBIDDEN_RELEASE_CLAIMS = (
    "0.1.2 is approved",
    "v0.1.2 is approved",
    "0.1.2 is released",
    "v0.1.2 is released",
    "publish 0.1.2",
    "tag v0.1.2",
    "npm install -g @docushell/ethos-pdf@0.1.2",
    "python3 -m pip install ethos-pdf==0.1.2",
    "cargo add ethos-doc-core@0.1.2",
    "cargo add ethos-verify@0.1.2",
    "cargo add ethos-pdf@0.1.2",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalized(path: Path) -> str:
    return re.sub(r"\s+", " ", read(path))


class Patch012ReadinessPrepTests(unittest.TestCase):
    def test_record_binds_source_and_prep_contents(self) -> None:
        text = normalized(RECORD)
        raw = read(RECORD)

        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", raw)
        self.assertIn(f"Patch-prep source commit: `{SOURCE_COMMIT}`", text)
        self.assertIn(f"Patch-prep source tree: `{SOURCE_TREE}`", text)
        for item in PREP_CONTENTS:
            self.assertIn(item, text)

    def test_record_keeps_publication_and_support_boundaries_closed(self) -> None:
        text = normalized(RECORD)
        lower = text.lower()

        for phrase in (
            "does not approve a release",
            "does not approve a tag",
            "does not approve package publish",
            "does not approve a GitHub Release artifact",
            "does not approve hosted surfaces",
            "does not approve production positioning",
            "does not approve Windows packaged artifacts",
            "does not approve bundled project-maintained PDFium builds",
            "does not approve public benchmark reports",
            "does not approve public benchmark claims",
            "does not approve `ethos-doc`",
            "does not approve `ethos-rag`",
        ):
            self.assertIn(phrase, text)
        for phrase in FORBIDDEN_RELEASE_CLAIMS:
            self.assertNotIn(phrase, lower)
        self.assertIn("current public install baseline remains `0.1.1`", text)

    def test_public_readme_uses_professional_beta_wording_without_version_drift(self) -> None:
        text = read(README)
        lower = text.lower()

        self.assertIn("Status: public beta evaluation.", text)
        self.assertIn("deterministic document evidence layer", text)
        self.assertIn("source-grounded verification", text)
        self.assertIn("ETHOS_PDFIUM_LIBRARY_PATH", text)
        self.assertIn("cargo add ethos-doc-core@0.1.1", text)
        self.assertIn("python3 -m pip install ethos-pdf==0.1.1", text)
        self.assertIn("npm install -g @docushell/ethos-pdf@0.1.1", text)
        self.assertNotIn("not production-ready", lower)
        self.assertNotIn("not stable production surfaces", lower)
        for phrase in FORBIDDEN_RELEASE_CLAIMS:
            self.assertNotIn(phrase, lower)

    def test_package_manifests_remain_on_published_baseline(self) -> None:
        self.assertIn('version = "0.1.1"', read(WORKSPACE_CARGO))
        self.assertIn('version = "0.1.1"', read(PYPROJECT))
        self.assertIn('__version__ = "0.1.1"', read(PYTHON_INIT))
        self.assertIn('"version": "0.1.1"', read(NPM_PACKAGE))

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
