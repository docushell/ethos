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
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from check_release_state import (
    BEGIN_MARKER,
    END_MARKER,
    ReleaseStateError,
    check_documents,
    load_release_state,
    render_marked_block,
    write_documents,
)


RECORD_NAMES = {
    "rust_python_publication": "rust-python.md",
    "github_release_artifacts": "github.md",
    "npm_publication": "npm.md",
    "public_install_wording": "wording.md",
    "package_tags": "package-tags.md",
    "release_tag": "release-tag.md",
    "release_metadata": "release-metadata.md",
}


class ReleaseStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        validation = self.root / "docs/validation"
        validation.mkdir(parents=True)
        for name in RECORD_NAMES.values():
            (validation / name).write_text("record\n", encoding="utf-8")
        self.path = self.root / "docs/release-state.json"
        self.state = {
            "schema_version": 2,
            "as_of": "2026-07-02",
            "release": {
                "version": "0.3.0",
                "rust_crates": ["ethos-doc-core", "ethos-verify", "ethos-pdf"],
                "python_package": {"name": "ethos-pdf", "version": "0.3.0"},
                "npm_package": {
                    "name": "@docushell/ethos-pdf",
                    "version": "0.3.0",
                },
                "github_release": {
                    "tag": "v0.3.0",
                    "version": "0.3.0",
                    "name": "Release v0.3.0",
                    "latest": True,
                    "notes": "docs/releases/v0.3.0.md",
                    "platforms": ["macOS arm64", "Linux x64"],
                    "assets": ["ethos-macos-arm64.tar.gz", "ethos-linux-x64.tar.gz"],
                },
                "package_tags": [
                    "ethos-package-ethos-doc-core-0.3.0",
                    "ethos-package-ethos-verify-0.3.0",
                    "ethos-package-ethos-pdf-0.3.0",
                ],
                "pdfium_environment": "ETHOS_PDFIUM_LIBRARY_PATH",
            },
            "closed_lanes": {
                lane: f"docs/validation/{name}" for lane, name in RECORD_NAMES.items()
            },
            "blocked_lanes": ["DocuShell integration", "hosted surfaces"],
        }
        releases = self.root / "docs/releases"
        releases.mkdir(parents=True)
        (releases / "v0.3.0.md").write_text("release notes\n", encoding="utf-8")

    def write_state(self, state: object | None = None) -> None:
        self.path.write_text(json.dumps(state or self.state), encoding="utf-8")

    def test_render_is_deterministic_and_uses_all_current_surfaces(self) -> None:
        self.write_state()
        loaded = load_release_state(self.root, self.path)

        first = render_marked_block(loaded)
        second = render_marked_block(loaded)

        self.assertEqual(first, second)
        self.assertIn("v0.3.0 Rust library crates", first)
        self.assertIn("marked as the repository's latest release", first)
        self.assertIn("`@docushell/ethos-pdf@0.3.0` is live on npm", first)
        self.assertIn("DocuShell integration", first)
        for path in self.state["closed_lanes"].values():
            self.assertIn(path.removeprefix("docs/"), first)

    def test_unknown_top_level_field_is_rejected(self) -> None:
        state = deepcopy(self.state)
        state["unexpected"] = True
        self.write_state(state)

        with self.assertRaisesRegex(ReleaseStateError, "must contain exactly"):
            load_release_state(self.root, self.path)

    def test_package_versions_are_independent_and_rendered_explicitly(self) -> None:
        state = deepcopy(self.state)
        state["release"]["python_package"]["version"] = "0.2.0"
        state["release"]["npm_package"]["version"] = "0.2.1"
        self.write_state(state)

        rendered = render_marked_block(load_release_state(self.root, self.path))

        self.assertIn("wheel is live on PyPI. Its released version is `0.2.0`", rendered)
        self.assertIn("`@docushell/ethos-pdf@0.2.1` is live on npm", rendered)

    def test_invalid_package_version_is_rejected(self) -> None:
        state = deepcopy(self.state)
        state["release"]["npm_package"]["version"] = "latest"
        self.write_state(state)

        with self.assertRaisesRegex(ReleaseStateError, "stable MAJOR.MINOR.PATCH"):
            load_release_state(self.root, self.path)

    def test_current_github_release_must_be_latest(self) -> None:
        state = deepcopy(self.state)
        state["release"]["github_release"]["latest"] = False
        self.write_state(state)

        with self.assertRaisesRegex(ReleaseStateError, "must be marked latest"):
            load_release_state(self.root, self.path)

    def test_github_release_notes_must_be_tracked_under_docs_releases(self) -> None:
        state = deepcopy(self.state)
        state["release"]["github_release"]["notes"] = "README.md"
        self.write_state(state)

        with self.assertRaisesRegex(ReleaseStateError, "docs/releases"):
            load_release_state(self.root, self.path)

    def test_missing_record_is_rejected(self) -> None:
        state = deepcopy(self.state)
        state["closed_lanes"]["npm_publication"] = "docs/validation/missing.md"
        self.write_state(state)

        with self.assertRaisesRegex(ReleaseStateError, "record does not exist"):
            load_release_state(self.root, self.path)

    def test_record_path_escape_is_rejected(self) -> None:
        state = deepcopy(self.state)
        state["closed_lanes"]["npm_publication"] = "docs/validation/../../outside.md"
        self.write_state(state)

        with self.assertRaisesRegex(ReleaseStateError, "safe docs/validation"):
            load_release_state(self.root, self.path)

    def test_duplicate_blocker_is_rejected(self) -> None:
        state = deepcopy(self.state)
        state["blocked_lanes"].append("DocuShell integration")
        self.write_state(state)

        with self.assertRaisesRegex(ReleaseStateError, "must not contain duplicates"):
            load_release_state(self.root, self.path)

    def test_write_then_check_repairs_only_marked_region(self) -> None:
        self.write_state()
        block = render_marked_block(load_release_state(self.root, self.path))
        document = self.root / "status.md"
        document.write_text(
            f"prefix\n{BEGIN_MARKER}\nstale\n{END_MARKER}\nsuffix\n",
            encoding="utf-8",
        )

        with self.assertRaisesRegex(ReleaseStateError, "generated release state is stale"):
            check_documents([document], block)
        write_documents([document], block)
        check_documents([document], block)

        text = document.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("prefix\n"))
        self.assertTrue(text.endswith("\nsuffix\n"))


if __name__ == "__main__":
    unittest.main()
