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

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/release.yml"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class ReleaseArtifactWorkflowPrepTests(unittest.TestCase):
    def test_workflow_generates_draft_artifacts_without_publication(self) -> None:
        text = read(WORKFLOW)

        self.assertIn("cli-draft-artifacts", text)
        self.assertIn("macos-arm64", text)
        self.assertIn("linux-x64", text)
        self.assertIn("cargo build --locked --release -p ethos-cli", text)
        self.assertIn("write_release_artifact_inventory.py", text)
        self.assertIn("validate_release_artifact_inventory.py", text)
        self.assertIn("actions/upload-artifact@v4", text)
        self.assertNotIn("gh release create", text)
        self.assertNotIn("pypa/gh-action-pypi-publish", text)
        self.assertNotIn("npm publish", text)

    def test_preflight_runs_release_scope_guards_before_artifacts(self) -> None:
        text = read(WORKFLOW)

        preflight_index = text.index("preflight:")
        artifact_index = text.index("cli-draft-artifacts:")
        self.assertLess(preflight_index, artifact_index)
        for guard in (
            "test_public_surface_posture.py",
            "claims_gate.py",
            "test_first_public_release_scope_decision.py",
            "test_python_public_api_policy.py",
            "test_npm_binary_package_scaffold.py",
            "test_pdfium_manual_setup_contract.py",
        ):
            self.assertIn(guard, text)

    def test_inventory_writer_and_validator_accept_draft_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            artifact = root / "ethos-linux-x64.tar.gz"
            checksum = root / "ethos-linux-x64.tar.gz.sha256"
            inventory = root / "ethos-linux-x64.inventory.json"
            artifact.write_bytes(b"draft artifact bytes")
            digest = subprocess.check_output(
                ["python3", "-c", "import hashlib; print(hashlib.sha256(b'draft artifact bytes').hexdigest())"],
                encoding="utf-8",
            ).strip()
            checksum.write_text(f"{digest}  {artifact.name}\n", encoding="utf-8")

            subprocess.check_call(
                [
                    "python3",
                    ".github/scripts/write_release_artifact_inventory.py",
                    "--artifact",
                    str(artifact),
                    "--checksum",
                    str(checksum),
                    "--target",
                    "linux-x64",
                    "--out",
                    str(inventory),
                ],
                cwd=ROOT,
            )
            subprocess.check_call(
                ["python3", ".github/scripts/validate_release_artifact_inventory.py", str(inventory)],
                cwd=ROOT,
            )

            data = json.loads(inventory.read_text(encoding="utf-8"))
            self.assertEqual("draft_not_release_ready", data["status"])
            self.assertEqual("blocked", data["publication"])
            self.assertEqual("caller-provided", data["pdfium_policy"])


if __name__ == "__main__":
    unittest.main()
