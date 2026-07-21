#!/usr/bin/env python3
"""Independently validate internal v0.5 performance evidence."""
from __future__ import annotations
import argparse, hashlib, json, statistics
from pathlib import Path

def error(message: str) -> None:
    raise ValueError(message)

def median(samples: object, expected: int, label: str) -> int:
    if not isinstance(samples, list) or len(samples) != expected or any(type(value) is not int or value <= 0 for value in samples):
        error(f"{label} must contain {expected} positive integer samples")
    return int(statistics.median(samples))

def validate(record: object, baseline: Path | None = None, candidate: Path | None = None, source: Path | None = None, citations: Path | None = None) -> dict[str, object]:
    if not isinstance(record, dict): error("record must be an object")
    required = {"schema", "baseline_version", "candidate_version", "baseline_binary_sha256", "candidate_binary_sha256", "source_sha256", "citations_sha256", "single_request_cold_ns", "batch_32_ns", "derived"}
    if set(record) != required or record["schema"] != "ethos.v0_5_performance_record.v1": error("record schema is unsupported")
    if (record["baseline_version"], record["candidate_version"]) != ("0.4.0", "0.5.0"): error("record versions are not v0.4.0/v0.5.0")
    for key in ("baseline_binary_sha256", "candidate_binary_sha256", "source_sha256", "citations_sha256"):
        if not isinstance(record[key], str) or len(record[key]) != 64 or any(char not in "0123456789abcdef" for char in record[key]): error(f"{key} is not a lowercase sha256")
    if baseline is not None and hashlib.sha256(baseline.read_bytes()).hexdigest() != record["baseline_binary_sha256"]: error("baseline binary hash mismatch")
    if candidate is not None and hashlib.sha256(candidate.read_bytes()).hexdigest() != record["candidate_binary_sha256"]: error("candidate binary hash mismatch")
    if source is not None and hashlib.sha256(source.read_bytes()).hexdigest() != record["source_sha256"]: error("source hash mismatch")
    if citations is not None and hashlib.sha256(citations.read_bytes()).hexdigest() != record["citations_sha256"]: error("citations hash mismatch")
    single, batch, derived = record["single_request_cold_ns"], record["batch_32_ns"], record["derived"]
    if not isinstance(single, dict) or set(single) != {"baseline", "candidate"} or not isinstance(batch, dict) or set(batch) != {"individual_process", "batch_elapsed"} or not isinstance(derived, dict) or set(derived) != {"baseline_median_ns", "candidate_median_ns", "individual_median_ns", "batch_median_ns", "passed"}: error("record measurements have an unexpected shape")
    bm, cm, im, batch_median = median(single["baseline"], 30, "baseline cold"), median(single["candidate"], 30, "candidate cold"), median(batch["individual_process"], 32, "individual process"), median(batch["batch_elapsed"], 30, "batch elapsed")
    passed = cm * 100 <= bm * 110 and batch_median * 2 <= im * 32
    if (derived["baseline_median_ns"], derived["candidate_median_ns"], derived["individual_median_ns"], derived["batch_median_ns"], derived["passed"]) != (bm, cm, im, batch_median, passed): error("derived performance values are inconsistent")
    if not passed: error("performance thresholds failed")
    return {"passed": True, "baseline_median_ns": bm, "candidate_median_ns": cm, "batch_elapsed_ns": batch["batch_elapsed"]}

def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--record", required=True, type=Path); parser.add_argument("--baseline-bin", type=Path); parser.add_argument("--candidate-bin", type=Path); parser.add_argument("--source", type=Path); parser.add_argument("--citations", type=Path); args = parser.parse_args()
    try: result = validate(json.loads(args.record.read_text(encoding="utf-8")), args.baseline_bin, args.candidate_bin, args.source, args.citations)
    except (OSError, json.JSONDecodeError, ValueError) as exc: raise SystemExit(f"validate-v0-5-performance: error: {exc}") from exc
    print(json.dumps(result, sort_keys=True)); return 0
if __name__ == "__main__": raise SystemExit(main())
