#!/usr/bin/env python3
"""Guard v0.5.0 core activation while v0.4.0 remains publicly published."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VERSION = "0.5.0"
PUBLISHED_NPM_PAYLOAD = "0.4.0"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


class V050CoreVersionActivationTests(unittest.TestCase):
    def test_core_release_metadata_is_activated_in_lockstep(self) -> None:
        cargo = read("Cargo.toml")
        cli = read("crates/ethos-cli/Cargo.toml")
        lock = read("Cargo.lock")
        self.assertIn(f'version = "{VERSION}"', cargo)
        for dependency in ("ethos-core", "ethos-layout", "ethos-tables"):
            self.assertIn(f'version = "{VERSION}"', next(line for line in cargo.splitlines() if line.startswith(dependency)))
        for dependency in ("ethos-pdf", "ethos-verify", "ethos-grounding-opendataloader-json"):
            self.assertIn(f'version = "{VERSION}"', next(line for line in cli.splitlines() if line.startswith(dependency)))
        self.assertGreaterEqual(lock.count(f'version = "{VERSION}"'), 7)
        self.assertIn(f'version = "{VERSION}"', read("pyproject.toml"))
        self.assertIn(f'__version__ = "{VERSION}"', read("python/ethos_pdf/__init__.py"))

    def test_draft_artifact_workflows_derive_the_activated_version(self) -> None:
        workflow = read(".github/workflows/release.yml")
        self.assertEqual(2, workflow.count("tomllib.load(open('Cargo.toml','rb'))['workspace']['package']['version']"))
        self.assertIn(
            "tomllib.load(open(''Cargo.toml'',''rb''))[''workspace''][''package''][''version']",
            workflow,
        )
        self.assertEqual(2, workflow.count('--expected-version "ethos ${{ steps.version.outputs.value }}"'))
        self.assertEqual(2, workflow.count('--version ${{ steps.version.outputs.value }}'))

    def test_public_install_wording_is_not_advanced_to_the_candidate(self) -> None:
        claims = read("docs/public-boundary-claims.json")
        readme = read("README.md")
        self.assertNotIn("0.5.0", readme)
        self.assertNotIn("0.5.0", claims)

    def test_npm_payload_remains_on_published_release_until_refreshed_from_core_a(self) -> None:
        manifest = json.loads(read("packages/npm/ethos-pdf/vendor/manifest.json"))
        package = json.loads(read("packages/npm/ethos-pdf/package.json"))
        self.assertEqual(PUBLISHED_NPM_PAYLOAD, manifest["cli_version"])
        self.assertEqual(PUBLISHED_NPM_PAYLOAD, package["version"])

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
