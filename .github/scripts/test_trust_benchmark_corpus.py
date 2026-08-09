#!/usr/bin/env python3
"""Validate NIP-3.1 corpus structure, determinism, integrity, and verifier labels."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path


EXPECTED_CATEGORIES = {
    "grounded",
    "fabricated-quote",
    "wrong-page",
    "paraphrase-drift",
    "split-quote",
    "stale-fingerprint",
    "capability-limited",
}


def fail(message: str) -> None:
    raise SystemExit(f"trust benchmark corpus: {message}")


def file_tree(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=False, capture_output=True, text=True)


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, separators=(",", ":"), sort_keys=True) + "\n", encoding="utf-8")


def citation(check: dict) -> dict:
    value = {"kind": check["kind"], "citation": check["citation"]}
    if "text" in check:
        value["text"] = check["text"]
    return value


def verify_run(
    ethos: Path,
    source: Path,
    fingerprint: str,
    checks: list[dict],
    work: Path,
    name: str,
    *,
    stale: bool = False,
    crop_capability: bool = False,
) -> None:
    citations_path = work / f"{name}.citations.json"
    report_path = work / f"{name}.report.json"
    envelope_fingerprint = f"sha256:{'0' * 64}" if stale else fingerprint
    write_json(citations_path, {
        "claims": [citation(check) for check in checks],
        "document_fingerprint": envelope_fingerprint,
    })
    command = [str(ethos), "verify", str(source), "--citations", str(citations_path), "--out", str(report_path)]
    if crop_capability:
        config = json.loads((Path(__file__).parents[2] / "schemas/examples/verification-config.example.json").read_text())
        config["evidence"]["include_crops"] = True
        config_path = work / f"{name}.config.json"
        write_json(config_path, config)
        command.extend(["--config", str(config_path)])
    result = run(command)
    if result.returncode != 0:
        fail(f"{name} verifier exited {result.returncode}: {result.stderr.strip()}")
    # verify emits an in-toto Statement; the report is its predicate
    report = json.loads(report_path.read_text())["predicate"]
    if len(report["checks"]) != len(checks):
        fail(f"{name} report check count drifted")
    for expected, actual in zip(checks, report["checks"]):
        if actual["status"] != expected["expected_status"]:
            fail(f"{name} {actual['id']} expected status {expected['expected_status']}, got {actual['status']}")
        if actual.get("reason") != expected["expected_reason"]:
            fail(f"{name} {actual['id']} expected reason {expected['expected_reason']}, got {actual.get('reason')}")
    if stale and not report["fingerprint_stale"]:
        fail(f"{name} did not fail closed on stale fingerprint")
    if crop_capability:
        if "missing_crop_support" not in report["capability_limits"]:
            fail(f"{name} omitted missing_crop_support")
        if "capability_limited" not in report["warnings"]:
            fail(f"{name} omitted capability_limited warning")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ethos", type=Path, default=Path("target/debug/ethos"))
    parser.add_argument("--fixtures", type=Path, default=Path("fixtures/trust-benchmark/v1"))
    args = parser.parse_args()
    root = Path(__file__).parents[2]
    generator = root / "fixtures/trust-benchmark/generate.py"
    fixtures = (root / args.fixtures).resolve() if not args.fixtures.is_absolute() else args.fixtures
    ethos = (root / args.ethos).resolve() if not args.ethos.is_absolute() else args.ethos
    if not ethos.is_file():
        fail(f"missing Ethos CLI: {ethos}")

    with tempfile.TemporaryDirectory() as temporary:
        temporary_root = Path(temporary)
        first = temporary_root / "first"
        second = temporary_root / "second"
        for output in (first, second):
            result = run([sys.executable, str(generator), "--output", str(output)])
            if result.returncode != 0:
                fail(f"generator failed: {result.stderr.strip()}")
        first_tree = file_tree(first)
        if first_tree != file_tree(second):
            fail("double-run outputs are not byte-identical")
        if first_tree != file_tree(fixtures):
            fail("committed v1 corpus differs from deterministic generator output")

        manifest = json.loads((fixtures / "manifest.json").read_text())
        documents = manifest["documents"]
        checks = [check for document in documents for check in document["checks"]]
        if len(documents) != 20 or manifest["document_count"] != 20:
            fail("expected exactly 20 documents")
        if len(checks) != 200 or manifest["check_count"] != 200:
            fail("expected exactly 200 checks")
        categories = Counter(check["category"] for check in checks)
        if set(categories) != EXPECTED_CATEGORIES:
            fail(f"category coverage drifted: {sorted(categories)}")

        review = json.loads((fixtures.parent / "review-record.json").read_text())
        spot_check = review["human_spot_check"]
        sampled = spot_check["checks"]
        if review["first_review"]["status"] != "complete" or review["second_review"]["status"] != "complete":
            fail("two-pass label review is incomplete")
        if spot_check["status"] != "complete" or len(sampled) != 40:
            fail("human spot-check must contain 40 completed checks")
        if spot_check["decision_counts"] != {"agree": 40, "corrected": 0}:
            fail("human spot-check decision counts do not match the accepted review")
        documents_by_id = {document["id"]: document for document in documents}
        sampled_categories = Counter()
        for sample_id in sampled:
            document_id, check_number = sample_id.rsplit("/", 1)
            document = documents_by_id.get(document_id)
            index = int(check_number) - 1
            if document is None or not 0 <= index < len(document["checks"]):
                fail(f"review sample does not resolve: {sample_id}")
            sampled_categories[document["checks"][index]["category"]] += 1
        if dict(sorted(sampled_categories.items())) != spot_check["category_counts"]:
            fail("human spot-check category counts drifted")
        if set(sampled_categories) != EXPECTED_CATEGORIES:
            fail("human spot-check no longer covers every required category")

        for document in documents:
            pdf = fixtures / document["source_pdf"]
            source = fixtures / document["source"]
            if hashlib.sha256(pdf.read_bytes()).hexdigest() != document["pdf_sha256"]:
                fail(f"{document['id']} PDF hash drifted")
            fingerprint = run([str(ethos), "fingerprint", str(source)])
            if fingerprint.returncode != 0 or fingerprint.stdout.strip() != document["document_fingerprint"]:
                fail(f"{document['id']} canonical document integrity failed: {fingerprint.stderr.strip()}")
            doc_checks = document["checks"]
            verify_run(ethos, source, document["document_fingerprint"], doc_checks[:8], temporary_root, f"{document['id']}-normal")
            verify_run(ethos, source, document["document_fingerprint"], doc_checks[8:9], temporary_root, f"{document['id']}-stale", stale=True)
            verify_run(ethos, source, document["document_fingerprint"], doc_checks[9:], temporary_root, f"{document['id']}-capability", crop_capability=True)

    print(f"trust benchmark corpus: ok (20 documents, 200 checks, {len(EXPECTED_CATEGORIES)} categories)")


if __name__ == "__main__":
    main()
