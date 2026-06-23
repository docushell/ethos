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
import re
import subprocess
import tempfile
import unittest
from pathlib import Path
from shutil import copytree


ROOT = Path(__file__).resolve().parents[2]
PACKAGE_DIR = ROOT / "packages/npm/ethos-pdf"
PACKAGE_JSON = PACKAGE_DIR / "package.json"
BIN = PACKAGE_DIR / "bin/ethos-pdf.js"
VENDOR_ASSEMBLY = PACKAGE_DIR / "scripts" / "prepare-vendor.js"
README = PACKAGE_DIR / "README.md"
QUICKSTART = PACKAGE_DIR / "QUICKSTART.md"
NOTICE = PACKAGE_DIR / "NOTICE"
LICENSE = PACKAGE_DIR / "LICENSE"
VENDOR_MANIFEST = PACKAGE_DIR / "vendor" / "manifest.json"
SUPPORTED_TARGETS = {
    "darwin:arm64": {
        "binary": "ethos-darwin-arm64",
        "release_asset": "ethos-macos-arm64.tar.gz",
        "release_asset_sha256": "eac79cddc6f5fc834ecc279401905729978d73e99ae11a2bea82d7356a4bcd88",
    },
    "linux:x64": {
        "binary": "ethos-linux-x64",
        "release_asset": "ethos-linux-x64.tar.gz",
        "release_asset_sha256": "842aa4b71333aecc54f344d9f5362160d0943d8efd32dffabe99dc19553916a0",
    },
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class NpmBinaryPackageScaffoldTests(unittest.TestCase):
    def test_package_metadata_is_bounded_to_supported_release_targets(self) -> None:
        package = json.loads(read(PACKAGE_JSON))

        self.assertEqual("@docushell/ethos-pdf", package["name"])
        self.assertEqual("0.1.1", package["version"])
        self.assertEqual("Apache-2.0", package["license"])
        self.assertEqual({"ethos": "./bin/ethos-pdf.js"}, package["bin"])
        self.assertIn("vendor/", package["files"])
        self.assertEqual(["darwin", "linux"], package["os"])
        self.assertEqual(["arm64", "x64"], package["cpu"])
        self.assertEqual(">=18", package["engines"]["node"])
        self.assertEqual("node scripts/prepare-vendor.js", package["scripts"]["prepare:vendor"])
        self.assertNotIn("dependencies", package)

    def test_vendor_manifest_binds_supported_targets_to_release_assets(self) -> None:
        manifest = json.loads(read(VENDOR_MANIFEST))

        self.assertEqual(1, manifest["version"])
        self.assertEqual("@docushell/ethos-pdf", manifest["package"])
        self.assertEqual(SUPPORTED_TARGETS, manifest["targets"])
        for target in manifest["targets"].values():
            self.assertRegex(target["release_asset_sha256"], r"^[a-f0-9]{64}$")

    def test_platform_selection_is_exact_and_rejects_windows(self) -> None:
        result = subprocess.run(
            ["node", "test/platform-selection.test.js"],
            cwd=PACKAGE_DIR,
            check=False,
            encoding="utf-8",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("platform selection ok", result.stdout)

    def test_package_docs_keep_pdfium_and_publication_boundaries(self) -> None:
        text = read(README)
        normalized = re.sub(r"\s+", " ", text)

        self.assertIn("macOS arm64", text)
        self.assertIn("Linux x64", text)
        self.assertIn("does not bundle PDFium", text)
        self.assertIn("ETHOS_PDFIUM_LIBRARY_PATH", text)
        self.assertIn("QUICKSTART.md", text)
        self.assertIn("not approved for public publication", text)
        self.assertIn("does not include public benchmark reports or claims", normalized)

        quickstart = read(QUICKSTART)
        self.assertIn("ETHOS_PDFIUM_LIBRARY_PATH", quickstart)
        self.assertIn("libpdfium", quickstart)

    def test_release_scaffold_contains_required_notice_and_license_files(self) -> None:
        self.assertTrue(BIN.is_file())
        self.assertTrue(VENDOR_ASSEMBLY.is_file())
        self.assertTrue(QUICKSTART.is_file())
        self.assertTrue(NOTICE.is_file())
        self.assertTrue(LICENSE.is_file())
        self.assertTrue(VENDOR_MANIFEST.is_file())
        self.assertIn("no bundled PDFium", read(NOTICE))
        self.assertIn("Apache License", read(LICENSE))

    def test_npm_pack_includes_vendor_payload_when_binaries_are_present(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ethos-npm-pack-") as temp:
            package_copy = Path(temp) / "ethos-pdf"
            copytree(PACKAGE_DIR, package_copy, ignore=lambda _dir, names: {"node_modules", "*.tgz"} & set(names))
            vendor = package_copy / "vendor"
            for target in SUPPORTED_TARGETS.values():
                binary = vendor / target["binary"]
                binary.write_text("#!/usr/bin/env sh\nexit 0\n", encoding="utf-8")
                binary.chmod(0o755)

            result = subprocess.run(
                ["npm", "pack", "--json", "--dry-run"],
                cwd=package_copy,
                check=False,
                encoding="utf-8",
                env={**os.environ, "npm_config_cache": str(Path(temp) / "npm-cache")},
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

        self.assertEqual(0, result.returncode, result.stderr)
        pack = json.loads(result.stdout)[0]
        files = {entry["path"] for entry in pack["files"]}
        self.assertIn("vendor/manifest.json", files)
        self.assertIn("vendor/ethos-darwin-arm64", files)
        self.assertIn("vendor/ethos-linux-x64", files)
        self.assertNotIn("vendor/ethos-win32-x64", files)


if __name__ == "__main__":
    unittest.main()
