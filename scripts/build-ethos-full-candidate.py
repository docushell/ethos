#!/usr/bin/env python3
"""Build deterministic, non-publishable ethos-full proposal archives."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import re
import stat
import tarfile
from pathlib import Path
from typing import NoReturn


TARGETS = {
    "macos-arm64": "lib/libpdfium.dylib",
    "linux-x64": "lib/libpdfium.so",
}
STATUS = "proposal_evidence_not_release_ready"


def fail(message: str) -> NoReturn:
    raise SystemExit(f"build-ethos-full-candidate: error: {message}")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_required(path: Path, label: str) -> bytes:
    if not path.is_file() or path.is_symlink():
        fail(f"missing regular {label}: {path}")
    data = path.read_bytes()
    if not data:
        fail(f"empty {label}: {path}")
    return data


def load_profile(path: Path, target: str) -> tuple[dict[str, object], dict[str, object], str]:
    try:
        profile = json.loads(path.read_text(encoding="utf-8"))
        backend = profile["backend"]
        artifact = backend["platform_artifacts"][target]
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as error:
        fail(f"invalid profile {path}: {error}")
    if backend.get("id") != "pdfium":
        fail("profile backend.id must be pdfium")
    flags = backend.get("build_flags", {})
    if flags.get("pdf_enable_v8") is not False or flags.get("pdf_enable_xfa") is not False:
        fail("profile must disable PDFium V8 and XFA")
    if artifact.get("runtime_library_path") != TARGETS[target]:
        fail(f"profile runtime path for {target} must be {TARGETS[target]}")
    expected_hash = artifact.get("runtime_library_sha256")
    if not isinstance(expected_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_hash):
        fail(f"profile runtime sha256 for {target} is invalid")
    archive_hash = backend.get("platform_hashes", {}).get(target)
    if not isinstance(archive_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", archive_hash):
        fail(f"profile archive sha256 for {target} is invalid")
    return backend, artifact, archive_hash


def read_pdfium_archive(
    path: Path, expected_hash: str, runtime_relpath: str
) -> tuple[bytes, bytes, dict[str, bytes]]:
    archive_bytes = read_required(path, "PDFium archive")
    archive_hash = sha256_bytes(archive_bytes)
    if archive_hash != expected_hash:
        fail(f"PDFium archive sha256 mismatch: got {archive_hash}, expected {expected_hash}")
    try:
        with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as archive:
            members: dict[str, tarfile.TarInfo] = {}
            for member in archive.getmembers():
                if member.name in members:
                    fail(f"duplicate PDFium archive entry: {member.name}")
                members[member.name] = member

            def regular_file(name: str, label: str) -> bytes:
                member = members.get(name)
                if member is None or not member.isfile():
                    fail(f"missing regular {label} in PDFium archive: {name}")
                handle = archive.extractfile(member)
                if handle is None:
                    fail(f"unreadable {label} in PDFium archive: {name}")
                data = handle.read()
                if not data:
                    fail(f"empty {label} in PDFium archive: {name}")
                return data

            runtime = regular_file(runtime_relpath, "PDFium runtime")
            package_license = regular_file("LICENSE", "PDFium LICENSE")
            notices = {
                name.removeprefix("licenses/"): regular_file(
                    name, "PDFium third-party notice"
                )
                for name, member in sorted(members.items())
                if name.startswith("licenses/") and member.isfile()
            }
    except (tarfile.TarError, OSError) as error:
        fail(f"invalid PDFium archive {path}: {error}")
    if "pdfium.txt" not in notices:
        fail("PDFium archive must include licenses/pdfium.txt")
    return runtime, package_license, notices


def wrapper(runtime_path: str) -> bytes:
    return (
        "#!/bin/sh\n"
        "set -eu\n"
        'root=$(CDPATH= cd -P -- "$(dirname "$0")" && pwd)\n'
        f'export ETHOS_PDFIUM_LIBRARY_PATH="$root/{runtime_path}"\n'
        'exec "$root/bin/ethos" "$@"\n'
    ).encode("utf-8")


def add_bytes(archive: tarfile.TarFile, name: str, data: bytes, mode: int) -> None:
    info = tarfile.TarInfo(name)
    info.size = len(data)
    info.mode = mode
    info.uid = 0
    info.gid = 0
    info.uname = ""
    info.gname = ""
    info.mtime = 0
    archive.addfile(info, io.BytesIO(data))


def build(args: argparse.Namespace) -> tuple[Path, Path, Path]:
    if not re.fullmatch(r"[0-9A-Za-z][0-9A-Za-z.+-]*", args.version):
        fail("version must contain only letters, digits, dot, plus, or hyphen")

    profile_path = Path(args.profile)
    ethos_path = Path(args.ethos_binary)
    pdfium_archive = Path(args.pdfium_archive)
    out_dir = Path(args.out_dir)
    backend, artifact, expected_archive_hash = load_profile(profile_path, args.target)

    ethos = read_required(ethos_path, "Ethos binary")
    if not ethos_path.stat().st_mode & stat.S_IXUSR:
        fail(f"Ethos binary is not executable: {ethos_path}")
    runtime_relpath = TARGETS[args.target]
    runtime, pdfium_license, license_files = read_pdfium_archive(
        pdfium_archive, expected_archive_hash, runtime_relpath
    )
    runtime_hash = sha256_bytes(runtime)
    if runtime_hash != artifact["runtime_library_sha256"]:
        fail(
            f"PDFium runtime sha256 mismatch: got {runtime_hash}, "
            f"expected {artifact['runtime_library_sha256']}"
        )

    project_license = read_required(Path(args.project_license), "project LICENSE")
    project_notice = read_required(Path(args.project_notice), "project NOTICE")

    root = f"ethos-full-{args.version}-{args.target}"
    payload: dict[str, tuple[bytes, int]] = {
        "LICENSE": (project_license, 0o644),
        "NOTICE": (project_notice, 0o644),
        "bin/ethos": (ethos, 0o755),
        "ethos": (wrapper(runtime_relpath), 0o755),
        runtime_relpath: (runtime, 0o755),
        "third-party/pdfium/LICENSE": (pdfium_license, 0o644),
    }
    for relative, notice in sorted(license_files.items()):
        payload[f"third-party/pdfium/licenses/{relative}"] = (
            notice,
            0o644,
        )

    entries = [
        {"path": name, "sha256": sha256_bytes(data), "size_bytes": len(data)}
        for name, (data, _mode) in sorted(payload.items())
    ]
    manifest = {
        "schema": "ethos.full_candidate_manifest.v1",
        "status": STATUS,
        "publication": "blocked_pending_adr_0015",
        "artifact_class": "ethos-full",
        "target": args.target,
        "version": args.version,
        "launcher": "ethos",
        "pdfium": {
            "phase": backend.get("phase"),
            "version": backend.get("version"),
            "upstream_version": backend.get("upstream_version"),
            "source": backend.get("distribution", {}).get("source"),
            "runtime_library_path": runtime_relpath,
            "runtime_library_sha256": runtime_hash,
            "v8": "disabled",
            "xfa": "disabled",
        },
        "entries": entries,
    }
    payload["artifact-manifest.json"] = (
        (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8"),
        0o644,
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    archive_path = out_dir / f"{root}.tar.gz"
    with archive_path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.GNU_FORMAT) as archive:
                for name, (data, mode) in sorted(payload.items()):
                    add_bytes(archive, f"{root}/{name}", data, mode)

    archive_hash = sha256_bytes(archive_path.read_bytes())
    checksum_path = archive_path.with_suffix(archive_path.suffix + ".sha256")
    checksum_path.write_text(f"{archive_hash}  {archive_path.name}\n", encoding="utf-8")
    inventory_path = out_dir / f"{root}.inventory.json"
    inventory = {
        "schema": "ethos.full_candidate_inventory.v1",
        "status": STATUS,
        "publication": "blocked_pending_adr_0015",
        "artifact": archive_path.name,
        "sha256": archive_hash,
        "size_bytes": archive_path.stat().st_size,
        "target": args.target,
    }
    inventory_path.write_text(
        json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return archive_path, checksum_path, inventory_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, choices=tuple(TARGETS))
    parser.add_argument("--version", required=True)
    parser.add_argument("--ethos-binary", required=True)
    parser.add_argument("--pdfium-archive", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--profile", default="profiles/ethos-deterministic-v1.json")
    parser.add_argument("--project-license", default="LICENSE")
    parser.add_argument("--project-notice", default="NOTICE")
    archive, checksum, inventory = build(parser.parse_args())
    print(archive)
    print(checksum)
    print(inventory)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
