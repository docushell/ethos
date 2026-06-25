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

import ast
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PYPROJECT = ROOT / "pyproject.toml"
INIT = ROOT / "python/ethos_pdf/__init__.py"
README = ROOT / "python/README.md"

PUBLIC_API = (
    "EthosCli",
    "EthosCommandError",
    "CorruptPdfError",
    "EthosNotFoundError",
    "EthosOutputError",
    "EthosPythonSurfaceError",
    "EthosTimeoutError",
    "InvalidPdfError",
    "ParseTimeoutError",
    "PdfiumNotFoundError",
    "anchor",
    "crop_element",
    "parse_pdf_json",
    "parse_pdf_markdown",
    "parse_pdf_text",
    "verify",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def pyproject_text() -> str:
    return read(PYPROJECT)


def parse_init_assignments() -> dict[str, object]:
    module = ast.parse(read(INIT))
    values: dict[str, object] = {}
    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    values[target.id] = ast.literal_eval(node.value)
    return values


class PythonPublicApiPolicyTests(unittest.TestCase):
    def test_package_metadata_declares_public_release_policy(self) -> None:
        text = pyproject_text()

        self.assertIn('name = "ethos-pdf"', text)
        self.assertIn('version = "0.1.2"', text)
        self.assertIn('requires-python = ">=3.8"', text)
        self.assertIn('license = "Apache-2.0"', text)
        self.assertNotIn('license = { text = "Apache-2.0" }', text)
        self.assertNotIn("License :: OSI Approved :: Apache Software License", text)
        self.assertIn('readme = "python/README.md"', text)
        self.assertIn('package-dir = { "" = "python" }', text)

    def test_public_module_version_and_all_match_metadata(self) -> None:
        assignments = parse_init_assignments()

        self.assertEqual("0.1.2", assignments["__version__"])
        self.assertEqual(list(PUBLIC_API), assignments["__all__"])

    def test_readme_documents_semver_and_exact_public_api_boundary(self) -> None:
        text = read(README)
        normalized = re.sub(r"\s+", " ", text)

        self.assertIn("public semver API beginning at `0.1.0`", normalized)
        self.assertIn("Python `>=3.8`", normalized)
        self.assertIn("Patch releases must not break", normalized)
        for name in PUBLIC_API:
            self.assertIn(f"`{name}`", text)
        self.assertIn("caller-provided local `ethos` CLI binary", normalized)
        self.assertIn("does not bundle PDFium", normalized)
        self.assertIn("does not publish hosted surfaces", normalized)

    def test_no_runtime_dependencies_are_declared_yet(self) -> None:
        self.assertNotIn("dependencies", pyproject_text())
        self.assertNotIn("[project.optional-dependencies]", pyproject_text())


if __name__ == "__main__":
    unittest.main()
