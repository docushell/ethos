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
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Optional


REQUIRED_FILES = ("ethos", "LICENSE", "NOTICE", "pdfium-manual-setup.md")
PDFIUM_MESSAGE = (
    "PDFium not found: set ETHOS_PDFIUM_LIBRARY_PATH to the caller-provided "
    "PDFium dynamic library path. Run ethos doctor for setup diagnostics, run "
    "ethos doctor --require-pdfium after setting it, and see "
    "docs/pdfium-manual-setup.md."
)


def run(command: list[str], env: Optional[dict[str, str]] = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        encoding="utf-8",
        env=env,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def smoke_artifact(artifact_dir: Path, expected_version: str, target: str) -> Dict[str, object]:
    for required in REQUIRED_FILES:
        path = artifact_dir / required
        require(path.is_file(), f"artifact is missing required file: {required}")

    ethos = artifact_dir / "ethos"
    version = run([str(ethos), "--version"])
    require(version.returncode == 0, f"ethos --version failed: {version.stderr}")
    require(
        version.stdout.strip() == expected_version,
        f"unexpected version output: {version.stdout.strip()!r}",
    )

    help_result = run([str(ethos), "--help"])
    require(help_result.returncode == 0, f"ethos --help failed: {help_result.stderr}")
    for command_group in ("doc", "rag", "security", "verify", "fingerprint"):
        require(
            command_group in help_result.stdout,
            f"ethos --help did not list expected command group: {command_group}",
        )

    with tempfile.TemporaryDirectory() as temp:
        input_pdf = Path(temp) / "missing-pdfium-smoke.pdf"
        input_pdf.write_bytes(b"%PDF-1.4\n%%EOF\n")
        env = dict(os.environ)
        env.pop("ETHOS_PDFIUM_LIBRARY_PATH", None)
        missing_pdfium = run(
            [str(ethos), "doc", "parse", str(input_pdf), "--format", "json"],
            env=env,
        )
    require(
        missing_pdfium.returncode == 12,
        f"missing PDFium smoke expected exit 12, got {missing_pdfium.returncode}: "
        f"{missing_pdfium.stderr}",
    )
    require(
        PDFIUM_MESSAGE in missing_pdfium.stderr,
        "missing PDFium smoke did not include the setup guidance",
    )
    return {
        "schema": "ethos.release_artifact_smoke.v1",
        "target": target,
        "artifact_dir": artifact_dir.name,
        "required_files": list(REQUIRED_FILES),
        "version_stdout": version.stdout.strip(),
        "help_command_groups": ["doc", "rag", "security", "verify", "fingerprint"],
        "missing_pdfium_exit_code": missing_pdfium.returncode,
        "missing_pdfium_message": PDFIUM_MESSAGE,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", required=True)
    parser.add_argument("--expected-version", default="ethos 0.1.1")
    parser.add_argument("--target", required=True, choices=("macos-arm64", "linux-x64"))
    parser.add_argument("--out")
    args = parser.parse_args()

    evidence = smoke_artifact(Path(args.artifact_dir), args.expected_version, args.target)
    if args.out:
        Path(args.out).write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
