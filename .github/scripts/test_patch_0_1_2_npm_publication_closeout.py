#!/usr/bin/env python3
#
# Copyright 2026 The Ethos maintainers
#
# Licensed under the Apache License, Version 2.0 (the "License");
#

from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "docs/validation/patch-0-1-2-npm-publication-closeout-validation-2026-06-24.md"
VALIDATION_README = ROOT / "docs/validation/README.md"

SOURCE_SHORT = "b7476e9"
SOURCE_COMMIT = "b7476e95db438b849d12e44a54296da9380091e2"
SOURCE_TREE = "958417827cb1678ec2bf492c12a698143c58f58b"
PACKAGE = "@docushell/ethos-pdf"
VERSION = "0.1.2"
SHASUM = "39b85d74f588666bfbf69e423a189c2039743de4"
INTEGRITY = "sha512-3loga13tnAkUkjuOrjKjpA0D3Cm5lW6Al8OwTyRx7NGMt6EB4gMpZOoaSCPjZWchYv7as1uPaEnZyOqrmFOPxg=="
TARBALL = "https://registry.npmjs.org/@docushell/ethos-pdf/-/ethos-pdf-0.1.2.tgz"
UNPACKED_SIZE = 3934993


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalized(path: Path) -> str:
    return re.sub(r"\s+", " ", read(path))


def npm_view(*args: str) -> str:
    with tempfile.TemporaryDirectory(prefix="ethos-npm-view-") as temp:
        return subprocess.check_output(
            ["npm", "view", *args, "--registry=https://registry.npmjs.org/"],
            cwd=ROOT,
            encoding="utf-8",
            env={**os.environ, "npm_config_cache": str(Path(temp) / "npm-cache")},
            stderr=subprocess.DEVNULL,
        ).strip()


class Patch012NpmPublicationCloseoutTests(unittest.TestCase):
    def test_record_is_source_bound_and_indexed(self) -> None:
        record = normalized(RECORD)
        readme = normalized(VALIDATION_README)

        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"npm publication closeout source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"npm publication closeout source tree: `{SOURCE_TREE}`", record)
        self.assertIn(RECORD.name, readme)
        self.assertIn("patch 0.1.2 npm publication closeout", readme)

    def test_record_captures_publish_and_registry_evidence(self) -> None:
        record = normalized(RECORD)

        for expected in (
            "+ @docushell/ethos-pdf@0.1.2",
            SHASUM,
            INTEGRITY,
            TARBALL,
            "fileCount",
            str(UNPACKED_SIZE),
            "2026-06-24T17:48:40.528Z",
            "v23.11.1",
            "10.9.2",
            "ETHOS_PDFIUM_LIBRARY_PATH",
            "The registry latest is now `0.1.2`",
        ):
            self.assertIn(expected, record)

    def test_registry_reports_published_candidate(self) -> None:
        self.assertEqual(VERSION, npm_view(f"{PACKAGE}", "version"))
        versions = json.loads(npm_view(f"{PACKAGE}", "versions", "--json"))
        self.assertIn("0.0.0-reserved.0", versions)
        self.assertIn("0.1.0", versions)
        self.assertIn("0.1.1", versions)
        self.assertIn(VERSION, versions)
        metadata = json.loads(npm_view(f"{PACKAGE}@{VERSION}", "--json"))
        dist = metadata["dist"]

        self.assertEqual(SOURCE_COMMIT, metadata["gitHead"])
        self.assertEqual("23.11.1", metadata["_nodeVersion"])
        self.assertEqual("10.9.2", metadata["_npmVersion"])
        self.assertEqual(SHASUM, dist["shasum"])
        self.assertEqual(INTEGRITY, dist["integrity"])
        self.assertEqual(TARBALL, dist["tarball"])
        self.assertEqual(11, dist["fileCount"])
        self.assertEqual(UNPACKED_SIZE, dist["unpackedSize"])

    def test_retained_blockers_and_public_path_hygiene(self) -> None:
        raw = read(RECORD)
        lower = normalized(RECORD).lower()

        for blocker in (
            "Public installation wording remains blocked.",
            "Hosted surfaces remain blocked.",
            "Production positioning remains blocked.",
            "Public benchmark reports remain blocked.",
            "Public benchmark claims remain blocked.",
            "Windows packaged artifacts remain blocked.",
            "Bundled project-maintained PDFium builds remain blocked.",
            "`ethos-doc` remains blocked.",
            "`ethos-rag` remains blocked.",
        ):
            self.assertIn(blocker, raw)
        for forbidden in (
            "production-ready",
            "hosted surfaces approved",
            "public benchmark claims approved",
            "windows packaged artifacts approved",
            "bundled pdfium approved",
        ):
            self.assertNotIn(forbidden, lower)
        self.assertNotIn("/Users/", raw)
        self.assertNotIn("/private/tmp", raw)
        self.assertNotIn("saumildiwaker", raw)


if __name__ == "__main__":
    unittest.main()
