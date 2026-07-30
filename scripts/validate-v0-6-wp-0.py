#!/usr/bin/env python3
"""Run the WP-0 mapping feasibility check against the pinned real parser output."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures/foreign/opendataloader/real"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run() -> dict[str, object]:
    manifest = json.loads((FIXTURE / "manifest.json").read_text(encoding="utf-8"))
    output_path = FIXTURE / manifest["output_json"]
    source_path = FIXTURE / manifest["source_pdf"]
    output = json.loads(output_path.read_text(encoding="utf-8"))
    kids = output.get("kids", [])
    gaps = [
        "page dimensions are absent from parser output",
        "coordinate origin is absent from parser output",
    ]
    result = {
        "status": "blocked",
        "parser": manifest["parser"],
        "parser_version": manifest["version"],
        "source_pdf_sha256_matches_manifest": sha256(source_path) == manifest["source_pdf_sha256"],
        "output_json_sha256_matches_manifest": sha256(output_path) == manifest["output_json_sha256"],
        "mapped_element_count": len(kids),
        "stable_source_ids_present": all(isinstance(item.get("id"), int) for item in kids),
        "deterministic_order_present": all(item.get("page number") == 1 for item in kids),
        "capabilities": {"tables": False},
        "gaps": gaps,
        "decision": "stop before schema freeze; do not invent geometry, origin, or capabilities",
    }
    if not result["source_pdf_sha256_matches_manifest"] or not result["output_json_sha256_matches_manifest"]:
        raise SystemExit("pinned fixture hash mismatch")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(run(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
