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

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from llama_index.core.schema import NodeWithScore, TextNode


ROOT = Path(__file__).resolve().parents[2]
SHARED = ROOT / "examples/citation-emission"
PYTHON_PACKAGE = ROOT / "python"
for path in [SHARED, PYTHON_PACKAGE]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from ethos_pdf import emit_llamaindex_citations  # noqa: E402
from framework_example import run_example  # noqa: E402


def build_results(records: list[dict[str, Any]]) -> list[NodeWithScore]:
    return [
        NodeWithScore(
            node=TextNode(text=record["text"], metadata=record["metadata"]),
            score=1.0,
        )
        for record in records
    ]


if __name__ == "__main__":
    raise SystemExit(
        run_example("llamaindex", build_results, emit_llamaindex_citations)
    )
