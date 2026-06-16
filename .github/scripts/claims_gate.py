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

"""Claims-discipline grep gate (plan §12; PRD §11.3, §14, §1.4).

Scans MARKETING SURFACES (allowlist below) for banned claim phrases. Policy documents that
quote these phrases as prohibitions (PRD, plan, benchmark plan, governance, contributing,
determinism contract, schema descriptions) are deliberately not scanned — the gate exists
for surfaces users read as claims.

Add new marketing surfaces (announcements/, blog posts, binding READMEs) to SURFACES as
they appear. Exit 1 on any hit.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

SURFACES = [
    "README.md",
    "docs/roadmap.md",
    "docs/landscape-log.md",
    "examples",
    "announcements",
    "bindings",
    "crates/ethos-cli/README.md",
]

BANNED = [
    (re.compile(r"#1\b"), '"#1" claim'),
    (re.compile(r"best[- ]in[- ]class", re.I), '"best-in-class" claim'),
    (re.compile(r"pixel[- ]level proof", re.I), '"pixel-level proof" claim'),
    (re.compile(r"semantic proof", re.I), '"semantic proof" claim'),
    (re.compile(r"arithmetic proof", re.I), '"arithmetic proof" claim'),
    (re.compile(r"largest (public )?failure corpus", re.I), "unearned failure-corpus claim"),
    (re.compile(r"world[- ]?class", re.I), "superlative claim"),
    (re.compile(r"fastest\b", re.I), "speed superlative (needs reproducible benchmark + G1 pass)"),
    (re.compile(r"state[- ]of[- ]the[- ]art", re.I), "superlative claim"),
]

SCAN_SUFFIXES = {".md", ".txt", ".html", ".py", ".rs", ".ts", ".js", ".ipynb"}

hits = 0
for surface in SURFACES:
    path = ROOT / surface
    if not path.exists():
        continue
    files = [path] if path.is_file() else [
        p for p in path.rglob("*") if p.is_file() and p.suffix in SCAN_SUFFIXES
    ]
    for f in files:
        try:
            text = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for pattern, label in BANNED:
                if pattern.search(line):
                    print(f"CLAIMS-GATE {f.relative_to(ROOT)}:{lineno}: {label}: {line.strip()[:120]}")
                    hits += 1

if hits:
    print(f"\n{hits} banned claim phrase(s). Numbers come from reproducible harness JSON or not at all.")
    sys.exit(1)
print("claims gate green")
