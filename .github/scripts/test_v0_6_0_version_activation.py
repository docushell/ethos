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
"""Guard v0.6.0 core activation while v0.5.0 remains the published public baseline.

The workspace, the Python package, and the internal crate pins move to 0.6.0 together so release
artifacts build at the right version. Nothing about that makes 0.6.0 installable: the advertised
install commands, the claims registry, and the vendored npm payload keep naming the published
0.5.0 until v0.6.0 artifacts actually publish.

The npm payload deliberately does **not** advance here. That package ships a vendored CLI binary,
and no v0.6.0 binary exists yet, so bumping the package version would advertise a version the
package does not contain. It advances when the payload is refreshed from published v0.6.0
artifacts, under its own recorded boundary exception.

Published-baseline assertions live in `test_v0_5_0_version_activation.py`. This module owns
activation only.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ACTIVATED = "0.6.0"
PUBLISHED = "0.5.0"
INTERNAL_WORKSPACE_DEPENDENCIES = ("ethos-core", "ethos-layout", "ethos-tables")
INTERNAL_CLI_DEPENDENCIES = ("ethos-pdf", "ethos-verify", "ethos-grounding-opendataloader-json")


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _registry_claims(claims_json: str) -> list[str]:
    """Every claim string in docs/public-boundary-claims.json, flattened."""
    registry = json.loads(claims_json)
    return [
        claim
        for surface in registry["surfaces"].values()
        for claim in surface["claims"]
    ]


class V060CoreVersionActivationTests(unittest.TestCase):
    def test_core_release_metadata_is_activated_in_lockstep(self) -> None:
        cargo = read("Cargo.toml")
        cli = read("crates/ethos-cli/Cargo.toml")
        lock = read("Cargo.lock")

        self.assertIn(f'version = "{ACTIVATED}"', cargo)
        for dependency in INTERNAL_WORKSPACE_DEPENDENCIES:
            line = next(line for line in cargo.splitlines() if line.startswith(dependency))
            self.assertIn(f'version = "{ACTIVATED}"', line, dependency)
        for dependency in INTERNAL_CLI_DEPENDENCIES:
            line = next(line for line in cli.splitlines() if line.startswith(dependency))
            self.assertIn(f'version = "{ACTIVATED}"', line, dependency)

        # Every workspace member resolves at the activated version.
        self.assertGreaterEqual(lock.count(f'version = "{ACTIVATED}"'), 7)
        self.assertIn(f'version = "{ACTIVATED}"', read("pyproject.toml"))
        self.assertIn(f'__version__ = "{ACTIVATED}"', read("python/ethos_pdf/__init__.py"))

    def test_public_install_wording_is_not_advanced_to_the_candidate(self) -> None:
        claims = read("docs/public-boundary-claims.json")
        readme = read("README.md")
        active_readme = readme.split("### 60-second `ethos-full` install", 1)[0]

        # Activation is not publication. Until v0.6.0 reaches the registries, advertising it would
        # send users to an install command that cannot succeed. Prose about the v0.6.0 plan is
        # fine; an install command naming it is not.
        for command in (
            f"cargo add ethos-doc-core@{ACTIVATED}",
            f"cargo add ethos-verify@{ACTIVATED}",
            f"cargo add ethos-pdf@{ACTIVATED}",
            f"python3 -m pip install ethos-pdf=={ACTIVATED}",
            f"npm install -g @docushell/ethos-pdf@{ACTIVATED}",
            f"@docushell/ethos-pdf@{ACTIVATED}",
        ):
            self.assertNotIn(command, active_readme, command)
            self.assertNotIn(command, claims, command)
        self.assertIn(f"npm install -g @docushell/ethos-pdf@{PUBLISHED}", active_readme)

        # The activated version may appear in the registry only where it states a fact about the
        # bytes in this tree, never where it advertises something installable. After a payload
        # refresh the vendored binaries really do report the activated version, and saying so is
        # the honest claim; a blanket ban forced the registry to describe its own payload wrongly.
        for claim in _registry_claims(claims):
            if ACTIVATED not in claim:
                continue
            self.assertEqual(
                f"Its vendored CLI binaries report `ethos {ACTIVATED}`.",
                claim,
                f"only the vendored-binary claim may name the activated version: {claim}",
            )

    def test_npm_payload_stays_on_the_published_release_until_refreshed(self) -> None:
        manifest = json.loads(read("packages/npm/ethos-pdf/vendor/manifest.json"))
        package = json.loads(read("packages/npm/ethos-pdf/package.json"))
        lock = json.loads(read("packages/npm/ethos-pdf/package-lock.json"))
        versions = {
            manifest["cli_version"],
            package["version"],
            lock["version"],
            lock["packages"][""].get("version"),
        }

        if versions == {ACTIVATED}:
            # A refresh to the activated version is allowed only with its recorded exception,
            # mirroring how the v0.5.0 payload refresh was governed.
            self.assertIn(
                f"boundary-exception: refresh the v{ACTIVATED} npm B payload from frozen core-A",
                read("CHANGELOG.md"),
            )
        else:
            self.assertEqual({PUBLISHED}, versions)

    def test_release_state_still_records_the_published_version(self) -> None:
        state = json.loads(read("docs/release-state.json"))

        # The release ledger describes what is live, not what is being prepared.
        self.assertEqual(PUBLISHED, state["release"]["version"])


if __name__ == "__main__":
    unittest.main()
