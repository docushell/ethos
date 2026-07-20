#!/usr/bin/env python3
"""Guard the v0.4.0 source activation without changing published-install wording."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VERSION = "0.4.0"
PUBLISHED = "0.3.0"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


class V040VersionActivationTests(unittest.TestCase):
    def test_release_metadata_is_activated_in_lockstep(self) -> None:
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
        self.assertEqual(VERSION, json.loads(read("packages/npm/ethos-pdf/package.json"))["version"])
        npm_lock = json.loads(read("packages/npm/ethos-pdf/package-lock.json"))
        self.assertEqual(VERSION, npm_lock["version"])
        self.assertEqual(VERSION, npm_lock["packages"][""]["version"])

    def test_draft_artifact_workflow_uses_activated_version(self) -> None:
        workflow = read(".github/workflows/release.yml")
        self.assertEqual(2, workflow.count(f'--expected-version "ethos {VERSION}"'))
        self.assertEqual(2, workflow.count(f"--version {VERSION}"))

    def test_published_install_wording_stays_on_current_release(self) -> None:
        claims = read("docs/public-boundary-claims.json")
        readme = read("README.md")
        for expected in (
            f"cargo add ethos-doc-core@{PUBLISHED}",
            f"python3 -m pip install ethos-pdf=={PUBLISHED}",
            f"npm install -g @docushell/ethos-pdf@{PUBLISHED}",
        ):
            self.assertIn(expected, readme)
            self.assertIn(expected, claims)

    def test_mcp_prototype_remains_excluded(self) -> None:
        cargo = read("Cargo.toml")
        workflow = read(".github/workflows/release.yml")
        mcp = json.loads(read("packages/npm/ethos-mcp/package.json"))
        self.assertNotIn("ethos-mcp", cargo)
        self.assertNotIn("ethos-mcp", workflow)
        self.assertEqual(PUBLISHED, mcp["version"])
        self.assertEqual(PUBLISHED, mcp["dependencies"]["@docushell/ethos-pdf"])


if __name__ == "__main__":
    unittest.main()
