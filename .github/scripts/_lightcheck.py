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

import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args],
        cwd=ROOT,
        encoding="utf-8",
        stderr=subprocess.DEVNULL,
    ).strip()


def base_ref() -> str:
    configured = os.environ.get("ETHOS_LIGHT_CHECK_BASE")
    if configured:
        try:
            git("rev-parse", "--verify", configured)
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(
                f"ETHOS_LIGHT_CHECK_BASE does not resolve: {configured}"
            ) from exc
        return configured

    try:
        return git("merge-base", "HEAD", "origin/main")
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            "origin/main does not resolve; fetch origin/main or set ETHOS_LIGHT_CHECK_BASE"
        ) from exc


def changed_files() -> list[str]:
    base = base_ref()
    blobs = [
        git("diff", "--name-only", f"{base}...HEAD"),
        git("diff", "--name-only", "--cached"),
        git("diff", "--name-only"),
        git("ls-files", "--others", "--exclude-standard"),
    ]
    return sorted({line for blob in blobs for line in blob.splitlines() if line})


def added_changelog_lines(path: Path) -> list[str]:
    if not path.is_file():
        return []

    base = base_ref()
    blobs = [
        git("diff", "--unified=0", f"{base}...HEAD", "--", path.relative_to(ROOT).as_posix()),
        git("diff", "--unified=0", "--cached", "--", path.relative_to(ROOT).as_posix()),
        git("diff", "--unified=0", "--", path.relative_to(ROOT).as_posix()),
    ]

    lines: list[str] = []
    for blob in blobs:
        for line in blob.splitlines():
            if line.startswith("+++") or not line.startswith("+"):
                continue
            lines.append(line[1:].strip())

    if path.relative_to(ROOT).as_posix() in git("ls-files", "--others", "--exclude-standard").splitlines():
        lines.extend(line.strip() for line in path.read_text(encoding="utf-8").splitlines())

    return lines


def has_added_marker(path: Path, marker: str) -> bool:
    prefix = f"{marker}:"
    for line in added_changelog_lines(path):
        normalized = line.removeprefix("- ").strip()
        if normalized.startswith(prefix) and normalized[len(prefix) :].strip():
            return True
    return False
