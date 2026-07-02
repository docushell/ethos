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

"""Run closed-lane record guards from one explicit, ordered manifest."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Sequence


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = Path(__file__).with_name("frozen_record_guards.json")
MANIFEST_KEYS = {"schema_version", "guards"}
SCRIPT_PREFIX = (".github", "scripts")


class ManifestError(ValueError):
    """The frozen-record guard manifest is unsafe or malformed."""


def _safe_guard_path(root: Path, value: object) -> Path:
    if not isinstance(value, str) or not value:
        raise ManifestError("each guard must be a non-empty string")
    if "\\" in value:
        raise ManifestError(f"guard paths must use '/' separators: {value!r}")

    relative = PurePosixPath(value)
    if relative.is_absolute() or ".." in relative.parts or "." in relative.parts:
        raise ManifestError(f"guard path escapes the repository: {value!r}")
    if relative.parts[:2] != SCRIPT_PREFIX or len(relative.parts) != 3:
        raise ManifestError(
            f"guard must be a direct child of .github/scripts: {value!r}"
        )
    if not relative.name.startswith("test_") or relative.suffix != ".py":
        raise ManifestError(f"guard must match .github/scripts/test_*.py: {value!r}")

    root_resolved = root.resolve()
    script = root.joinpath(*relative.parts)
    try:
        script.resolve().relative_to(root_resolved)
    except ValueError as error:
        raise ManifestError(f"guard path escapes the repository: {value!r}") from error
    if not script.is_file():
        raise ManifestError(f"guard script does not exist: {value}")
    return script


def load_manifest(root: Path, manifest_path: Path) -> list[tuple[str, Path]]:
    try:
        raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ManifestError(f"cannot read guard manifest {manifest_path}: {error}") from error

    if not isinstance(raw, dict) or set(raw) != MANIFEST_KEYS:
        raise ManifestError(
            "manifest must be an object with exactly 'schema_version' and 'guards'"
        )
    if raw["schema_version"] != 1:
        raise ManifestError("manifest schema_version must be 1")
    guards = raw["guards"]
    if not isinstance(guards, list) or not guards:
        raise ManifestError("manifest guards must be a non-empty array")

    seen: set[str] = set()
    validated: list[tuple[str, Path]] = []
    for value in guards:
        if isinstance(value, str) and value in seen:
            raise ManifestError(f"duplicate guard path: {value}")
        script = _safe_guard_path(root, value)
        seen.add(value)
        validated.append((value, script))
    return validated


def run_guards(
    root: Path,
    guards: Sequence[tuple[str, Path]],
    *,
    python: str,
) -> int:
    total = len(guards)
    for index, (label, script) in enumerate(guards, start=1):
        print(f"frozen record guard {index}/{total}: {label}", flush=True)
        result = subprocess.run([python, str(script)], cwd=root, check=False)
        if result.returncode != 0:
            print(
                f"frozen record guard failed ({result.returncode}): {label}",
                file=sys.stderr,
                flush=True,
            )
            return result.returncode
    print(f"frozen record guards passed: {total}", flush=True)
    return 0


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help="ordered JSON guard manifest",
    )
    parser.add_argument(
        "--python",
        default=sys.executable,
        help="Python interpreter forwarded to every guard (default: current interpreter)",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        guards = load_manifest(ROOT, args.manifest)
    except ManifestError as error:
        print(f"frozen record guard manifest error: {error}", file=sys.stderr)
        return 2
    return run_guards(ROOT, guards, python=args.python)


if __name__ == "__main__":
    raise SystemExit(main())
