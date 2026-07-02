#!/usr/bin/env python3
#
# Copyright 2026 The Ethos maintainers
#
# Licensed under the Apache License, Version 2.0 (the "License");
#

"""Verify the live GitHub Release metadata declared by docs/release-state.json."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Mapping, Sequence

from check_release_state import ROOT, load_release_state


DEFAULT_STATE = ROOT / "docs/release-state.json"
API_ROOT = "https://api.github.com"


class ReleaseMetadataError(ValueError):
    """Live GitHub Release metadata does not match the declared current state."""


def _object(value: object, label: str) -> Mapping[str, object]:
    if not isinstance(value, dict):
        raise ReleaseMetadataError(f"{label} must be a JSON object")
    return value


def _asset_names(release: Mapping[str, object]) -> list[str]:
    assets = release.get("assets")
    if not isinstance(assets, list):
        raise ReleaseMetadataError("release assets must be a JSON array")
    names: list[str] = []
    for index, asset in enumerate(assets):
        item = _object(asset, f"release asset {index}")
        name = item.get("name")
        if not isinstance(name, str) or not name:
            raise ReleaseMetadataError(f"release asset {index} has no name")
        names.append(name)
    return names


def validate_release_metadata(
    github: Mapping[str, object],
    latest: Mapping[str, object],
    release: Mapping[str, object],
    expected_notes: str,
) -> None:
    expected_tag = github["tag"]
    if latest.get("tag_name") != expected_tag:
        raise ReleaseMetadataError(
            f"GitHub latest release is {latest.get('tag_name')!r}; expected {expected_tag!r}"
        )
    if latest.get("id") != release.get("id"):
        raise ReleaseMetadataError("latest release and tag release resolve to different objects")
    if release.get("tag_name") != expected_tag:
        raise ReleaseMetadataError("tag release does not match release-state.json")
    if release.get("name") != github["name"]:
        raise ReleaseMetadataError(
            f"release name is {release.get('name')!r}; expected {github['name']!r}"
        )
    if release.get("draft") is not False:
        raise ReleaseMetadataError("current release must not be a draft")
    if release.get("prerelease") is not False:
        raise ReleaseMetadataError("current release must not be a prerelease")
    body = release.get("body")
    if not isinstance(body, str) or body.strip() != expected_notes.strip():
        raise ReleaseMetadataError("live release body differs from the canonical notes file")

    expected_assets = github["assets"]
    if not isinstance(expected_assets, list):
        raise ReleaseMetadataError("declared release assets must be an array")
    actual_assets = _asset_names(release)
    if sorted(actual_assets) != sorted(expected_assets):
        raise ReleaseMetadataError(
            f"live release assets differ: actual={sorted(actual_assets)!r} "
            f"expected={sorted(expected_assets)!r}"
        )


def fetch_json(url: str) -> Mapping[str, object]:
    separator = "&" if "?" in url else "?"
    uncached_url = f"{url}{separator}_ethos_check={time.time_ns()}"
    headers = {
        "Accept": "application/vnd.github+json",
        "Cache-Control": "no-cache",
        "User-Agent": "ethos-release-metadata-check",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(uncached_url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return _object(json.load(response), url)
    except (OSError, urllib.error.URLError, json.JSONDecodeError) as error:
        raise ReleaseMetadataError(f"cannot read {url}: {error}") from error


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default="docushell/ethos", help="GitHub OWNER/REPO")
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.repo.count("/") != 1 or any(not part for part in args.repo.split("/")):
        print("release metadata error: --repo must use OWNER/REPO", file=sys.stderr)
        return 2
    try:
        state = load_release_state(ROOT, args.state)
        release_state = _object(state["release"], "release state")
        github = _object(release_state["github_release"], "GitHub release state")
        notes_path = ROOT / str(github["notes"])
        notes = notes_path.read_text(encoding="utf-8")
        latest = fetch_json(f"{API_ROOT}/repos/{args.repo}/releases/latest")
        release = fetch_json(f"{API_ROOT}/repos/{args.repo}/releases/tags/{github['tag']}")
        validate_release_metadata(github, latest, release, notes)
    except (OSError, ReleaseMetadataError, ValueError) as error:
        print(f"release metadata error: {error}", file=sys.stderr)
        return 1
    print(f"live GitHub release metadata matches {github['tag']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
