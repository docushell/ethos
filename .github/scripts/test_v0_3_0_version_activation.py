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
from validation_record_source import assert_record_source_binding


ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "docs/validation/v0-3-0-version-activation-validation-2026-07-01.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"
RELEASE_PREP = ROOT / "docs/v0-3-0-release-prep.md"
MAKEFILE = ROOT / "Makefile"
README = ROOT / "README.md"
CLAIMS = ROOT / "docs/public-boundary-claims.json"
INSTALL_WORDING_SURFACES = (
    ROOT / "README.md",
    ROOT / "python/README.md",
    ROOT / "python/QUICKSTART.md",
    ROOT / "packages/npm/ethos-pdf/README.md",
    ROOT / "packages/npm/ethos-pdf/QUICKSTART.md",
    ROOT / "crates/ethos-core/README.md",
    ROOT / "crates/ethos-verify/README.md",
    ROOT / "crates/ethos-pdf/README.md",
    ROOT / "adapters/grounding/opendataloader-json/README.md",
)
CARGO = ROOT / "Cargo.toml"
CARGO_LOCK = ROOT / "Cargo.lock"
CLI_CARGO = ROOT / "crates/ethos-cli/Cargo.toml"
PYPROJECT = ROOT / "pyproject.toml"
PYTHON_INIT = ROOT / "python/ethos_pdf/__init__.py"
NPM_PACKAGE = ROOT / "packages/npm/ethos-pdf/package.json"

SOURCE_SHORT = "57e3821"
SOURCE_COMMIT = "57e3821b63b119ee6ca8e52322ddde2fb05dde66"
SOURCE_TREE = "7fd3dd7bcd4d8b503483a06752fdc5e5cb587695"
VERSION = "0.3.0"
RUST_PYTHON_PUBLIC_BASELINE = "0.2.0"
NPM_PUBLIC_BASELINE = "0.2.1"
RELEASE_CANDIDATE_SENTENCE = (
    "v0.3.0 source versions are activated for app-answer-release contract validation."
)
FORBIDDEN_INSTALL_WORDING = (
    "cargo add ethos-doc-core@0.3.0",
    "cargo add ethos-verify@0.3.0",
    "cargo add ethos-pdf@0.3.0",
    "python3 -m pip install ethos-pdf==0.3.0",
    "npm install -g @docushell/ethos-pdf@0.3.0",
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


class V030VersionActivationTests(unittest.TestCase):
    def test_record_is_source_bound_and_indexed(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)

        assert_record_source_binding(
            self,
            root=ROOT,
            raw_record=raw,
            normalized_record=record,
            validated_head=SOURCE_SHORT,
            source_label="v0.3.0 version activation",
            source_commit=SOURCE_COMMIT,
            source_tree=SOURCE_TREE,
        )

        for path in (VALIDATION_README, EXECUTION_STATUS, PUBLIC_RELEASE_CHECKLIST):
            text = normalized(path)
            self.assertIn(RECORD.name, text, str(path))
            self.assertIn("v0.3.0 version activation", text.lower(), str(path))
            self.assertIn("remain blocked", text, str(path))

    def test_rust_and_python_versions_are_activated_without_npm_bump(self) -> None:
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
        self.assertEqual(NPM_PUBLIC_BASELINE, npm["version"])

    def test_public_install_commands_remain_on_current_published_baseline(self) -> None:
        readme = read(README)
        claims = json.loads(read(CLAIMS))["surfaces"]["readme"]["claims"]
        joined_claims = "\n".join(claims)

        for expected in (
            f"cargo add ethos-doc-core@{RUST_PYTHON_PUBLIC_BASELINE}",
            f"cargo add ethos-verify@{RUST_PYTHON_PUBLIC_BASELINE}",
            f"cargo add ethos-pdf@{RUST_PYTHON_PUBLIC_BASELINE}",
            f"python3 -m pip install ethos-pdf=={RUST_PYTHON_PUBLIC_BASELINE}",
            f"npm install -g @docushell/ethos-pdf@{NPM_PUBLIC_BASELINE}",
        ):
            self.assertIn(expected, readme)
            self.assertIn(expected, joined_claims)

        for forbidden in FORBIDDEN_INSTALL_WORDING:
            self.assertNotIn(forbidden, readme)
            self.assertNotIn(forbidden, joined_claims)
            for path in INSTALL_WORDING_SURFACES:
                self.assertNotIn(forbidden, read(path), str(path))

    def test_activation_record_declares_release_candidate_wording_only(self) -> None:
        record = normalized(RECORD)

        self.assertIn(RELEASE_CANDIDATE_SENTENCE, record)
        self.assertIn("No `0.3.0` registry install wording is approved", record)
        self.assertIn("npm remains at `0.2.1`", record)
        self.assertIn("not a Node API or Node SDK", record)

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
            "does not approve public installation wording for `0.3.0`",
            "does not approve npm CLI alignment",
            "does not approve hosted surfaces",
            "does not approve production positioning",
            "does not approve Windows packaged artifacts",
            "does not approve bundled project-maintained PDFium builds",
            "does not approve public benchmark claims",
            "does not approve `ethos-doc`",
            "does not approve `ethos-rag`",
            "does not approve DocuShell integration",
        ):
            self.assertIn(phrase, record)
        for private in PRIVATE_PATH_MARKERS:
            self.assertNotIn(private, raw)

    def test_v0_3_release_prep_runs_activation_guard_after_decision_guard(self) -> None:
        makefile = read(MAKEFILE)
        decision_guard = "$(PYTHON) .github/scripts/test_v0_3_0_release_approval_decision.py"
        activation_guard = "$(PYTHON) .github/scripts/test_v0_3_0_version_activation.py"
        claims = "$(PYTHON) .github/scripts/claims_gate.py"
        block = target_block("v0-3-release-prep")

        self.assertIn(activation_guard, block)
        self.assertEqual(1, makefile.count(activation_guard))
        self.assertLess(block.index(decision_guard), block.index(activation_guard))
        self.assertLess(block.index(activation_guard), block.index(claims))

    def test_release_prep_keeps_current_artifact_workflow_out_of_scope(self) -> None:
        text = normalized(RELEASE_PREP)

        self.assertIn("`.github/workflows/release.yml` artifact workflow", text)
        self.assertIn('`--expected-version "ethos 0.2.0"`', text)
        self.assertIn("Do not use that workflow as evidence for `0.3.0` CLI artifact readiness", text)
        self.assertIn("separate CLI artifact lane", text)


if __name__ == "__main__":
    unittest.main()
