#!/usr/bin/env python3
#
# Copyright 2026 The Ethos maintainers
#
# Licensed under the Apache License, Version 2.0 (the "License");
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

from makefile_guard import target_block
from validation_record_source import assert_record_source_binding


ROOT = Path(__file__).resolve().parents[2]
PACKAGE_DIR = ROOT / "packages/npm/ethos-pdf"
PACKAGE_TARBALL = PACKAGE_DIR / "docushell-ethos-pdf-0.2.1.tgz"
RECORD = ROOT / "docs/validation/v0-2-0-npm-vendor-refresh-validation-2026-06-25.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"

SOURCE_SHORT = "aba17c7"
SOURCE_COMMIT = "aba17c7254f2e42b9ccbf71db1a3b53113dc0e18"
SOURCE_TREE = "2029e1a25629f80f251ac6ab670231187bada0a9"
MACOS_ARTIFACT_SHA256 = "c588ee77bbaf99a7d933673e6cd9db190f5992e47d40955def803435a9f9fc5a"
LINUX_ARTIFACT_SHA256 = "00137b20ca2c2a2d2089df1d135920b021b0905d779b1347d134e8a2fb7bfa23"
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
    "vendor/ethos-darwin-arm64": "e139da8fe635a3e6a42fafb49d66fcf674dbff3d7bdd8dfe844b9eb424e5b53e",
    "vendor/ethos-linux-x64": "5ab007b03eba6b1730e95053d1b0095b892a40272b610232568295a67c076a83",
    "vendor/manifest.json": "a5cd55d7670e41ede06eb7955cae76a553ebf9ba506ed374d9a409b75f3dde40",
}
EXPECTED_PACK_SHASUM = "8f2e2633edb60cea415915c4646da7e9b4dfb4ed"
EXPECTED_PACK_SHA256 = "c832c9efb3fc8d5480070d8eeb76e00b73f7396d9346a1d490c6ee9109708b2b"
EXPECTED_PACK_INTEGRITY = (
    "sha512-WFNV1h/H90FssbhQBxBsriunVa1XIp8MAWeBtstJ+FKF7AsQkkXEoiSY1WQPDZ3BH6iobHuM2j/ZQ2u6zMcfdA=="
)
EXPECTED_NODE_VERSION = "v23.11.1"
EXPECTED_NPM_VERSION = "10.9.2"
PRIVATE_PATH_MARKERS = (
    "/" + "Users/",
    "/" + "private/tmp",
    "/" + "private/var",
    "/" + "var/folders",
    "saumil" + "diwaker",
    "Desktop/" + "Stuff",
    "project/repo/" + "ethos",
)
FORBIDDEN_APPROVALS = (
    "npm publication approved",
    "npm publish approved",
    "github release artifact publication approved",
    "registry publication approved",
    "pypi upload approved",
    "release tag creation approved",
    "package tag creation approved",
    "public installation wording approved",
    "production-ready",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalized(path: Path) -> str:
    return re.sub(r"\s+", " ", read(path))


def pack_candidate(temp: str) -> tuple[dict[str, object], str, str]:
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
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    return json.loads(result.stdout)[0], env["npm_config_cache"], result.stdout


class V020NpmVendorRefreshTests(unittest.TestCase):
    def test_vendor_payload_files_are_exact_draft_artifact_derived_binaries(self) -> None:
        for relative_path, expected in EXPECTED_VENDOR_SHA256.items():
            self.assertEqual(expected, sha256(PACKAGE_DIR / relative_path))

        manifest = json.loads(read(PACKAGE_DIR / "vendor/manifest.json"))
        self.assertEqual(MACOS_ARTIFACT_SHA256, manifest["targets"]["darwin:arm64"]["release_asset_sha256"])
        self.assertEqual(LINUX_ARTIFACT_SHA256, manifest["targets"]["linux:x64"]["release_asset_sha256"])

    def test_npm_pack_candidate_contents_and_checksums(self) -> None:
        node_version = subprocess.check_output(["node", "--version"], encoding="utf-8").strip()
        npm_version = subprocess.check_output(["npm", "--version"], encoding="utf-8").strip()
        exact_pack_toolchain = (
            node_version == EXPECTED_NODE_VERSION and npm_version == EXPECTED_NPM_VERSION
        )

        with tempfile.TemporaryDirectory(prefix="ethos-v0-2-npm-candidate-") as temp:
            try:
                pack, _, _ = pack_candidate(temp)
                files = {entry["path"]: entry for entry in pack["files"]}

                self.assertEqual("@docushell/ethos-pdf", pack["name"])
                self.assertEqual("0.2.1", pack["version"])
                self.assertEqual("docushell-ethos-pdf-0.2.1.tgz", pack["filename"])
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

    def test_candidate_tarball_installs_and_preserves_pdfium_boundary(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ethos-v0-2-npm-install-") as temp:
            try:
                _, _, _ = pack_candidate(temp)
                env = {**os.environ, "npm_config_cache": str(Path(temp) / "npm-cache")}
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
                self.assertEqual("ethos 0.2.0", version.stdout.strip())

                missing_pdfium = subprocess.run(
                    [str(ethos), "doctor", "--require-pdfium"],
                    check=False,
                    encoding="utf-8",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                self.assertEqual(12, missing_pdfium.returncode)
                combined = missing_pdfium.stdout + missing_pdfium.stderr
                self.assertIn("ethos 0.2.0", combined)
                self.assertIn("darwin:arm64", combined)
                self.assertIn("approved npm vendor manifest", combined)
                self.assertIn("ETHOS_PDFIUM_LIBRARY_PATH", combined)
            finally:
                PACKAGE_TARBALL.unlink(missing_ok=True)

    def test_candidate_evidence_record_is_source_bound_indexed_and_blocked(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)
        readme = normalized(VALIDATION_README)
        execution = normalized(EXECUTION_STATUS)
        checklist = normalized(PUBLIC_RELEASE_CHECKLIST)
        block = target_block("v0-2-release-prep")
        draft_guard = "$(PYTHON) .github/scripts/test_v0_2_0_draft_artifact_evidence.py"
        vendor_guard = "$(PYTHON) .github/scripts/test_v0_2_0_npm_vendor_refresh.py"
        claims = "$(PYTHON) .github/scripts/claims_gate.py"

        assert_record_source_binding(
            self,
            root=ROOT,
            raw_record=raw,
            normalized_record=record,
            validated_head=SOURCE_SHORT,
            source_label="v0.2.0 npm vendor refresh",
            source_commit=SOURCE_COMMIT,
            source_tree=SOURCE_TREE,
        )
        for expected in (
            MACOS_ARTIFACT_SHA256,
            LINUX_ARTIFACT_SHA256,
            EXPECTED_PACK_SHASUM,
            EXPECTED_PACK_SHA256,
            EXPECTED_PACK_INTEGRITY,
            f"Node.js: `{EXPECTED_NODE_VERSION}`",
            f"npm: `{EXPECTED_NPM_VERSION}`",
            "durable package-content provenance",
            "per-file vendor SHA256 values as the durable content binding",
            "ethos 0.2.0",
            "exit code 12",
            "`@docushell/ethos-pdf@0.2.0` was published and then deprecated",
            "`@docushell/ethos-pdf@0.2.1` was published",
        ):
            self.assertIn(expected, record)
        for text in (readme, execution, checklist):
            self.assertIn(RECORD.name, text)
            self.assertIn("npm vendor", text.lower())
            self.assertIn("ethos 0.2.0", text)
        for forbidden in FORBIDDEN_APPROVALS:
            self.assertNotIn(forbidden, record.lower())
        for marker in PRIVATE_PATH_MARKERS:
            self.assertNotIn(marker, raw)
        self.assertIn(vendor_guard, block)
        self.assertEqual(1, block.count(vendor_guard))
        self.assertLess(block.index(draft_guard), block.index(vendor_guard))
        self.assertLess(block.index(vendor_guard), block.index(claims))


if __name__ == "__main__":
    unittest.main()
