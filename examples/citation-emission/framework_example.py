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

"""Shared offline runner for the LangChain and LlamaIndex examples."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable


EXAMPLE_DIR = Path(__file__).resolve().parent
ROOT = EXAMPLE_DIR.parents[1]
PYTHON_PACKAGE = ROOT / "python"
if str(PYTHON_PACKAGE) not in sys.path:
    sys.path.insert(0, str(PYTHON_PACKAGE))

from ethos_pdf import citation_json_bytes  # noqa: E402


CASES = {
    "grounded": ("model-output.grounded.json", 0),
    "fabricated": ("model-output.fabricated-quote.json", 1),
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def retrieval_records() -> list[dict[str, Any]]:
    chunks_path = ROOT / "schemas/examples/chunks.example.jsonl"
    chunks = [json.loads(line) for line in chunks_path.read_text().splitlines() if line]
    records = []
    for chunk in chunks:
        metadata = {
            "document_fingerprint": chunk["document_fingerprint"],
            "page_refs": chunk["page_refs"],
            "element_refs": chunk["element_refs"],
        }
        if chunk["id"] == "c000002":
            # Table coordinates must be explicitly exposed; the helper never infers them.
            metadata["table_cells"] = [{"table_id": "t0001", "row": 1, "col": 1}]
        records.append({"text": chunk["text"], "metadata": metadata})
    return records


def run_example(
    framework: str,
    build_results: Callable[[list[dict[str, Any]]], list[Any]],
    emit_citations: Callable[..., dict[str, Any]],
) -> int:
    parser = argparse.ArgumentParser(
        description=f"Run the offline Ethos {framework} citation-emission example."
    )
    parser.add_argument("--case", choices=sorted(CASES), default="fabricated")
    parser.add_argument("--ethos-bin", type=Path, default=ROOT / "target/debug/ethos")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / f"target/rag-framework-examples/{framework}",
    )
    args = parser.parse_args()

    if not args.ethos_bin.is_file():
        parser.error(f"Ethos CLI not found: {args.ethos_bin}; run cargo build -p ethos-cli")

    model_file, expected_exit = CASES[args.case]
    model_output = load_json(EXAMPLE_DIR / model_file)
    results = build_results(retrieval_records())
    citations = emit_citations(results, model_output["answer"], model_output["claims"])

    case_dir = args.out_dir / args.case
    case_dir.mkdir(parents=True, exist_ok=True)
    citations_path = case_dir / "citations.json"
    report_path = case_dir / "verification-report.json"
    citations_path.write_bytes(citation_json_bytes(citations))
    if report_path.exists():
        report_path.unlink()

    completed = subprocess.run(
        [
            str(args.ethos_bin),
            "verify",
            str(ROOT / "schemas/examples/document.example.json"),
            "--citations",
            str(citations_path),
            "--fail-on-ungrounded",
            "--out",
            str(report_path),
        ],
        check=False,
        text=True,
        capture_output=True,
    )
    if completed.returncode != expected_exit or not report_path.is_file():
        sys.stderr.write(completed.stderr)
        sys.stderr.write(
            f"expected verifier exit {expected_exit} with a report; "
            f"received {completed.returncode}\n"
        )
        return 2
    return completed.returncode
