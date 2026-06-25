#
# Copyright 2026 The Ethos maintainers
#
# Licensed under the Apache License, Version 2.0 (the "License");
#

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Protocol


class _Asserts(Protocol):
    def assertEqual(self, first: object, second: object, msg: object = ...) -> None: ...
    def assertIn(self, member: object, container: object, msg: object = ...) -> None: ...
    def assertRegex(self, text: str, expected_regex: str, msg: object = ...) -> None: ...
    def assertTrue(self, expr: object, msg: object = ...) -> None: ...


_SHA1 = r"[0-9a-f]{40}"


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        encoding="utf-8",
        stderr=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        check=False,
    )


def _commit_exists(root: Path, commit: str) -> bool:
    return _git(root, "cat-file", "-e", f"{commit}^{{commit}}").returncode == 0


def assert_record_source_binding(
    case: _Asserts,
    *,
    root: Path,
    raw_record: str,
    normalized_record: str,
    validated_head: str,
    source_label: str,
    source_commit: str,
    source_tree: str,
) -> None:
    """Validate a release record's source binding without requiring commit reachability.

    Validation records need to survive squash merges and fresh main checkouts. The record itself
    carries the immutable commit and tree values; when that commit object is available locally, this
    helper also verifies the tree. If the object is not available, the self-contained record binding
    remains enforceable instead of making CI depend on branch-history preservation.
    """

    case.assertRegex(source_commit, f"^{_SHA1}$")
    case.assertRegex(source_tree, f"^{_SHA1}$")
    case.assertTrue(
        source_commit.startswith(validated_head),
        f"{validated_head!r} must be a prefix of {source_commit!r}",
    )
    case.assertIn(f"Validated source HEAD before this record: `{validated_head}`", raw_record)
    case.assertIn(f"{source_label} source commit: `{source_commit}`", normalized_record)
    case.assertIn(f"{source_label} source tree: `{source_tree}`", normalized_record)

    if _commit_exists(root, source_commit):
        tree = _git(root, "rev-parse", f"{source_commit}^{{tree}}")
        case.assertEqual(0, tree.returncode)
        case.assertEqual(source_tree, tree.stdout.strip())
