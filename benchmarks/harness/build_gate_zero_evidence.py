#!/usr/bin/env python3
"""Build publishable Gate Zero evidence bundles from a saved result JSON."""

from __future__ import annotations

import argparse
import json
import platform
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import run_gate_zero


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RESULT = ROOT / "benchmarks" / "results" / "gate-zero" / "macos-arm64" / "g1.json"
DEFAULT_OUT_ROOT = ROOT / "benchmarks" / "results" / "gate-zero"
TIMESTAMP_RE = re.compile(r"^[0-9]{8}T[0-9]{6}Z$")
REQUIRED_RESULT_KEYS = {
    "schema_version",
    "status",
    "corpus",
    "parser_target",
    "command",
    "host",
    "deterministic_profile_sha256",
    "inputs",
    "competitors",
    "runs",
    "summary",
}
PARSER_LABELS = {
    "ethos": "Ethos",
    "opendataloader-pdf": "OpenDataLoader",
    "edgeparse": "EdgeParse",
    "liteparse": "LiteParse",
    "pymupdf4llm": "PyMuPDF4LLM",
}
PARSER_ORDER = (
    "ethos",
    "opendataloader-pdf",
    "edgeparse",
    "liteparse",
    "pymupdf4llm",
)


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def timestamp_to_iso(timestamp: str) -> str:
    validate_timestamp(timestamp)
    parsed = datetime.strptime(timestamp, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    return parsed.isoformat().replace("+00:00", "Z")


def validate_timestamp(timestamp: str) -> None:
    if not TIMESTAMP_RE.fullmatch(timestamp):
        raise ValueError("timestamp must use YYYYMMDDTHHMMSSZ")


def repo_path(repo_root: Path, path: Path) -> str:
    return run_gate_zero.report_path(repo_root, path)


def load_result(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"result JSON does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"result JSON is invalid: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"result JSON must be an object: {path}")
    validate_result_shape(value, path)
    return value


def validate_result_shape(result: dict[str, Any], path: Path) -> None:
    missing = sorted(REQUIRED_RESULT_KEYS - set(result))
    if missing:
        raise ValueError(f"result JSON is missing required keys in {path}: {', '.join(missing)}")
    if result.get("schema_version") != "ethos-gate-zero-result-v1":
        raise ValueError(f"result JSON has unsupported schema_version in {path}")
    competitors = result.get("competitors")
    if not isinstance(competitors, dict):
        raise ValueError(f"result JSON competitors must be an object: {path}")
    for key in ["adapters", "runs", "summaries"]:
        if key not in competitors:
            raise ValueError(f"result JSON competitors.{key} is missing in {path}")


def read_reproduction_command(command: str | None, command_file: Path | None) -> str:
    if command and command_file:
        raise ValueError("use either --reproduction-command or --reproduction-command-file, not both")
    if command_file is not None:
        try:
            command = command_file.read_text(encoding="utf-8")
        except FileNotFoundError as exc:
            raise FileNotFoundError(f"reproduction command file does not exist: {command_file}") from exc
    command = (command or "").strip()
    if not command:
        raise ValueError("reproduction command is required")
    return command


def status_line_path(line: str) -> str:
    path = line[3:] if len(line) > 3 else ""
    if " -> " in path:
        path = path.split(" -> ", 1)[1]
    return path


def is_ignored_status_line(repo_root: Path, line: str, ignored_paths: list[Path]) -> bool:
    path_text = status_line_path(line)
    if not path_text:
        return False
    status_path = (repo_root / path_text).resolve()
    for ignored_path in ignored_paths:
        ignored = ignored_path.resolve()
        if status_path == ignored or ignored in status_path.parents:
            return True
    return False


def git_metadata(repo_root: Path, ignored_paths: list[Path] | None = None) -> dict[str, Any]:
    ignored_paths = ignored_paths or []

    def run_git(args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-C", str(repo_root), *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

    head = run_git(["rev-parse", "HEAD"])
    if head.returncode != 0:
        return {
            "available": False,
            "error": head.stderr.strip() or head.stdout.strip() or "git metadata unavailable",
        }
    status = run_git(["status", "--short"])
    status_lines = [
        line for line in status.stdout.splitlines()
        if not is_ignored_status_line(repo_root, line, ignored_paths)
    ] if status.returncode == 0 else []
    return {
        "available": True,
        "commit": head.stdout.strip(),
        "dirty": bool(status_lines),
        "status_short": status_lines,
    }


def observed_host() -> dict[str, Any]:
    return {
        "platform": platform.platform(),
        "machine": platform.machine(),
        "python": platform.python_version(),
        "platform_key": run_gate_zero.current_platform_key(),
    }


def mib(value: int | float | None) -> str:
    if value is None:
        return "n/a"
    return f"{float(value) / (1024 * 1024):.1f}"


def ms(value: int | float | None) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.2f}"


def short_hash(value: str | None) -> str:
    if not value:
        return "n/a"
    return f"`{value[:12]}`"


def parser_rows(result: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    summaries = result["competitors"]["summaries"]
    rows: list[tuple[str, dict[str, Any]]] = [("ethos", result["summary"])]
    for parser_id in PARSER_ORDER:
        if parser_id == "ethos":
            continue
        if parser_id in summaries:
            rows.append((parser_id, summaries[parser_id]))
    return rows


def edgeparse_determinism_failures(result: dict[str, Any]) -> list[dict[str, Any]]:
    runs = result["competitors"]["runs"].get("edgeparse", [])
    failures: list[dict[str, Any]] = []
    for run in runs:
        run_failures = run.get("failures", [])
        if "output_sha256 changed across iterations" not in run_failures:
            continue
        corpus_file = run.get("corpus_file", {})
        failures.append(
            {
                "id": corpus_file.get("id"),
                "file": corpus_file.get("file"),
                "failures": run_failures,
            }
        )
    return failures


def build_summary_markdown(
    result: dict[str, Any],
    *,
    platform_key: str,
    gate: str,
    source_result: str,
    raw_result_sha256: str,
    created_at: str,
) -> str:
    host = result.get("host", {}).get("selected", {})
    lines = [
        f"# Gate Zero {gate.upper()} {platform_key} Evidence Summary",
        "",
        f"- Source result: `{source_result}`",
        f"- Source result SHA256: `{raw_result_sha256}`",
        f"- Generated at: `{created_at}`",
        f"- Overall status: `{result['status']}`",
        f"- Ethos status: `{result['summary']['status']}`",
        f"- Host: `{host.get('id', 'unknown')}`",
        f"- Corpus: `{result['corpus'].get('id', 'unknown')}`",
        f"- Reproduction command: `reproduction-command.txt`",
        f"- Host attestation: `host-attestation.json`",
        "",
        "## Parser Results",
        "",
        "| Parser | Status | Failed Runs | Iterations | p50 ms | p95 ms | p99 ms | Peak RSS MiB | Install MiB | Output SHA256 |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for parser_id, summary in parser_rows(result):
        failed_runs = f"{summary['runs_failed']}/{summary['runs_total']}"
        lines.append(
            "| "
            f"{PARSER_LABELS.get(parser_id, parser_id)} | "
            f"`{summary['status']}` | "
            f"{failed_runs} | "
            f"{summary['iterations']} | "
            f"{ms(summary['duration_ms_p50'])} | "
            f"{ms(summary['duration_ms_p95'])} | "
            f"{ms(summary['duration_ms_p99'])} | "
            f"{mib(summary['peak_rss_bytes'])} | "
            f"{mib(summary['install_size_bytes'])} | "
            f"{short_hash(summary['output_sha256'])} |"
        )

    edgeparse_failures = edgeparse_determinism_failures(result)
    lines.extend(["", "## EdgeParse Determinism Note", ""])
    if edgeparse_failures:
        lines.append(
            "EdgeParse is recorded as a context/non-gating competitor row and failed "
            "G1 determinism because `output_sha256 changed across iterations`."
        )
        lines.append("")
        for failure in edgeparse_failures:
            corpus_id = failure.get("id") or failure.get("file") or "<unknown>"
            lines.append(f"- `{corpus_id}`")
        lines.extend(
            [
                "",
                "Ethos passed all top-level G1 determinism checks in this result. "
                "The overall benchmark status is `fail` because competitor failures "
                "are preserved as benchmark data.",
            ]
        )
    else:
        lines.append("No EdgeParse output-hash determinism failures are recorded in this result.")

    lines.extend(
        [
            "",
            "## Interpretation Guardrail",
            "",
            "This summary supports claims about recorded determinism, footprint, and measured "
            "latency/RSS for this pinned corpus and host. It does not claim Ethos is the "
            "fastest parser overall.",
            "",
        ]
    )
    return "\n".join(lines)


def build_host_attestation(
    result: dict[str, Any],
    *,
    repo_root: Path,
    source_result: str,
    result_path: Path,
    platform_key: str,
    gate: str,
    created_at: str,
    benchmark_commit: str | None,
    ignored_git_paths: list[Path] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": "ethos-gate-zero-host-attestation-v1",
        "gate": gate,
        "platform": platform_key,
        "generated_at": created_at,
        "source_result": source_result,
        "source_result_sha256": run_gate_zero.sha256_file(result_path),
        "source_result_canonical_sha256": run_gate_zero.sha256_c14n_value(result),
        "benchmark_commit": benchmark_commit,
        "result_host": result["host"],
        "result_inputs": result["inputs"],
        "bundle_host_observed": observed_host(),
        "bundle_git": git_metadata(repo_root, ignored_git_paths),
    }


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text if text.endswith("\n") else f"{text}\n", encoding="utf-8")


def write_json(path: Path, value: Any) -> None:
    run_gate_zero.write_json(path, value)


def checksums_for(paths: list[Path], bundle_dir: Path) -> list[dict[str, str]]:
    rows = []
    for path in sorted(paths, key=lambda item: item.relative_to(bundle_dir).as_posix()):
        rows.append(
            {
                "path": path.relative_to(bundle_dir).as_posix(),
                "sha256": run_gate_zero.sha256_file(path),
            }
        )
    return rows


def write_checksums(path: Path, rows: list[dict[str, str]]) -> None:
    text = "".join(f"{row['sha256']}  {row['path']}\n" for row in rows)
    write_text(path, text)


def verify_checksums(bundle_dir: Path, checksum_file: Path | None = None) -> list[str]:
    checksum_file = checksum_file or bundle_dir / "SHA256SUMS"
    failures: list[str] = []
    for index, line in enumerate(checksum_file.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            expected, relative_path = line.split("  ", 1)
        except ValueError:
            failures.append(f"line {index} is malformed")
            continue
        path = bundle_dir / relative_path
        if not path.is_file():
            failures.append(f"{relative_path} is missing")
            continue
        actual = run_gate_zero.sha256_file(path)
        if actual != expected:
            failures.append(f"{relative_path} sha256 mismatch: expected={expected} actual={actual}")
    return failures


def build_evidence_bundle(
    *,
    repo_root: Path,
    result_path: Path,
    out_root: Path,
    platform_key: str | None,
    gate: str,
    timestamp: str,
    reproduction_command: str,
    benchmark_commit: str | None = None,
    force: bool = False,
) -> dict[str, Any]:
    validate_timestamp(timestamp)
    if not reproduction_command.strip():
        raise ValueError("reproduction command is required")

    repo_root = repo_root.resolve()
    result_path = result_path.resolve()
    out_root = out_root.resolve()
    result = load_result(result_path)
    platform_key = platform_key or result.get("host", {}).get("selected", {}).get("platform")
    if not platform_key:
        raise ValueError("platform key is required when result host.selected.platform is missing")
    evidence_root = out_root / platform_key / "evidence"
    bundle_dir = out_root / platform_key / "evidence" / gate / timestamp
    created_at = timestamp_to_iso(timestamp)
    source_result = repo_path(repo_root, result_path)
    raw_result_sha256 = run_gate_zero.sha256_file(result_path)
    host_attestation = build_host_attestation(
        result,
        repo_root=repo_root,
        source_result=source_result,
        result_path=result_path,
        platform_key=platform_key,
        gate=gate,
        created_at=created_at,
        benchmark_commit=benchmark_commit,
        ignored_git_paths=[evidence_root],
    )
    summary_text = build_summary_markdown(
        result,
        platform_key=platform_key,
        gate=gate,
        source_result=source_result,
        raw_result_sha256=raw_result_sha256,
        created_at=created_at,
    )

    if bundle_dir.exists() and not force:
        raise FileExistsError(f"evidence bundle already exists: {bundle_dir}")
    bundle_dir.mkdir(parents=True, exist_ok=True)
    if force:
        legacy_signature_path = bundle_dir / "SIGNATURE.json"
        if legacy_signature_path.exists():
            legacy_signature_path.unlink()

    raw_path = bundle_dir / "raw" / f"{gate}-{platform_key}-{timestamp}.json"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(result_path, raw_path)

    reproduction_path = bundle_dir / "reproduction-command.txt"
    write_text(reproduction_path, reproduction_command.strip())

    host_path = bundle_dir / "host-attestation.json"
    write_json(host_path, host_attestation)

    summary_path = bundle_dir / "SUMMARY.md"
    write_text(summary_path, summary_text)

    manifest_path = bundle_dir / "evidence-manifest.json"
    preliminary_artifacts = [host_path, raw_path, reproduction_path, summary_path]
    artifact_rows = checksums_for(preliminary_artifacts, bundle_dir)
    manifest = {
        "schema_version": "ethos-gate-zero-evidence-v1",
        "gate": gate,
        "platform": platform_key,
        "created_at": created_at,
        "source_result": source_result,
        "source_result_sha256": raw_result_sha256,
        "source_result_canonical_sha256": run_gate_zero.sha256_c14n_value(result),
        "source_result_status": result["status"],
        "ethos_status": result["summary"]["status"],
        "edgeparse_determinism_failures": edgeparse_determinism_failures(result),
        "benchmark_commit": benchmark_commit,
        "artifacts": artifact_rows,
    }
    write_json(manifest_path, manifest)

    checksum_path = bundle_dir / "SHA256SUMS"
    checksum_rows = checksums_for([*preliminary_artifacts, manifest_path], bundle_dir)
    write_checksums(checksum_path, checksum_rows)

    digest_path = bundle_dir / "SHA256SUMS.digest.json"
    checksum_digest = {
        "schema_version": "ethos-gate-zero-checksum-digest-v1",
        "digest_type": "sha256",
        "payload": "SHA256SUMS",
        "payload_sha256": run_gate_zero.sha256_file(checksum_path),
        "note": "This is a checksum digest for the checksum manifest, not a public-key signature.",
    }
    write_json(digest_path, checksum_digest)

    return {
        "bundle_dir": str(bundle_dir),
        "manifest": manifest,
        "checksums": checksum_rows,
        "checksum_digest": checksum_digest,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--result", type=Path, default=DEFAULT_RESULT)
    parser.add_argument("--out-root", type=Path, default=DEFAULT_OUT_ROOT)
    parser.add_argument("--platform")
    parser.add_argument("--gate", default="g1")
    parser.add_argument("--timestamp", default=utc_timestamp())
    parser.add_argument("--reproduction-command")
    parser.add_argument("--reproduction-command-file", type=Path)
    parser.add_argument("--benchmark-commit")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        reproduction_command = read_reproduction_command(
            args.reproduction_command,
            args.reproduction_command_file,
        )
        report = build_evidence_bundle(
            repo_root=args.repo_root,
            result_path=args.result,
            out_root=args.out_root,
            platform_key=args.platform,
            gate=args.gate,
            timestamp=args.timestamp,
            reproduction_command=reproduction_command,
            benchmark_commit=args.benchmark_commit,
            force=args.force,
        )
    except Exception as exc:
        print(f"Gate Zero evidence bundle: {exc}", file=sys.stderr)
        return 2
    print(report["bundle_dir"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
