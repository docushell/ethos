#!/usr/bin/env python3
#
# Copyright 2026 The Ethos maintainers
#
# Licensed under the Apache License, Version 2.0 (the "License");
#

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from validation_record_source import assert_record_source_binding


ROOT = Path(__file__).resolve().parents[2]


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args],
        cwd=ROOT,
        encoding="utf-8",
        stderr=subprocess.DEVNULL,
    ).strip()


class ValidationRecordSourceTests(unittest.TestCase):
    def test_unreachable_commit_binding_is_self_contained(self) -> None:
        commit = "a" * 40
        tree = "b" * 40
        raw = f"Validated source HEAD before this record: `{commit[:7]}`"
        normalized = (
            f"example validation source commit: `{commit}` "
            f"example validation source tree: `{tree}`"
        )
        with tempfile.TemporaryDirectory() as temp:
            assert_record_source_binding(
                self,
                root=Path(temp),
                raw_record=raw,
                normalized_record=normalized,
                validated_head=commit[:7],
                source_label="example validation",
                source_commit=commit,
                source_tree=tree,
            )

    def test_reachable_commit_tree_is_verified(self) -> None:
        commit = git("rev-parse", "HEAD")
        tree = git("rev-parse", "HEAD^{tree}")
        raw = f"Validated source HEAD before this record: `{commit[:7]}`"
        normalized = (
            f"reachable validation source commit: `{commit}` "
            f"reachable validation source tree: `{tree}`"
        )

        assert_record_source_binding(
            self,
            root=ROOT,
            raw_record=raw,
            normalized_record=normalized,
            validated_head=commit[:7],
            source_label="reachable validation",
            source_commit=commit,
            source_tree=tree,
        )

    def test_reachable_commit_tree_mismatch_fails(self) -> None:
        commit = git("rev-parse", "HEAD")
        raw = f"Validated source HEAD before this record: `{commit[:7]}`"
        normalized = (
            f"reachable validation source commit: `{commit}` "
            f"reachable validation source tree: `{'c' * 40}`"
        )

        with self.assertRaises(AssertionError):
            assert_record_source_binding(
                self,
                root=ROOT,
                raw_record=raw,
                normalized_record=normalized,
                validated_head=commit[:7],
                source_label="reachable validation",
                source_commit=commit,
                source_tree="c" * 40,
            )


if __name__ == "__main__":
    unittest.main()
