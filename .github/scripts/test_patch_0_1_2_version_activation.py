#!/usr/bin/env python3
#
# Copyright 2026 The Ethos maintainers
#
# Licensed under the Apache License, Version 2.0 (the "License");
#

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from makefile_guard import target_block


ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "docs/validation/patch-0-1-2-version-activation-validation-2026-06-24.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"
MAKEFILE = ROOT / "Makefile"
README = ROOT / "README.md"
CARGO = ROOT / "Cargo.toml"
CARGO_LOCK = ROOT / "Cargo.lock"
CLI_CARGO = ROOT / "crates/ethos-cli/Cargo.toml"
PYPROJECT = ROOT / "pyproject.toml"
PYTHON_INIT = ROOT / "python/ethos_pdf/__init__.py"
NPM_PACKAGE = ROOT / "packages/npm/ethos-pdf/package.json"

SOURCE_SHORT = "0252cc7"
SOURCE_COMMIT = "0252cc7800d51cb1ec673698be5646b4fb945066"
SOURCE_TREE = "ec9e4481ab237192d10942e9ce8d0b4a908c15b8"

FORBIDDEN_RELEASE_CLAIMS = (
    "0.1.2 is released",
    "v0.1.2 is released",
    "0.1.2 is published",
    "v0.1.2 is published",
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


class Patch012VersionActivationTests(unittest.TestCase):
    def test_record_binds_source_and_declares_activation_scope(self) -> None:
        record = normalized(RECORD)
        raw = read(RECORD)

        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", raw)
        self.assertIn(f"Version-activation source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Version-activation source tree: `{SOURCE_TREE}`", record)
        self.assertIn("Rust workspace and Python source/package metadata move to `0.1.2`", record)
        self.assertIn("npm remains at `0.1.1` until matching `0.1.2` CLI artifacts exist", record)

    def test_rust_and_python_versions_are_activated(self) -> None:
        cargo = read(CARGO)
        cli = read(CLI_CARGO)
        lock = read(CARGO_LOCK)

        self.assertIn('version = "0.1.2"', cargo)
        self.assertIn('ethos-core = { package = "ethos-doc-core", path = "crates/ethos-core", version = "0.1.2"', cargo)
        self.assertIn('ethos-layout = { path = "crates/ethos-layout", version = "0.1.2" }', cargo)
        self.assertIn('ethos-tables = { path = "crates/ethos-tables", version = "0.1.2" }', cargo)
        self.assertIn('ethos-pdf = { path = "../ethos-pdf", version = "0.1.2" }', cli)
        self.assertIn('ethos-verify = { path = "../ethos-verify", version = "0.1.2" }', cli)
        self.assertIn('ethos-grounding-opendataloader-json = { path = "../../adapters/grounding/opendataloader-json", version = "0.1.2" }', cli)
        self.assertGreaterEqual(lock.count('version = "0.1.2"'), 7)
        self.assertIn('version = "0.1.2"', read(PYPROJECT))
        self.assertIn('__version__ = "0.1.2"', read(PYTHON_INIT))

    def test_npm_and_public_install_wording_wait_for_artifacts(self) -> None:
        npm = json.loads(read(NPM_PACKAGE))
        readme = read(README)

        self.assertEqual("0.1.1", npm["version"])
        self.assertIn("cargo add ethos-doc-core@0.1.1", readme)
        self.assertIn("cargo add ethos-verify@0.1.1", readme)
        self.assertIn("cargo add ethos-pdf@0.1.1", readme)
        self.assertIn("python3 -m pip install ethos-pdf==0.1.1", readme)
        self.assertIn("npm install -g @docushell/ethos-pdf@0.1.1", readme)
        for phrase in FORBIDDEN_RELEASE_CLAIMS:
            self.assertNotIn(phrase, readme.lower())

    def test_boundaries_remain_closed(self) -> None:
        record = normalized(RECORD)
        lower = record.lower()

        for phrase in (
            "does not approve a release",
            "does not approve a tag",
            "does not approve package publish",
            "does not approve a GitHub Release artifact",
            "does not approve public installation wording for `0.1.2`",
            "does not approve hosted surfaces",
            "does not approve production positioning",
            "does not approve Windows packaged artifacts",
            "does not approve bundled project-maintained PDFium builds",
            "does not approve public benchmark reports",
            "does not approve public benchmark claims",
            "does not approve `ethos-doc`",
            "does not approve `ethos-rag`",
        ):
            self.assertIn(phrase, record)
        for phrase in FORBIDDEN_RELEASE_CLAIMS:
            self.assertNotIn(phrase, lower)

    def test_record_is_indexed_and_release_candidate_prep_runs_guard(self) -> None:
        record_name = RECORD.name
        block = target_block("release-candidate-prep")
        readiness_guard = "$(PYTHON) .github/scripts/test_patch_0_1_2_readiness_prep.py"
        activation_guard = "$(PYTHON) .github/scripts/test_patch_0_1_2_version_activation.py"

        self.assertIn(record_name, read(VALIDATION_README))
        self.assertIn(record_name, read(EXECUTION_STATUS))
        self.assertIn(record_name, read(PUBLIC_RELEASE_CHECKLIST))
        self.assertIn(activation_guard, block)
        self.assertEqual(1, read(MAKEFILE).count(activation_guard))
        self.assertLess(block.index(readiness_guard), block.index(activation_guard))

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
