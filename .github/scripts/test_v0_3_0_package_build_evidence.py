#!/usr/bin/env python3
#
# Copyright 2026 The Ethos maintainers
#
# Licensed under the Apache License, Version 2.0 (the "License");
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
from validation_record_source import assert_record_source_binding


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / ".github/scripts/package_publication_candidate_activation.py"
RECORD = ROOT / "docs/validation/v0-3-0-package-build-evidence-validation-2026-07-01.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"
MAKEFILE = ROOT / "Makefile"
PYPROJECT = ROOT / "pyproject.toml"
PY_INIT = ROOT / "python/ethos_pdf/__init__.py"
NPM_PACKAGE = ROOT / "packages/npm/ethos-pdf/package.json"

SOURCE_SHORT = "4b6d219"
SOURCE_COMMIT = "4b6d219df1757b6e4728c16c8023bee5c8cf8962"
SOURCE_TREE = "2920f830f92f8290c2bf4cc661874c2641499688"
VERSION = "0.3.0"
WHEEL = "ethos_pdf-0.3.0-py3-none-any.whl"
WHEEL_SHA256 = "9eb106deafcd1d9717e5e7b67dc9413180421aba25a5257266352d09540b3265"
EXPECTED_CRATES = {
    "ethos-doc-core": (
        "ethos-doc-core-0.3.0.crate",
        "7ba41a2ae299a53a4677153beaaec5ed486a07b5da08b2ef13974b9a0be141cb",
    ),
    "ethos-verify": (
        "ethos-verify-0.3.0.crate",
        "00f001455ca207e65aaf464551d3ba05945cda0b06e9e1036f49ac587accbb95",
    ),
    "ethos-pdf": (
        "ethos-pdf-0.3.0.crate",
        "c2f4f2ccb6de6e54cd3257597cd28e7f6dec2a6d22befbd230d2c4cf31931cfd",
    ),
}
EXPECTED_WHEEL_FILES = (
    "ethos_pdf/__init__.py",
    "ethos_pdf/_cli.py",
    "ethos_pdf-0.3.0.dist-info/METADATA",
    "ethos_pdf-0.3.0.dist-info/RECORD",
    "ethos_pdf-0.3.0.dist-info/WHEEL",
    "ethos_pdf-0.3.0.dist-info/licenses/LICENSE",
    "ethos_pdf-0.3.0.dist-info/licenses/NOTICE",
    "ethos_pdf-0.3.0.dist-info/top_level.txt",
)
FORBIDDEN = (
    "pypi upload approved",
    "pypi publication approved",
    "crates.io publication approved",
    "npm publication approved",
    "github release publication approved",
    "public installation approved",
    "public install wording approved",
    "installable 0.3.0 wording approved",
    "doc shell integration approved",
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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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
    with tempfile.TemporaryDirectory(prefix="ethos-v0-3-python-wheel-") as temp:
        workspace = Path(temp) / "ethos"
        out_dir = Path(temp) / "dist"
        install_dir = Path(temp) / "install"
        shutil.copytree(ROOT, workspace, ignore=should_ignore)

        env = dict(os.environ)
        env["SOURCE_DATE_EPOCH"] = "0"
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
            env=env,
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

        smoke_env = dict(os.environ)
        smoke_env["PYTHONPATH"] = str(install_dir)
        smoke = run(
            [
                sys.executable,
                "-c",
                (
                    "import ethos_pdf; "
                    "from ethos_pdf import EthosCli, proof_summary, app_answer_release_decision; "
                    "print(ethos_pdf.__version__); "
                    "print(EthosCli.__name__); "
                    "print(callable(proof_summary)); "
                    "print(callable(app_answer_release_decision)); "
                    "summary = {"
                    "'proof_status': 'verified',"
                    "'request_certified': True,"
                    "'reusable_grounded_check_ids': ['v0001'],"
                    "'needs_review_check_ids': [],"
                    "'proof_limitations': []"
                    "}; "
                    "decision = app_answer_release_decision("
                    "'What was revenue?',"
                    "summary,"
                    "[{"
                    "'id': 'claim-revenue',"
                    "'text': 'Revenue was $12.4M.',"
                    "'check_ids': ['v0001'],"
                    "'question_relevance': 'direct_answer',"
                    "'claim_type': 'source_fact'"
                    "}]"
                    "); "
                    "print(decision['app_status']); "
                    "print(decision['final_answer_claim_ids'][0])"
                ),
            ],
            workspace,
            env=smoke_env,
        )
        if smoke.returncode != 0:
            raise AssertionError(
                "python wheel import/helper smoke failed\n"
                f"stdout:\n{smoke.stdout}\n"
                f"stderr:\n{smoke.stderr}"
            )

        with zipfile.ZipFile(wheel) as archive:
            files = sorted(archive.namelist())
            metadata = archive.read("ethos_pdf-0.3.0.dist-info/METADATA").decode("utf-8")
            wheel_metadata = archive.read("ethos_pdf-0.3.0.dist-info/WHEEL").decode("utf-8")

        return {
            "wheel": wheel.name,
            "sha256": sha256(wheel),
            "files": files,
            "metadata": metadata,
            "wheel_metadata": wheel_metadata,
            "smoke_stdout": smoke.stdout.strip().splitlines(),
        }


class V030PackageBuildEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.candidate = run_candidate_activation()
        cls.wheel = build_python_wheel()

    def test_record_is_source_bound_and_indexed(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)

        assert_record_source_binding(
            self,
            root=ROOT,
            raw_record=raw,
            normalized_record=record,
            validated_head=SOURCE_SHORT,
            source_label="v0.3.0 package/build evidence",
            source_commit=SOURCE_COMMIT,
            source_tree=SOURCE_TREE,
        )
        for path in (VALIDATION_README, EXECUTION_STATUS, PUBLIC_RELEASE_CHECKLIST):
            text = normalized(path)
            self.assertIn(RECORD.name, text, str(path))
            self.assertIn("v0.3.0 package/build evidence", text.lower(), str(path))
            self.assertIn("installable `0.3.0` wording remains blocked", text.lower(), str(path))

    def test_rust_candidate_artifacts_are_0_3_0_and_registry_equivalent(self) -> None:
        candidate = self.candidate
        artifacts = {artifact["package"]: artifact for artifact in candidate["artifacts"]}

        self.assertEqual("pass", candidate["status"])
        self.assertEqual(VERSION, candidate["candidate_version"])
        self.assertEqual(["ethos-doc-core", "ethos-verify", "ethos-pdf"], candidate["candidate_packages"])
        self.assertEqual("pass", candidate["registry_equivalent_consumer_check"])
        self.assertFalse(candidate["package_publication_approved"])
        self.assertFalse(candidate["public_installation_approved"])
        self.assertEqual(set(EXPECTED_CRATES), set(artifacts))
        for package, (crate_file, crate_hash) in EXPECTED_CRATES.items():
            self.assertEqual(crate_file, artifacts[package]["crate_file"])
            self.assertEqual(crate_hash, artifacts[package]["sha256"])

    def test_python_wheel_candidate_is_0_3_0_and_helper_smoke_passes(self) -> None:
        wheel = self.wheel

        self.assertEqual(WHEEL, wheel["wheel"])
        self.assertEqual(WHEEL_SHA256, wheel["sha256"])
        for expected in EXPECTED_WHEEL_FILES:
            self.assertIn(expected, wheel["files"])
        self.assertIn("Name: ethos-pdf", str(wheel["metadata"]))
        self.assertIn("Version: 0.3.0", str(wheel["metadata"]))
        self.assertIn("Requires-Python: >=3.8", str(wheel["metadata"]))
        self.assertIn("License-Expression: Apache-2.0", str(wheel["metadata"]))
        self.assertIn("Wheel-Version: 1.0", str(wheel["wheel_metadata"]))
        self.assertIn("Root-Is-Purelib: true", str(wheel["wheel_metadata"]))
        self.assertIn("Tag: py3-none-any", str(wheel["wheel_metadata"]))
        self.assertEqual(
            ["0.3.0", "EthosCli", "True", "True", "certified", "claim-revenue"],
            wheel["smoke_stdout"],
        )

    def test_source_metadata_and_public_install_baseline_remain_split(self) -> None:
        self.assertIn('version = "0.3.0"', read(PYPROJECT))
        self.assertIn('__version__ = "0.3.0"', read(PY_INIT))
        self.assertEqual("0.2.1", json.loads(read(NPM_PACKAGE))["version"])

    def test_record_keeps_publication_artifact_npm_and_docushell_boundaries_blocked(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)
        lower = record.lower()

        for expected in (
            WHEEL_SHA256,
            "ethos-doc-core-0.3.0.crate",
            "ethos-verify-0.3.0.crate",
            "ethos-pdf-0.3.0.crate",
            "This record does not approve `cargo publish`.",
            "This record does not approve PyPI upload.",
            "This record does not approve `npm publish`.",
            "This record does not approve GitHub Release artifact publication.",
            "This record does not approve installable `0.3.0` public wording.",
            "This record does not approve DocuShell integration.",
            "CLI artifact evidence remains out of scope for this record.",
            "npm package evidence remains out of scope for this record.",
        ):
            self.assertIn(expected, record)
        for forbidden in FORBIDDEN:
            self.assertNotIn(forbidden, lower)
        for marker in PRIVATE_PATH_MARKERS:
            self.assertNotIn(marker, raw)

    def test_v0_3_release_prep_runs_package_evidence_guard_before_claims(self) -> None:
        block = target_block("v0-3-release-prep")
        activation_guard = "$(PYTHON) .github/scripts/test_v0_3_0_version_activation.py"
        evidence_guard = "$(PYTHON) .github/scripts/test_v0_3_0_package_build_evidence.py"
        claims_guard = "$(PYTHON) .github/scripts/claims_gate.py"

        self.assertIn(evidence_guard, block)
        self.assertEqual(1, block.count(evidence_guard))
        self.assertLess(block.index(activation_guard), block.index(evidence_guard))
        self.assertLess(block.index(evidence_guard), block.index(claims_guard))


if __name__ == "__main__":
    unittest.main()
