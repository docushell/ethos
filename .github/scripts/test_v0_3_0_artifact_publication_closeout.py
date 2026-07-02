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
RECORD = ROOT / (
    "docs/validation/"
    "v0-3-0-artifact-publication-closeout-validation-2026-07-02.md"
)
DECISION = ROOT / (
    "docs/validation/"
    "v0-3-0-artifact-publication-approval-decision-validation-2026-07-01.md"
)
REQUEST = ROOT / (
    "docs/validation/"
    "v0-3-0-artifact-publication-approval-request-validation-2026-07-01.md"
)
DRAFT_EVIDENCE = ROOT / "docs/validation/v0-3-0-draft-artifact-evidence-validation-2026-07-01.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"
RELEASE_PREP = ROOT / "docs/v0-3-0-release-prep.md"
MAKEFILE = ROOT / "Makefile"

SOURCE_SHORT = "4aa8b8b"
SOURCE_COMMIT = "4aa8b8bf25685f9cd6691669ea791a38ecc1a84a"
SOURCE_TREE = "150a7262277e810c5b6253a9b7f403c0d286a191"
APPROVAL_DECISION_SOURCE_COMMIT = "a20b42a7927052f727fcaaa585a7a050aec02abe"
REQUEST_SOURCE_COMMIT = "d6496e82e613e653edc197db4cf4153271d131dc"
ARTIFACT_SOURCE_COMMIT = "7287358475a96e827d536f0d2d250a1c2961ba84"
RUN_URL = "https://github.com/docushell/ethos/actions/runs/28531102130"
RELEASE_URL = "https://github.com/docushell/ethos/releases/tag/v0.3.0"
MACOS_SHA256 = "efb163f140bf4afffd1caeb396f79e42f484591c3e90a86810ca6c0f0c209c96"
LINUX_SHA256 = "b549ba5968e04b7679a8d3e879cd45d27f3e9a6fd226eee5c270a4e4f5c01405"

API_DIGESTS = (
    "sha256:efb163f140bf4afffd1caeb396f79e42f484591c3e90a86810ca6c0f0c209c96",
    "sha256:f86a3d1b556e4e0f601c4e9cf06917b522f900717ab1d2e33eb46faf46bf81e9",
    "sha256:13e944876ad34ecbb07dc66ff8887135472f17f2baf72864a5edbae21a335845",
    "sha256:78ad54e090e661ff1e192dd471ac49190a1afb94c33405d7b74312d8724a3608",
    "sha256:b549ba5968e04b7679a8d3e879cd45d27f3e9a6fd226eee5c270a4e4f5c01405",
    "sha256:ecd6785bc8a8c952df31ef99d4e2f612c4a28590f9bdaa67c22eae09775411ed",
    "sha256:cbfe3c0494043f3a4fa3b0d300f6bd8cec222dd24a93a7282b8c0cabf42eec2a",
    "sha256:1198fde1293ae32eb1b016b789e191d0ef93a86e3e9bc0c91cf3719fe1917e34",
)
APPROVED_WORDING = (
    "Ethos v0.3.0 CLI artifacts for macOS arm64 and Linux x64 are requested for GitHub "
    "Release evaluation with caller-provided PDFium. Rust crates `ethos-doc-core`, "
    "`ethos-verify`, and `ethos-pdf` at `0.3.0`, plus the Python `ethos-pdf` wheel at "
    "`0.3.0`, are already live. npm alignment/publication, public `0.3.0` install wording, "
    "release/package tags, DocuShell integration, hosted surfaces, production positioning, "
    "Windows packaged artifacts, bundled project-maintained PDFium builds, `ethos-doc`, "
    "`ethos-rag`, public benchmark reports, public benchmark claims, and speed, footprint, "
    "parser-quality, table-quality, or production claims remain blocked."
)
FORBIDDEN_SCOPE_EXPANSION = (
    "npm vendor refresh approved",
    "npm publication approved",
    "package tag creation approved",
    "public installation wording approved",
    "public install wording approved",
    "installable 0.3.0 wording approved",
    "docushell integration approved",
    "production-ready",
    "hosted surfaces approved",
    "windows packaged artifacts approved",
    "bundled pdfium approved",
    "public benchmark claims approved",
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


class V030ArtifactPublicationCloseoutTests(unittest.TestCase):
    def test_record_is_source_bound_and_links_evidence(self) -> None:
        raw = read(RECORD)
        text = normalized(RECORD)

        assert_record_source_binding(
            self,
            root=ROOT,
            raw_record=raw,
            normalized_record=text,
            validated_head=SOURCE_SHORT,
            source_label="v0.3.0 artifact publication closeout",
            source_commit=SOURCE_COMMIT,
            source_tree=SOURCE_TREE,
        )
        for expected in (
            DECISION.name,
            REQUEST.name,
            DRAFT_EVIDENCE.name,
            f"Approval decision source commit accepted before publication: `{APPROVAL_DECISION_SOURCE_COMMIT}`",
            f"Approval request source commit accepted before publication: `{REQUEST_SOURCE_COMMIT}`",
            f"Artifact workflow source commit accepted before publication: `{ARTIFACT_SOURCE_COMMIT}`",
            RUN_URL,
            RELEASE_URL,
        ):
            self.assertIn(expected, text)

    def test_release_metadata_and_exact_published_assets_are_recorded(self) -> None:
        text = normalized(RECORD)

        for expected in (
            "Status: **v0.3.0 GitHub Release artifact publication complete**",
            "GitHub Release tag: `v0.3.0`",
            "Release name: `Release v0.3.0`",
            "Release draft status: `false`",
            "Release prerelease status: `false`",
            f"Release targetCommitish display value: `{SOURCE_COMMIT}`",
            f"Tag target: `{SOURCE_COMMIT}`",
            "ethos-macos-arm64.tar.gz",
            "ethos-macos-arm64.tar.gz.sha256",
            "ethos-macos-arm64.inventory.json",
            "ethos-macos-arm64.smoke.json",
            "ethos-linux-x64.tar.gz",
            "ethos-linux-x64.tar.gz.sha256",
            "ethos-linux-x64.inventory.json",
            "ethos-linux-x64.smoke.json",
            MACOS_SHA256,
            LINUX_SHA256,
        ):
            self.assertIn(expected, text)
        for digest in API_DIGESTS:
            self.assertIn(digest, text)

    def test_sidecar_payload_release_wording_and_pdfium_posture(self) -> None:
        text = normalized(RECORD)
        wording_record = re.sub(r"\s+", " ", read(RECORD).replace("> ", ""))

        for expected in (
            "schema `ethos.release_artifact_inventory.v1`, target `macos-arm64`, status `draft_not_release_ready`, publication `blocked`",
            "schema `ethos.release_artifact_smoke.v1`, target `macos-arm64`, version `ethos 0.3.0`",
            "schema `ethos.release_artifact_inventory.v1`, target `linux-x64`, status `draft_not_release_ready`, publication `blocked`",
            "schema `ethos.release_artifact_smoke.v1`, target `linux-x64`, version `ethos 0.3.0`",
            "`LICENSE`",
            "`NOTICE`",
            "`ethos`",
            "`pdfium-manual-setup.md`",
            "missing-PDFium guidance preserved the caller-provided PDFium posture",
            "PDFium remains caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`",
        ):
            self.assertIn(expected, text)
        self.assertIn(APPROVED_WORDING, wording_record)

    def test_retains_blockers_public_path_hygiene_and_install_baseline(self) -> None:
        raw = read(RECORD)
        lower = normalized(RECORD).lower()

        for expected in (
            "`packages/npm/ethos-pdf/vendor/manifest.json` must not be refreshed",
            "The public install baseline remains current published `0.2.0` Rust/Python and `0.2.1` npm",
            "README installation examples remain unchanged",
            "npm vendor refresh remains blocked",
            "npm publication remains blocked",
            "Package tag creation remains blocked",
            "Public installation wording remains blocked",
            "DocuShell integration remains blocked",
            "Hosted surfaces remain blocked",
            "Production positioning remains blocked",
            "Windows packaged artifacts remain blocked",
            "Bundled project-maintained PDFium builds remain blocked",
            "Public benchmark reports remain blocked",
            "Public benchmark claims remain blocked",
            "`ethos-doc` remains blocked",
            "`ethos-rag` remains blocked",
            "No additional GitHub Release targets are approved by this closeout.",
        ):
            self.assertIn(expected, raw)
        for phrase in FORBIDDEN_SCOPE_EXPANSION:
            self.assertNotIn(phrase, lower)
        for marker in PRIVATE_PATH_MARKERS:
            self.assertNotIn(marker, raw)

    def test_record_is_indexed_statused_and_wired_after_decision_guard(self) -> None:
        readme = normalized(VALIDATION_README)
        execution = normalized(EXECUTION_STATUS)
        checklist = normalized(PUBLIC_RELEASE_CHECKLIST)
        release_prep = normalized(RELEASE_PREP)
        block = target_block("v0-3-release-prep")
        decision_guard = "$(PYTHON) .github/scripts/test_v0_3_0_artifact_publication_approval_decision.py"
        closeout_guard = "$(PYTHON) .github/scripts/test_v0_3_0_artifact_publication_closeout.py"
        public_surface_guard = "$(PYTHON) .github/scripts/test_public_surface_posture.py"

        for text in (readme, execution, checklist, release_prep):
            self.assertIn(RECORD.name, text)
            self.assertIn("v0.3.0 artifact publication closeout", text.lower())
            self.assertIn("GitHub Release `v0.3.0`", text)
            self.assertIn("npm vendor refresh", text)
            self.assertIn("public install wording", text)
        self.assertIn("GitHub Release artifact upload remains blocked", execution)
        self.assertIn(closeout_guard, block)
        self.assertEqual(1, read(MAKEFILE).count(closeout_guard))
        self.assertLess(block.index(decision_guard), block.index(closeout_guard))
        self.assertLess(block.index(closeout_guard), block.index(public_surface_guard))


if __name__ == "__main__":
    unittest.main()
