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
DOC = ROOT / "docs/pdfium-manual-setup.md"
README = ROOT / "README.md"
PDF_CRATE_README = ROOT / "crates/ethos-pdf/README.md"
PDF_CRATE = ROOT / "crates/ethos-pdf/src/lib.rs"
PYTHON_README = ROOT / "python/README.md"
NPM_README = ROOT / "packages/npm/ethos-pdf/README.md"
PYTHON_TESTS = ROOT / "python/tests/test_cli_surface.py"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalized(path: Path) -> str:
    return re.sub(r"\s+", " ", read(path))


class PdfiumManualSetupContractTests(unittest.TestCase):
    def test_manual_setup_doc_defines_caller_provided_boundary(self) -> None:
        text = normalized(DOC)

        self.assertIn("keeps PDFium caller-provided", text)
        self.assertIn("do not bundle PDFium and do not download PDFium", text)
        self.assertIn("ETHOS_PDFIUM_LIBRARY_PATH", text)
        self.assertIn("Python import and npm package installation must not require PDFium", text)
        self.assertIn("does not approve bundled project-maintained PDFium builds", text)

    def test_readme_has_bounded_two_minute_pdf_parse_quickstart(self) -> None:
        text = normalized(README)

        self.assertIn("2-minute PDF parse quickstart", text)
        self.assertIn("fixtures/synthetic/simple-text/document.pdf", text)
        self.assertIn("ethos doctor --require-pdfium", text)
        self.assertIn("ethos doc parse fixtures/synthetic/simple-text/document.pdf --format json", text)
        self.assertIn("ethos doc parse fixtures/synthetic/simple-text/document.pdf --format text", text)
        self.assertIn("caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`", text)
        self.assertIn("does not download, install, repair, or vet untrusted dynamic libraries", text)
        self.assertIn("evaluation smoke path, not a benchmark", text)
        self.assertIn("born-digital", text)

    def test_rust_backend_missing_pdfium_error_names_env_var(self) -> None:
        text = read(PDF_CRATE)

        self.assertIn("PDFium not found: set {PDFIUM_LIBRARY_PATH_ENV}", text)
        self.assertIn("caller-provided PDFium dynamic library path", text)

    def test_surface_docs_reference_same_setup_contract(self) -> None:
        for path in (PDF_CRATE_README, PYTHON_README, NPM_README):
            text = normalized(path)
            self.assertIn("ETHOS_PDFIUM_LIBRARY_PATH", text, str(path))
            self.assertRegex(text, r"(does not bundle PDFium|No PDFium binary is bundled)", str(path))

    def test_python_surface_preserves_missing_pdfium_cli_stderr(self) -> None:
        text = read(PYTHON_TESTS)

        self.assertIn('"ETHOS_FAKE_MODE": "missing-pdfium"', text)
        self.assertIn("PDFium not found", text)
        self.assertIn("ETHOS_PDFIUM_LIBRARY_PATH", text)
        self.assertIn("EthosCommandError", text)


if __name__ == "__main__":
    unittest.main()
