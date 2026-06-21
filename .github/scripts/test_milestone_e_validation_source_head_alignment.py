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

from functools import lru_cache
import re
import subprocess
import unittest
from pathlib import Path

from makefile_guard import target_block


ROOT = Path(__file__).resolve().parents[2]
VALIDATION_DIR = ROOT / "docs/validation"
PREP_SCOPE = ROOT / "docs/milestone-e-prep-scope.md"
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"

SOURCE_HEAD_RE = re.compile(
    r"^- Validated source HEAD before this record: `([0-9a-f]{7,40})`$",
    re.MULTILINE,
)

FORBIDDEN_RECORD_WORDING = [
    "public beta is approved",
    "public reports are approved",
    "public result wording approved",
    "release-ready",
    "release artifact approved",
    "package-ready",
    "package publication approved",
    "production-ready",
    "production positioning approved",
    "benchmark-validated",
    "public benchmark pass",
    "speed validated",
    "fastest",
    "launch-ready",
    "hosted surface approved",
    "hosted demo approved",
    "demo-ready",
    "complete demo plan",
    "broad demo approved",
    "performance validated",
    "quality validated",
    "footprint validated",
    "table-quality validated",
    "parser-quality validated",
]


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args],
        cwd=ROOT,
        encoding="utf-8",
        stderr=subprocess.DEVNULL,
    ).strip()


def validation_records() -> list[Path]:
    return sorted(VALIDATION_DIR.glob("milestone-e-*-validation-*.md"))


def source_heads(record: Path) -> list[str]:
    return SOURCE_HEAD_RE.findall(record.read_text(encoding="utf-8"))


@lru_cache(maxsize=None)
def resolve_commit(revision: str) -> str:
    return git("rev-parse", "--verify", f"{revision}^{{commit}}")


@lru_cache(maxsize=None)
def try_resolve_commit(revision: str) -> str | None:
    try:
        return resolve_commit(revision)
    except subprocess.CalledProcessError:
        return None


@lru_cache(maxsize=None)
def introducing_commit(record: Path) -> str | None:
    relative = str(record.relative_to(ROOT))
    commits = git("log", "--all", "--diff-filter=A", "--format=%H", "--", relative)
    if not commits:
        return None
    return commits.splitlines()[-1]


@lru_cache(maxsize=None)
def milestone_e_records_added_by(commit: str) -> tuple[str, ...]:
    records = git(
        "show",
        "--diff-filter=A",
        "--format=",
        "--name-only",
        commit,
        "--",
        str(VALIDATION_DIR.relative_to(ROOT)),
    )

    return tuple(
        name
        for name in records.splitlines()
        if Path(name).name.startswith("milestone-e-")
        and Path(name).name.endswith(".md")
    )


def has_single_milestone_e_record_add(added_records: tuple[str, ...]) -> bool:
    return len(added_records) == 1


def can_infer_source_head_from_add_parent(record: Path) -> bool:
    add_commit = introducing_commit(record)
    if add_commit is None:
        return True

    return has_single_milestone_e_record_add(milestone_e_records_added_by(add_commit))


class MilestoneEValidationSourceHeadAlignmentTests(unittest.TestCase):
    def test_every_milestone_e_validation_record_has_one_source_head_line(self) -> None:
        records = validation_records()

        self.assertGreater(len(records), 0)
        for record in records:
            self.assertEqual(1, len(source_heads(record)), str(record.relative_to(ROOT)))

    def test_source_head_lines_resolve_when_history_contains_source_commits(self) -> None:
        for record in validation_records():
            [source_head] = source_heads(record)

            self.assertRegex(source_head, r"^[0-9a-f]{7,40}$", str(record.relative_to(ROOT)))
            resolved_source_head = try_resolve_commit(source_head)
            if resolved_source_head is None:
                self.assertFalse(
                    can_infer_source_head_from_add_parent(record),
                    str(record.relative_to(ROOT)),
                )
            else:
                self.assertEqual(40, len(resolved_source_head), str(record.relative_to(ROOT)))

    def test_source_head_matches_parent_when_checked_out_history_preserves_record_add(self) -> None:
        current_head = resolve_commit("HEAD")

        for record in validation_records():
            [source_head] = source_heads(record)
            add_commit = introducing_commit(record)

            if add_commit is None:
                expected_source_head = current_head
            elif can_infer_source_head_from_add_parent(record):
                expected_source_head = resolve_commit(f"{add_commit}^")
            else:
                continue

            resolved_source_head = try_resolve_commit(source_head)
            self.assertIsNotNone(resolved_source_head, str(record.relative_to(ROOT)))
            self.assertEqual(
                expected_source_head,
                resolved_source_head,
                str(record.relative_to(ROOT)),
            )

    def test_squash_added_record_batches_do_not_infer_source_head_from_merge_parent(self) -> None:
        self.assertTrue(
            has_single_milestone_e_record_add(
                ("docs/validation/milestone-e-example-validation-2026-06-20.md",)
            ),
            "single-record additions preserve a specific parent source-head relationship",
        )

        self.assertFalse(
            has_single_milestone_e_record_add(
                (
                    "docs/validation/milestone-e-example-one-validation-2026-06-20.md",
                    "docs/validation/milestone-e-example-two-validation-2026-06-20.md",
                )
            ),
            "batch-added records model a squash/import shape where parent inference is unavailable",
        )

    def test_scope_status_and_roadmap_name_validation_source_head_alignment(self) -> None:
        for path in (PREP_SCOPE, EXECUTION_STATUS, ROADMAP):
            normalized = " ".join(path.read_text(encoding="utf-8").split())

            self.assertIn("validation-record source-head alignment", normalized, str(path))
            self.assertIn("Validated source HEAD before this record", normalized, str(path))
            self.assertIn("does not resolve or soften blockers", normalized, str(path))

    def test_make_target_runs_source_head_guard_after_validation_record_index(self) -> None:
        block = target_block("milestone-e-prep")

        index_record_guard = "$(PYTHON) .github/scripts/test_milestone_e_validation_record_index_validation_record.py"
        source_head_guard = "$(PYTHON) .github/scripts/test_milestone_e_validation_source_head_alignment.py"
        source_head_record_guard = (
            "$(PYTHON) .github/scripts/test_milestone_e_validation_source_head_alignment_validation_record.py"
        )
        sequence_guard = "$(PYTHON) .github/scripts/test_milestone_e_prep_guard_sequence_index.py"

        self.assertIn(source_head_guard, block)
        self.assertIn(source_head_record_guard, block)
        self.assertLess(block.index(index_record_guard), block.index(source_head_guard))
        self.assertLess(block.index(source_head_guard), block.index(source_head_record_guard))
        self.assertLess(block.index(source_head_record_guard), block.index(sequence_guard))
        self.assertLess(block.index(source_head_record_guard), block.index("git diff --check"))

    def test_ci_runs_source_head_guard_once_in_order(self) -> None:
        text = CI_WORKFLOW.read_text(encoding="utf-8")
        index_record_guard = "python3 .github/scripts/test_milestone_e_validation_record_index_validation_record.py"
        source_head_guard = "python3 .github/scripts/test_milestone_e_validation_source_head_alignment.py"
        source_head_record_guard = (
            "python3 .github/scripts/test_milestone_e_validation_source_head_alignment_validation_record.py"
        )
        sequence_guard = "python3 .github/scripts/test_milestone_e_prep_guard_sequence_index.py"

        self.assertIn(source_head_guard, text)
        self.assertIn(source_head_record_guard, text)
        self.assertEqual(1, text.count(source_head_guard))
        self.assertEqual(1, text.count(source_head_record_guard))
        self.assertLess(text.index(index_record_guard), text.index(source_head_guard))
        self.assertLess(text.index(source_head_guard), text.index(source_head_record_guard))
        self.assertLess(text.index(source_head_record_guard), text.index(sequence_guard))

    def test_ci_source_head_guard_has_full_history_checkout(self) -> None:
        text = CI_WORKFLOW.read_text(encoding="utf-8")
        test_job_start = text.index("  test:\n")
        next_job_start = text.index("\n  verify-portability:", test_job_start)
        test_job = text[test_job_start:next_job_start]
        source_head_guard = "python3 .github/scripts/test_milestone_e_validation_source_head_alignment.py"
        full_history_checkout = (
            "- uses: actions/checkout@v4\n"
            "        with:\n"
            "          fetch-depth: 0"
        )

        self.assertIn(full_history_checkout, test_job)
        self.assertLess(test_job.index("fetch-depth: 0"), test_job.index(source_head_guard))

    def test_validation_records_avoid_scope_expansion_language(self) -> None:
        text = "\n".join(
            record.read_text(encoding="utf-8").lower()
            for record in validation_records()
        )

        for phrase in FORBIDDEN_RECORD_WORDING:
            self.assertNotIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
