#!/usr/bin/env python3
"""Guard the published v0.5.0 public baseline while a later version activates in the core.

v0.5.0 was published on 2026-07-21 to crates.io (`ethos-doc-core`, `ethos-verify`, `ethos-pdf`),
PyPI (`ethos-pdf`), npm (`@docushell/ethos-pdf`), and GitHub Release `v0.5.0`. It remains the
version users can actually install, so the advertised install commands and the shipped npm payload
must keep naming it until a later release publishes.

Core version activation moved to `test_v0_6_0_version_activation.py` when the workspace advanced to
0.6.0. This module now guards only the published direction.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VERSION = "0.5.0"
PUBLISHED_NPM_PAYLOAD = VERSION


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


class V050CoreVersionActivationTests(unittest.TestCase):
    def test_draft_artifact_workflows_derive_the_activated_version(self) -> None:
        workflow = read(".github/workflows/release.yml")
        self.assertEqual(2, workflow.count("tomllib.load(open('Cargo.toml','rb'))['workspace']['package']['version']"))
        self.assertIn(
            "tomllib.load(open(''Cargo.toml'',''rb''))[''workspace''][''package''][''version']",
            workflow,
        )
        self.assertEqual(2, workflow.count('--expected-version "ethos ${{ steps.version.outputs.value }}"'))
        self.assertEqual(2, workflow.count('--version ${{ steps.version.outputs.value }}'))

    def test_public_install_wording_matches_the_published_release(self) -> None:
        claims = read("docs/public-boundary-claims.json")
        readme = read("README.md")
        active_readme = readme.split("### 60-second `ethos-full` install", 1)[0]
        # The published baseline is the advertised one. Nothing may still point at the previous
        # release, and the exact install commands must name the published version.
        for surface, text in (("README.md", active_readme), ("claims registry", claims)):
            self.assertNotIn("0.4.0", text, surface)
        for command in (
            f"cargo add ethos-doc-core@{VERSION}",
            f"cargo add ethos-verify@{VERSION}",
            f"cargo add ethos-pdf@{VERSION}",
            f"python3 -m pip install ethos-pdf=={VERSION}",
            f"npm install -g @docushell/ethos-pdf@{VERSION}",
        ):
            self.assertIn(command, active_readme, command)
            self.assertIn(command, claims, command)

    def test_npm_payload_matches_the_published_release(self) -> None:
        manifest = json.loads(read("packages/npm/ethos-pdf/vendor/manifest.json"))
        package = json.loads(read("packages/npm/ethos-pdf/package.json"))
        lock = json.loads(read("packages/npm/ethos-pdf/package-lock.json"))
        versions = {
            manifest["cli_version"],
            package["version"],
            lock["version"],
            lock["packages"][""].get("version"),
        }
        self.assertEqual({PUBLISHED_NPM_PAYLOAD}, versions)
        # The payload refresh that moved these off the previous release keeps its recorded
        # boundary exception.
        self.assertIn(
            "boundary-exception: refresh the v0.5.0 npm B payload from frozen core-A",
            read("CHANGELOG.md"),
        )

    def test_mcp_prototype_remains_excluded(self) -> None:
        cargo = read("Cargo.toml")
        workflow = read(".github/workflows/release.yml")
        mcp = json.loads(read("packages/npm/ethos-mcp/package.json"))
        self.assertNotIn("ethos-mcp", cargo)
        self.assertNotIn("ethos-mcp", workflow)
        self.assertNotEqual(VERSION, mcp["version"])
        self.assertNotEqual(VERSION, mcp["dependencies"]["@docushell/ethos-pdf"])


if __name__ == "__main__":
    unittest.main()
