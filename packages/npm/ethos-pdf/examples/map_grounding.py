#!/usr/bin/env python3
"""Map one pinned parser result into the strict Ethos Grounding JSON contract."""

from __future__ import annotations

import json
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


def centipoints(value: object) -> int:
    return int((Decimal(str(value)) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def map_grounding(parser: dict, metadata: dict) -> dict:
    page = metadata["pages"][0]
    elements = []
    for item in parser["kids"]:
        left, bottom, right, top = item["bounding box"]
        elements.append(
            {
                "id": f"element-{item['id']}",
                "page": f"page-{item['page number']}",
                "bbox": [
                    centipoints(left),
                    centipoints(Decimal(str(page["height"])) - Decimal(str(top))),
                    centipoints(right),
                    centipoints(Decimal(str(page["height"])) - Decimal(str(bottom))),
                ],
                "kind": "heading" if item["type"] == "heading" else "text_block",
                "text": item["content"],
            }
        )
    return {
        "artifact_type": "ethos.grounding.v1",
        "schema_version": "1.0.0",
        "source": {
            "media_type": "application/pdf",
            "sha256": f"sha256:{metadata['source_pdf_sha256']}",
        },
        "producer": {"name": "opendataloader-mapper-example", "version": "1.0.0"},
        "capabilities": {"spans": False, "char_offsets": False, "tables": False},
        "coordinate_system": {"unit": "centipoint", "origin": "top-left"},
        "pages": [
            {
                "id": f"page-{entry['index']}",
                "index": entry["index"],
                "width": centipoints(entry["width"]),
                "height": centipoints(entry["height"]),
                "rotation": entry["rotation"],
            }
            for entry in metadata["pages"]
        ],
        "elements": elements,
    }


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        print("usage: map_grounding.py parser-output.json page-metadata.json output.json", file=sys.stderr)
        return 2
    parser = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    metadata = json.loads(Path(argv[2]).read_text(encoding="utf-8"))
    Path(argv[3]).write_text(json.dumps(map_grounding(parser, metadata), ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
