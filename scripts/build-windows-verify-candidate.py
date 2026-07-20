#!/usr/bin/env python3
"""Build a deterministic, verify-only Windows x64 draft archive."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path
from typing import NoReturn


ROOT_NAME = "ethos-windows-x64"
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)


def fail(message: str) -> NoReturn:
    raise SystemExit(f"build-windows-verify-candidate: error: {message}")


def read_required(path: Path, label: str) -> bytes:
    if not path.is_file() or path.is_symlink():
        fail(f"missing regular {label}: {path}")
    data = path.read_bytes()
    if not data:
        fail(f"empty {label}: {path}")
    return data


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def add_file(archive: zipfile.ZipFile, name: str, data: bytes, mode: int) -> None:
    info = zipfile.ZipInfo(f"{ROOT_NAME}/{name}", ZIP_TIMESTAMP)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = (mode & 0xFFFF) << 16
    archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def quickstart(version: str) -> bytes:
    return (
        f"Ethos {version} Windows x64 verify-only draft\r\n"
        "\r\n"
        "From PowerShell, starting beside the downloaded archive:\r\n"
        "\r\n"
        "Expand-Archive .\\ethos-windows-x64.zip -DestinationPath .\r\n"
        ".\\ethos-windows-x64\\ethos.exe verify "
        ".\\ethos-windows-x64\\verify-example\\document.json --citations "
        ".\\ethos-windows-x64\\verify-example\\citations.json --fail-on-ungrounded\r\n"
        "\r\n"
        "This draft bundles no PDFium. PDF-backed commands fail closed until a caller-provided "
        "runtime is configured; see pdfium-manual-setup.md. Ethos verifies citation grounding "
        "against the supplied source representation, not semantic truth.\r\n"
    ).encode("utf-8")


def build(args: argparse.Namespace) -> tuple[Path, Path]:
    if not re.fullmatch(r"[0-9A-Za-z][0-9A-Za-z.+-]*", args.version):
        fail("version must contain only letters, digits, dot, plus, or hyphen")

    payload: dict[str, tuple[bytes, int]] = {
        "LICENSE": (read_required(Path(args.project_license), "project LICENSE"), 0o644),
        "NOTICE": (read_required(Path(args.project_notice), "project NOTICE"), 0o644),
        "PDFIUM-MANUAL-SETUP.md": (
            read_required(Path(args.pdfium_setup), "PDFium setup guide"),
            0o644,
        ),
        "VERIFY-QUICKSTART.txt": (quickstart(args.version), 0o644),
        "ethos.exe": (read_required(Path(args.ethos_binary), "Windows Ethos binary"), 0o755),
        "verify-example/citations.json": (
            read_required(Path(args.citations), "verification citations fixture"),
            0o644,
        ),
        "verify-example/document.json": (
            read_required(Path(args.document), "verification document fixture"),
            0o644,
        ),
    }
    manifest = {
        "schema": "ethos.windows_verify_candidate_manifest.v1",
        "status": "draft_not_release_ready",
        "publication": "blocked",
        "target": "windows-x64",
        "version": args.version,
        "artifact_scope": "verify-only",
        "pdfium_included": False,
        "entries": [
            {"path": name, "sha256": sha256(data), "size_bytes": len(data)}
            for name, (data, _mode) in sorted(payload.items())
        ],
    }
    payload["artifact-manifest.json"] = (
        (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8"),
        0o644,
    )

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    archive_path = out_dir / f"{ROOT_NAME}.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        for name, (data, mode) in sorted(payload.items()):
            add_file(archive, name, data, mode)

    archive_hash = sha256(archive_path.read_bytes())
    checksum_path = out_dir / f"{ROOT_NAME}.zip.sha256"
    checksum_path.write_text(f"{archive_hash}  {archive_path.name}\n", encoding="utf-8")
    return archive_path, checksum_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ethos-binary", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--project-license", default="LICENSE")
    parser.add_argument("--project-notice", default="NOTICE")
    parser.add_argument("--pdfium-setup", default="docs/pdfium-manual-setup.md")
    parser.add_argument("--document", default="schemas/examples/document.example.json")
    parser.add_argument("--citations", default="examples/verify/native_grounded_citations.json")
    archive, checksum = build(parser.parse_args())
    print(archive)
    print(checksum)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
