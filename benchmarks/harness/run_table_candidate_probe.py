#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "ethos-table-candidate-probe-v1"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Ethos' internal table-candidate probe over selected PDFs."
    )
    parser.add_argument("--ethos-bin", type=Path, required=True)
    parser.add_argument("--pdf-root", type=Path, required=True)
    parser.add_argument("--doc-id", action="append", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path)
    parser.add_argument("--expected-markdown-dir", type=Path)
    parser.add_argument("--timeout-sec", type=int, default=120)
    return parser.parse_args(argv)


def run_command(
    command: list[str],
    *,
    env: dict[str, str] | None,
    timeout_sec: int,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        env=env,
        timeout=timeout_sec,
    )


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def candidate_markdown(report: dict[str, Any]) -> str:
    return "\n".join(table.get("markdown", "") for table in report.get("tables", []))


def expected_markdown_record(expected_dir: Path | None, doc_id: str, candidate: str) -> dict[str, Any]:
    if expected_dir is None:
        return {
            "available": False,
            "exact_match": None,
            "path": None,
            "sha256": None,
        }

    path = expected_dir / f"{doc_id}.md"
    if not path.exists():
        return {
            "available": False,
            "exact_match": None,
            "path": str(path),
            "sha256": None,
        }

    expected = path.read_text(encoding="utf-8")
    return {
        "available": True,
        "exact_match": expected == candidate,
        "path": str(path),
        "sha256": sha256_text(expected),
    }


def probe_document(
    *,
    ethos_bin: Path,
    pdf_root: Path,
    doc_id: str,
    work_dir: Path,
    expected_markdown_dir: Path | None,
    timeout_sec: int,
) -> dict[str, Any]:
    pdf_path = pdf_root / f"{doc_id}.pdf"
    doc_json = work_dir / "documents" / f"{doc_id}.ethos.json"
    probe_json = work_dir / "probes" / f"{doc_id}.tables.json"
    doc_json.parent.mkdir(parents=True, exist_ok=True)
    probe_json.parent.mkdir(parents=True, exist_ok=True)

    parse = run_command(
        [
            str(ethos_bin),
            "doc",
            "parse",
            str(pdf_path),
            "--format",
            "json",
            "--out",
            str(doc_json),
        ],
        env=None,
        timeout_sec=timeout_sec,
    )
    if parse.returncode != 0:
        return {
            "doc_id": doc_id,
            "status": "fail",
            "stage": "parse",
            "pdf": str(pdf_path),
            "parse_returncode": parse.returncode,
            "stderr": parse.stderr,
        }

    env = os.environ.copy()
    env["ETHOS_INTERNAL_TABLE_CANDIDATE_PROBE"] = "1"
    probe = run_command(
        [
            str(ethos_bin),
            "__table-candidate-probe",
            str(doc_json),
            "--out",
            str(probe_json),
        ],
        env=env,
        timeout_sec=timeout_sec,
    )
    if probe.returncode != 0:
        return {
            "doc_id": doc_id,
            "status": "fail",
            "stage": "probe",
            "pdf": str(pdf_path),
            "document": str(doc_json),
            "probe_returncode": probe.returncode,
            "stderr": probe.stderr,
        }

    report = read_json(probe_json)
    markdown = candidate_markdown(report)
    expected = expected_markdown_record(expected_markdown_dir, doc_id, markdown)

    return {
        "doc_id": doc_id,
        "status": "pass",
        "pdf": str(pdf_path),
        "pdf_sha256": sha256_file(pdf_path),
        "document": str(doc_json),
        "document_sha256": sha256_file(doc_json),
        "probe_report": str(probe_json),
        "probe_report_sha256": sha256_file(probe_json),
        "candidate_markdown_sha256": sha256_text(markdown),
        "expected_markdown": expected,
        "tables_total": report.get("summary", {}).get("tables_total", 0),
    }


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    work_dir = args.work_dir or (args.out.parent / f"{args.out.stem}-work")
    work_dir.mkdir(parents=True, exist_ok=True)

    documents = [
        probe_document(
            ethos_bin=args.ethos_bin,
            pdf_root=args.pdf_root,
            doc_id=doc_id,
            work_dir=work_dir,
            expected_markdown_dir=args.expected_markdown_dir,
            timeout_sec=args.timeout_sec,
        )
        for doc_id in args.doc_id
    ]

    passed = [doc for doc in documents if doc["status"] == "pass"]
    compared = [
        doc
        for doc in passed
        if doc.get("expected_markdown", {}).get("available") is True
    ]
    exact_matches = [
        doc
        for doc in compared
        if doc.get("expected_markdown", {}).get("exact_match") is True
    ]

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ethos_bin": str(args.ethos_bin),
        "pdf_root": str(args.pdf_root),
        "work_dir": str(work_dir),
        "summary": {
            "documents_total": len(documents),
            "documents_passed": len(passed),
            "documents_failed": len(documents) - len(passed),
            "candidate_tables_total": sum(int(doc.get("tables_total", 0)) for doc in passed),
            "expected_markdown_compared": len(compared),
            "expected_markdown_exact_matches": len(exact_matches),
        },
        "documents": documents,
    }


def main() -> None:
    args = parse_args()
    report = build_report(args)
    write_json(args.out, report)
    print(f"table candidate probe: {report['summary']}")


if __name__ == "__main__":
    main()
