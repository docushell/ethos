#!/usr/bin/env python3
#
# Copyright 2026 The Ethos maintainers
#
# Licensed under the Apache License, Version 2.0 (the "License");
#

from __future__ import annotations

import re
import unittest
from pathlib import Path

from makefile_guard import target_block
from validation_record_source import assert_record_source_binding


ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "docs/validation/v0-2-0-package-build-evidence-validation-2026-06-25.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"
MAKEFILE = ROOT / "Makefile"
RELEASE_WORKFLOW = ROOT / ".github/workflows/release.yml"

SOURCE_SHORT = "977306e"
SOURCE_COMMIT = "977306eb19dbd4070a600bff36e6f52a1e26f776"
SOURCE_TREE = "6ad9746f54c75985ad1069b73926e1877bf7d848"
PYTHON_WHEEL_SHA256 = "5eb6eabb1d3e8a4d6d5f0280741a89103701c13706182e9004d5bf6ec2402ef4"
MACOS_ARTIFACT_SHA256 = "2a41e3457cc074394ad0e347c967d8e90e353a1179d8beaa2dda82c2725ad84a"
NPM_SHASUM = "42a0d591e6dd55ee0a9b6ed9976e455786b643c0"
NPM_INTEGRITY = (
    "sha512-98NfgYjTl49v+gahz+lrnOk3BDEvnDGYwHEIAWknksJIiwfZ7thzP0Q2WMZFJpwfVW1C/9oeccG5b5lbwmlFiA=="
)
GUARD_NAME = "test_v0_2_0_package_build_evidence.py"
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
    "pypi upload approved",
    "npm publish approved",
    "github release approved",
    "installable 0.2.0 wording approved",
    "release tag creation approved",
    "package tag creation approved",
    "hosted surfaces approved",
    "production-ready",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalized(path: Path) -> str:
    return re.sub(r"\s+", " ", read(path))


class V020PackageBuildEvidenceTests(unittest.TestCase):
    def test_record_is_source_bound_and_indexed(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)

        assert_record_source_binding(
            self,
            root=ROOT,
            raw_record=raw,
            normalized_record=record,
            validated_head=SOURCE_SHORT,
            source_label="v0.2.0 package/build",
            source_commit=SOURCE_COMMIT,
            source_tree=SOURCE_TREE,
        )

        for path in (VALIDATION_README, EXECUTION_STATUS, PUBLIC_RELEASE_CHECKLIST):
            text = normalized(path)
            self.assertIn(RECORD.name, text, str(path))
            self.assertIn("package/build", text.lower(), str(path))

    def test_record_captures_python_cli_and_npm_evidence(self) -> None:
        record = normalized(RECORD)

        for expected in (
            "python3 .github/scripts/test_release_artifact_workflow_prep.py",
            "cargo build --locked --release -p ethos-cli",
            "make python-surface-test PYTHON=python3",
            "npm test --prefix packages/npm/ethos-pdf",
            "Successfully built ethos_pdf-0.2.0-py3-none-any.whl",
            "Successfully installed ethos-pdf-0.2.0",
            "Name: ethos-pdf",
            "Version: 0.2.0",
            PYTHON_WHEEL_SHA256,
            MACOS_ARTIFACT_SHA256,
            "version_stdout: ethos 0.2.0",
            "missing_pdfium_exit_code: 12",
            "name: @docushell/ethos-pdf",
            "filename: docushell-ethos-pdf-0.2.0.tgz",
            NPM_SHASUM,
            NPM_INTEGRITY,
            "node packages/npm/ethos-pdf/bin/ethos-pdf.js --version: ethos 0.1.2",
        ):
            self.assertIn(expected, record)

    def test_npm_and_cross_platform_artifact_blockers_remain_explicit(self) -> None:
        record = normalized(RECORD)

        for expected in (
            "npm v0.2.0 artifact candidacy: BLOCKED by vendored ethos 0.1.2 payload",
            "Linux x64 CLI artifact evidence remains required before any two-platform GitHub Release artifact approval or npm vendor refresh decision.",
            "npm vendor refresh remains blocked until both v0.2.0 CLI artifact payloads exist.",
            "`npm publish` remains blocked.",
            "PyPI upload remains blocked.",
            "GitHub Release `v0.2.0` artifact upload remains blocked.",
            "Installable `0.2.0` public wording remains blocked.",
            "`ethos-doc` remains blocked.",
            "`ethos-rag` remains blocked.",
        ):
            self.assertIn(expected, record)

    def test_record_captures_historical_v0_2_workflow_smoke(self) -> None:
        record = normalized(RECORD)

        self.assertIn('`--expected-version "ethos 0.2.0"`', record)
        self.assertIn(
            'python3 .github/scripts/smoke_release_cli_artifact.py --expected-version "ethos 0.2.0" --target macos-arm64',
            record,
        )
        self.assertIn("version_stdout: ethos 0.2.0", record)
        self.assertNotIn('`--expected-version "ethos 0.1.2"`', record)

    def test_boundaries_private_paths_and_v0_2_release_prep_guard(self) -> None:
        raw = read(RECORD)
        lower = raw.lower()
        block = target_block("v0-2-release-prep")
        guard = f"$(PYTHON) .github/scripts/{GUARD_NAME}"
        dry_run_guard = (
            "$(PYTHON) .github/scripts/"
            "test_v0_2_0_ethos_doc_core_cargo_publish_dry_run_evidence.py"
        )
        claims = "$(PYTHON) .github/scripts/claims_gate.py"

        for forbidden in FORBIDDEN_APPROVALS:
            self.assertNotIn(forbidden, lower)
        for private in PRIVATE_PATH_MARKERS:
            self.assertNotIn(private, raw)
        self.assertIn(guard, block)
        self.assertLess(block.index(dry_run_guard), block.index(guard))
        self.assertLess(block.index(guard), block.index(claims))


if __name__ == "__main__":
    unittest.main()
