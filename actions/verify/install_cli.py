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
"""Install one checksum-pinned Ethos CLI from a release archive."""

from __future__ import annotations

import argparse
import hashlib
import os
import platform
import shutil
import tarfile
import tempfile
import urllib.request
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_digest(path: Path, expected: str, label: str) -> None:
    actual = sha256(path)
    if actual != expected:
        raise SystemExit(f"{label} SHA256 mismatch: expected {expected}, got {actual}")


def install(url: str, archive_sha256: str, binary_sha256: str, out: Path) -> None:
    if platform.system() != "Linux" or platform.machine() not in {"x86_64", "AMD64"}:
        raise SystemExit("Ethos verify Action supports only Linux x64 runners")

    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="ethos-action-") as temp:
        archive = Path(temp) / "ethos-linux-x64.tar.gz"
        urllib.request.urlretrieve(url, archive)
        require_digest(archive, archive_sha256, "release archive")

        with tarfile.open(archive, "r:gz") as bundle:
            candidates = [
                member for member in bundle.getmembers()
                if member.isfile() and Path(member.name).name == "ethos"
            ]
            if len(candidates) != 1:
                raise SystemExit("release archive must contain exactly one Ethos executable")
            source = bundle.extractfile(candidates[0])
            if source is None:
                raise SystemExit("could not read Ethos executable from release archive")
            with out.open("wb") as destination:
                shutil.copyfileobj(source, destination)

    require_digest(out, binary_sha256, "Ethos executable")
    os.chmod(out, 0o755)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--archive-sha256", required=True)
    parser.add_argument("--binary-sha256", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    install(args.url, args.archive_sha256, args.binary_sha256, Path(args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
