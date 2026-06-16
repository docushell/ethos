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
#

"""Run the public verify-alpha demo cases and compare them to goldens."""

import argparse
import difflib
import json
import shutil
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
        "name": "native-split-quote",
        "input": "examples/verify/native_split_quote_document.json",
        "citations": "examples/verify/native_split_quote_citations.json",
        "golden": "examples/verify/goldens/native_split_quote_report.json",
    },
    {
        "name": "native-non-v1-claims",
        "input": "schemas/examples/document.example.json",
        "citations": "examples/verify/native_non_v1_claims_citations.json",
        "golden": "examples/verify/goldens/native_non_v1_claims_report.json",
    },
    {
        "name": "native-ungrounded",
        "input": "schemas/examples/document.example.json",
        "citations": "examples/verify/native_ungrounded_citations.json",
        "golden": "examples/verify/goldens/native_ungrounded_report.json",
    },
    {
        "name": "opendataloader-not-found",
        "input": "examples/verify/opendataloader.json",
        "grounding": "opendataloader-json",
        "citations": "examples/verify/opendataloader_not_found_citations.json",
        "golden": "examples/verify/goldens/opendataloader_not_found_report.json",
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

USAGE_ERROR_CASES = [
    {
        "name": "invalid-table-cell-citation",
        "input": "schemas/examples/document.example.json",
        "citations": "examples/verify/invalid_table_cell_citations.json",
        "stderr_contains": "table_cell citation must include table_id and cell",
    },
    {
        "name": "invalid-bbox-citation",
        "input": "schemas/examples/document.example.json",
        "citations": "examples/verify/invalid_bbox_citations.json",
        "stderr_contains": "citation bbox requires page unless another target locator is present",
    },
    {
        "name": "opendataloader-malformed-bbox-input",
        "input": "examples/verify/opendataloader_malformed_bbox.json",
        "grounding": "opendataloader-json",
        "citations": "examples/verify/opendataloader_grounded_citations.json",
        "stderr_contains": "opendataloader-json adapter: bbox is malformed (x0>x1 or y0>y1)",
    },
    {
        "name": "opendataloader-unknown-page-input",
        "input": "examples/verify/opendataloader_unknown_page.json",
        "grounding": "opendataloader-json",
        "citations": "examples/verify/opendataloader_grounded_citations.json",
        "stderr_contains": "opendataloader-json adapter: element.page references unknown page",
    },
]

SUMMARY_CASES = [
    {
        "name": "native-ungrounded-summary",
        "input": "schemas/examples/document.example.json",
        "citations": "examples/verify/native_ungrounded_citations.json",
        "expected_exit": 1,
        "fail_on_ungrounded": True,
        "stdout_contains": [
            "ethos verify summary\n",
            (
                "verification_config_sha256: "
                "4bb224166a04a25fed2dd3ecdb9638ddcc5b398658532b73f1c0547e4983d0b0\n"
            ),
            "all_evidence_grounded: false\n",
            (
                "grounding_capabilities: "
                "spans=true,char_offsets=true,tables=true,fingerprint=true,"
                "coordinate_origin=top-left,crop_support=false\n"
            ),
            "checks_not_found: 1\n",
            "checks_mismatch: 1\n",
            (
                "- v0001 status=mismatch reason=text_mismatch kind=quote "
                "locator=page:p0001;element_id:e000002 "
                "match_method=normalized_text_contains\n"
            ),
            (
                "  diagnostic: target resolved, but target text did not match "
                "claimed text under normalized_text_contains; no semantic inference was attempted\n"
            ),
            (
                "- v0002 status=not_found reason=element_not_found kind=presence "
                "locator=element_id:missing-element match_method=none\n"
            ),
            (
                "  diagnostic: element_id locator did not resolve in the grounding source\n"
            ),
        ],
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


def list_crop_descriptors(crop_dir):
    return sorted(
        path
        for path in crop_dir.iterdir()
        if path.name.startswith("crop-") and path.suffix == ".json"
    )


def compare_crop_dirs(left_dir, right_dir, name):
    left = list_crop_descriptors(left_dir)
    right = list_crop_descriptors(right_dir)
    left_names = [path.name for path in left]
    right_names = [path.name for path in right]
    if left_names != right_names:
        raise SystemExit(f"{name} crop descriptor filenames differ across repeated runs")
    if not left:
        raise SystemExit(f"{name} wrote no crop descriptors")
    for left_path, right_path in zip(left, right):
        if left_path.read_bytes() != right_path.read_bytes():
            raise SystemExit(
                f"{name} crop descriptor {left_path.name} differs across repeated runs"
            )
    print(f"ok    {name} crop descriptors are byte-identical across runs ({len(left)} files)")
    return left


def validate_crop_descriptors(descriptor_paths, schema_path, repo_root, name):
    from jsonschema import Draft202012Validator

    schema = load_json(schema_path)
    validator = Draft202012Validator(schema)
    for path in descriptor_paths:
        errors = sorted(
            validator.iter_errors(load_json(path)),
            key=lambda error: list(error.absolute_path),
        )
        if errors:
            details = "\n".join(
                f"/{'/'.join(str(part) for part in error.absolute_path)}: {error.message}"
                for error in errors[:8]
            )
            raise SystemExit(
                f"{name} crop descriptor {relative(path, repo_root)} failed schema validation\n{details}"
            )
    print(f"ok    {name} crop descriptors validate against {relative(schema_path, repo_root)}")


def validate_report_crop_links(report_path, descriptor_paths, name):
    report = load_json(report_path)
    expected = {}
    for check in report.get("checks", []):
        evidence = check.get("evidence") or {}
        crop_ref = evidence.get("crop_ref")
        if crop_ref:
            expected.setdefault(crop_ref, []).append(check["id"])

    actual = {}
    for path in descriptor_paths:
        descriptor = load_json(path)
        actual[path.name] = descriptor["check_ids"]

    if expected != actual:
        raise SystemExit(
            f"{name} crop descriptors do not match verification report crop_ref bindings"
        )
    print(f"ok    {name} crop descriptors match report crop_ref bindings")


def descriptor_for_check(descriptor_paths, check_id, name):
    matches = [
        path for path in descriptor_paths if load_json(path).get("check_ids") == [check_id]
    ]
    if len(matches) != 1:
        raise SystemExit(
            f"{name} expected exactly one crop descriptor for {check_id}, got {len(matches)}"
        )
    return matches[0]


def verify_crop_descriptor_case(args):
    name = "native-grounded-crops"
    first = args.out_dir / f"{name}.run1.json"
    second = args.out_dir / f"{name}.run2.json"
    first_crop_dir = args.out_dir / f"{name}.run1.crops"
    second_crop_dir = args.out_dir / f"{name}.run2.crops"
    for crop_dir in [first_crop_dir, second_crop_dir]:
        if crop_dir.exists():
            shutil.rmtree(crop_dir)
        crop_dir.mkdir(parents=True)

    command = [
        str(args.ethos_bin),
        "verify",
        str(args.repo_root / "schemas/examples/document.example.json"),
        "--citations",
        str(args.repo_root / "examples/verify/native_grounded_citations.json"),
    ]

    run_verify(
        [*command, "--crop-dir", str(first_crop_dir), "--out", str(first)],
        args.repo_root,
        name,
    )
    run_verify(
        [*command, "--crop-dir", str(second_crop_dir), "--out", str(second)],
        args.repo_root,
        name,
    )
    compare_bytes(first, second, name)
    descriptor_paths = compare_crop_dirs(first_crop_dir, second_crop_dir, name)
    validate_report_crop_links(first, descriptor_paths, name)
    validate_crop_descriptors(
        descriptor_paths,
        args.repo_root / "schemas/ethos-crop-descriptor.schema.json",
        args.repo_root,
        name,
    )
    compare_json(
        descriptor_for_check(descriptor_paths, "v0001", name),
        args.repo_root / "schemas/examples/crop-descriptor.example.json",
        args.repo_root,
        f"{name} first descriptor",
    )


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


def verify_usage_error_case(case, args):
    command = [
        str(args.ethos_bin),
        "verify",
        str(args.repo_root / case["input"]),
        "--citations",
        str(args.repo_root / case["citations"]),
    ]
    if "grounding" in case:
        command.extend(["--grounding", case["grounding"]])

    print("$ " + " ".join(str(part) for part in command), flush=True)
    result = subprocess.run(command, cwd=args.repo_root, capture_output=True, check=False)
    if result.returncode != 2:
        sys.stderr.write(f"{case['name']} exited {result.returncode}, expected 2\n")
        sys.stderr.write(result.stderr.decode("utf-8", errors="replace"))
        sys.stderr.write(result.stdout.decode("utf-8", errors="replace"))
        raise SystemExit(1)
    if result.stdout:
        raise SystemExit(f"{case['name']} wrote unexpected stdout")
    stderr = result.stderr.decode("utf-8", errors="replace")
    if case["stderr_contains"] not in stderr:
        raise SystemExit(
            f"{case['name']} stderr did not contain {case['stderr_contains']!r}\n{stderr}"
        )
    print(f"ok    {case['name']} exits 2 with expected usage diagnostic")


def verify_summary_case(case, args):
    command = [
        str(args.ethos_bin),
        "verify",
        str(args.repo_root / case["input"]),
        "--citations",
        str(args.repo_root / case["citations"]),
        "--format",
        "summary",
    ]
    if "grounding" in case:
        command.extend(["--grounding", case["grounding"]])
    if case.get("fail_on_ungrounded", False):
        command.append("--fail-on-ungrounded")

    print("$ " + " ".join(str(part) for part in command), flush=True)
    result = subprocess.run(command, cwd=args.repo_root, capture_output=True, check=False)
    expected_exit = case["expected_exit"]
    if result.returncode != expected_exit:
        sys.stderr.write(
            f"{case['name']} exited {result.returncode}, expected {expected_exit}\n"
        )
        sys.stderr.write(result.stderr.decode("utf-8", errors="replace"))
        sys.stderr.write(result.stdout.decode("utf-8", errors="replace"))
        raise SystemExit(1)
    if result.stderr:
        raise SystemExit(f"{case['name']} wrote unexpected stderr")
    stdout = result.stdout.decode("utf-8", errors="replace")
    try:
        json.loads(stdout)
    except json.JSONDecodeError:
        pass
    else:
        raise SystemExit(f"{case['name']} summary output unexpectedly parsed as JSON")
    for expected in case["stdout_contains"]:
        if expected not in stdout:
            raise SystemExit(
                f"{case['name']} stdout did not contain {expected!r}\n{stdout}"
            )
    print(f"ok    {case['name']} summary includes expected diagnostics")


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
    for case in USAGE_ERROR_CASES:
        verify_usage_error_case(case, args)
    for case in SUMMARY_CASES:
        verify_summary_case(case, args)
    verify_crop_descriptor_case(args)

    print("\nverify-alpha demo checks passed")


if __name__ == "__main__":
    main()
