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

import copy
import json
from pathlib import Path
import unittest

from table_model_validation import diagnose_table_model

ROOT = Path(__file__).resolve().parents[1]
DOCUMENT_EXAMPLE = ROOT / "schemas" / "examples" / "document.example.json"


def valid_payload() -> dict:
    return copy.deepcopy(json.loads(DOCUMENT_EXAMPLE.read_text(encoding="utf-8"))["payload"])


def cell(row: int, col: int, bbox: list[int], row_span: int = 1, col_span: int = 1) -> dict:
    return {
        "row": row,
        "col": col,
        "row_span": row_span,
        "col_span": col_span,
        "bbox": bbox,
        "text": f"{row},{col}",
    }


class TableModelValidationTests(unittest.TestCase):
    def test_valid_complete_grid_has_no_diagnostics(self) -> None:
        self.assertEqual(diagnose_table_model(valid_payload(), "fixture"), [])

    def test_header_rows_must_fit_table(self) -> None:
        payload = valid_payload()
        payload["tables"][0]["header_rows"] = 3

        self.assertEqual(
            diagnose_table_model(payload, "fixture")[:1],
            ["fixture: table t0001 header_rows 3 exceeds n_rows 2"],
        )

    def test_header_cols_must_fit_table(self) -> None:
        payload = valid_payload()
        payload["tables"][0]["header_cols"] = 3

        self.assertEqual(
            diagnose_table_model(payload, "fixture")[:1],
            ["fixture: table t0001 header_cols 3 exceeds n_cols 2"],
        )

    def test_cell_row_must_fit_table_dimensions(self) -> None:
        payload = valid_payload()
        payload["tables"][0]["cells"][0]["row"] = 2

        self.assertIn(
            "fixture: table t0001 cell[0] row 2 is outside n_rows 2",
            diagnose_table_model(payload, "fixture"),
        )

    def test_cell_col_must_fit_table_dimensions(self) -> None:
        payload = valid_payload()
        payload["tables"][0]["cells"][0]["col"] = 2

        self.assertIn(
            "fixture: table t0001 cell[0] col 2 is outside n_cols 2",
            diagnose_table_model(payload, "fixture"),
        )

    def test_cell_row_span_must_fit_table_dimensions(self) -> None:
        payload = valid_payload()
        payload["tables"][0]["cells"][2]["row_span"] = 2

        self.assertIn(
            "fixture: table t0001 cell[2] row_span 2 from row 1 exceeds n_rows 2",
            diagnose_table_model(payload, "fixture"),
        )

    def test_cell_col_span_must_fit_table_dimensions(self) -> None:
        payload = valid_payload()
        payload["tables"][0]["cells"][3]["col_span"] = 2

        self.assertIn(
            "fixture: table t0001 cell[3] col_span 2 from col 1 exceeds n_cols 2",
            diagnose_table_model(payload, "fixture"),
        )

    def test_cell_bbox_must_stay_inside_table_bbox(self) -> None:
        payload = valid_payload()
        payload["tables"][0]["cells"][0]["bbox"] = [-1, 0, 100, 50]

        self.assertIn(
            "fixture: table t0001 cell[0] bbox is outside table bbox",
            diagnose_table_model(payload, "fixture"),
        )

    def test_overlapping_cell_coverage_fails_closed(self) -> None:
        payload = valid_payload()
        payload["tables"][0]["cells"][1]["col"] = 0

        self.assertIn(
            "fixture: table t0001 cell[1] overlaps covered slot (0,0) already covered by cell[0]",
            diagnose_table_model(payload, "fixture"),
        )

    def test_missing_cell_coverage_fails_closed(self) -> None:
        payload = valid_payload()
        payload["tables"][0]["cells"] = payload["tables"][0]["cells"][:-1]

        self.assertIn(
            "fixture: table t0001 missing cell coverage at (1,1)",
            diagnose_table_model(payload, "fixture"),
        )

    def test_spanned_cells_can_cover_multiple_grid_slots(self) -> None:
        payload = valid_payload()
        payload["tables"][0]["cells"] = [
            cell(0, 0, [7200, 13000, 54000, 16500], col_span=2),
            cell(1, 0, [7200, 16500, 30600, 20000]),
            cell(1, 1, [30600, 16500, 54000, 20000]),
        ]

        self.assertEqual(diagnose_table_model(copy.deepcopy(payload), "fixture"), [])


if __name__ == "__main__":
    unittest.main()
