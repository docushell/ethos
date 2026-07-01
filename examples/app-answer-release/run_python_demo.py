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

from __future__ import annotations

import argparse
import difflib
import json
import sys
from pathlib import Path
from typing import Any


DEMO_DIR = Path(__file__).resolve().parent
ROOT = DEMO_DIR.parents[1]
PYTHON_PACKAGE = ROOT / "python"
if str(PYTHON_PACKAGE) not in sys.path:
    sys.path.insert(0, str(PYTHON_PACKAGE))

from ethos_pdf import app_answer_release_decision, proof_summary  # noqa: E402


def load_json(name: str) -> Any:
    return json.loads((DEMO_DIR / name).read_text(encoding="utf-8"))


def dumps_json(value: Any) -> str:
    return json.dumps(value, indent=2) + "\n"


def build_decision() -> dict[str, Any]:
    report = load_json("verification-report.json")
    expected_summary = load_json("proof-summary.json")
    claim_payload = load_json("claims.json")

    summary = proof_summary(report)
    if summary != expected_summary:
        raise RuntimeError("proof_summary(verification-report.json) changed")

    return app_answer_release_decision(
        claim_payload["question"],
        summary,
        claim_payload["claims"],
        verification_report_ref=claim_payload["verification_report_ref"],
        notes=claim_payload["notes"],
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the Ethos app-answer-release reference demo.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if the generated decision differs from expected-decision.json.",
    )
    args = parser.parse_args()

    decision = build_decision()
    rendered = dumps_json(decision)

    if args.check:
        expected = load_json("expected-decision.json")
        if decision != expected:
            expected_rendered = dumps_json(expected)
            diff = "".join(
                difflib.unified_diff(
                    expected_rendered.splitlines(keepends=True),
                    rendered.splitlines(keepends=True),
                    fromfile="expected-decision.json",
                    tofile="generated-decision.json",
                )
            )
            print(diff, file=sys.stderr)
            return 1

    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
