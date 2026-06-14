#!/usr/bin/env python3
"""Run the public verify-alpha demo cases and compare them to goldens."""

import argparse
import difflib
import json
import subprocess
import sys
from pathlib import Path


CASES = [
    {
        "name": "native-grounded",
        "input": "schemas/examples/document.example.json",
        "citations": "examples/verify/native_grounded_citations.json",
        "golden": "examples/verify/goldens/native_grounded_report.json",
    },
    {
        "name": "opendataloader-grounded",
        "input": "examples/verify/opendataloader.json",
        "grounding": "opendataloader-json",
        "citations": "examples/verify/opendataloader_grounded_citations.json",
        "golden": "examples/verify/goldens/opendataloader_grounded_report.json",
    },
    {
        "name": "native-stale",
        "input": "schemas/examples/document.example.json",
        "citations": "examples/verify/native_stale_citations.json",
        "golden": "examples/verify/goldens/native_stale_report.json",
    },
    {
        "name": "opendataloader-capability-limited",
        "input": "examples/verify/opendataloader_no_tables.json",
        "grounding": "opendataloader-json",
        "citations": "examples/verify/opendataloader_table_cell_citations.json",
        "golden": "examples/verify/goldens/opendataloader_capability_limited_report.json",
    },
    {
        "name": "real-opendataloader-grounded",
        "input": "fixtures/foreign/opendataloader/real/opendataloader-output.json",
        "grounding": "opendataloader-json",
        "citations": "fixtures/foreign/opendataloader/real/citations.json",
        "golden": "fixtures/foreign/opendataloader/real/expected.verification_report.json",
    },
    {
        "name": "real-opendataloader-ungrounded",
        "input": "fixtures/foreign/opendataloader/real/opendataloader-output.json",
        "grounding": "opendataloader-json",
        "citations": "fixtures/foreign/opendataloader/real/ungrounded_citations.json",
        "golden": "fixtures/foreign/opendataloader/real/expected.ungrounded.verification_report.json",
    },
]


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--ethos-bin", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    return parser.parse_args()


def relative(path, root):
    try:
        return path.relative_to(root)
    except ValueError:
        return path


def load_json(path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def pretty_json(value):
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def run_verify(command, repo_root, name):
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


def compare_bytes(left, right, name):
    if left.read_bytes() != right.read_bytes():
        raise SystemExit(f"{name} is not byte-identical across repeated runs")
    print(f"ok    {name} is byte-identical across runs")


def compare_json(actual_path, expected_path, repo_root, name):
    actual = load_json(actual_path)
    expected = load_json(expected_path)
    if actual == expected:
        print(f"ok    {name} matches {relative(expected_path, repo_root)}")
        return

    diff = "".join(
        difflib.unified_diff(
            pretty_json(expected).splitlines(keepends=True),
            pretty_json(actual).splitlines(keepends=True),
            fromfile=str(relative(expected_path, repo_root)),
            tofile=str(relative(actual_path, repo_root)),
        )
    )
    raise SystemExit(f"{name} golden mismatch\n{diff}")


def verify_case(case, args):
    first = args.out_dir / f"{case['name']}.run1.json"
    second = args.out_dir / f"{case['name']}.run2.json"
    command = [
        str(args.ethos_bin),
        "verify",
        str(args.repo_root / case["input"]),
    ]
    if "grounding" in case:
        command.extend(["--grounding", case["grounding"]])
    command.extend(["--citations", str(args.repo_root / case["citations"])])

    run_verify([*command, "--out", str(first)], args.repo_root, case["name"])
    run_verify([*command, "--out", str(second)], args.repo_root, case["name"])
    compare_bytes(first, second, case["name"])
    compare_json(first, args.repo_root / case["golden"], args.repo_root, case["name"])


def main():
    args = parse_args()
    args.repo_root = args.repo_root.resolve()
    args.ethos_bin = args.ethos_bin.resolve()
    args.out_dir = args.out_dir.resolve()

    if not args.ethos_bin.exists():
        raise SystemExit(f"ethos binary does not exist: {args.ethos_bin}")

    args.out_dir.mkdir(parents=True, exist_ok=True)

    for case in CASES:
        verify_case(case, args)

    print("\nverify-alpha demo checks passed")


if __name__ == "__main__":
    main()
