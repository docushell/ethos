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
"""Run Ethos verification and emit deterministic GitHub workflow annotations."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


def escape_data(value: object) -> str:
    return str(value).replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def escape_property(value: object) -> str:
    return escape_data(value).replace(":", "%3A").replace(",", "%2C")


def annotation(level: str, source: str, title: str, message: str) -> str:
    return (
        f"::{level} file={escape_property(source)},title={escape_property(title)}::"
        f"{escape_data(message)}"
    )


def load_report(path: Path) -> dict[str, Any]:
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"verification report is missing or invalid: {error}") from error
    if not isinstance(report, dict) or not isinstance(report.get("checks"), list):
        raise ValueError("verification report must contain a checks array")
    if not isinstance(report.get("all_evidence_grounded"), bool):
        raise ValueError("verification report must contain all_evidence_grounded")
    if not isinstance(report.get("capability_limits", []), list):
        raise ValueError("verification report capability_limits must be an array")
    return report


def claim_summary(check: dict[str, Any]) -> str:
    claim = check.get("claim") if isinstance(check.get("claim"), dict) else {}
    text = claim.get("text")
    if isinstance(text, str) and text:
        return text[:200]
    return str(claim.get("kind") or "citation")


def report_annotations(report: dict[str, Any], source: str) -> list[str]:
    lines: list[str] = []
    for check in report["checks"]:
        if not isinstance(check, dict):
            raise ValueError("verification report contains a malformed check")
        status = check.get("status")
        if status == "grounded":
            continue
        check_id = str(check.get("id") or "unknown")
        reason = str(check.get("reason") or "not_grounded")
        lines.append(
            annotation(
                "error",
                source,
                f"Ethos citation {check_id}",
                f"{status or 'unknown'} ({reason}): {claim_summary(check)}",
            )
        )
    for limit in report.get("capability_limits", []):
        lines.append(
            annotation(
                "warning",
                source,
                "Ethos capability limited",
                str(limit),
            )
        )
    return lines


def run(ethos: Path, source: str, citations: str, grounding: str, report_path: Path) -> int:
    if not ethos.is_file():
        print(annotation("error", source, "Ethos operational error", "pinned CLI is missing"))
        return 2
    command = [str(ethos), "verify", source, "--citations", citations]
    if grounding != "native":
        command.extend(["--grounding", grounding])
    command.extend(["--out", str(report_path), "--fail-on-ungrounded"])
    report_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except OSError as error:
        print(annotation("error", source, "Ethos operational error", str(error)))
        return 2

    if result.returncode >= 2:
        detail = result.stderr.strip() or f"Ethos exited {result.returncode}"
        print(annotation("error", source, "Ethos operational error", detail))
        return result.returncode

    try:
        report = load_report(report_path)
        lines = report_annotations(report, source)
    except ValueError as error:
        print(annotation("error", source, "Ethos operational error", str(error)))
        return 2
    for line in lines:
        print(line)

    grounded = report["all_evidence_grounded"]
    if result.returncode == 0 and grounded:
        return 0
    if result.returncode == 1 and not grounded and any(line.startswith("::error") for line in lines):
        return 1
    print(
        annotation(
            "error",
            source,
            "Ethos operational error",
            "CLI exit code and canonical report disagree",
        )
    )
    return 2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ethos", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--citations", required=True)
    parser.add_argument("--grounding", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    return run(Path(args.ethos), args.source, args.citations, args.grounding, Path(args.report))


if __name__ == "__main__":
    raise SystemExit(main())
