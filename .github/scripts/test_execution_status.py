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

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXECUTION_STATUS = ROOT / "docs/execution-status.md"


def status_text() -> str:
    return EXECUTION_STATUS.read_text(encoding="utf-8")


class ExecutionStatusTests(unittest.TestCase):
    def test_status_is_scoped_to_internal_continuation(self) -> None:
        text = status_text()

        self.assertIn(
            "Status: v0.3.0 Rust library crates `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` "
            "are live on crates.io, and the Python `ethos-pdf` wheel is live on PyPI.",
            text,
        )
        self.assertIn(
            "v0.2.0 remains the public CLI artifact baseline with GitHub Release `v0.2.0` "
            "macOS arm64/Linux x64 artifacts, and npm remains `@docushell/ethos-pdf@0.2.1`",
            text,
        )
        self.assertIn("Public `0.3.0` install wording", text)
        self.assertIn("GitHub Release artifact upload", text)
        self.assertIn("npm publication/alignment", text)
        self.assertIn("DocuShell integration remain blocked", text)
        self.assertIn(
            "npm `@docushell/ethos-pdf@0.2.0` is deprecated because it shipped stale CLI binaries",
            text,
        )
        self.assertIn("Internal Milestone D source-only closeout remains complete", text)
        self.assertIn(
            "Ethos is pre-alpha. It verifies whether AI citations are grounded in document "
            "evidence across native Ethos JSON and supported foreign parser outputs.",
            text,
        )
        self.assertIn("docs/validation/milestone-d-final-closeout-validation-2026-06-19.md", text)
        self.assertIn("docs/milestone-d-verify-citations-contract.md", text)
        self.assertIn("docs/milestone-d-claim-kind-boundary-contract.md", text)
        self.assertIn("docs/milestone-d-grounding-source-contract.md", text)
        self.assertIn("docs/milestone-d-capability-downgrade-contract.md", text)
        self.assertIn("docs/milestone-d-opendataloader-adapter-shape-contract.md", text)
        self.assertIn("docs/milestone-d-crop-element-contract.md", text)
        self.assertIn("docs/milestone-d-crop-element-surface-shape-contract.md", text)
        self.assertIn("docs/milestone-d-sandbox-subprocess-contract.md", text)
        self.assertNotIn("Status: Pre-alpha / Milestone B entry.", text)
        self.assertNotIn("v1 contract prep has started", text)

    def test_internal_check_command_is_documented(self) -> None:
        text = status_text()

        self.assertIn("make milestone-b-internal-checks", text)
        self.assertIn("make milestone-c-internal-checks", text)
        self.assertIn("make milestone-d-verify-citations-contract", text)
        self.assertIn("make milestone-d-claim-kind-boundary-contract", text)
        self.assertIn("make milestone-d-grounding-source-contract", text)
        self.assertIn("make milestone-d-capability-downgrade-contract", text)
        self.assertIn("make milestone-d-opendataloader-adapter-shape-contract", text)
        self.assertIn("make milestone-d-crop-element-contract", text)
        self.assertIn("make milestone-d-crop-element-surface-shape-contract", text)
        self.assertIn("make milestone-d-sandbox-subprocess-contract", text)
        self.assertIn("make milestone-d-internal-contracts", text)
        self.assertIn("make milestone-e-prep", text)
        self.assertIn("docs/validation/milestone-d-contract-closeout-validation-2026-06-19.md", text)
        self.assertIn("docs/validation/milestone-d-final-closeout-validation-2026-06-19.md", text)
        self.assertIn("docs/validation/milestone-e-final-closeout-validation-2026-06-20.md", text)
        self.assertIn("Full 13-D exit is complete for the current source-only pre-alpha scope", text)
        self.assertIn("CI has a static guard for that target's command wiring", text)

    def test_public_posture_boundary_remains_explicit(self) -> None:
        text = status_text()

        self.assertIn(
            "Public language may use this exact approved sentence on the current source, Rust crate, Python wheel, "
            "npm package, macOS arm64 CLI artifact, and Linux x64 CLI artifact evaluation surfaces",
            text,
        )
        self.assertIn(
            "Ethos is a deterministic document evidence layer for source-grounded verification and "
            "citation checking across native Ethos JSON and supported foreign parser outputs. The current "
            "beta includes the GitHub source repository, Rust library crates `ethos-doc-core`, "
            "`ethos-verify`, and `ethos-pdf` at `0.1.2`, the Python `ethos-pdf` wheel at `0.1.2`, "
            "the npm `@docushell/ethos-pdf@0.1.2` package, and GitHub Release `v0.1.2` macOS "
            "arm64/Linux x64 CLI artifacts. PDFium-backed commands use caller-provided PDFium through "
            "`ETHOS_PDFIUM_LIBRARY_PATH`.",
            text,
        )
        self.assertIn(
            "v0.3.0 Rust library crates `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` are live on crates.io",
            text,
        )
        self.assertIn("the Python `ethos-pdf` wheel is live on PyPI", text)
        self.assertIn("v0.2.0 remains the public CLI artifact baseline", text)
        self.assertIn("npm remains `@docushell/ethos-pdf@0.2.1`", text)
        self.assertIn("GitHub Release `v0.2.0` macOS arm64/Linux x64 artifacts", text)
        self.assertIn("docs/validation/v0-3-0-publication-closeout-validation-2026-07-01.md", text)
        self.assertIn("ethos-doc-core", text)
        self.assertIn("ethos-verify", text)
        self.assertIn("ethos-pdf", text)
        self.assertIn(
            "Patch `0.1.1` closeout records supersede those historical blockers only for the approved "
            "source, Rust crate, Python wheel, npm package, macOS arm64 CLI artifact, and Linux x64 CLI "
            "artifact evaluation surfaces.",
            text,
        )
        self.assertIn(
            "Hosted surfaces, Windows packaged artifacts, bundled project-maintained PDFium builds, "
            "`ethos-doc`, and `ethos-rag` remain blocked.",
            text,
        )
        self.assertIn("All wording beyond that sentence still requires claim-audit", text)
        self.assertIn("Closed for the exact approved pre-alpha sentence only", text)
        self.assertIn("milestone-e-public-beta-source-only-approval-validation-2026-06-20.md", text)
        self.assertIn("Approved Next-Step Sequence", text)
        self.assertIn("Close H1: closed for public-safe evidence acceptance only", text)
        self.assertIn("H1 is closed for public-safe evidence acceptance only", text)
        self.assertIn("Close H2: closed for the exact source-snapshot candidate", text)
        self.assertIn("docs/validation/h2-source-snapshot-closeout-660f268-2026-06-20.md", text)
        self.assertIn("Run release-candidate validation gates", text)
        self.assertIn("does not approve public benchmark claims", text)
        self.assertIn("Post-D blockers/future work", text)
        self.assertIn("these are not D closeout requirements", text)
        self.assertIn("product-differentiating path remains verification and grounding first", text)


if __name__ == "__main__":
    unittest.main()
