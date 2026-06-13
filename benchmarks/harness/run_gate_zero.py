#!/usr/bin/env python3
"""Gate Zero harness readiness guard.

The G1/G2/G3 measurement runner must not execute until the corpus/hardware
manifest is frozen and every reference competitor is pinned. This script makes
that precondition executable and emits JSON so blocked runs are auditable.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import signal
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / "benchmarks" / "gate-zero" / "manifest.json"
DEFAULT_COMPETITORS = ROOT / "benchmarks" / "competitors.lock.json"
DEFAULT_RESULTS = ROOT / "benchmarks" / "results" / "gate-zero" / "readiness.json"
DEFAULT_GATE_ZERO_RESULT = ROOT / "benchmarks" / "results" / "gate-zero" / "g1.json"
DEFAULT_PROFILE = ROOT / "profiles" / "ethos-deterministic-v1.json"
HEX64 = re.compile(r"[0-9a-f]{64}")
EXPECTED_GATE_ZERO_COMPETITORS = {
    "opendataloader-pdf",
    "edgeparse",
    "liteparse",
    "pymupdf4llm",
}
COMPETITOR_IDS = (
    "opendataloader-pdf",
    "edgeparse",
    "liteparse",
    "pymupdf4llm",
)
COMPETITOR_COMMAND_LABELS = {
    "opendataloader-pdf": "<opendataloader-command>",
    "edgeparse": "<edgeparse-command>",
    "liteparse": "<liteparse-command>",
    "pymupdf4llm": "<pymupdf4llm-python>",
}
RESULT_COMPETITOR_LOCK_STATUSES = {"FROZEN", "FROZEN-SIGNED"}
PYMUPDF4LLM_SCRIPT = (
    "import sys, pymupdf4llm; "
    "sys.stdout.write(pymupdf4llm.to_json(sys.argv[1], show_progress=False, use_ocr=False))"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def c14n_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_c14n_value(value: Any) -> str:
    return sha256_bytes(c14n_json_bytes(value))


def sha256_c14n_file(path: Path) -> str:
    return sha256_c14n_value(load_json(path))


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path | None, value: Any) -> None:
    text = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)
    if path is None:
        print(text)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{text}\n", encoding="utf-8")


def report_path(repo_root: Path, path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(repo_root.resolve()))
    except ValueError:
        return str(path)


def percentile(values: list[float], pct: float) -> float | None:
    if not values:
        return None
    if len(values) == 1:
        return values[0]
    ordered = sorted(values)
    rank = (len(ordered) - 1) * pct
    lower = int(rank)
    upper = min(lower + 1, len(ordered) - 1)
    weight = rank - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def path_size_bytes(path: Path) -> int:
    if path.is_file():
        return path.stat().st_size
    total = 0
    for child in path.rglob("*"):
        if child.is_file():
            total += child.stat().st_size
    return total


def output_tree_hash(path: Path) -> str:
    files = [
        child
        for child in sorted(path.rglob("*"), key=lambda item: item.relative_to(path).as_posix())
        if child.is_file()
    ]
    projection = [
        {
            "path": child.relative_to(path).as_posix(),
            "sha256": sha256_file(child),
        }
        for child in files
    ]
    return sha256_c14n_value(projection)


def current_platform_key() -> str:
    system = platform.system().lower()
    machine = platform.machine().lower()
    if system == "darwin" and machine in {"arm64", "aarch64"}:
        return "macos-arm64"
    if system == "linux" and machine in {"x86_64", "amd64"}:
        return "linux-x64"
    if system == "windows" and machine in {"amd64", "x86_64"}:
        return "windows-x64"
    return f"{system}-{machine}"


def child_pids(pid: int) -> list[int]:
    if os.name != "posix":
        return []
    try:
        completed = subprocess.run(
            ["pgrep", "-P", str(pid)],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except OSError:
        return []
    if completed.returncode not in {0, 1}:
        return []
    pids: list[int] = []
    for line in completed.stdout.decode("utf-8", errors="replace").splitlines():
        try:
            pids.append(int(line.strip()))
        except ValueError:
            pass
    return pids


def process_tree_pids(root_pid: int) -> list[int]:
    seen: set[int] = set()
    pending = [root_pid]
    while pending:
        pid = pending.pop()
        if pid in seen:
            continue
        seen.add(pid)
        pending.extend(child_pids(pid))
    return sorted(seen)


def process_tree_rss_bytes(root_pid: int) -> int | None:
    if os.name != "posix":
        return None
    pids = process_tree_pids(root_pid)
    if not pids:
        return None
    try:
        completed = subprocess.run(
            ["ps", "-o", "rss=", "-p", ",".join(str(pid) for pid in pids)],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except OSError:
        return None
    if completed.returncode != 0:
        return None
    total_kib = 0
    for line in completed.stdout.decode("utf-8", errors="replace").splitlines():
        try:
            total_kib += int(line.strip())
        except ValueError:
            pass
    if total_kib <= 0:
        return None
    return total_kib * 1024


def kill_process_tree(process: subprocess.Popen[bytes]) -> None:
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGKILL)
            return
        except ProcessLookupError:
            return
        except OSError:
            pass
    process.kill()


def measure_command(args: list[str], timeout_sec: float) -> dict[str, Any]:
    start = time.perf_counter()
    peak_rss: int | None = None
    timeout = False
    with tempfile.TemporaryFile() as stdout_file, tempfile.TemporaryFile() as stderr_file:
        process = subprocess.Popen(
            args,
            stdout=stdout_file,
            stderr=stderr_file,
            start_new_session=os.name == "posix",
        )
        while True:
            sampled_rss = process_tree_rss_bytes(process.pid)
            if sampled_rss is not None:
                peak_rss = max(peak_rss or 0, sampled_rss)
            if process.poll() is not None:
                break
            if time.perf_counter() - start > timeout_sec:
                timeout = True
                kill_process_tree(process)
                process.wait()
                break
            time.sleep(0.02)

        stdout_file.seek(0)
        stderr_file.seek(0)
        completed = subprocess.CompletedProcess(
            args,
            124 if timeout else process.returncode,
            stdout=stdout_file.read(),
            stderr=stderr_file.read(),
        )
    return {
        "completed": completed,
        "duration_ms": (time.perf_counter() - start) * 1000.0,
        "peak_rss_bytes": peak_rss,
        "timeout": timeout,
    }


def is_filled(value: Any) -> bool:
    return value is not None and value != "" and value != "_____________"


def check_manifest(manifest: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if manifest.get("frozen") is not True:
        blockers.append("Gate Zero manifest is not frozen")
    if str(manifest.get("status", "")).upper() not in {"FROZEN", "FROZEN-SIGNED"}:
        blockers.append("Gate Zero manifest status is not FROZEN/FROZEN-SIGNED")

    record = manifest.get("freeze_record", {})
    if not is_filled(record.get("frozen_at")):
        blockers.append("Gate Zero freeze_record.frozen_at is blank")
    if not is_filled(record.get("signed_by")):
        blockers.append("Gate Zero freeze_record.signed_by is blank")

    corpus = manifest.get("corpus", [])
    if not corpus:
        blockers.append("Gate Zero corpus[] is empty")
    for index, entry in enumerate(corpus, 1):
        prefix = f"Gate Zero corpus entry {index}"
        for field in ["file", "sha256", "pages", "subsets", "provenance", "license"]:
            if not is_filled(entry.get(field)):
                blockers.append(f"{prefix} missing {field}")
        sha = str(entry.get("sha256", ""))
        if not HEX64.fullmatch(sha):
            blockers.append(f"{prefix} sha256 is not lowercase hex")

    performance_hosts = [
        host for host in manifest.get("hardware", []) if host.get("role") == "performance"
    ]
    if not performance_hosts:
        blockers.append("Gate Zero manifest has no performance hardware host")
    for host in performance_hosts:
        host_id = host.get("id", "<unknown>")
        for field in ["model", "cpu", "ram", "os", "kernel", "runner"]:
            if not is_filled(host.get(field)):
                blockers.append(f"hardware {host_id} missing {field}")

    return blockers


def check_competitors(lock: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if str(lock.get("status", "")).upper() not in {"PINNED", "FROZEN", "FROZEN-SIGNED"}:
        blockers.append("competitors lock status is not PINNED/FROZEN/FROZEN-SIGNED")

    entries = lock.get("gate_zero", [])
    if not entries:
        blockers.append("competitors lock gate_zero[] is empty")
    found = {entry.get("id") for entry in entries}
    for competitor_id in sorted(EXPECTED_GATE_ZERO_COMPETITORS - found):
        blockers.append(f"competitor {competitor_id} missing from gate_zero lock")
    for entry in entries:
        competitor_id = entry.get("id", "<unknown>")
        if entry.get("pinned") is not True:
            blockers.append(f"competitor {competitor_id} is not pinned")
        if not is_filled(entry.get("version")):
            blockers.append(f"competitor {competitor_id} missing version")
        if not is_filled(entry.get("artifact_sha256")):
            blockers.append(f"competitor {competitor_id} missing artifact_sha256")
        sha = str(entry.get("artifact_sha256", ""))
        if not HEX64.fullmatch(sha):
            blockers.append(f"competitor {competitor_id} artifact_sha256 is not lowercase hex")
        platform_artifacts = entry.get("platform_artifacts")
        if platform_artifacts is not None:
            if not isinstance(platform_artifacts, dict) or not platform_artifacts:
                blockers.append(
                    f"competitor {competitor_id} platform_artifacts is not a non-empty object"
                )
            else:
                for platform_key, artifact in sorted(platform_artifacts.items()):
                    if not isinstance(artifact, dict):
                        blockers.append(
                            f"competitor {competitor_id} platform_artifacts.{platform_key} "
                            "is not an object"
                        )
                        continue
                    platform_sha = str(artifact.get("artifact_sha256", ""))
                    if not HEX64.fullmatch(platform_sha):
                        blockers.append(
                            f"competitor {competitor_id} platform_artifacts.{platform_key} "
                            "artifact_sha256 is not lowercase hex"
                        )
                    if not is_filled(artifact.get("artifact_filename")):
                        blockers.append(
                            f"competitor {competitor_id} platform_artifacts.{platform_key} "
                            "missing artifact_filename"
                        )
        if "jvm_version" in entry and not is_filled(entry.get("jvm_version")):
            blockers.append(f"competitor {competitor_id} missing jvm_version")
        if "python_version" in entry and not is_filled(entry.get("python_version")):
            blockers.append(f"competitor {competitor_id} missing python_version")

    return blockers


def build_readiness_report(
    repo_root: Path,
    manifest_path: Path,
    competitors_path: Path,
) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    competitors = load_json(competitors_path)
    manifest_blockers = check_manifest(manifest)
    competitor_blockers = check_competitors(competitors)
    blockers = manifest_blockers + competitor_blockers

    return {
        "schema_version": "ethos-gate-zero-readiness-v1",
        "status": "ready" if not blockers else "blocked",
        "harness": {
            "name": "gate-zero-readiness",
            "runner": "benchmarks/harness/run_gate_zero.py",
            "scope": "readiness-only",
        },
        "inputs": {
            "repo_root": str(repo_root),
            "manifest": str(manifest_path.relative_to(repo_root)),
            "manifest_sha256": sha256_file(manifest_path),
            "competitors_lock": str(competitors_path.relative_to(repo_root)),
            "competitors_lock_sha256": sha256_file(competitors_path),
        },
        "blockers": {
            "manifest": manifest_blockers,
            "competitors": competitor_blockers,
        },
        "summary": {
            "blockers_total": len(blockers),
            "manifest_blockers": len(manifest_blockers),
            "competitor_blockers": len(competitor_blockers),
        },
    }


def build_report(
    repo_root: Path,
    manifest_path: Path,
    competitors_path: Path,
) -> dict[str, Any]:
    return build_readiness_report(repo_root, manifest_path, competitors_path)


def result_freeze_blockers(competitors: dict[str, Any]) -> list[str]:
    status = str(competitors.get("status", "")).upper()
    if status not in RESULT_COMPETITOR_LOCK_STATUSES:
        return ["competitors lock status is not FROZEN/FROZEN-SIGNED for result generation"]
    return []


def select_host(manifest: dict[str, Any], requested_host_id: str | None) -> dict[str, Any] | None:
    hosts = [
        host for host in manifest.get("hardware", []) if host.get("role") == "performance"
    ]
    if requested_host_id:
        return next((host for host in hosts if host.get("id") == requested_host_id), None)
    platform_key = current_platform_key()
    return next((host for host in hosts if host.get("platform") == platform_key), None)


def env_path(name: str) -> Path | None:
    value = os.environ.get(name)
    return Path(value) if value else None


def resolve_competitor_paths(
    args: argparse.Namespace,
    competitor_id: str,
) -> tuple[Path | None, Path | None, Path | None]:
    if competitor_id == "opendataloader-pdf":
        command = args.opendataloader_command or env_path("ETHOS_OPENDATALOADER_PDF_BIN")
        if command is None and args.opendataloader_root is not None:
            command = args.opendataloader_root / "scripts" / "run-cli.sh"
        artifact = args.opendataloader_artifact or env_path("ETHOS_OPENDATALOADER_PDF_ARTIFACT")
        install_path = args.opendataloader_install_path or artifact
        return command, artifact, install_path
    if competitor_id == "edgeparse":
        command = args.edgeparse_command or env_path("ETHOS_EDGEPARSE_BIN")
        artifact = args.edgeparse_artifact or env_path("ETHOS_EDGEPARSE_ARTIFACT")
        install_path = args.edgeparse_install_path or artifact
        return command, artifact, install_path
    if competitor_id == "liteparse":
        command = args.liteparse_command or env_path("ETHOS_LITEPARSE_BIN")
        artifact = args.liteparse_artifact or env_path("ETHOS_LITEPARSE_ARTIFACT")
        install_path = args.liteparse_install_path or artifact
        return command, artifact, install_path
    if competitor_id == "pymupdf4llm":
        command = args.pymupdf4llm_python or env_path("ETHOS_PYMUPDF4LLM_PYTHON")
        artifact = args.pymupdf4llm_artifact or env_path("ETHOS_PYMUPDF4LLM_ARTIFACT")
        install_path = args.pymupdf4llm_install_path or artifact
        return command, artifact, install_path
    raise ValueError(f"unknown competitor: {competitor_id}")


def warning_ids(doc: dict[str, Any]) -> list[str]:
    payload = doc.get("payload", {})
    warnings = payload.get("security_warnings", []) + payload.get("parser_warnings", [])
    return [warning.get("id") for warning in warnings if isinstance(warning.get("id"), str)]


def is_fingerprint_form(value: Any) -> bool:
    return (
        isinstance(value, str)
        and value.startswith("sha256:")
        and HEX64.fullmatch(value[7:]) is not None
    )


def run_entry_result(
    entry: dict[str, Any],
    parser_target: str,
    command: list[str],
    failures: list[str],
    actual_sha256: str | None = None,
) -> dict[str, Any]:
    return {
        "corpus_file": {
            "id": entry.get("id"),
            "file": entry["file"],
            "sha256": entry["sha256"],
            "actual_sha256": actual_sha256,
            "pages": entry["pages"],
            "subsets": entry["subsets"],
        },
        "parser_target": parser_target,
        "command": command,
        "exit_code": None,
        "duration_ms_p50": None,
        "duration_ms_p95": None,
        "duration_ms_p99": None,
        "peak_rss_bytes": None,
        "output_sha256": None,
        "payload_sha256": None,
        "document_fingerprint": None,
        "warning_ids": [],
        "status": "fail",
        "failures": failures,
    }


def run_ethos_entry(
    repo_root: Path,
    ethos_bin: Path,
    entry: dict[str, Any],
    iterations: int,
    timeout_sec: float,
) -> dict[str, Any]:
    file_path = repo_root / entry["file"]
    command = [str(ethos_bin), "doc", "parse", str(file_path), "--format", "json"]
    report_command = [
        report_path(repo_root, ethos_bin),
        "doc",
        "parse",
        entry["file"],
        "--format",
        "json",
    ]
    try:
        actual_sha256 = sha256_file(file_path)
    except FileNotFoundError:
        return run_entry_result(entry, "ethos", report_command, ["corpus file is missing"])
    if actual_sha256 != entry["sha256"]:
        return run_entry_result(
            entry,
            "ethos",
            report_command,
            [
                "corpus sha256 mismatch: "
                f"manifest={entry['sha256']} actual={actual_sha256}"
            ],
            actual_sha256,
        )

    durations: list[float] = []
    rss_values: list[int] = []
    output_hashes: list[str] = []
    payload_hashes: list[str] = []
    fingerprints: list[str] = []
    warning_id_sets: list[list[str]] = []
    exit_codes: list[int] = []
    failures: list[str] = []

    for _ in range(iterations):
        measured = measure_command(command, timeout_sec)
        completed: subprocess.CompletedProcess[bytes] = measured["completed"]
        durations.append(measured["duration_ms"])
        if measured["peak_rss_bytes"] is not None:
            rss_values.append(measured["peak_rss_bytes"])
        exit_codes.append(completed.returncode)
        if measured["timeout"]:
            failures.append(f"command timed out after {timeout_sec:g}s")
            continue
        if completed.returncode != 0:
            stderr = completed.stderr.decode("utf-8", errors="replace").strip()
            failures.append(f"exit {completed.returncode}: {stderr}")
            continue
        output_hashes.append(sha256_bytes(completed.stdout))
        try:
            doc = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            failures.append(f"stdout is not JSON: {exc}")
            continue
        payload_sha256 = doc.get("payload_sha256")
        if not isinstance(payload_sha256, str) or HEX64.fullmatch(payload_sha256) is None:
            failures.append("payload_sha256 is missing or malformed")
        else:
            payload_hashes.append(payload_sha256)
        fingerprint = doc.get("fingerprint")
        if not is_fingerprint_form(fingerprint):
            failures.append("document fingerprint is missing or malformed")
        else:
            fingerprints.append(fingerprint)
        warning_id_sets.append(warning_ids(doc))

    if len(set(output_hashes)) > 1:
        failures.append("output_sha256 changed across iterations")
    if len(set(payload_hashes)) > 1:
        failures.append("payload_sha256 changed across iterations")
    if len(set(fingerprints)) > 1:
        failures.append("document fingerprint changed across iterations")
    if len({tuple(ids) for ids in warning_id_sets}) > 1:
        failures.append("warning ids changed across iterations")

    return {
        "corpus_file": {
            "id": entry.get("id"),
            "file": entry["file"],
            "sha256": entry["sha256"],
            "actual_sha256": actual_sha256,
            "pages": entry["pages"],
            "subsets": entry["subsets"],
        },
        "parser_target": "ethos",
        "command": report_command,
        "exit_code": exit_codes[-1] if exit_codes else None,
        "duration_ms_p50": percentile(durations, 0.50),
        "duration_ms_p95": percentile(durations, 0.95),
        "duration_ms_p99": percentile(durations, 0.99),
        "peak_rss_bytes": max(rss_values) if rss_values else None,
        "output_sha256": output_hashes[0] if output_hashes else None,
        "payload_sha256": payload_hashes[0] if payload_hashes else None,
        "document_fingerprint": fingerprints[0] if fingerprints else None,
        "warning_ids": warning_id_sets[0] if warning_id_sets else [],
        "status": "pass" if not failures else "fail",
        "failures": failures,
    }


def competitor_lock_entry(lock: dict[str, Any], competitor_id: str) -> dict[str, Any] | None:
    return next(
        (entry for entry in lock.get("gate_zero", []) if entry.get("id") == competitor_id),
        None,
    )


def opendataloader_lock_entry(lock: dict[str, Any]) -> dict[str, Any] | None:
    return competitor_lock_entry(lock, "opendataloader-pdf")


def lock_artifact_record(
    lock_entry: dict[str, Any] | None,
    platform_key: str | None,
) -> dict[str, Any] | None:
    if lock_entry is None:
        return None
    platform_artifacts = lock_entry.get("platform_artifacts")
    if platform_key and isinstance(platform_artifacts, dict):
        record = platform_artifacts.get(platform_key)
        if isinstance(record, dict):
            return record
    return lock_entry


def lock_artifact_hash(
    lock_entry: dict[str, Any] | None,
    platform_key: str | None = None,
) -> str | None:
    if lock_entry is None:
        return None
    record = lock_artifact_record(lock_entry, platform_key)
    if record is None:
        return None
    value = record.get("artifact_sha256")
    return value if isinstance(value, str) and HEX64.fullmatch(value) else None


def competitor_command_template(competitor_id: str) -> list[str]:
    if competitor_id == "opendataloader-pdf":
        return [
            COMPETITOR_COMMAND_LABELS[competitor_id],
            "--quiet",
            "--format",
            "json",
            "--image-output",
            "external",
            "--reading-order",
            "xycut",
            "--table-method",
            "default",
            "--threads",
            "1",
            "--output-dir",
            "<output-dir>",
            "<input-pdf>",
        ]
    if competitor_id == "edgeparse":
        return [
            COMPETITOR_COMMAND_LABELS[competitor_id],
            "<input-pdf>",
            "--format",
            "json",
            "--output-dir",
            "<output-dir>",
        ]
    if competitor_id == "liteparse":
        return [
            COMPETITOR_COMMAND_LABELS[competitor_id],
            "parse",
            "<input-pdf>",
            "--format",
            "json",
            "--output",
            "<output-file>",
            "--no-ocr",
            "--num-workers",
            "1",
            "--quiet",
        ]
    if competitor_id == "pymupdf4llm":
        return [
            COMPETITOR_COMMAND_LABELS[competitor_id],
            "-c",
            "<pymupdf4llm-script>",
            "<input-pdf>",
        ]
    raise ValueError(f"unknown competitor: {competitor_id}")


def build_competitor_adapter(
    competitor_id: str,
    command_path: Path | None,
    artifact_path: Path | None,
    install_path: Path | None,
    lock_entry: dict[str, Any] | None,
    platform_key: str | None = None,
) -> dict[str, Any]:
    blockers: list[str] = []
    notes: list[str] = []
    command: list[str] | None = None
    artifact_sha256: str | None = None
    install_size_bytes: int | None = None
    if lock_entry is None:
        blockers.append(f"{competitor_id} lock entry is missing")
    else:
        if lock_entry.get("pinned") is not True:
            blockers.append(f"{competitor_id} is not pinned")
        if not is_filled(lock_entry.get("version")):
            blockers.append(f"{competitor_id} version is missing")
        if not is_filled(lock_entry.get("artifact_sha256")):
            blockers.append(f"{competitor_id} artifact_sha256 is missing")
    expected_artifact_sha256 = lock_artifact_hash(lock_entry, platform_key)
    if command_path is None:
        notes.append(f"command not configured; Ethos-only result mode does not execute {competitor_id}")
    elif not command_path.is_file():
        blockers.append(f"{competitor_id} command does not exist")
    elif not os.access(command_path, os.X_OK):
        blockers.append(f"{competitor_id} command is not executable")
    if command_path is not None:
        if artifact_path is None:
            blockers.append(f"{competitor_id} artifact path is not configured")
        elif not artifact_path.is_file():
            blockers.append(f"{competitor_id} artifact path does not exist")
        else:
            artifact_sha256 = sha256_file(artifact_path)
            if expected_artifact_sha256 and artifact_sha256 != expected_artifact_sha256:
                blockers.append(f"{competitor_id} artifact sha256 does not match lock")
        if install_path is None:
            blockers.append(f"{competitor_id} install path is not configured")
        elif not install_path.exists():
            blockers.append(f"{competitor_id} install path does not exist")
        else:
            install_size_bytes = path_size_bytes(install_path)
    if command_path is not None and not blockers:
        command = competitor_command_template(competitor_id)
    else:
        command = None
    status = "ready" if command and not blockers else "not_configured"
    if blockers:
        status = "blocked"
    return {
        "id": competitor_id,
        "status": status,
        "mode": "execute" if command else "metadata_only",
        "command": COMPETITOR_COMMAND_LABELS[competitor_id] if command_path else None,
        "command_template": command,
        "artifact": {
            "path": f"<{competitor_id}-artifact>" if artifact_path else None,
            "sha256": artifact_sha256,
            "expected_sha256": expected_artifact_sha256,
        },
        "install_size_bytes": install_size_bytes,
        "lock": lock_entry,
        "blockers": blockers,
        "notes": notes,
    }


def build_opendataloader_adapter(
    command_path: Path | None,
    artifact_path: Path | None,
    install_path: Path | None,
    lock_entry: dict[str, Any] | None,
) -> dict[str, Any]:
    return build_competitor_adapter(
        "opendataloader-pdf",
        command_path,
        artifact_path,
        install_path,
        lock_entry,
    )


def report_competitor_command(competitor_id: str, entry: dict[str, Any]) -> list[str]:
    command = competitor_command_template(competitor_id)
    return [
        entry["file"] if value == "<input-pdf>" else value
        for value in command
    ]


def competitor_execution_command(
    competitor_id: str,
    command_path: Path,
    file_path: Path,
    output_dir: Path,
) -> tuple[list[str], Path | None, bool]:
    if competitor_id == "opendataloader-pdf":
        output_file = output_dir / f"{file_path.stem}.json"
        return (
            [
                str(command_path),
                "--quiet",
                "--format",
                "json",
                "--image-output",
                "external",
                "--reading-order",
                "xycut",
                "--table-method",
                "default",
                "--threads",
                "1",
                "--output-dir",
                str(output_dir),
                str(file_path),
            ],
            output_file,
            True,
        )
    if competitor_id == "edgeparse":
        output_file = output_dir / f"{file_path.stem}.json"
        return (
            [
                str(command_path),
                str(file_path),
                "--format",
                "json",
                "--output-dir",
                str(output_dir),
            ],
            output_file,
            True,
        )
    if competitor_id == "liteparse":
        output_file = output_dir / f"{file_path.stem}.json"
        return (
            [
                str(command_path),
                "parse",
                str(file_path),
                "--format",
                "json",
                "--output",
                str(output_file),
                "--no-ocr",
                "--num-workers",
                "1",
                "--quiet",
            ],
            output_file,
            True,
        )
    if competitor_id == "pymupdf4llm":
        return (
            [str(command_path), "-c", PYMUPDF4LLM_SCRIPT, str(file_path)],
            None,
            False,
        )
    raise ValueError(f"unknown competitor: {competitor_id}")


def run_competitor_entry(
    repo_root: Path,
    competitor_id: str,
    command_path: Path,
    entry: dict[str, Any],
    iterations: int,
    timeout_sec: float,
) -> dict[str, Any]:
    file_path = repo_root / entry["file"]
    report_command = report_competitor_command(competitor_id, entry)
    try:
        actual_sha256 = sha256_file(file_path)
    except FileNotFoundError:
        return run_entry_result(
            entry,
            competitor_id,
            report_command,
            ["corpus file is missing"],
        )
    if actual_sha256 != entry["sha256"]:
        return run_entry_result(
            entry,
            competitor_id,
            report_command,
            [
                "corpus sha256 mismatch: "
                f"manifest={entry['sha256']} actual={actual_sha256}"
            ],
            actual_sha256,
        )

    durations: list[float] = []
    rss_values: list[int] = []
    output_hashes: list[str] = []
    exit_codes: list[int] = []
    failures: list[str] = []

    for _ in range(iterations):
        with tempfile.TemporaryDirectory(prefix=f"ethos-{competitor_id}-") as tmp:
            output_dir = Path(tmp)
            command, output_file, expects_json_file = competitor_execution_command(
                competitor_id,
                command_path,
                file_path,
                output_dir,
            )
            measured = measure_command(command, timeout_sec)
            completed: subprocess.CompletedProcess[bytes] = measured["completed"]
            durations.append(measured["duration_ms"])
            if measured["peak_rss_bytes"] is not None:
                rss_values.append(measured["peak_rss_bytes"])
            exit_codes.append(completed.returncode)
            if measured["timeout"]:
                failures.append(f"command timed out after {timeout_sec:g}s")
                continue
            if completed.returncode != 0:
                stderr = completed.stderr.decode("utf-8", errors="replace").strip()
                stdout = completed.stdout.decode("utf-8", errors="replace").strip()
                detail = stderr or stdout
                failures.append(f"exit {completed.returncode}: {detail}")
                continue
            if expects_json_file:
                assert output_file is not None
                if not output_file.is_file():
                    failures.append("expected JSON output file was not produced")
                    continue
                output = output_file.read_bytes()
                try:
                    json.loads(output)
                except json.JSONDecodeError as exc:
                    failures.append(f"output JSON is invalid: {exc}")
                    continue
                output_hashes.append(output_tree_hash(output_dir))
                continue
            output = completed.stdout
            if not output.strip():
                failures.append("expected text output was not produced")
                continue
            if competitor_id == "pymupdf4llm":
                try:
                    json.loads(output)
                except json.JSONDecodeError as exc:
                    failures.append(f"stdout JSON is invalid: {exc}")
                    continue
            output_hashes.append(sha256_bytes(output))

    if len(set(output_hashes)) > 1:
        failures.append("output_sha256 changed across iterations")

    return {
        "corpus_file": {
            "id": entry.get("id"),
            "file": entry["file"],
            "sha256": entry["sha256"],
            "actual_sha256": actual_sha256,
            "pages": entry["pages"],
            "subsets": entry["subsets"],
        },
        "parser_target": competitor_id,
        "command": report_command,
        "exit_code": exit_codes[-1] if exit_codes else None,
        "duration_ms_p50": percentile(durations, 0.50),
        "duration_ms_p95": percentile(durations, 0.95),
        "duration_ms_p99": percentile(durations, 0.99),
        "peak_rss_bytes": max(rss_values) if rss_values else None,
        "output_sha256": output_hashes[0] if output_hashes else None,
        "payload_sha256": None,
        "document_fingerprint": None,
        "warning_ids": [],
        "status": "pass" if not failures else "fail",
        "failures": failures,
    }


def run_opendataloader_entry(
    repo_root: Path,
    command_path: Path,
    entry: dict[str, Any],
    iterations: int,
    timeout_sec: float,
) -> dict[str, Any]:
    return run_competitor_entry(
        repo_root,
        "opendataloader-pdf",
        command_path,
        entry,
        iterations,
        timeout_sec,
    )


def aggregate_output_hash(runs: list[dict[str, Any]]) -> str | None:
    if not runs or any(run["status"] != "pass" for run in runs):
        return None
    projection = [
        {
            "corpus_file": {
                "id": run["corpus_file"]["id"],
                "file": run["corpus_file"]["file"],
                "sha256": run["corpus_file"]["sha256"],
            },
            "document_fingerprint": run["document_fingerprint"],
            "output_sha256": run["output_sha256"],
            "payload_sha256": run.get("payload_sha256"),
            "warning_ids": run["warning_ids"],
        }
        for run in runs
    ]
    return sha256_c14n_value(projection)


def parser_summary(
    runs: list[dict[str, Any]],
    iterations: int,
    install_size_bytes: int | None,
) -> dict[str, Any]:
    failed_runs = [run for run in runs if run["status"] != "pass"]
    duration_p50_values = [
        run["duration_ms_p50"] for run in runs if run["duration_ms_p50"] is not None
    ]
    duration_p95_values = [
        run["duration_ms_p95"] for run in runs if run["duration_ms_p95"] is not None
    ]
    duration_p99_values = [
        run["duration_ms_p99"] for run in runs if run["duration_ms_p99"] is not None
    ]
    rss_values = [
        run["peak_rss_bytes"] for run in runs if run["peak_rss_bytes"] is not None
    ]
    return {
        "status": "fail" if failed_runs else "pass",
        "runs_total": len(runs),
        "runs_failed": len(failed_runs),
        "iterations": iterations,
        "duration_ms_p50": statistics.median(duration_p50_values)
        if duration_p50_values
        else None,
        "duration_ms_p95": max(duration_p95_values, default=None),
        "duration_ms_p99": max(duration_p99_values, default=None),
        "peak_rss_bytes": max(rss_values, default=None),
        "output_sha256": aggregate_output_hash(runs),
        "install_size_bytes": install_size_bytes,
    }


def build_result_report(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = args.repo_root.resolve()
    manifest_path = args.manifest.resolve()
    competitors_path = args.competitors_lock.resolve()
    manifest = load_json(manifest_path)
    competitors = load_json(competitors_path)
    readiness = build_readiness_report(repo_root, manifest_path, competitors_path)
    freeze_blockers = result_freeze_blockers(competitors)
    host = select_host(manifest, args.host_id)
    result_blockers = list(freeze_blockers)
    if host is None:
        result_blockers.append("no matching performance host for this runner")
    if not args.deterministic_profile.is_file():
        result_blockers.append("deterministic profile is missing")
    if not args.ethos_bin.is_file():
        result_blockers.append("ethos binary is missing")
    if readiness["status"] != "ready":
        result_blockers.append("Gate Zero readiness is blocked")
    artifact_platform = host.get("platform") if isinstance(host, dict) else current_platform_key()

    competitor_commands: dict[str, Path | None] = {}
    competitor_adapters: list[dict[str, Any]] = []
    for competitor_id in COMPETITOR_IDS:
        command_path, artifact_path, install_path = resolve_competitor_paths(args, competitor_id)
        competitor_commands[competitor_id] = command_path
        adapter = build_competitor_adapter(
            competitor_id,
            command_path,
            artifact_path,
            install_path,
            competitor_lock_entry(competitors, competitor_id),
            artifact_platform,
        )
        competitor_adapters.append(adapter)
        if command_path is not None and adapter["status"] == "blocked":
            result_blockers.extend(adapter["blockers"])

    runs: list[dict[str, Any]] = []
    competitor_runs: dict[str, list[dict[str, Any]]] = {
        competitor_id: [] for competitor_id in COMPETITOR_IDS
    }
    if not result_blockers:
        for entry in manifest.get("corpus", []):
            runs.append(
                run_ethos_entry(
                    repo_root,
                    args.ethos_bin.resolve(),
                    entry,
                    args.iterations,
                    args.timeout_sec,
                )
            )
        for adapter in competitor_adapters:
            competitor_id = adapter["id"]
            if adapter["status"] != "ready":
                continue
            command_path = competitor_commands[competitor_id]
            assert command_path is not None
            for entry in manifest.get("corpus", []):
                competitor_runs[competitor_id].append(
                    run_competitor_entry(
                        repo_root,
                        competitor_id,
                        command_path,
                        entry,
                        args.iterations,
                        args.timeout_sec,
                    )
                )

    ethos_summary = parser_summary(runs, args.iterations, path_size_bytes(args.install_path))
    competitor_summaries = {
        adapter["id"]: parser_summary(
            competitor_runs[adapter["id"]],
            args.iterations,
            adapter["install_size_bytes"],
        )
        for adapter in competitor_adapters
    }
    failed_runs = [run for run in runs if run["status"] != "pass"]
    failed_competitor_runs = [
        run
        for runs_for_competitor in competitor_runs.values()
        for run in runs_for_competitor
        if run["status"] != "pass"
    ]
    status = "blocked" if result_blockers else (
        "fail" if failed_runs or failed_competitor_runs else "pass"
    )
    command = [
        report_path(repo_root, args.ethos_bin),
        "doc",
        "parse",
        "<corpus-file>",
        "--format",
        "json",
    ]
    return {
        "schema_version": "ethos-gate-zero-result-v1",
        "status": status,
        "corpus": {
            "id": manifest.get("corpus_id", "gate-zero-v1"),
            "manifest": str(manifest_path.relative_to(repo_root)),
            "manifest_sha256": sha256_file(manifest_path),
        },
        "parser_target": "ethos",
        "command": command,
        "exit_code": None if not runs else runs[-1]["exit_code"],
        "duration_ms_p50": ethos_summary["duration_ms_p50"],
        "duration_ms_p95": ethos_summary["duration_ms_p95"],
        "duration_ms_p99": ethos_summary["duration_ms_p99"],
        "peak_rss_bytes": ethos_summary["peak_rss_bytes"],
        "output_sha256": ethos_summary["output_sha256"],
        "install_size_bytes": ethos_summary["install_size_bytes"],
        "host": {
            "selected": host,
            "observed": {
                "platform": platform.platform(),
                "machine": platform.machine(),
                "python": platform.python_version(),
                "platform_key": current_platform_key(),
            },
        },
        "deterministic_profile_sha256": sha256_c14n_file(args.deterministic_profile)
        if args.deterministic_profile.is_file()
        else None,
        "inputs": {
            "competitors_lock": str(competitors_path.relative_to(repo_root)),
            "competitors_lock_sha256": sha256_file(competitors_path),
            "deterministic_profile": report_path(repo_root, args.deterministic_profile),
            "deterministic_profile_file_sha256": sha256_file(args.deterministic_profile)
            if args.deterministic_profile.is_file()
            else None,
            "ethos_bin": report_path(repo_root, args.ethos_bin),
            "ethos_bin_sha256": sha256_file(args.ethos_bin) if args.ethos_bin.is_file() else None,
            "install_path": report_path(repo_root, args.install_path),
        },
        "readiness": {
            "status": readiness["status"],
            "summary": readiness["summary"],
            "blockers": readiness["blockers"],
        },
        "blockers": result_blockers,
        "competitors": {
            "adapters": competitor_adapters,
            "runs": competitor_runs,
            "summaries": competitor_summaries,
        },
        "runs": runs,
        "summary": ethos_summary,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["readiness", "ethos"], default="readiness")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--competitors-lock", type=Path, default=DEFAULT_COMPETITORS)
    parser.add_argument("--out", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--stdout", action="store_true", help="write report to stdout instead of --out")
    parser.add_argument("--ethos-bin", type=Path, default=ROOT / "target" / "release" / "ethos")
    parser.add_argument("--host-id")
    parser.add_argument("--deterministic-profile", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument("--install-path", type=Path, default=ROOT / "target" / "release" / "ethos")
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument("--timeout-sec", type=float, default=120.0)
    parser.add_argument("--opendataloader-root", type=Path)
    parser.add_argument("--opendataloader-command", type=Path)
    parser.add_argument("--opendataloader-artifact", type=Path)
    parser.add_argument("--opendataloader-install-path", type=Path)
    parser.add_argument("--edgeparse-command", type=Path)
    parser.add_argument("--edgeparse-artifact", type=Path)
    parser.add_argument("--edgeparse-install-path", type=Path)
    parser.add_argument("--liteparse-command", type=Path)
    parser.add_argument("--liteparse-artifact", type=Path)
    parser.add_argument("--liteparse-install-path", type=Path)
    parser.add_argument("--pymupdf4llm-python", type=Path)
    parser.add_argument("--pymupdf4llm-artifact", type=Path)
    parser.add_argument("--pymupdf4llm-install-path", type=Path)
    args = parser.parse_args(argv)

    if not args.manifest.is_file():
        parser.error(f"--manifest does not exist: {args.manifest}")
    if not args.competitors_lock.is_file():
        parser.error(f"--competitors-lock does not exist: {args.competitors_lock}")
    if args.iterations < 1:
        parser.error("--iterations must be >= 1")
    if args.timeout_sec <= 0:
        parser.error("--timeout-sec must be > 0")
    if args.mode == "ethos":
        if args.out == DEFAULT_RESULTS:
            args.out = DEFAULT_GATE_ZERO_RESULT
        if not args.install_path.exists():
            parser.error(f"--install-path does not exist: {args.install_path}")
    return args


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    repo_root = args.repo_root.resolve()
    manifest_path = args.manifest.resolve()
    competitors_path = args.competitors_lock.resolve()
    report = (
        build_readiness_report(repo_root, manifest_path, competitors_path)
        if args.mode == "readiness"
        else build_result_report(args)
    )
    write_json(None if args.stdout else args.out, report)
    if report["status"] == "ready":
        print("Gate Zero readiness: ready")
        return 0
    if report["status"] == "pass":
        print("Gate Zero result: pass")
        return 0
    print(f"Gate Zero {args.mode}: {report['status']}", file=sys.stderr)
    blockers = report["blockers"]
    if isinstance(blockers, dict):
        for group in blockers.values():
            for blocker in group:
                print(f"- {blocker}", file=sys.stderr)
    else:
        for blocker in blockers:
            print(f"- {blocker}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
