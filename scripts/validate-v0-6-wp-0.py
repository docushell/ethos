#!/usr/bin/env python3
"""Run the WP-0 mapping feasibility proof against the pinned ODL 2.5.0 result."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures/foreign/opendataloader/real"
OUTPUT_PATH = FIXTURE / "opendataloader-2.5.0-output.json"
PAGE_METADATA_PATH = FIXTURE / "wp0-page-metadata.json"
SOURCE_PATH = FIXTURE / "source.pdf"
EXPECTED_VENDOR_VERSION = "2.5.0"
EXPECTED_VENDOR_SHA256 = "516ce47832a6726e87cb17db77c20174ca8cabbe9a6b56db1418babc7c9ddcba"
EXPECTED_SOURCE_SHA256 = "082f9f8c800fda43b13d097ccf3a603e1f8048987fb497fd2be4cba6817001ee"
EXPECTED_OUTPUT_SHA256 = "9f9b8f8d331750a26aebd40a916c8e169647bb76d0232c76549c79274b514ec1"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def quantize_points(value: float) -> int:
    scaled = value * 100
    return math.floor(scaled + 0.5) if scaled >= 0 else math.ceil(scaled - 0.5)


def mapped_bbox(raw: list[float], page_height: int) -> list[int]:
    x0, y0, x1, y1 = raw
    return [
        quantize_points(x0),
        quantize_points(page_height - y1),
        quantize_points(x1),
        quantize_points(page_height - y0),
    ]


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n").encode()


def run(vendor_jar: Path | None, vendor_version_file: Path | None) -> dict[str, object]:
    source_hash = sha256(SOURCE_PATH)
    output_hash = sha256(OUTPUT_PATH)
    metadata = json.loads(PAGE_METADATA_PATH.read_text(encoding="utf-8"))
    parser_output = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
    pages = metadata["pages"]
    page_by_index = {page["index"]: page for page in pages}
    kids = parser_output.get("kids", [])

    vendor_hash = sha256(vendor_jar) if vendor_jar else None
    vendor_version = vendor_version_file.read_text(encoding="utf-8").strip() if vendor_version_file else None
    vendor_verified = (
        vendor_hash == EXPECTED_VENDOR_SHA256
        and (vendor_version is None or vendor_version == EXPECTED_VENDOR_VERSION)
    )

    elements = []
    for item in kids:
        page_index = item["page number"]
        page = page_by_index[page_index]
        elements.append({
            "id": f"odl-{item['id']}",
            "page": f"page-{page_index}",
            "bbox": mapped_bbox(item["bounding box"], page["height"]),
            "kind": str(item["type"]).lower(),
            "text": item["content"],
        })

    mapped = {
        "artifact_type": "ethos.grounding.v1",
        "schema_version": "1.0.0",
        "source": {"media_type": "application/pdf", "sha256": f"sha256:{source_hash}"},
        "producer": {"name": "opendataloader-pdf", "version": EXPECTED_VENDOR_VERSION},
        "capabilities": {"spans": False, "char_offsets": False, "tables": False},
        "coordinate_system": {"unit": "centipoint", "origin": "top-left"},
        "pages": [
            {
                "id": f"page-{page['index']}",
                "index": page["index"],
                "width": quantize_points(page["width"]),
                "height": quantize_points(page["height"]),
                "rotation": page["rotation"],
            }
            for page in pages
        ],
        "elements": elements,
    }
    mapped_hash = hashlib.sha256(canonical_bytes(mapped)).hexdigest()
    passed = (
        vendor_verified
        and source_hash == EXPECTED_SOURCE_SHA256
        and output_hash == EXPECTED_OUTPUT_SHA256
        and metadata["source_pdf_sha256"] == EXPECTED_SOURCE_SHA256
        and metadata["origin"] == "bottom-left"
        and all(item["page number"] in page_by_index for item in kids)
        and all(item["id"] is not None for item in kids)
    )
    return {
        "status": "passed" if passed else "blocked",
        "parser": "opendataloader-pdf",
        "parser_version": EXPECTED_VENDOR_VERSION,
        "vendor_jar_sha256": vendor_hash,
        "vendor_jar_sha256_matches": vendor_hash == EXPECTED_VENDOR_SHA256,
        "vendor_version_file": vendor_version,
        "source_pdf_sha256": source_hash,
        "source_pdf_sha256_matches": source_hash == EXPECTED_SOURCE_SHA256,
        "parser_output_sha256": output_hash,
        "parser_output_sha256_matches": output_hash == EXPECTED_OUTPUT_SHA256,
        "page_geometry_source": "source PDF sidecar bound to source_pdf_sha256",
        "coordinate_conversion": "bottom-left points -> top-left centipoints using page height",
        "mapped_artifact_sha256": mapped_hash,
        "mapped_artifact": mapped,
        "decision": (
            "mapping feasible; WP-0 evidence is ready for manual ADR and posture review"
            if passed
            else "stop before schema freeze; run with the pinned DocuShell vendor JAR"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--vendor-jar", type=Path)
    parser.add_argument("--vendor-version-file", type=Path)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result = run(args.vendor_jar, args.vendor_version_file)
    args.output.write_bytes(canonical_bytes(result))
    print(args.output)
    return 0 if result["status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
