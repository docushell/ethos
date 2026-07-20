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

"""Create a byte-identical gzip-compressed CLI release archive."""

from __future__ import annotations

import argparse
import gzip
import tarfile
from pathlib import Path


ARCHIVE_MTIME = 0


def add_file(archive: tarfile.TarFile, source: Path, arcname: str) -> None:
    info = tarfile.TarInfo(arcname)
    info.size = source.stat().st_size
    info.mode = 0o755 if source.name == "ethos" else 0o644
    info.mtime = ARCHIVE_MTIME
    info.uid = 0
    info.gid = 0
    info.uname = "root"
    info.gname = "root"
    with source.open("rb") as payload:
        archive.addfile(info, payload)


def build_archive(artifact_dir: Path, output: Path) -> None:
    artifact_dir = artifact_dir.resolve()
    required_files = ("ethos", "LICENSE", "NOTICE", "pdfium-manual-setup.md")
    missing = [name for name in required_files if not (artifact_dir / name).is_file()]
    if missing:
        raise ValueError(f"artifact directory is missing required files: {', '.join(missing)}")

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as destination:
        with gzip.GzipFile(filename="", mode="wb", fileobj=destination, mtime=ARCHIVE_MTIME) as compressed:
            with tarfile.open(mode="w", fileobj=compressed, format=tarfile.PAX_FORMAT) as archive:
                root = tarfile.TarInfo(f"{artifact_dir.name}/")
                root.type = tarfile.DIRTYPE
                root.mode = 0o755
                root.mtime = ARCHIVE_MTIME
                root.uid = 0
                root.gid = 0
                root.uname = "root"
                root.gname = "root"
                archive.addfile(root)
                for name in required_files:
                    add_file(archive, artifact_dir / name, f"{artifact_dir.name}/{name}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        build_archive(args.artifact_dir, args.out)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
