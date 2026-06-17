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

from typing import Any


def diagnose_table_model(payload: dict[str, Any], label: str = "document.example.json") -> list[str]:
    """Return deterministic diagnostics for table/cell invariants JSON Schema cannot express."""
    diagnostics: list[str] = []
    for table in payload.get("tables", []):
        table_id = table.get("id", "<unknown>")
        n_rows = table.get("n_rows")
        n_cols = table.get("n_cols")
        header_rows = table.get("header_rows", 0)
        header_cols = table.get("header_cols", 0)

        if not isinstance(n_rows, int) or not isinstance(n_cols, int):
            continue
        if not isinstance(header_rows, int) or not isinstance(header_cols, int):
            continue

        if header_rows > n_rows:
            diagnostics.append(
                f"{label}: table {table_id} header_rows {header_rows} exceeds n_rows {n_rows}"
            )
        if header_cols > n_cols:
            diagnostics.append(
                f"{label}: table {table_id} header_cols {header_cols} exceeds n_cols {n_cols}"
            )

        coverage: dict[tuple[int, int], int] = {}
        for cell_index, cell in enumerate(table.get("cells", [])):
            row = cell.get("row")
            col = cell.get("col")
            row_span = cell.get("row_span")
            col_span = cell.get("col_span")
            if not all(isinstance(v, int) for v in [row, col, row_span, col_span]):
                continue

            context = f"table {table_id} cell[{cell_index}]"
            if row >= n_rows:
                diagnostics.append(
                    f"{label}: {context} row {row} is outside n_rows {n_rows}"
                )
                continue
            if col >= n_cols:
                diagnostics.append(
                    f"{label}: {context} col {col} is outside n_cols {n_cols}"
                )
                continue
            if row + row_span > n_rows:
                diagnostics.append(
                    f"{label}: {context} row_span {row_span} from row {row} exceeds n_rows {n_rows}"
                )
                continue
            if col + col_span > n_cols:
                diagnostics.append(
                    f"{label}: {context} col_span {col_span} from col {col} exceeds n_cols {n_cols}"
                )
                continue

            if not bbox_contains(table.get("bbox"), cell.get("bbox")):
                diagnostics.append(f"{label}: {context} bbox is outside table bbox")

            for r in range(row, row + row_span):
                for c in range(col, col + col_span):
                    covered_by = coverage.get((r, c))
                    if covered_by is not None:
                        diagnostics.append(
                            f"{label}: {context} overlaps covered slot ({r},{c}) "
                            f"already covered by cell[{covered_by}]"
                        )
                    else:
                        coverage[(r, c)] = cell_index

        for r in range(n_rows):
            for c in range(n_cols):
                if (r, c) not in coverage:
                    diagnostics.append(
                        f"{label}: table {table_id} missing cell coverage at ({r},{c})"
                    )
    return diagnostics


def bbox_contains(outer: Any, inner: Any) -> bool:
    if not (is_bbox(outer) and is_bbox(inner)):
        return True
    return (
        inner[0] >= outer[0]
        and inner[1] >= outer[1]
        and inner[2] <= outer[2]
        and inner[3] <= outer[3]
    )


def is_bbox(value: Any) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 4
        and all(isinstance(coord, int) for coord in value)
    )
