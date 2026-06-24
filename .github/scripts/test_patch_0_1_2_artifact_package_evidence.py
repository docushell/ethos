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

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from makefile_guard import target_block


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / ".github/scripts/package_publication_candidate_activation.py"
RECORD = ROOT / "docs/validation/patch-0-1-2-artifact-package-evidence-validation-2026-06-24.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"
PYPROJECT = ROOT / "pyproject.toml"
PY_INIT = ROOT / "python/ethos_pdf/__init__.py"
NPM_PACKAGE = ROOT / "packages/npm/ethos-pdf/package.json"

SOURCE_SHORT = "6f81938"
SOURCE_COMMIT = "6f819381e189e98f5aa3177deb52901c89447ab4"
SOURCE_TREE = "7cae3956d5d01aac1005b675332c97451df3cbb8"
VERSION = "0.1.2"
WHEEL = "ethos_pdf-0.1.2-py3-none-any.whl"
EXPECTED_CRATES = {
    "ethos-doc-core": "ethos-doc-core-0.1.2.crate",
    "ethos-verify": "ethos-verify-0.1.2.crate",
    "ethos-pdf": "ethos-pdf-0.1.2.crate",
}
EXPECTED_WHEEL_FILES = (
    "ethos_pdf/__init__.py",
    "ethos_pdf/_cli.py",
    "ethos_pdf-0.1.2.dist-info/METADATA",
    "ethos_pdf-0.1.2.dist-info/RECORD",
    "ethos_pdf-0.1.2.dist-info/WHEEL",
    "ethos_pdf-0.1.2.dist-info/licenses/LICENSE",
    "ethos_pdf-0.1.2.dist-info/licenses/NOTICE",
    "ethos_pdf-0.1.2.dist-info/top_level.txt",
)
FORBIDDEN = (
    "pypi upload approved",
    "pypi publication approved",
    "crates.io publication approved",
    "npm publication approved",
    "github release publication approved",
    "public installation approved",
    "public install wording approved",
    "vendor payload refreshed",
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


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args],
        cwd=ROOT,
        encoding="utf-8",
        stderr=subprocess.DEVNULL,
    ).strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(command: list[str], cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )


def run_candidate_activation() -> dict:
    result = run(["python3", str(SCRIPT), "--json"], ROOT)
    if result.returncode != 0:
        raise AssertionError(
            "candidate activation script failed\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return json.loads(result.stdout)


def should_ignore(_: str, names: list[str]) -> set[str]:
    ignored = {
        ".git",
        "target",
        "build",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        "ethos_pdf.egg-info",
    }
    return {name for name in names if name in ignored}


def build_python_wheel() -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="ethos-python-wheel-") as temp:
        workspace = Path(temp) / "ethos"
        out_dir = Path(temp) / "dist"
        install_dir = Path(temp) / "install"
        shutil.copytree(ROOT, workspace, ignore=should_ignore)

        build = run(
            [
                sys.executable,
                "-m",
                "build",
                "--wheel",
                "--outdir",
                str(out_dir),
            ],
            workspace,
        )
        if build.returncode != 0:
            raise AssertionError(
                "python wheel build failed\n"
                f"stdout:\n{build.stdout}\n"
                f"stderr:\n{build.stderr}"
            )

        wheel = out_dir / WHEEL
        if not wheel.is_file():
            raise AssertionError(f"missing expected wheel: {WHEEL}")

        install = run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--no-deps",
                "--force-reinstall",
                "--target",
                str(install_dir),
                str(wheel),
            ],
            workspace,
        )
        if install.returncode != 0:
            raise AssertionError(
                "python wheel install smoke failed\n"
                f"stdout:\n{install.stdout}\n"
                f"stderr:\n{install.stderr}"
            )

        env = dict(os.environ)
        env["PYTHONPATH"] = str(install_dir)
        smoke = run(
            [
                sys.executable,
                "-c",
                (
                    "import ethos_pdf; "
                    "print(ethos_pdf.__version__); "
                    "print(ethos_pdf.EthosCli.__name__); "
                    "print(ethos_pdf.EthosCommandError.__name__)"
                ),
            ],
            workspace,
            env=env,
        )
        if smoke.returncode != 0:
            raise AssertionError(
                "python wheel import smoke failed\n"
                f"stdout:\n{smoke.stdout}\n"
                f"stderr:\n{smoke.stderr}"
            )

        with zipfile.ZipFile(wheel) as archive:
            files = sorted(archive.namelist())
            metadata = archive.read("ethos_pdf-0.1.2.dist-info/METADATA").decode("utf-8")
            wheel_metadata = archive.read("ethos_pdf-0.1.2.dist-info/WHEEL").decode("utf-8")

        return {
            "wheel": wheel.name,
            "sha256": sha256(wheel),
            "files": files,
            "metadata": metadata,
            "wheel_metadata": wheel_metadata,
            "smoke_stdout": smoke.stdout.strip().splitlines(),
        }


class Patch012ArtifactPackageEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.candidate = run_candidate_activation()
        cls.wheel = build_python_wheel()

    def test_record_is_source_bound_and_indexed(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)
        readme = normalized(VALIDATION_README)

        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", raw)
        self.assertIn(f"Patch 0.1.2 artifact/package evidence source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Patch 0.1.2 artifact/package evidence source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))
        self.assertIn(RECORD.name, readme)
        self.assertIn("patch 0.1.2 artifact/package evidence validation", readme)

    def test_crate_candidate_artifacts_are_0_1_2_and_registry_equivalent_consumer_checks(self) -> None:
        candidate = self.candidate
        artifacts = {artifact["package"]: artifact for artifact in candidate["artifacts"]}

        self.assertEqual("pass", candidate["status"])
        self.assertEqual(VERSION, candidate["candidate_version"])
        self.assertEqual(["ethos-doc-core", "ethos-verify", "ethos-pdf"], candidate["candidate_packages"])
        self.assertEqual("pass", candidate["registry_equivalent_consumer_check"])
        self.assertFalse(candidate["package_publication_approved"])
        self.assertFalse(candidate["public_installation_approved"])
        self.assertEqual(set(EXPECTED_CRATES), set(artifacts))
        for package, crate_file in EXPECTED_CRATES.items():
            self.assertEqual(crate_file, artifacts[package]["crate_file"])
            self.assertRegex(artifacts[package]["sha256"], r"^[0-9a-f]{64}$")

    def test_python_wheel_candidate_is_0_1_2_and_importable(self) -> None:
        wheel = self.wheel

        self.assertEqual(WHEEL, wheel["wheel"])
        self.assertRegex(str(wheel["sha256"]), r"^[0-9a-f]{64}$")
        for expected in EXPECTED_WHEEL_FILES:
            self.assertIn(expected, wheel["files"])
        self.assertIn("Name: ethos-pdf", str(wheel["metadata"]))
        self.assertIn("Version: 0.1.2", str(wheel["metadata"]))
        self.assertIn("Requires-Python: >=3.8", str(wheel["metadata"]))
        self.assertIn("License-Expression: Apache-2.0", str(wheel["metadata"]))
        self.assertIn("Wheel-Version: 1.0", str(wheel["wheel_metadata"]))
        self.assertIn("Root-Is-Purelib: true", str(wheel["wheel_metadata"]))
        self.assertIn("Tag: py3-none-any", str(wheel["wheel_metadata"]))
        self.assertEqual(["0.1.2", "EthosCli", "EthosCommandError"], wheel["smoke_stdout"])

    def test_source_metadata_and_public_install_baseline_remain_split(self) -> None:
        self.assertIn('version = "0.1.2"', read(PYPROJECT))
        self.assertIn('__version__ = "0.1.2"', read(PY_INIT))
        self.assertEqual("0.1.2", json.loads(read(NPM_PACKAGE))["version"])

        for path in (EXECUTION_STATUS, PUBLIC_RELEASE_CHECKLIST):
            doc = normalized(path)
            self.assertIn(RECORD.name, doc, str(path))
            self.assertIn("public install baseline remains `0.1.1`", doc, str(path))
            self.assertIn("public installation wording remains blocked", doc, str(path))

    def test_record_keeps_publication_vendor_refresh_and_claim_boundaries_blocked(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)
        lower = record.lower()

        for expected in (
            "This record does not approve publishing any package.",
            "This record does not approve PyPI upload.",
            "This record does not approve crates.io publication.",
            "This record does not approve npm publication.",
            "This record does not approve GitHub Release artifact publication.",
            "This record does not refresh the checked-in npm vendor payload.",
            "public install baseline remains `0.1.1`",
            "Actual registry publication remains blocked",
            "GitHub Release artifact publication remains blocked",
            "npm vendor refresh remains blocked",
            "Public installation wording remains blocked",
            "PDFium remains caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`.",
        ):
            self.assertIn(expected, record)
        for forbidden in FORBIDDEN:
            self.assertNotIn(forbidden, lower)
        for marker in PRIVATE_PATH_MARKERS:
            self.assertNotIn(marker, raw)

    def test_release_candidate_prep_runs_this_guard_after_version_activation(self) -> None:
        block = target_block("release-candidate-prep")
        version_guard = "$(PYTHON) .github/scripts/test_patch_0_1_2_version_activation.py"
        evidence_guard = "$(PYTHON) .github/scripts/test_patch_0_1_2_artifact_package_evidence.py"
        first_public_guard = "$(PYTHON) .github/scripts/test_first_public_release_artifact_evidence.py"

        self.assertIn(evidence_guard, block)
        self.assertEqual(1, block.count(evidence_guard))
        self.assertLess(block.index(version_guard), block.index(evidence_guard))
        self.assertLess(block.index(evidence_guard), block.index(first_public_guard))


if __name__ == "__main__":
    unittest.main()
