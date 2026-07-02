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

"""Validate release-state.json and check or render current-status prose."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Mapping, Sequence


ROOT = Path(__file__).resolve().parents[2]
STATE_PATH = ROOT / "docs/release-state.json"
STATUS_DOCUMENTS = (
    ROOT / "docs/execution-status.md",
    ROOT / "docs/public-release-checklist.md",
)
BEGIN_MARKER = "<!-- BEGIN GENERATED CURRENT RELEASE STATE -->"
END_MARKER = "<!-- END GENERATED CURRENT RELEASE STATE -->"
TOP_LEVEL_KEYS = {"schema_version", "as_of", "release", "closed_lanes", "blocked_lanes"}
RELEASE_KEYS = {
    "version",
    "rust_crates",
    "python_package",
    "npm_package",
    "github_release",
    "package_tags",
    "pdfium_environment",
}
PACKAGE_KEYS = {"name", "version"}
GITHUB_RELEASE_KEYS = {
    "tag",
    "version",
    "name",
    "latest",
    "notes",
    "platforms",
    "assets",
}
REQUIRED_CLOSED_LANES = (
    "rust_python_publication",
    "github_release_artifacts",
    "npm_publication",
    "public_install_wording",
    "package_tags",
    "release_tag",
    "release_metadata",
)
SEMVER = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+")
LANE_ID = re.compile(r"[a-z][a-z0-9_]*")
ENVIRONMENT_NAME = re.compile(r"[A-Z][A-Z0-9_]*")


class ReleaseStateError(ValueError):
    """The release state or its generated documentation is invalid."""


def _exact_keys(value: object, expected: set[str], label: str) -> Mapping[str, object]:
    if not isinstance(value, dict) or set(value) != expected:
        raise ReleaseStateError(f"{label} must contain exactly {sorted(expected)}")
    return value


def _string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ReleaseStateError(f"{label} must be a non-empty trimmed string")
    return value


def _unique_strings(value: object, label: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ReleaseStateError(f"{label} must be a non-empty array")
    strings = [_string(item, f"{label} item") for item in value]
    if len(strings) != len(set(strings)):
        raise ReleaseStateError(f"{label} must not contain duplicates")
    return strings


def _record_path(root: Path, value: object, lane: str) -> str:
    text = _string(value, f"closed_lanes.{lane}")
    if "\\" in text:
        raise ReleaseStateError(f"closed_lanes.{lane} must use '/' separators")
    path = PurePosixPath(text)
    if (
        path.is_absolute()
        or ".." in path.parts
        or path.parts[:2] != ("docs", "validation")
        or path.suffix != ".md"
    ):
        raise ReleaseStateError(
            f"closed_lanes.{lane} must be a safe docs/validation/*.md path"
        )
    resolved = root.joinpath(*path.parts)
    try:
        resolved.resolve().relative_to(root.resolve())
    except ValueError as error:
        raise ReleaseStateError(f"closed_lanes.{lane} escapes the repository") from error
    if not resolved.is_file():
        raise ReleaseStateError(f"closed_lanes.{lane} record does not exist: {text}")
    return text


def load_release_state(root: Path, path: Path) -> dict[str, object]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ReleaseStateError(f"cannot read release state {path}: {error}") from error
    state = dict(_exact_keys(raw, TOP_LEVEL_KEYS, "release state"))
    if state["schema_version"] != 2:
        raise ReleaseStateError("schema_version must be 2")

    as_of = _string(state["as_of"], "as_of")
    try:
        dt.date.fromisoformat(as_of)
    except ValueError as error:
        raise ReleaseStateError("as_of must be an ISO 8601 calendar date") from error

    release = dict(_exact_keys(state["release"], RELEASE_KEYS, "release"))
    version = _string(release["version"], "release.version")
    if SEMVER.fullmatch(version) is None:
        raise ReleaseStateError("release.version must be a stable MAJOR.MINOR.PATCH version")

    rust_crates = _unique_strings(release["rust_crates"], "release.rust_crates")
    for crate in rust_crates:
        if re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", crate) is None:
            raise ReleaseStateError(f"invalid Rust crate name: {crate}")

    for field in ("python_package", "npm_package"):
        package = _exact_keys(release[field], PACKAGE_KEYS, f"release.{field}")
        _string(package["name"], f"release.{field}.name")
        package_version = _string(package["version"], f"release.{field}.version")
        if SEMVER.fullmatch(package_version) is None:
            raise ReleaseStateError(
                f"release.{field}.version must be a stable MAJOR.MINOR.PATCH version"
            )

    github = _exact_keys(release["github_release"], GITHUB_RELEASE_KEYS, "release.github_release")
    if github["version"] != version or github["tag"] != f"v{version}":
        raise ReleaseStateError("GitHub release version and tag must match release.version")
    if github["name"] != f"Release v{version}":
        raise ReleaseStateError("GitHub release name must match release.version")
    if github["latest"] is not True:
        raise ReleaseStateError("the current GitHub release must be marked latest")
    notes = _string(github["notes"], "release.github_release.notes")
    notes_path = PurePosixPath(notes)
    if (
        notes_path.is_absolute()
        or ".." in notes_path.parts
        or notes_path.parts[:2] != ("docs", "releases")
        or notes_path.suffix != ".md"
        or not root.joinpath(*notes_path.parts).is_file()
    ):
        raise ReleaseStateError(
            "release.github_release.notes must name an existing docs/releases/*.md file"
        )
    _unique_strings(github["platforms"], "release.github_release.platforms")
    _unique_strings(github["assets"], "release.github_release.assets")

    package_tags = _unique_strings(release["package_tags"], "release.package_tags")
    expected_tags = [f"ethos-package-{crate}-{version}" for crate in rust_crates]
    if package_tags != expected_tags:
        raise ReleaseStateError(
            "release.package_tags must match release.rust_crates in the same order"
        )
    environment = _string(release["pdfium_environment"], "release.pdfium_environment")
    if ENVIRONMENT_NAME.fullmatch(environment) is None:
        raise ReleaseStateError("release.pdfium_environment must be an environment variable name")

    closed = state["closed_lanes"]
    if not isinstance(closed, dict) or set(closed) != set(REQUIRED_CLOSED_LANES):
        raise ReleaseStateError(
            f"closed_lanes must contain exactly {sorted(REQUIRED_CLOSED_LANES)}"
        )
    for lane in REQUIRED_CLOSED_LANES:
        if LANE_ID.fullmatch(lane) is None:
            raise ReleaseStateError(f"invalid closed lane id: {lane}")
        _record_path(root, closed[lane], lane)

    blockers = _unique_strings(state["blocked_lanes"], "blocked_lanes")
    if "DocuShell integration" not in blockers:
        raise ReleaseStateError("blocked_lanes must retain DocuShell integration until approved")

    state["release"] = release
    return state


def _human_join(values: Sequence[str]) -> str:
    if len(values) == 1:
        return values[0]
    return f"{', '.join(values[:-1])}, and {values[-1]}"


def render_current_status(state: Mapping[str, object]) -> str:
    release = state["release"]
    assert isinstance(release, dict)
    version = release["version"]
    rust_crates = [f"`{name}`" for name in release["rust_crates"]]
    python_package = release["python_package"]
    npm_package = release["npm_package"]
    github = release["github_release"]
    assert isinstance(python_package, dict)
    assert isinstance(npm_package, dict)
    assert isinstance(github, dict)
    platforms = "/".join(github["platforms"])
    package_tags = _human_join([f"`{tag}`" for tag in release["package_tags"]])
    blockers = _human_join(list(state["blocked_lanes"]))
    closed = state["closed_lanes"]
    assert isinstance(closed, dict)

    status = (
        f"Status: v{version} Rust library crates {_human_join(rust_crates)} are live on crates.io, "
        f"and the Python `{python_package['name']}` wheel is live on PyPI. Its released version is "
        f"`{python_package['version']}`. GitHub Release `{github['tag']}` is marked as the "
        "repository's latest release and contains closed-out "
        f"{platforms} CLI artifacts for evaluation with "
        f"caller-provided PDFium through `{release['pdfium_environment']}`. npm "
        f"`{npm_package['name']}@{npm_package['version']}` is live on npm. The exact v{version} "
        f"public install wording packet is approved and closed out. Package-tag creation for "
        f"{package_tags} is closed out, and the existing release tag is closed out."
    )
    records = "Current closeout records: " + "; ".join(
        f"[{lane.replace('_', ' ')}]({PurePosixPath(closed[lane]).relative_to('docs')})"
        for lane in REQUIRED_CLOSED_LANES
    ) + "."
    blocked = f"Still blocked: {blockers}."
    return f"{status}\n\n{records}\n\n{blocked}"


def render_marked_block(state: Mapping[str, object]) -> str:
    return f"{BEGIN_MARKER}\n{render_current_status(state)}\n{END_MARKER}"


def replace_marked_block(text: str, block: str) -> str:
    if text.count(BEGIN_MARKER) != 1 or text.count(END_MARKER) != 1:
        raise ReleaseStateError("status document must contain exactly one generated marker pair")
    begin = text.index(BEGIN_MARKER)
    end = text.index(END_MARKER, begin) + len(END_MARKER)
    return text[:begin] + block + text[end:]


def check_documents(documents: Sequence[Path], block: str) -> None:
    for document in documents:
        try:
            text = document.read_text(encoding="utf-8")
        except OSError as error:
            raise ReleaseStateError(f"cannot read status document {document}: {error}") from error
        if replace_marked_block(text, block) != text:
            try:
                display_path = document.relative_to(ROOT)
            except ValueError:
                display_path = document
            raise ReleaseStateError(
                f"generated release state is stale in {display_path}; run "
                "python3 .github/scripts/check_release_state.py --write"
            )


def write_documents(documents: Sequence[Path], block: str) -> None:
    for document in documents:
        text = document.read_text(encoding="utf-8")
        updated = replace_marked_block(text, block)
        if updated != text:
            document.write_text(updated, encoding="utf-8")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="check generated prose (default)")
    mode.add_argument("--write", action="store_true", help="rewrite generated prose in place")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        state = load_release_state(ROOT, STATE_PATH)
        block = render_marked_block(state)
        if args.write:
            write_documents(STATUS_DOCUMENTS, block)
            print("release state rendered")
        else:
            check_documents(STATUS_DOCUMENTS, block)
            print("release state check passed")
    except ReleaseStateError as error:
        print(f"release state error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
