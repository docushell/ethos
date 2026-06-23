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

import hashlib
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE_DIR = ROOT / "packages/npm/ethos-pdf"
PACKAGE_TARBALL = PACKAGE_DIR / "docushell-ethos-pdf-0.1.0.tgz"
EXPECTED_FILES = {
    "LICENSE",
    "NOTICE",
    "QUICKSTART.md",
    "README.md",
    "bin/ethos-pdf.js",
    "package.json",
    "scripts/postinstall.js",
    "scripts/prepare-vendor.js",
    "vendor/ethos-darwin-arm64",
    "vendor/ethos-linux-x64",
    "vendor/manifest.json",
}
EXPECTED_VENDOR_SHA256 = {
    "vendor/ethos-darwin-arm64": "f1b0c9e47dace78b7e8b3639b9445afe9a01f0db5d5b7b0bd81858def4df2cf5",
    "vendor/ethos-linux-x64": "7ef796a6d1c86b7c3b5b1afe58dd9cc348b706cec441602833540d8a0c9260ac",
    "vendor/manifest.json": "0d03124957255dca55b7374e3318707da488f4b6648bfcec5e6e598079353b1f",
}
EXPECTED_PACK_SHASUM = "17a053c5ccb802bca2a295e1b1d0e6106c6a3ca6"
EXPECTED_PACK_SHA256 = "8d0483d69a6de471dee52c8ef06d46712c06861682a0d7319ca573fdb1fe6376"
EXPECTED_PACK_INTEGRITY = (
    "sha512-uWTHYd9Hfkm3nkahK2UchCMOVvYWe82z03jffZnX6aYPqYGd6LkuiEoTH5DjrXl+oA817EjlE88fIKBxZbhjMw=="
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class NpmTarballCandidateEvidenceTests(unittest.TestCase):
    def test_vendor_payload_files_are_exact_release_derived_binaries(self) -> None:
        for relative_path, expected in EXPECTED_VENDOR_SHA256.items():
            self.assertEqual(expected, sha256(PACKAGE_DIR / relative_path))

    def test_npm_pack_candidate_contents_and_checksums(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ethos-npm-candidate-") as temp:
            env = {**os.environ, "npm_config_cache": str(Path(temp) / "npm-cache")}
            result = subprocess.run(
                ["npm", "pack", "--json"],
                cwd=PACKAGE_DIR,
                check=False,
                encoding="utf-8",
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            try:
                self.assertEqual(0, result.returncode, result.stderr)
                pack = json.loads(result.stdout)[0]
                files = {entry["path"]: entry for entry in pack["files"]}

                self.assertEqual("@docushell/ethos-pdf", pack["name"])
                self.assertEqual("0.1.0", pack["version"])
                self.assertEqual("docushell-ethos-pdf-0.1.0.tgz", pack["filename"])
                self.assertEqual(EXPECTED_PACK_SHASUM, pack["shasum"])
                self.assertEqual(EXPECTED_PACK_INTEGRITY, pack["integrity"])
                self.assertEqual(EXPECTED_FILES, set(files))
                self.assertEqual(493, files["vendor/ethos-darwin-arm64"]["mode"])
                self.assertEqual(493, files["vendor/ethos-linux-x64"]["mode"])
                self.assertEqual(EXPECTED_PACK_SHA256, sha256(PACKAGE_TARBALL))
            finally:
                PACKAGE_TARBALL.unlink(missing_ok=True)

    def test_candidate_tarball_installs_and_preserves_pdfium_boundary(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ethos-npm-install-") as temp:
            env = {**os.environ, "npm_config_cache": str(Path(temp) / "npm-cache")}
            pack = subprocess.run(
                ["npm", "pack", "--json"],
                cwd=PACKAGE_DIR,
                check=False,
                encoding="utf-8",
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            try:
                self.assertEqual(0, pack.returncode, pack.stderr)
                install = subprocess.run(
                    ["npm", "install", str(PACKAGE_TARBALL), "--prefix", temp],
                    cwd=ROOT,
                    check=False,
                    encoding="utf-8",
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                self.assertEqual(0, install.returncode, install.stderr)

                ethos = Path(temp) / "node_modules/.bin/ethos"
                version = subprocess.run(
                    [str(ethos), "--version"],
                    check=False,
                    encoding="utf-8",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                self.assertEqual(0, version.returncode, version.stderr)
                self.assertEqual("ethos 0.1.0", version.stdout.strip())

                dummy_pdf = Path(temp) / "dummy.pdf"
                dummy_pdf.write_text("%PDF-1.4\n%%EOF\n", encoding="utf-8")
                missing_pdfium = subprocess.run(
                    [str(ethos), "doc", "parse", str(dummy_pdf), "--format", "json"],
                    check=False,
                    encoding="utf-8",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                self.assertEqual(12, missing_pdfium.returncode)
                self.assertIn(
                    "ETHOS_PDFIUM_LIBRARY_PATH",
                    missing_pdfium.stdout + missing_pdfium.stderr,
                )
            finally:
                PACKAGE_TARBALL.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
