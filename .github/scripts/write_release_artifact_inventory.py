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
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--checksum", required=True)
    parser.add_argument("--target", required=True, choices=("macos-arm64", "linux-x64"))
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    artifact = Path(args.artifact)
    checksum = Path(args.checksum)
    out = Path(args.out)
    checksum_text = checksum.read_text(encoding="utf-8").strip()
    artifact_hash = sha256(artifact)
    if artifact_hash not in checksum_text:
        raise SystemExit("artifact checksum file does not contain computed SHA256")

    manifest = {
        "schema": "ethos.release_artifact_inventory.v1",
        "status": "draft_not_release_ready",
        "artifact_class": "github-release-binary",
        "target": args.target,
        "artifact": artifact.name,
        "sha256": artifact_hash,
        "pdfium_policy": "caller-provided",
        "publication": "blocked",
        "required_notices": ["LICENSE", "NOTICE", "docs/pdfium-manual-setup.md"],
    }
    out.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
