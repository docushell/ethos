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
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/release.yml"
SMOKE_SCRIPT = ROOT / ".github/scripts/smoke_release_cli_artifact.py"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class ReleaseArtifactWorkflowPrepTests(unittest.TestCase):
    def test_workflow_generates_draft_artifacts_without_publication(self) -> None:
        text = read(WORKFLOW)

        self.assertIn("cli-draft-artifacts", text)
        self.assertIn("macos-arm64", text)
        self.assertIn("linux-x64", text)
        self.assertIn("windows-verify-draft-artifact", text)
        self.assertIn("windows-x64", text)
        self.assertIn("cargo build --locked --release -p ethos-cli", text)
        self.assertIn("build-windows-verify-candidate.py", text)
        self.assertIn("Windows candidate archives differ", text)
        self.assertIn("write_release_artifact_inventory.py", text)
        self.assertIn("smoke_release_cli_artifact.py", text)
        self.assertIn('--expected-version "ethos 0.4.0"', text)
        self.assertIn("--target \"${{ matrix.artifact_target }}\"", text)
        self.assertIn("*.smoke.json", text)
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
            "test_python_public_api_policy.py",
            "test_npm_binary_package_scaffold.py",
            "test_pdfium_manual_setup_contract.py",
            "test_windows_verify_candidate.py",
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
            self.assertFalse(data["pdfium_included"])
            self.assertEqual("cli-caller-provided-pdfium", data["artifact_scope"])

    def test_inventory_writer_and_validator_accept_windows_verify_only_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            artifact = root / "ethos-windows-x64.zip"
            checksum = root / "ethos-windows-x64.zip.sha256"
            inventory = root / "ethos-windows-x64.inventory.json"
            artifact.write_bytes(b"draft Windows artifact bytes")
            digest = subprocess.check_output(
                [
                    "python3",
                    "-c",
                    "import hashlib; print(hashlib.sha256(b'draft Windows artifact bytes').hexdigest())",
                ],
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
                    "windows-x64",
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
            self.assertEqual("verify-only", data["artifact_scope"])
            self.assertFalse(data["pdfium_included"])
            self.assertIn("VERIFY-QUICKSTART.txt", data["required_notices"])

    def test_release_artifact_smoke_checks_version_help_and_missing_pdfium(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            artifact = Path(temp) / "ethos-linux-x64"
            artifact.mkdir()
            for name in ("LICENSE", "NOTICE", "pdfium-manual-setup.md"):
                (artifact / name).write_text(f"{name}\n", encoding="utf-8")
            ethos = artifact / "ethos"
            ethos.write_text(
                """#!/usr/bin/env python3
import sys
if sys.argv[1:] == ["--version"]:
    print("ethos 0.1.1")
    raise SystemExit(0)
if sys.argv[1:] == ["--help"]:
    print("doc rag security verify fingerprint")
    raise SystemExit(0)
if sys.argv[1:3] == ["doc", "parse"]:
    print(
        "PDFium not found: set ETHOS_PDFIUM_LIBRARY_PATH to the caller-provided PDFium dynamic library path. Run ethos doctor for setup diagnostics, run ethos doctor --require-pdfium after setting it, and see docs/pdfium-manual-setup.md.",
        file=sys.stderr,
    )
    raise SystemExit(12)
raise SystemExit(2)
""",
                encoding="utf-8",
            )
            ethos.chmod(0o755)

            env = dict(os.environ)
            env["ETHOS_PDFIUM_LIBRARY_PATH"] = "/must/be/cleared/by/smoke"
            smoke = artifact.with_suffix(".smoke.json")
            subprocess.check_call(
                [
                    "python3",
                    str(SMOKE_SCRIPT),
                    "--artifact-dir",
                    str(artifact),
                    "--expected-version",
                    "ethos 0.1.1",
                    "--target",
                    "linux-x64",
                    "--out",
                    str(smoke),
                ],
                cwd=ROOT,
                env=env,
            )
            evidence = json.loads(smoke.read_text(encoding="utf-8"))
            self.assertEqual("ethos.release_artifact_smoke.v1", evidence["schema"])
            self.assertEqual("linux-x64", evidence["target"])
            self.assertEqual("ethos 0.1.1", evidence["version_stdout"])
            self.assertEqual(12, evidence["missing_pdfium_exit_code"])
            self.assertIn("ETHOS_PDFIUM_LIBRARY_PATH", evidence["missing_pdfium_message"])

    def test_windows_smoke_verifies_fixture_twice_and_keeps_pdfium_absent(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            artifact = Path(temp) / "ethos-windows-x64"
            (artifact / "verify-example").mkdir(parents=True)
            for name in (
                "LICENSE",
                "NOTICE",
                "PDFIUM-MANUAL-SETUP.md",
                "VERIFY-QUICKSTART.txt",
                "verify-example/document.json",
                "verify-example/citations.json",
            ):
                (artifact / name).write_text(f"{name}\n", encoding="utf-8")
            ethos = artifact / "ethos.exe"
            ethos.write_text(
                """#!/usr/bin/env python3
import sys
if sys.argv[1:] == ["--version"]:
    print("ethos 0.3.0")
    raise SystemExit(0)
if sys.argv[1:] == ["--help"]:
    print("doc rag security verify fingerprint")
    raise SystemExit(0)
if sys.argv[1:3] == ["doc", "parse"]:
    print(
        "PDFium not found: set ETHOS_PDFIUM_LIBRARY_PATH to the caller-provided PDFium dynamic library path. Run ethos doctor for setup diagnostics, run ethos doctor --require-pdfium after setting it, and see docs/pdfium-manual-setup.md.",
        file=sys.stderr,
    )
    raise SystemExit(12)
if sys.argv[1:2] == ["verify"]:
    print('{"gate_passed":true}')
    raise SystemExit(0)
raise SystemExit(2)
""",
                encoding="utf-8",
            )
            ethos.chmod(0o755)
            smoke = artifact.with_suffix(".smoke.json")
            subprocess.check_call(
                [
                    "python3",
                    str(SMOKE_SCRIPT),
                    "--artifact-dir",
                    str(artifact),
                    "--expected-version",
                    "ethos 0.3.0",
                    "--target",
                    "windows-x64",
                    "--out",
                    str(smoke),
                ],
                cwd=ROOT,
            )
            evidence = json.loads(smoke.read_text(encoding="utf-8"))
            self.assertEqual("verify-only", evidence["artifact_scope"])
            self.assertEqual(0, evidence["verification_exit_code"])
            self.assertEqual(12, evidence["missing_pdfium_exit_code"])
            self.assertEqual(64, len(evidence["verification_stdout_sha256"]))

if __name__ == "__main__":
    unittest.main()
