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

import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
VALIDATOR_PATH = ROOT / "validate_fixtures.py"


def load_validator_module():
    spec = importlib.util.spec_from_file_location(
        "validate_fixtures_under_test",
        VALIDATOR_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {VALIDATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(io.StringIO()):
        spec.loader.exec_module(module)
    return module


VALIDATOR = load_validator_module()


class FixtureValidatorTableRefTests(unittest.TestCase):
    def setUp(self) -> None:
        VALIDATOR.failures = 0

    def tearDown(self) -> None:
        VALIDATOR.failures = 0

    def test_table_refs_reject_unknown_page_refs(self) -> None:
        failures, output = self.validate_table_refs(
            [{"id": "t0001", "page_refs": ["p9999"], "cells": [self.cited_cell()]}],
        )

        self.assertEqual(failures, 1)
        self.assertIn("tables.json tables[0] references unknown page 'p9999'", output)

    def test_table_refs_reject_unknown_warning_refs(self) -> None:
        failures, output = self.validate_table_refs(
            [
                {
                    "id": "t0001",
                    "page_refs": ["p0001"],
                    "warning_refs": ["w9999"],
                    "cells": [self.cited_cell()],
                }
            ],
        )

        self.assertEqual(failures, 1)
        self.assertIn(
            "tables.json tables[0] references unknown warning 'w9999'",
            output,
        )

    def test_table_refs_reject_unknown_span_refs(self) -> None:
        failures, output = self.validate_table_refs(
            [
                {
                    "id": "t0001",
                    "page_refs": ["p0001"],
                    "cells": [{"span_refs": ["s999999"], "element_refs": ["e000001"]}],
                }
            ],
        )

        self.assertEqual(failures, 1)
        self.assertIn(
            "tables.json tables[0] cell[0] references unknown span 's999999'",
            output,
        )

    def test_table_refs_reject_unknown_element_refs(self) -> None:
        failures, output = self.validate_table_refs(
            [
                {
                    "id": "t0001",
                    "page_refs": ["p0001"],
                    "cells": [{"span_refs": ["s000001"], "element_refs": ["e999999"]}],
                }
            ],
        )

        self.assertEqual(failures, 1)
        self.assertIn(
            "tables.json tables[0] cell[0] references unknown element 'e999999'",
            output,
        )

    def test_table_refs_reject_cells_without_grounding_refs(self) -> None:
        failures, output = self.validate_table_refs(
            [{"id": "t0001", "page_refs": ["p0001"], "cells": [{}]}],
        )

        self.assertEqual(failures, 1)
        self.assertIn(
            "tables.json tables[0] cell[0] in table t0001 must cite span_refs or element_refs",
            output,
        )

    def test_non_table_fixture_rejects_committed_table_golden(self) -> None:
        with tempfile.TemporaryDirectory(dir=VALIDATOR.ROOT) as tempdir:
            fixture_dir = Path(tempdir)
            (fixture_dir / VALIDATOR.TABLE_GOLDEN).write_text("[]\n", encoding="utf-8")

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                VALIDATOR.validate_table_goldens(
                    fixture_dir,
                    {"subsets": ["layout"]},
                    {"pages": [], "spans": []},
                    {"elements": []},
                )

        self.assertEqual(VALIDATOR.failures, 1)
        self.assertIn(
            "tables.json exists but fixture is not tagged tables",
            output.getvalue(),
        )

    def test_table_fixture_requires_table_golden(self) -> None:
        with tempfile.TemporaryDirectory(dir=VALIDATOR.ROOT) as tempdir:
            fixture_dir = Path(tempdir)

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                VALIDATOR.validate_table_goldens(
                    fixture_dir,
                    {"subsets": ["tables"]},
                    {"pages": [], "spans": []},
                    {"elements": []},
                )

        self.assertEqual(VALIDATOR.failures, 1)
        self.assertIn("tables.json missing for tables fixture", output.getvalue())

    def test_table_ref_arrays_reject_malformed_refs(self) -> None:
        failures, output = self.validate_table_refs(
            [{"id": "t0001", "page_refs": "p0001", "cells": [self.cited_cell()]}],
        )

        self.assertEqual(failures, 1)
        self.assertIn("tables.json tables[0].page_refs must be an array", output)

        VALIDATOR.failures = 0

        failures, output = self.validate_table_refs(
            [
                {
                    "id": "t0001",
                    "page_refs": ["p0001"],
                    "cells": [{"span_refs": [""], "element_refs": ["e000001"]}],
                }
            ],
        )

        self.assertEqual(failures, 1)
        self.assertIn(
            "tables.json tables[0] cell[0].span_refs[0] must be a non-empty string",
            output,
        )

    def validate_table_refs(self, tables) -> tuple[int, str]:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            VALIDATOR.validate_table_refs(
                "tables.json",
                tables,
                {
                    "pages": [{"id": "p0001"}],
                    "spans": [{"id": "s000001"}],
                    "warnings": [{"id": "w0001"}],
                },
                {
                    "elements": [{"id": "e000001"}],
                    "warnings": [{"id": "w0002"}],
                },
            )
        return VALIDATOR.failures, output.getvalue()

    @staticmethod
    def cited_cell() -> dict[str, list[str]]:
        return {"span_refs": ["s000001"], "element_refs": ["e000001"]}


class FixtureValidatorRegionRefTests(unittest.TestCase):
    def setUp(self) -> None:
        VALIDATOR.failures = 0

    def tearDown(self) -> None:
        VALIDATOR.failures = 0

    def test_region_refs_reject_unknown_pages(self) -> None:
        failures, output = self.validate_regions(
            [
                {
                    "id": "r0001",
                    "page": "p9999",
                    "bbox": [10, 20, 30, 40],
                    "kind": "unknown",
                }
            ],
        )

        self.assertEqual(failures, 1)
        self.assertIn(
            "extraction.json regions[0] references unknown page 'p9999'",
            output,
        )

    def test_region_refs_reject_malformed_bbox(self) -> None:
        failures, output = self.validate_regions(
            [
                {
                    "id": "r0001",
                    "page": "p0001",
                    "bbox": [30, 20, 10, 40],
                    "kind": "unknown",
                }
            ],
        )

        self.assertEqual(failures, 1)
        self.assertIn(
            "extraction.json regions[0].bbox must satisfy x0<=x1 and y0<=y1",
            output,
        )

    def test_region_refs_reject_non_four_integer_bbox(self) -> None:
        cases = [
            [10, 20, 30],
            [10, 20, 30, 40.5],
            [10, True, 30, 40],
        ]
        for bbox in cases:
            with self.subTest(bbox=bbox):
                VALIDATOR.failures = 0
                failures, output = self.validate_regions(
                    [
                        {
                            "id": "r0001",
                            "page": "p0001",
                            "bbox": bbox,
                            "kind": "unknown",
                        }
                    ],
                )

                self.assertEqual(failures, 1)
                self.assertIn(
                    "extraction.json regions[0].bbox must be a four-integer array",
                    output,
                )

    def test_region_refs_reject_bbox_outside_page_bounds(self) -> None:
        failures, output = self.validate_regions(
            [
                {
                    "id": "r0001",
                    "page": "p0001",
                    "bbox": [10, 20, 1001, 40],
                    "kind": "unknown",
                }
            ],
        )

        self.assertEqual(failures, 1)
        self.assertIn(
            "extraction.json regions[0].bbox must stay within page bounds",
            output,
        )

    def test_region_refs_reject_unknown_warning_refs(self) -> None:
        failures, output = self.validate_regions(
            [
                {
                    "id": "r0001",
                    "page": "p0001",
                    "bbox": [10, 20, 30, 40],
                    "kind": "unknown",
                    "warning_refs": ["w9999"],
                }
            ],
        )

        self.assertEqual(failures, 1)
        self.assertIn(
            "extraction.json regions[0] references unknown warning 'w9999'",
            output,
        )

    def test_warning_refs_reject_unknown_region_refs(self) -> None:
        failures, output = self.validate_regions(
            [
                {
                    "id": "r0001",
                    "page": "p0001",
                    "bbox": [10, 20, 30, 40],
                    "kind": "unknown",
                }
            ],
            [{"id": "w0001", "region_ref": "r9999"}],
        )

        self.assertEqual(failures, 1)
        self.assertIn(
            "extraction.json warnings[0] references unknown region 'r9999'",
            output,
        )

    def test_region_refs_reject_duplicate_region_ids(self) -> None:
        failures, output = self.validate_regions(
            [
                {
                    "id": "r0001",
                    "page": "p0001",
                    "bbox": [10, 20, 30, 40],
                    "kind": "unknown",
                },
                {
                    "id": "r0001",
                    "page": "p0001",
                    "bbox": [50, 60, 70, 80],
                    "kind": "unknown",
                },
            ],
        )

        self.assertEqual(failures, 1)
        self.assertIn("extraction.json regions[1].id duplicates 'r0001'", output)

    def test_layout_element_region_refs_reject_unknown_regions(self) -> None:
        failures, output = self.validate_layout_region_refs(
            {"elements": [{"id": "e000001", "region_ref": "r9999"}], "warnings": []},
        )

        self.assertEqual(failures, 1)
        self.assertIn("layout.json elements[0] references unknown region 'r9999'", output)

    def test_layout_warning_region_refs_reject_unknown_regions(self) -> None:
        failures, output = self.validate_layout_region_refs(
            {"elements": [], "warnings": [{"id": "w0001", "region_ref": "r9999"}]},
        )

        self.assertEqual(failures, 1)
        self.assertIn("layout.json warnings[0] references unknown region 'r9999'", output)

    def test_valid_region_refs_are_accepted(self) -> None:
        failures, output = self.validate_regions(
            [
                {
                    "id": "r0001",
                    "page": "p0001",
                    "bbox": [10, 20, 30, 40],
                    "kind": "unknown",
                    "warning_refs": ["w0001"],
                }
            ],
            [{"id": "w0001", "region_ref": "r0001"}],
        )

        self.assertEqual(failures, 0)
        self.assertEqual(output, "")

    def validate_regions(self, regions, warnings=None) -> tuple[int, str]:
        extraction = {
            "pages": [{"id": "p0001", "width": 1000, "height": 1000}],
            "regions": regions,
            "warnings": warnings or [{"id": "w0001"}],
        }
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            VALIDATOR.validate_extraction_region_refs("extraction.json", extraction)
        return VALIDATOR.failures, output.getvalue()

    def validate_layout_region_refs(self, layout) -> tuple[int, str]:
        extraction = {
            "regions": [
                {"id": "r0001", "page": "p0001", "bbox": [10, 20, 30, 40]}
            ],
        }
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            VALIDATOR.validate_layout_region_refs("layout.json", layout, extraction)
        return VALIDATOR.failures, output.getvalue()


if __name__ == "__main__":
    unittest.main()
