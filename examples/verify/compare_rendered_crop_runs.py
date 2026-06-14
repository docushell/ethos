#!/usr/bin/env python3
"""Compare two rendered-crop verification runs.

The default mode validates that two runs are comparable logical evidence runs, then
reports whether full rendered artifacts are byte-identical. Use
--require-rendered-equality only when the caller intentionally wants PNG/descriptor
byte equality to be a hard gate.
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--left-run", type=Path, required=True)
    parser.add_argument("--right-run", type=Path, required=True)
    parser.add_argument("--left-label", default="left")
    parser.add_argument("--right-label", default="right")
    parser.add_argument("--require-rendered-equality", action="store_true")
    return parser.parse_args()


def load_json(path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def sha256_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_file(path):
    if not path.is_file():
        raise SystemExit(f"missing file: {path}")
    return path


def require_dir(path):
    if not path.is_dir():
        raise SystemExit(f"missing directory: {path}")
    return path


def run_paths(run_dir):
    return {
        "document": require_file(run_dir / "document.json"),
        "report": require_file(run_dir / "verification-report.json"),
        "crops": require_dir(run_dir / "crops"),
    }


def crop_files(crop_dir, suffix):
    return sorted(
        path for path in crop_dir.iterdir() if path.name.startswith("crop-") and path.suffix == suffix
    )


def report_evidence_summary(report):
    summary = []
    for check in report.get("checks", []):
        evidence = check.get("evidence") or {}
        summary.append(
            {
                "id": check.get("id"),
                "status": check.get("status"),
                "page": evidence.get("page"),
                "bbox": evidence.get("bbox"),
                "crop_ref": evidence.get("crop_ref"),
            }
        )
    return summary


def descriptor_summary(path):
    descriptor = load_json(path)
    return {
        "name": path.name,
        "sha256": sha256_file(path),
        "check_ids": descriptor.get("check_ids"),
        "page": descriptor.get("page"),
        "bbox": descriptor.get("bbox"),
        "rendering_status": descriptor.get("rendering_status"),
        "rendered_ref": descriptor.get("rendered_ref"),
        "rendered_sha256": descriptor.get("rendered_sha256"),
        "rendered_size": [
            descriptor.get("rendered_width_px"),
            descriptor.get("rendered_height_px"),
        ],
        "text_sha256": descriptor.get("text_sha256"),
    }


def print_compare(label, left, right, mismatches, hard=False):
    if left == right:
        print(f"ok    {label}: {left}")
        return
    status = "fail" if hard else "diff"
    print(f"{status}  {label}:")
    print(f"      left : {left}")
    print(f"      right: {right}")
    mismatches.append((label, hard))


def main():
    args = parse_args()
    left_run = args.left_run.resolve()
    right_run = args.right_run.resolve()
    left_paths = run_paths(left_run)
    right_paths = run_paths(right_run)

    left_doc = load_json(left_paths["document"])
    right_doc = load_json(right_paths["document"])
    left_report = load_json(left_paths["report"])
    right_report = load_json(right_paths["report"])

    mismatches = []

    print(f"left_run  {args.left_label}: {left_run}")
    print(f"right_run {args.right_label}: {right_run}")

    print_compare(
        "document_fingerprint",
        left_doc.get("fingerprint"),
        right_doc.get("fingerprint"),
        mismatches,
        hard=True,
    )
    print_compare(
        "source_fingerprint",
        (left_doc.get("source") or {}).get("fingerprint"),
        (right_doc.get("source") or {}).get("fingerprint"),
        mismatches,
        hard=True,
    )
    print_compare(
        "payload_sha256",
        left_doc.get("payload_sha256"),
        right_doc.get("payload_sha256"),
        mismatches,
        hard=True,
    )
    print_compare(
        "report_document_fingerprint",
        left_report.get("document_fingerprint"),
        right_report.get("document_fingerprint"),
        mismatches,
        hard=True,
    )
    print_compare(
        "all_evidence_grounded",
        left_report.get("all_evidence_grounded"),
        right_report.get("all_evidence_grounded"),
        mismatches,
        hard=True,
    )

    left_evidence = report_evidence_summary(left_report)
    right_evidence = report_evidence_summary(right_report)
    print_compare(
        "check_identity_status_page",
        [(item["id"], item["status"], item["page"]) for item in left_evidence],
        [(item["id"], item["status"], item["page"]) for item in right_evidence],
        mismatches,
        hard=True,
    )
    print_compare(
        "evidence_bbox",
        [(item["id"], item["bbox"]) for item in left_evidence],
        [(item["id"], item["bbox"]) for item in right_evidence],
        mismatches,
    )
    print_compare(
        "evidence_crop_ref",
        [(item["id"], item["crop_ref"]) for item in left_evidence],
        [(item["id"], item["crop_ref"]) for item in right_evidence],
        mismatches,
    )

    print_compare(
        "document_json_sha256",
        sha256_file(left_paths["document"]),
        sha256_file(right_paths["document"]),
        mismatches,
    )
    print_compare(
        "verification_report_sha256",
        sha256_file(left_paths["report"]),
        sha256_file(right_paths["report"]),
        mismatches,
    )

    left_descriptors = [descriptor_summary(path) for path in crop_files(left_paths["crops"], ".json")]
    right_descriptors = [descriptor_summary(path) for path in crop_files(right_paths["crops"], ".json")]
    if not left_descriptors or not right_descriptors:
        raise SystemExit("both runs must contain at least one rendered crop descriptor")
    print_compare(
        "descriptor_count",
        len(left_descriptors),
        len(right_descriptors),
        mismatches,
        hard=True,
    )
    print_compare(
        "descriptor_names",
        [item["name"] for item in left_descriptors],
        [item["name"] for item in right_descriptors],
        mismatches,
    )
    print_compare(
        "descriptor_sha256",
        [item["sha256"] for item in left_descriptors],
        [item["sha256"] for item in right_descriptors],
        mismatches,
    )
    print_compare(
        "descriptor_bbox",
        [(item["check_ids"], item["bbox"]) for item in left_descriptors],
        [(item["check_ids"], item["bbox"]) for item in right_descriptors],
        mismatches,
    )
    print_compare(
        "rendered_size",
        [(item["check_ids"], item["rendered_size"]) for item in left_descriptors],
        [(item["check_ids"], item["rendered_size"]) for item in right_descriptors],
        mismatches,
    )

    left_pngs = crop_files(left_paths["crops"], ".png")
    right_pngs = crop_files(right_paths["crops"], ".png")
    if not left_pngs or not right_pngs:
        raise SystemExit("both runs must contain at least one rendered PNG crop")
    print_compare("png_count", len(left_pngs), len(right_pngs), mismatches, hard=True)
    print_compare("png_names", [path.name for path in left_pngs], [path.name for path in right_pngs], mismatches)
    print_compare("png_sha256", [sha256_file(path) for path in left_pngs], [sha256_file(path) for path in right_pngs], mismatches)
    print_compare("png_file_size", [path.stat().st_size for path in left_pngs], [path.stat().st_size for path in right_pngs], mismatches)

    hard_failures = [label for label, hard in mismatches if hard]
    artifact_diffs = [label for label, hard in mismatches if not hard]
    if hard_failures:
        print(f"\nlogical evidence comparison failed: {', '.join(hard_failures)}")
        return 1
    if artifact_diffs:
        print(f"\nlogical evidence comparison passed; rendered artifact equality failed: {', '.join(artifact_diffs)}")
        if args.require_rendered_equality:
            return 1
        return 0
    print("\nlogical evidence comparison passed; rendered artifacts are byte-identical")
    return 0


if __name__ == "__main__":
    sys.exit(main())
