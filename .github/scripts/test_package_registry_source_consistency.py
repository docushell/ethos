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

from __future__ import annotations

import json
import re
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SEMVER = r"[0-9]+\.[0-9]+\.[0-9]+"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def python_project_version(root: Path) -> str:
    match = re.search(rf'^version\s*=\s*"({SEMVER})"\s*$', read(root / "pyproject.toml"), re.MULTILINE)
    if match is None:
        raise ValueError("pyproject.toml has no exact project version")
    return match.group(1)


def validate_registry_surfaces(root: Path) -> list[str]:
    failures: list[str] = []
    try:
        python_version = python_project_version(root)
    except (OSError, ValueError) as error:
        failures.append(str(error))
        return failures

    try:
        npm_package = json.loads(read(root / "packages/npm/ethos-pdf/package.json"))
        npm_name = npm_package["name"]
        npm_version = npm_package["version"]
    except (OSError, json.JSONDecodeError, KeyError) as error:
        failures.append(f"invalid npm package metadata: {error}")
        return failures

    if not re.fullmatch(SEMVER, str(npm_version)):
        failures.append(f"npm package version is not exact semver: {npm_version}")
    try:
        vendor_manifest = json.loads(read(root / "packages/npm/ethos-pdf/vendor/manifest.json"))
        cli_version = vendor_manifest["cli_version"]
    except (OSError, json.JSONDecodeError, KeyError) as error:
        failures.append(f"invalid npm vendor manifest: {error}")
        return failures
    if not re.fullmatch(SEMVER, str(cli_version)):
        failures.append(f"vendor CLI version is not exact semver: {cli_version}")

    python_surfaces = (
        root / "python/README.md",
        root / "python/QUICKSTART.md",
    )
    expected_python_install = f"python3 -m pip install ethos-pdf=={python_version}"
    for path in python_surfaces:
        try:
            text = read(path)
        except OSError as error:
            failures.append(f"missing Python registry surface {path.relative_to(root)}: {error}")
            continue
        installs = re.findall(rf"python3 -m pip install ethos-pdf==({SEMVER})", text)
        if installs != [python_version]:
            failures.append(
                f"{path.relative_to(root)} must contain exactly one current install command "
                f"({expected_python_install}); found versions {installs}"
            )
        if "published evaluation wheel" not in text:
            failures.append(f"{path.relative_to(root)} does not identify the install as published")

    npm_surfaces = (
        root / "packages/npm/ethos-pdf/README.md",
        root / "packages/npm/ethos-pdf/QUICKSTART.md",
    )
    expected_publication = f"The current published npm package is `{npm_name}@{npm_version}`."
    expected_binary_version = f"Its vendored CLI binaries report `ethos {cli_version}`."
    expected_npm_install = f"npm install -g {npm_name}@{npm_version}"
    forbidden_postures = (
        re.compile(r"source package candidate", re.IGNORECASE),
        re.compile(r"publication[^.\n]*remain(?:s)? blocked", re.IGNORECASE),
        re.compile(r"current published npm package remains", re.IGNORECASE),
    )
    for path in npm_surfaces:
        try:
            text = read(path)
        except OSError as error:
            failures.append(f"missing npm registry surface {path.relative_to(root)}: {error}")
            continue
        normalized = re.sub(r"\s+", " ", text)
        if expected_publication not in normalized:
            failures.append(
                f"{path.relative_to(root)} is missing current-publication wording: "
                f"{expected_publication}"
            )
        if expected_binary_version not in normalized:
            failures.append(
                f"{path.relative_to(root)} is missing CLI version wording: {expected_binary_version}"
            )
        reported_versions = re.findall(rf"`ethos ({SEMVER})`", text)
        if reported_versions != [cli_version]:
            failures.append(
                f"{path.relative_to(root)} must report only CLI version {cli_version}; "
                f"found {reported_versions}"
            )
        for pattern in forbidden_postures:
            if pattern.search(text):
                failures.append(
                    f"{path.relative_to(root)} retains stale publication posture: {pattern.pattern}"
                )

    try:
        npm_quickstart = read(npm_surfaces[1])
    except OSError:
        npm_quickstart = ""
    installs = re.findall(
        rf"npm install -g {re.escape(str(npm_name))}@({SEMVER})", npm_quickstart
    )
    if installs != [npm_version]:
        failures.append(
            "packages/npm/ethos-pdf/QUICKSTART.md must contain exactly one current install "
            f"command ({expected_npm_install}); found versions {installs}"
        )

    return failures


def write_fixture(
    root: Path,
    *,
    python_version: str = "0.4.0",
    npm_version: str = "0.3.1",
    cli_version: str = "0.3.0",
) -> None:
    (root / "python").mkdir(parents=True)
    (root / "packages/npm/ethos-pdf/vendor").mkdir(parents=True)
    (root / "pyproject.toml").write_text(
        f'[project]\nname = "ethos-pdf"\nversion = "{python_version}"\n', encoding="utf-8"
    )
    (root / "packages/npm/ethos-pdf/package.json").write_text(
        json.dumps({"name": "@docushell/ethos-pdf", "version": npm_version}),
        encoding="utf-8",
    )
    (root / "packages/npm/ethos-pdf/vendor/manifest.json").write_text(
        json.dumps({"version": 1, "cli_version": cli_version, "targets": {}}),
        encoding="utf-8",
    )
    python_text = (
        "Install the published evaluation wheel from PyPI with:\n"
        f"python3 -m pip install ethos-pdf=={python_version}\n"
    )
    npm_text = (
        f"The current published npm package is `@docushell/ethos-pdf@{npm_version}`. "
        f"Its vendored CLI binaries report `ethos {cli_version}`.\n"
    )
    (root / "python/README.md").write_text(python_text, encoding="utf-8")
    (root / "python/QUICKSTART.md").write_text(python_text, encoding="utf-8")
    (root / "packages/npm/ethos-pdf/README.md").write_text(npm_text, encoding="utf-8")
    (root / "packages/npm/ethos-pdf/QUICKSTART.md").write_text(
        npm_text + f"npm install -g @docushell/ethos-pdf@{npm_version}\n", encoding="utf-8"
    )


class PackageRegistrySourceConsistencyTests(unittest.TestCase):
    def test_current_source_tree_is_consistent(self) -> None:
        self.assertEqual([], validate_registry_surfaces(ROOT))

    def test_rejects_stale_install_versions(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ethos-registry-consistency-") as temp:
            root = Path(temp)
            write_fixture(root)
            quickstart = root / "python/QUICKSTART.md"
            quickstart.write_text(
                read(quickstart).replace("==0.4.0", "==0.2.0"), encoding="utf-8"
            )
            failures = validate_registry_surfaces(root)
        self.assertTrue(any("found versions ['0.2.0']" in failure for failure in failures))

    def test_allows_independent_python_npm_and_cli_versions(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ethos-registry-consistency-") as temp:
            root = Path(temp)
            write_fixture(root)
            failures = validate_registry_surfaces(root)
        self.assertEqual([], failures)

    def test_rejects_npm_wording_stale_against_package_metadata(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ethos-registry-consistency-") as temp:
            root = Path(temp)
            write_fixture(root)
            package_json = root / "packages/npm/ethos-pdf/package.json"
            package_json.write_text(
                json.dumps({"name": "@docushell/ethos-pdf", "version": "0.3.2"}),
                encoding="utf-8",
            )
            failures = validate_registry_surfaces(root)
        self.assertTrue(any("missing current-publication wording" in failure for failure in failures))

    def test_rejects_cli_wording_stale_against_vendor_manifest(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ethos-registry-consistency-") as temp:
            root = Path(temp)
            write_fixture(root)
            manifest = root / "packages/npm/ethos-pdf/vendor/manifest.json"
            manifest.write_text(
                json.dumps({"version": 1, "cli_version": "0.3.2", "targets": {}}),
                encoding="utf-8",
            )
            failures = validate_registry_surfaces(root)
        self.assertTrue(any("missing CLI version wording" in failure for failure in failures))

    def test_rejects_invalid_cli_version_shape(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ethos-registry-consistency-") as temp:
            root = Path(temp)
            write_fixture(root, cli_version="0.3")
            failures = validate_registry_surfaces(root)
        self.assertIn("vendor CLI version is not exact semver: 0.3", failures)

    def test_rejects_stale_blocked_publication_posture(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ethos-registry-consistency-") as temp:
            root = Path(temp)
            write_fixture(root)
            readme = root / "packages/npm/ethos-pdf/README.md"
            readme.write_text(
                read(readme) + "npm publication and install wording remain blocked.\n",
                encoding="utf-8",
            )
            failures = validate_registry_surfaces(root)
        self.assertTrue(any("stale publication posture" in failure for failure in failures))

    def test_rejects_missing_install_command(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ethos-registry-consistency-") as temp:
            root = Path(temp)
            write_fixture(root)
            quickstart = root / "packages/npm/ethos-pdf/QUICKSTART.md"
            quickstart.write_text(
                read(quickstart).replace("npm install -g @docushell/ethos-pdf@0.3.1\n", ""),
                encoding="utf-8",
            )
            failures = validate_registry_surfaces(root)
        self.assertTrue(any("must contain exactly one current install command" in failure for failure in failures))


if __name__ == "__main__":
    unittest.main()
