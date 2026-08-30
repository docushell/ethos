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

import json
import os
import platform
import re
import subprocess
import tempfile
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
FETCH_SCRIPT = ROOT / "scripts/fetch-pdfium.sh"
PROFILE = ROOT / "profiles/ethos-deterministic-v1.json"


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
        self.assertIn("scripts/fetch-pdfium.sh", text)
        self.assertIn("archive sha256", text)
        self.assertIn("runtime-library sha256", text)
        self.assertIn("before extraction", text)
        self.assertIn("after extraction", text)
        self.assertIn("python -m ethos_pdf", text)
        self.assertIn("FROM --platform=linux/amd64", read(DOC))
        self.assertIn("RUN ethos doctor --require-pdfium", read(DOC))

    def test_fetch_script_mirrors_deterministic_profile_pins(self) -> None:
        profile = json.loads(read(PROFILE))["backend"]
        script = read(FETCH_SCRIPT)
        expected = {
            "RELEASE_TAG": profile["version"],
            "RELEASE_NAME": profile["upstream_version"],
            "MAC_ARM64_ARCHIVE": profile["platform_artifacts"]["macos-arm64"]["name"],
            "MAC_ARM64_ARCHIVE_SHA256": profile["platform_hashes"]["macos-arm64"],
            "MAC_ARM64_LIB_RELPATH": profile["platform_artifacts"]["macos-arm64"][
                "runtime_library_path"
            ],
            "MAC_ARM64_LIB_SHA256": profile["platform_artifacts"]["macos-arm64"][
                "runtime_library_sha256"
            ],
            "LINUX_X64_ARCHIVE": profile["platform_artifacts"]["linux-x64"]["name"],
            "LINUX_X64_ARCHIVE_SHA256": profile["platform_hashes"]["linux-x64"],
            "LINUX_X64_LIB_RELPATH": profile["platform_artifacts"]["linux-x64"][
                "runtime_library_path"
            ],
            "LINUX_X64_LIB_SHA256": profile["platform_artifacts"]["linux-x64"][
                "runtime_library_sha256"
            ],
        }
        for name, value in expected.items():
            self.assertIn(f'{name}="{value}"', script, name)

    def test_fetch_script_fails_closed_on_existing_runtime_hash_mismatch(self) -> None:
        runtime_by_platform = {
            ("Darwin", "arm64"): "lib/libpdfium.dylib",
            ("Linux", "x86_64"): "lib/libpdfium.so",
        }
        runtime = runtime_by_platform.get((platform.system(), platform.machine()))
        if runtime is None:
            self.skipTest("fetch script supports macOS arm64 and Linux x64")

        self.assertTrue(os.access(FETCH_SCRIPT, os.X_OK), "fetch script must be executable")
        with tempfile.TemporaryDirectory(prefix="ethos-pdfium-hash-mismatch-") as temp:
            library = Path(temp) / runtime
            library.parent.mkdir(parents=True)
            library.write_bytes(b"not the pinned runtime")
            result = subprocess.run(
                [str(FETCH_SCRIPT), temp],
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 1)
        self.assertIn("has sha256", result.stderr)
        self.assertIn("expected", result.stderr)

    def test_readme_has_bounded_two_minute_pdf_parse_quickstart(self) -> None:
        text = normalized(README)

        self.assertIn("2-minute PDF parse quickstart", text)
        self.assertIn("fixtures/synthetic/simple-text/document.pdf", text)
        self.assertIn("ethos doctor --require-pdfium", text)
        self.assertIn("ethos doc parse fixtures/synthetic/simple-text/document.pdf --format json", text)
        self.assertIn("ethos doc parse fixtures/synthetic/simple-text/document.pdf --format text", text)
        self.assertIn("caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`", text)
        self.assertIn("does not download, install, repair, or vet untrusted dynamic libraries", text)
        self.assertIn("smoke path, not a benchmark", text)
        self.assertIn("born-digital", text)

    def test_rust_backend_missing_pdfium_error_names_env_var(self) -> None:
        text = read(PDF_CRATE)

        self.assertIn("PDFium not found: set {PDFIUM_LIBRARY_PATH_ENV}", text)
        self.assertIn("caller-provided PDFium dynamic library path", text)
        self.assertIn("ethos doctor", text)
        self.assertIn("ethos doctor --require-pdfium", text)
        self.assertIn("docs/pdfium-manual-setup.md", text)

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
        self.assertIn("ethos doctor", text)
        self.assertIn("ethos doctor --require-pdfium", text)
        self.assertIn("docs/pdfium-manual-setup.md", text)
        self.assertIn("EthosCommandError", text)


if __name__ == "__main__":
    unittest.main()
