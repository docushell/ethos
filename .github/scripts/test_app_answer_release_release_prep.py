#!/usr/bin/env python3
#
# Copyright 2026 The Ethos maintainers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#

from __future__ import annotations

import re
import unittest
from pathlib import Path

from makefile_guard import target_block
from validation_record_source import assert_record_source_binding


ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "docs/validation/app-answer-release-contract-release-prep-validation-2026-07-01.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"
README = ROOT / "README.md"
CHANGELOG = ROOT / "CHANGELOG.md"
MAKEFILE = ROOT / "Makefile"
PYTHON_INIT = ROOT / "python/ethos_pdf/__init__.py"
NPM_PACKAGE = ROOT / "packages/npm/ethos-pdf/package.json"
CARGO_TOML = ROOT / "Cargo.toml"

SOURCE_SHORT = "d386568"
SOURCE_COMMIT = "d386568ef680f36f4a395543b21d34d2b17baccb"
SOURCE_TREE = "5891ab9c1e2fb4a9094d3d52c59ec57630aa871f"
CURRENT_BASELINE = "0.2.0"
SUGGESTED_TARGET = "0.3.0"
RECORD_NAME = "app-answer-release-contract-release-prep-validation-2026-07-01.md"

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


class AppAnswerReleaseReleasePrepTests(unittest.TestCase):
    def test_record_is_source_bound_and_indexed(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)

        assert_record_source_binding(
            self,
            root=ROOT,
            raw_record=raw,
            normalized_record=record,
            validated_head=SOURCE_SHORT,
            source_label="app-answer-release contract release prep",
            source_commit=SOURCE_COMMIT,
            source_tree=SOURCE_TREE,
        )

        for path in (VALIDATION_README, EXECUTION_STATUS, PUBLIC_RELEASE_CHECKLIST):
            text = normalized(path)
            self.assertIn(RECORD_NAME, text, str(path))
            self.assertIn("app-answer-release contract release prep", text.lower(), str(path))
            self.assertIn("remain blocked", text, str(path))

    def test_packet_names_scope_version_and_public_surfaces(self) -> None:
        record = normalized(RECORD)

        self.assertIn(
            "Status: **app-answer-release contract release-prep packet recorded; version bump, "
            "package publication, tag creation, artifact publication, installable `0.3.0` wording, "
            "npm publication, and DocuShell integration remain blocked**",
            record,
        )
        self.assertIn(f"Current published baseline: `{CURRENT_BASELINE}` Rust and Python surfaces", record)
        self.assertIn(f"Suggested target version for decider review: `{SUGGESTED_TARGET}`", record)
        self.assertIn("Target version proposal is not an approval.", record)
        for surface in [
            "docs/app-answer-release-contract.md",
            "schemas/ethos-app-answer-release-decision.schema.json",
            "schemas/examples/app-answer-release-decision.example.json",
            "examples/app-answer-release/run_python_demo.py",
            "examples/app-answer-release/expected-decision.json",
            "make app-answer-release-contract PYTHON=python3",
            "make app-answer-release-demo PYTHON=python3",
        ]:
            self.assertIn(surface, record)

    def test_package_decisions_are_bounded_and_npm_is_out_by_default(self) -> None:
        record = normalized(RECORD)

        self.assertIn("Rust decision requested", record)
        self.assertIn("workspace uses lockstep source versions", record)
        self.assertIn("`ethos-doc-core`, `ethos-verify`, and `ethos-pdf` together", record)
        self.assertIn("Python decision requested", record)
        self.assertIn("`ethos-pdf==0.3.0`", record)
        self.assertIn("npm decision requested: keep npm out of scope by default", record)
        self.assertIn("not a Node API or Node SDK", record)
        self.assertIn("CLI artifact decision requested: keep GitHub Release CLI artifact publication out of scope by default", record)
        self.assertIn("release tag `v0.3.0`", record)

    def test_product_boundary_and_non_approvals_remain_explicit(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)
        lower = record.lower()

        self.assertIn("Ethos owns citation grounding and derived proof summaries.", record)
        self.assertIn("Applications own question relevance labels.", record)
        self.assertIn("Applications own source-fact, synthesis, and unsupported-claim labels.", record)
        self.assertIn("Ethos verified citation grounding.", record)
        self.assertIn("Answer relevance: direct, partial, or off-topic.", record)

        for required in [
            "This prep record does not approve a version bump.",
            "This prep record does not create a release-candidate branch.",
            "This prep record does not approve `cargo publish`.",
            "This prep record does not approve PyPI upload.",
            "This prep record does not approve `npm publish`.",
            "This prep record does not create a GitHub Release.",
            "This prep record does not approve installable `0.3.0` public wording.",
            "This prep record does not approve a Node API, Node SDK, N-API binding, or WASM package.",
            "This prep record does not approve DocuShell integration.",
        ]:
            self.assertIn(required, record)

        for forbidden in [
            "version bump approved",
            "cargo publish approved",
            "pypi upload approved",
            "npm publish approved",
            "github release approved",
            "tag creation approved",
            "installable `0.3.0` public wording approved",
            "ethos verified the answer",
        ]:
            self.assertNotIn(forbidden, lower)
        for private in PRIVATE_PATH_MARKERS:
            self.assertNotIn(private, raw)

    def test_current_public_install_surfaces_are_not_bumped(self) -> None:
        self.assertIn('version = "0.2.0"', read(CARGO_TOML))
        self.assertIn('__version__ = "0.2.0"', read(PYTHON_INIT))
        self.assertIn('"version": "0.2.1"', read(NPM_PACKAGE))
        self.assertIn("cargo add ethos-doc-core@0.2.0", read(README))
        self.assertIn("python3 -m pip install ethos-pdf==0.2.0", read(README))
        self.assertIn("npm install -g @docushell/ethos-pdf@0.2.1", read(README))
        self.assertNotIn("cargo add ethos-doc-core@0.3.0", read(README))
        self.assertNotIn("python3 -m pip install ethos-pdf==0.3.0", read(README))
        self.assertNotIn("npm install -g @docushell/ethos-pdf@0.3.0", read(README))

    def test_make_target_runs_scoped_release_prep_guard(self) -> None:
        block = target_block("app-answer-release-release-prep")
        commands = [line.strip() for line in block.splitlines() if line.strip()]

        self.assertEqual(
            [
                "$(MAKE) app-answer-release-contract PYTHON=$(PYTHON)",
                "$(PYTHON) .github/scripts/test_app_answer_release_release_prep.py",
                "$(PYTHON) .github/scripts/test_public_surface_posture.py",
                "$(PYTHON) .github/scripts/test_ci_workflow.py",
                "git diff --check",
            ],
            commands,
        )
        self.assertIn("test_app_answer_release_release_prep.py", read(MAKEFILE))

    def test_changelog_records_boundary_exception_without_publication(self) -> None:
        text = normalized(CHANGELOG)

        self.assertIn("boundary-exception: record app-answer-release contract release-prep packet", text)
        self.assertIn("publication, tag creation, artifact publication, installable `0.3.0` wording", text)
        self.assertIn("DocuShell integration blocked", text)


if __name__ == "__main__":
    unittest.main()
