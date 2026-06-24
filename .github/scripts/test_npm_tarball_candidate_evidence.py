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
import re
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE_DIR = ROOT / "packages/npm/ethos-pdf"
PACKAGE_TARBALL = PACKAGE_DIR / "docushell-ethos-pdf-0.1.2.tgz"
RECORD = ROOT / "docs/validation/patch-0-1-2-npm-vendor-refresh-validation-2026-06-24.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
SOURCE_SHORT = "2323398"
SOURCE_COMMIT = "23233986035e0f4a20295b24a9cfafafe65aa117"
SOURCE_TREE = "750551f51094f0bc9625c781b8cc978431e431c3"
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
    "vendor/ethos-darwin-arm64": "47c2f4aaac6cb6a1ca5cf1d9a0cc1f897ef00c48cdd8549455de70f0fbc6bcc1",
    "vendor/ethos-linux-x64": "e75122f2954efbde6b8c07a98601b8d4a3b7a06647891a9e60d6aef4046649c3",
    "vendor/manifest.json": "d557e081b946be0f839b17b8593027e31267b668498e202372026020f68a97a1",
}
EXPECTED_PACK_SHASUM = "39b85d74f588666bfbf69e423a189c2039743de4"
EXPECTED_PACK_SHA256 = "77cbc9c79dd60cc16073690a186e149ecbaabacce035fb0bd3603b267ce64112"
EXPECTED_PACK_INTEGRITY = (
    "sha512-3loga13tnAkUkjuOrjKjpA0D3Cm5lW6Al8OwTyRx7NGMt6EB4gMpZOoaSCPjZWchYv7as1uPaEnZyOqrmFOPxg=="
)
EVIDENCE_PACK_SHASUM = EXPECTED_PACK_SHASUM
EVIDENCE_PACK_SHA256 = EXPECTED_PACK_SHA256
EVIDENCE_PACK_INTEGRITY = (
    EXPECTED_PACK_INTEGRITY
)
EXPECTED_NODE_VERSION = "v23.11.1"
EXPECTED_NPM_VERSION = "10.9.2"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalized(path: Path) -> str:
    return re.sub(r"\s+", " ", read(path))


class NpmTarballCandidateEvidenceTests(unittest.TestCase):
    def test_vendor_payload_files_are_exact_release_derived_binaries(self) -> None:
        for relative_path, expected in EXPECTED_VENDOR_SHA256.items():
            self.assertEqual(expected, sha256(PACKAGE_DIR / relative_path))

    def test_npm_pack_candidate_contents_and_checksums(self) -> None:
        node_version = subprocess.check_output(["node", "--version"], encoding="utf-8").strip()
        npm_version = subprocess.check_output(["npm", "--version"], encoding="utf-8").strip()
        exact_pack_toolchain = (
            node_version == EXPECTED_NODE_VERSION and npm_version == EXPECTED_NPM_VERSION
        )

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
                self.assertEqual("0.1.2", pack["version"])
                self.assertEqual("docushell-ethos-pdf-0.1.2.tgz", pack["filename"])
                self.assertEqual(EXPECTED_FILES, set(files))
                self.assertEqual(493, files["vendor/ethos-darwin-arm64"]["mode"])
                self.assertEqual(493, files["vendor/ethos-linux-x64"]["mode"])
                for relative_path, expected in EXPECTED_VENDOR_SHA256.items():
                    self.assertEqual(expected, sha256(PACKAGE_DIR / relative_path))
                if exact_pack_toolchain:
                    self.assertEqual(EXPECTED_PACK_SHASUM, pack["shasum"])
                    self.assertEqual(EXPECTED_PACK_INTEGRITY, pack["integrity"])
                    self.assertEqual(EXPECTED_PACK_SHA256, sha256(PACKAGE_TARBALL))
            finally:
                PACKAGE_TARBALL.unlink(missing_ok=True)

    def test_candidate_evidence_record_is_source_bound_and_indexed(self) -> None:
        record = normalized(RECORD)
        readme = normalized(VALIDATION_README)

        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"npm vendor refresh source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"npm vendor refresh source tree: `{SOURCE_TREE}`", record)
        self.assertIn(EVIDENCE_PACK_SHASUM, record)
        self.assertIn(EVIDENCE_PACK_SHA256, record)
        self.assertIn(EVIDENCE_PACK_INTEGRITY, record)
        self.assertIn(f"Node.js: `{EXPECTED_NODE_VERSION}`", record)
        self.assertIn(f"npm: `{EXPECTED_NPM_VERSION}`", record)
        self.assertIn("durable package-content provenance", record)
        self.assertIn("per-file vendor SHA256 values as the durable content binding", record)
        self.assertIn("ethos 0.1.2", record)
        self.assertIn("exit code `12`", record)
        self.assertIn("npm publication remains blocked", record)
        self.assertIn("Public installation wording remains blocked", record)
        self.assertNotIn("npm publication approved", record.lower())
        self.assertIn(RECORD.name, readme)
        self.assertIn("patch 0.1.2 npm vendor refresh validation", readme)

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
                self.assertEqual("ethos 0.1.2", version.stdout.strip())

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
