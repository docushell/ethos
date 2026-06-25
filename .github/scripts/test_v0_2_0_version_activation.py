#!/usr/bin/env python3
#
# Copyright 2026 The Ethos maintainers
#
# Licensed under the Apache License, Version 2.0 (the "License");
#

from __future__ import annotations

import json
import re
import subprocess
import unittest
from pathlib import Path

from makefile_guard import target_block


ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "docs/validation/v0-2-0-version-activation-validation-2026-06-25.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"
MAKEFILE = ROOT / "Makefile"
README = ROOT / "README.md"
CLAIMS = ROOT / "docs/public-boundary-claims.json"
CARGO = ROOT / "Cargo.toml"
CARGO_LOCK = ROOT / "Cargo.lock"
CLI_CARGO = ROOT / "crates/ethos-cli/Cargo.toml"
PYPROJECT = ROOT / "pyproject.toml"
PYTHON_INIT = ROOT / "python/ethos_pdf/__init__.py"
NPM_PACKAGE = ROOT / "packages/npm/ethos-pdf/package.json"

SOURCE_SHORT = "523e114"
SOURCE_COMMIT = "523e1143bec52e16e596593f5dd649df741b4971"
SOURCE_TREE = "8f13de3588a36927635a967cf120fba8f73a39f6"
VERSION = "0.2.0"
PUBLIC_BASELINE = "0.1.2"
RELEASE_CANDIDATE_SENTENCE = (
    "v0.2.0 release-candidate source versions are activated for JSON verification and evidence "
    "anchoring."
)
FORBIDDEN_INSTALL_WORDING = (
    "cargo add ethos-doc-core@0.2.0",
    "cargo add ethos-verify@0.2.0",
    "cargo add ethos-pdf@0.2.0",
    "python3 -m pip install ethos-pdf==0.2.0",
    "npm install -g @docushell/ethos-pdf@0.2.0",
    "0.2.0 is released",
    "v0.2.0 is released",
    "0.2.0 is published",
    "v0.2.0 is published",
)
PRIVATE_PATH_MARKERS = (
    "/" + "Users/",
    "/" + "private/tmp",
    "/" + "private/var",
    "/" + "var/folders",
    "saumil" + "diwaker",
    "Desktop/" + "Stuff",
    "project/repo/" + "ethos",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalized(path: Path) -> str:
    return re.sub(r"\s+", " ", read(path))


def normalized_markdown(path: Path) -> str:
    return re.sub(
        r"\s+",
        " ",
        " ".join(line.removeprefix("> ").strip() for line in read(path).splitlines()),
    )


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args],
        cwd=ROOT,
        encoding="utf-8",
        stderr=subprocess.DEVNULL,
    ).strip()


class V020VersionActivationTests(unittest.TestCase):
    def test_record_is_source_bound_and_indexed(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)

        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", raw)
        self.assertIn(f"v0.2.0 version activation source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"v0.2.0 version activation source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

        for path in (VALIDATION_README, EXECUTION_STATUS, PUBLIC_RELEASE_CHECKLIST):
            text = normalized(path)
            self.assertIn(RECORD.name, text, str(path))
            self.assertIn("v0.2.0 version activation", text.lower(), str(path))
            self.assertIn("remain blocked", text, str(path))

    def test_rust_python_and_npm_versions_are_activated(self) -> None:
        cargo = read(CARGO)
        cli = read(CLI_CARGO)
        lock = read(CARGO_LOCK)
        npm = json.loads(read(NPM_PACKAGE))

        self.assertIn(f'version = "{VERSION}"', cargo)
        self.assertIn(f'ethos-core = {{ package = "ethos-doc-core", path = "crates/ethos-core", version = "{VERSION}"', cargo)
        self.assertIn(f'ethos-layout = {{ path = "crates/ethos-layout", version = "{VERSION}" }}', cargo)
        self.assertIn(f'ethos-tables = {{ path = "crates/ethos-tables", version = "{VERSION}" }}', cargo)
        self.assertIn(f'ethos-pdf = {{ path = "../ethos-pdf", version = "{VERSION}" }}', cli)
        self.assertIn(f'ethos-verify = {{ path = "../ethos-verify", version = "{VERSION}" }}', cli)
        self.assertIn(
            f'ethos-grounding-opendataloader-json = {{ path = "../../adapters/grounding/opendataloader-json", version = "{VERSION}" }}',
            cli,
        )
        self.assertGreaterEqual(lock.count(f'version = "{VERSION}"'), 7)
        self.assertIn(f'version = "{VERSION}"', read(PYPROJECT))
        self.assertIn(f'__version__ = "{VERSION}"', read(PYTHON_INIT))
        self.assertEqual(VERSION, npm["version"])

    def test_public_install_commands_remain_on_approved_baseline(self) -> None:
        readme = read(README)
        claims = json.loads(read(CLAIMS))["surfaces"]["readme"]["claims"]
        joined_claims = "\n".join(claims)

        for expected in (
            f"cargo add ethos-doc-core@{PUBLIC_BASELINE}",
            f"cargo add ethos-verify@{PUBLIC_BASELINE}",
            f"cargo add ethos-pdf@{PUBLIC_BASELINE}",
            f"python3 -m pip install ethos-pdf=={PUBLIC_BASELINE}",
            f"npm install -g @docushell/ethos-pdf@{PUBLIC_BASELINE}",
        ):
            self.assertIn(expected, readme)
            self.assertIn(expected, joined_claims)

        self.assertIn(RELEASE_CANDIDATE_SENTENCE, normalized_markdown(README))
        self.assertIn(RELEASE_CANDIDATE_SENTENCE, joined_claims)
        for forbidden in FORBIDDEN_INSTALL_WORDING:
            self.assertNotIn(forbidden, readme)
            self.assertNotIn(forbidden, joined_claims)

    def test_boundaries_remain_closed(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)

        for phrase in (
            "does not approve a release",
            "does not approve a tag",
            "does not approve package publish",
            "does not approve npm publish",
            "does not approve PyPI publish",
            "does not approve crates.io publish",
            "does not approve a GitHub Release artifact",
            "does not approve public installation wording for `0.2.0`",
            "does not approve hosted surfaces",
            "does not approve production positioning",
            "does not approve Windows packaged artifacts",
            "does not approve bundled project-maintained PDFium builds",
            "does not approve public benchmark claims",
            "does not approve `ethos-doc`",
            "does not approve `ethos-rag`",
        ):
            self.assertIn(phrase, record)
        for private in PRIVATE_PATH_MARKERS:
            self.assertNotIn(private, raw)

    def test_v0_2_release_prep_runs_activation_guard_after_decision_guard(self) -> None:
        makefile = read(MAKEFILE)
        decision_guard = "$(PYTHON) .github/scripts/test_v0_2_0_release_approval_decision.py"
        activation_guard = "$(PYTHON) .github/scripts/test_v0_2_0_version_activation.py"
        claims = "$(PYTHON) .github/scripts/claims_gate.py"
        block = target_block("v0-2-release-prep")

        self.assertIn(activation_guard, block)
        self.assertEqual(1, makefile.count(activation_guard))
        self.assertLess(block.index(decision_guard), block.index(activation_guard))
        self.assertLess(block.index(activation_guard), block.index(claims))


if __name__ == "__main__":
    unittest.main()
