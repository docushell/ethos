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

"""Deterministic-profile font policy artifact checks."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

HEX256_LEN = 64
FALLBACK_BUNDLE_DIR = Path("crates/ethos-pdf/assets/fonts/liberation")


def diagnose_font_policy(root: Path, profile: dict[str, Any]) -> list[str]:
    diagnostics: list[str] = []
    font_policy = profile.get("font_policy")
    if not isinstance(font_policy, dict):
        return ["profile font_policy must be an object"]

    diagnostics.extend(diagnose_substitution_table(root, font_policy))
    diagnostics.extend(diagnose_fallback_bundle(root, font_policy))
    return diagnostics


def diagnose_substitution_table(root: Path, font_policy: dict[str, Any]) -> list[str]:
    substitution = font_policy.get("substitution_table")
    if not isinstance(substitution, dict):
        return ["font_policy.substitution_table must be an object"]

    path_value = substitution.get("path")
    if not isinstance(path_value, str) or not safe_relative_path(path_value):
        return ["font_policy.substitution_table.path must be a safe relative path"]

    sha_value = substitution.get("sha256")
    if not isinstance(sha_value, str) or not is_hex256(sha_value):
        return ["font_policy.substitution_table.sha256 must be lowercase hex sha256"]

    path = root / path_value
    if not path.is_file():
        return [f"font_policy.substitution_table.path missing: {path_value}"]

    actual = sha256_file(path)
    if actual != sha_value:
        return [
            "font_policy.substitution_table.sha256 mismatch "
            f"for {path_value}: expected {sha_value}, got {actual}"
        ]
    return []


def diagnose_fallback_bundle(root: Path, font_policy: dict[str, Any]) -> list[str]:
    fallback = font_policy.get("fallback_bundle")
    if not isinstance(fallback, dict):
        return ["font_policy.fallback_bundle must be an object"]

    sha_value = fallback.get("sha256")
    bundle_dir = root / FALLBACK_BUNDLE_DIR
    if sha_value is None:
        if bundle_dir.exists():
            return [
                "font_policy.fallback_bundle.sha256 is null but "
                f"{FALLBACK_BUNDLE_DIR.as_posix()} exists"
            ]
        return []

    if not isinstance(sha_value, str) or not is_hex256(sha_value):
        return ["font_policy.fallback_bundle.sha256 must be null or lowercase hex sha256"]
    if not bundle_dir.is_dir():
        return [
            "font_policy.fallback_bundle.sha256 is set but "
            f"{FALLBACK_BUNDLE_DIR.as_posix()} is missing"
        ]

    actual = sha256_directory(bundle_dir)
    if actual is None:
        return [f"font fallback bundle has no files: {FALLBACK_BUNDLE_DIR.as_posix()}"]
    if actual != sha_value:
        return [
            "font_policy.fallback_bundle.sha256 mismatch "
            f"for {FALLBACK_BUNDLE_DIR.as_posix()}: expected {sha_value}, got {actual}"
        ]
    return []


def safe_relative_path(value: str) -> bool:
    path = Path(value)
    return (
        bool(value)
        and not path.is_absolute()
        and ".." not in path.parts
        and str(path) == value
    )


def is_hex256(value: str) -> bool:
    return (
        len(value) == HEX256_LEN
        and value == value.lower()
        and all(ch in "0123456789abcdef" for ch in value)
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_directory(path: Path) -> str | None:
    files = sorted(item for item in path.rglob("*") if item.is_file())
    if not files:
        return None
    entries = {item.relative_to(path).as_posix(): sha256_file(item) for item in files}
    payload = json.dumps(entries, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(f"{payload}\n".encode("utf-8")).hexdigest()
