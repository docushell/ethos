#!/usr/bin/env python3
"""Run same-host rendered crop artifact determinism checks."""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--ethos-bin", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    return parser.parse_args()


def load_json(path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path, value):
    path.write_text(
        json.dumps(value, separators=(",", ":"), sort_keys=True) + "\n",
        encoding="utf-8",
    )


def run_command(command, repo_root, name):
    print("$ " + " ".join(str(part) for part in command), flush=True)
    result = subprocess.run(command, cwd=repo_root, capture_output=True, check=False)
    if result.returncode != 0:
        sys.stderr.write(f"{name} exited {result.returncode}\n")
        sys.stderr.write(result.stderr.decode("utf-8", errors="replace"))
        sys.stderr.write(result.stdout.decode("utf-8", errors="replace"))
        raise SystemExit(result.returncode)
    if result.stdout:
        raise SystemExit(f"{name} wrote unexpected stdout")
    if result.stderr:
        raise SystemExit(f"{name} wrote unexpected stderr")


def compare_file_bytes(left, right, label):
    if left.read_bytes() != right.read_bytes():
        raise SystemExit(f"{label} differs across repeated runs")
    print(f"ok    {label} is byte-identical across runs")


def files_by_suffix(path, suffix):
    return sorted(p for p in path.iterdir() if p.name.startswith("crop-") and p.suffix == suffix)


def compare_artifact_dirs(left_dir, right_dir, suffix, label):
    left = files_by_suffix(left_dir, suffix)
    right = files_by_suffix(right_dir, suffix)
    left_names = [path.name for path in left]
    right_names = [path.name for path in right]
    if left_names != right_names:
        raise SystemExit(f"{label} filenames differ across repeated runs")
    if not left:
        raise SystemExit(f"{label} wrote no {suffix} artifacts")
    for left_path, right_path in zip(left, right):
        compare_file_bytes(left_path, right_path, f"{label} {left_path.name}")
    return left


def validate_rendered_descriptors(report_path, doc_path, descriptor_paths, png_paths):
    report = load_json(report_path)
    doc = load_json(doc_path)
    png_by_name = {path.name: path for path in png_paths}
    expected_refs = {
        check["evidence"]["crop_ref"]
        for check in report["checks"]
        if check.get("evidence", {}).get("crop_ref")
    }
    actual_refs = {path.name for path in descriptor_paths}
    if expected_refs != actual_refs:
        raise SystemExit("descriptor crop_refs do not match verification report crop_refs")

    for descriptor_path in descriptor_paths:
        descriptor = load_json(descriptor_path)
        if descriptor["rendering_status"] != "rendered":
            raise SystemExit(f"{descriptor_path.name} is not marked rendered")
        if descriptor["document_fingerprint"] != report["document_fingerprint"]:
            raise SystemExit(f"{descriptor_path.name} document fingerprint does not match report")
        if descriptor["source_pdf_fingerprint"] != doc["source"]["fingerprint"]:
            raise SystemExit(f"{descriptor_path.name} source PDF fingerprint does not match document")
        if descriptor["rendered_format"] != "png":
            raise SystemExit(f"{descriptor_path.name} rendered format is not png")
        png_path = png_by_name.get(descriptor["rendered_ref"])
        if png_path is None:
            raise SystemExit(f"{descriptor_path.name} references missing PNG")
        png_bytes = png_path.read_bytes()
        if not png_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
            raise SystemExit(f"{png_path.name} does not have a PNG signature")
        if descriptor["rendered_sha256"] != hashlib.sha256(png_bytes).hexdigest():
            raise SystemExit(f"{descriptor_path.name} rendered_sha256 does not match PNG bytes")
        if descriptor["rendered_width_px"] < 1 or descriptor["rendered_height_px"] < 1:
            raise SystemExit(f"{descriptor_path.name} has invalid rendered dimensions")

    print("ok    rendered descriptors bind report, source PDF fingerprint, and PNG hashes")


def run_once(args, run_name, citations_path):
    run_dir = args.out_dir / run_name
    crop_dir = run_dir / "crops"
    run_dir.mkdir(parents=True)
    crop_dir.mkdir()
    source_pdf = args.repo_root / "fixtures/synthetic/simple-text/document.pdf"
    doc_path = run_dir / "document.json"
    report_path = run_dir / "verification-report.json"

    run_command(
        [
            str(args.ethos_bin),
            "doc",
            "parse",
            str(source_pdf),
            "--out",
            str(doc_path),
        ],
        args.repo_root,
        f"{run_name} parse",
    )
    run_command(
        [
            str(args.ethos_bin),
            "verify",
            str(doc_path),
            "--citations",
            str(citations_path),
            "--crop-dir",
            str(crop_dir),
            "--crop-source-pdf",
            str(source_pdf),
            "--out",
            str(report_path),
        ],
        args.repo_root,
        f"{run_name} verify rendered crops",
    )
    return {
        "crop_dir": crop_dir,
        "doc_path": doc_path,
        "report_path": report_path,
    }


def main():
    args = parse_args()
    args.repo_root = args.repo_root.resolve()
    args.ethos_bin = args.ethos_bin.resolve()
    args.out_dir = args.out_dir.resolve()

    pdfium = os.environ.get("ETHOS_PDFIUM_LIBRARY_PATH")
    if not pdfium or not Path(pdfium).is_file():
        raise SystemExit("ETHOS_PDFIUM_LIBRARY_PATH must point to libpdfium for rendered crop checks")
    if not args.ethos_bin.exists():
        raise SystemExit(f"ethos binary does not exist: {args.ethos_bin}")

    if args.out_dir.exists():
        shutil.rmtree(args.out_dir)
    args.out_dir.mkdir(parents=True)
    citations_path = args.out_dir / "citations.json"
    write_json(
        citations_path,
        [{"kind": "quote", "text": "Hello", "citation": {"element_id": "e000001"}}],
    )

    first = run_once(args, "run1", citations_path)
    second = run_once(args, "run2", citations_path)

    compare_file_bytes(first["doc_path"], second["doc_path"], "parsed document JSON")
    compare_file_bytes(first["report_path"], second["report_path"], "verification report JSON")
    descriptors = compare_artifact_dirs(
        first["crop_dir"], second["crop_dir"], ".json", "crop descriptors"
    )
    pngs = compare_artifact_dirs(first["crop_dir"], second["crop_dir"], ".png", "rendered PNG crops")
    validate_rendered_descriptors(first["report_path"], first["doc_path"], descriptors, pngs)

    print("\nrendered crop determinism checks passed")


if __name__ == "__main__":
    main()
