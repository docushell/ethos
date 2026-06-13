#!/usr/bin/env python3
"""Build publishable Gate Zero evidence bundles from a saved result JSON."""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

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
REQUIRED_G2_RESULT_KEYS = {
    "schema_version",
    "gate",
    "status",
    "platform",
    "corpus",
    "definition",
    "host",
    "inputs",
    "measurements",
    "evaluation",
    "blockers",
    "failures",
    "summary",
}
REQUIRED_G3_RESULT_KEYS = {
    "schema_version",
    "gate",
    "status",
    "platforms",
    "corpus",
    "definition",
    "host",
    "inputs",
    "comparison",
    "evaluation",
    "blockers",
    "failures",
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
REPRODUCTION_ENV_VARS = (
    {
        "name": "ETHOS_PDFIUM_LIBRARY_PATH",
        "kind": "file",
        "role": "Pinned PDFium dynamic library loaded by ethos-pdf.",
    },
    {
        "name": "ETHOS_PDFIUM_VERSION",
        "kind": "value",
        "role": "Pinned upstream PDFium version string.",
    },
    {
        "name": "ETHOS_PDFIUM_ARTIFACT_PATH",
        "kind": "file",
        "role": "Pinned PDFium artifact archive.",
    },
    {
        "name": "ETHOS_OPENDATALOADER_PDF_BIN",
        "kind": "file",
        "role": "OpenDataLoader command used by the Gate Zero harness.",
        "competitor_id": "opendataloader-pdf",
    },
    {
        "name": "ETHOS_OPENDATALOADER_PDF_ARTIFACT",
        "kind": "file",
        "role": "OpenDataLoader pinned artifact used to install/run the command.",
        "competitor_id": "opendataloader-pdf",
        "artifact": True,
    },
    {
        "name": "ETHOS_OPENDATALOADER_PDF_INSTALL_PATH",
        "kind": "directory",
        "role": "OpenDataLoader installed footprint path measured by the harness.",
        "competitor_id": "opendataloader-pdf",
    },
    {
        "name": "ETHOS_EDGEPARSE_BIN",
        "kind": "file",
        "role": "EdgeParse command used by the Gate Zero harness.",
        "competitor_id": "edgeparse",
    },
    {
        "name": "ETHOS_EDGEPARSE_ARTIFACT",
        "kind": "file",
        "role": "EdgeParse pinned artifact used to install/run the command.",
        "competitor_id": "edgeparse",
        "artifact": True,
    },
    {
        "name": "ETHOS_EDGEPARSE_INSTALL_PATH",
        "kind": "directory",
        "role": "EdgeParse installed footprint path measured by the harness.",
        "competitor_id": "edgeparse",
    },
    {
        "name": "ETHOS_LITEPARSE_BIN",
        "kind": "file",
        "role": "LiteParse command used by the Gate Zero harness.",
        "competitor_id": "liteparse",
    },
    {
        "name": "ETHOS_LITEPARSE_ARTIFACT",
        "kind": "file",
        "role": "LiteParse pinned artifact used to install/run the command.",
        "competitor_id": "liteparse",
        "artifact": True,
    },
    {
        "name": "ETHOS_LITEPARSE_INSTALL_PATH",
        "kind": "directory",
        "role": "LiteParse installed footprint path measured by the harness.",
        "competitor_id": "liteparse",
    },
    {
        "name": "ETHOS_PYMUPDF4LLM_PYTHON",
        "kind": "file",
        "role": "PyMuPDF4LLM Python interpreter used by the Gate Zero harness.",
        "competitor_id": "pymupdf4llm",
    },
    {
        "name": "ETHOS_PYMUPDF4LLM_ARTIFACT",
        "kind": "file",
        "role": "PyMuPDF4LLM pinned artifact used to install/run the command.",
        "competitor_id": "pymupdf4llm",
        "artifact": True,
    },
    {
        "name": "ETHOS_PYMUPDF4LLM_INSTALL_PATH",
        "kind": "directory",
        "role": "PyMuPDF4LLM installed footprint path measured by the harness.",
        "competitor_id": "pymupdf4llm",
    },
)
G2_REPRODUCTION_ENV_VAR_NAMES = {
    "ETHOS_PDFIUM_LIBRARY_PATH",
    "ETHOS_PDFIUM_VERSION",
    "ETHOS_PDFIUM_ARTIFACT_PATH",
    "ETHOS_OPENDATALOADER_PDF_ARTIFACT",
    "ETHOS_OPENDATALOADER_PDF_INSTALL_PATH",
}


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
    if result.get("schema_version") == "ethos-gate-zero-g2-result-v1":
        missing = sorted(REQUIRED_G2_RESULT_KEYS - set(result))
        if missing:
            raise ValueError(f"result JSON is missing required keys in {path}: {', '.join(missing)}")
        if result.get("gate") != "g2":
            raise ValueError(f"G2 result JSON must set gate=g2 in {path}")
        return
    if result.get("schema_version") == "ethos-gate-zero-g3-result-v1":
        missing = sorted(REQUIRED_G3_RESULT_KEYS - set(result))
        if missing:
            raise ValueError(f"result JSON is missing required keys in {path}: {', '.join(missing)}")
        if result.get("gate") != "g3":
            raise ValueError(f"G3 result JSON must set gate=g3 in {path}")
        return
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


def read_reproduction_env(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"reproduction env file does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"reproduction env JSON is invalid: {path}: {exc}") from exc
    validate_reproduction_env(value, path)
    return value


def validate_reproduction_env(value: Any, path: Path) -> None:
    if not isinstance(value, dict):
        raise ValueError(f"reproduction env JSON must be an object: {path}")
    required = {"schema_version", "status", "variables", "blockers"}
    missing = sorted(required - set(value))
    if missing:
        raise ValueError(f"reproduction env JSON is missing required keys in {path}: {', '.join(missing)}")
    if value.get("schema_version") != "ethos-gate-zero-reproduction-env-v1":
        raise ValueError(f"reproduction env JSON has unsupported schema_version in {path}")
    if value.get("status") not in {"complete", "incomplete"}:
        raise ValueError(f"reproduction env JSON status must be complete or incomplete in {path}")
    if not isinstance(value.get("variables"), list):
        raise ValueError(f"reproduction env JSON variables must be an array in {path}")
    if not isinstance(value.get("blockers"), list):
        raise ValueError(f"reproduction env JSON blockers must be an array in {path}")


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
    if result.get("schema_version") != "ethos-gate-zero-result-v1":
        return []
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


def build_g2_summary_markdown(
    result: dict[str, Any],
    *,
    platform_key: str,
    gate: str,
    source_result: str,
    raw_result_sha256: str,
    created_at: str,
    reproduction_env_status: str | None,
) -> str:
    host = result.get("host", {}).get("selected", {})
    summary = result["summary"]
    measurements = result["measurements"]
    ethos_items = measurements["ethos"]["items"]
    failures = result.get("failures", [])
    blockers = result.get("blockers", [])
    ratio = summary.get("ethos_to_opendataloader_ratio")
    ratio_text = "n/a" if ratio is None else f"{ratio:.4f}"
    lines = [
        f"# Gate Zero {gate.upper()} {platform_key} Evidence Summary",
        "",
        f"- Source result: `{source_result}`",
        f"- Source result SHA256: `{raw_result_sha256}`",
        f"- Generated at: `{created_at}`",
        f"- Overall status: `{result['status']}`",
        f"- Host: `{host.get('id', 'unknown')}`",
        f"- Corpus: `{result['corpus'].get('id', 'unknown')}`",
        f"- Definition: `{result['definition'].get('gates', 'unknown')}`",
        f"- Reproduction command: `reproduction-command.txt`",
        f"- Reproduction env: `reproduction-env.json` (`{reproduction_env_status or 'unknown'}`)",
        f"- Host attestation: `host-attestation.json`",
        "",
        "## Footprint Result",
        "",
        "| Subject | Bytes | MiB |",
        "| --- | ---: | ---: |",
        f"| Ethos base parser footprint | {summary['ethos_install_size_bytes'] or 'n/a'} | {mib(summary['ethos_install_size_bytes'])} |",
        f"| OpenDataLoader install footprint | {summary['opendataloader_install_size_bytes'] or 'n/a'} | {mib(summary['opendataloader_install_size_bytes'])} |",
        "",
        "## Thresholds",
        "",
        f"- Max Ethos footprint: `{summary['max_install_size_bytes']}` bytes",
        f"- Ethos/OpenDataLoader claim ratio threshold: `{summary['opendataloader_ratio_max']}`",
        f"- Measured Ethos/OpenDataLoader ratio: `{ratio_text}`",
        f"- One-tenth OpenDataLoader footprint claim supported: `{summary.get('opendataloader_ratio_claim_supported')}`",
        f"- PDFium V8 enabled: `{summary['pdfium_v8_enabled']}`",
        f"- PDFium XFA enabled: `{summary['pdfium_xfa_enabled']}`",
        "",
        "## Ethos Footprint Items",
        "",
        "| Role | Path | Bytes | SHA256 |",
        "| --- | --- | ---: | --- |",
    ]
    for item in ethos_items:
        lines.append(
            "| "
            f"{item['role']} | "
            f"`{item['path']}` | "
            f"{item['size_bytes'] if item['size_bytes'] is not None else 'n/a'} | "
            f"{short_hash(item.get('sha256') or item.get('tree_sha256'))} |"
        )

    if failures:
        lines.extend(["", "## Failures", ""])
        for failure in failures:
            lines.append(f"- {failure}")
    if blockers:
        lines.extend(["", "## Blockers", ""])
        for blocker in blockers:
            lines.append(f"- {blocker}")

    lines.extend(
        [
            "",
            "## Interpretation Guardrail",
            "",
            "G2 is a footprint gate only. It does not measure parser speed, output quality, "
            "or cross-platform determinism.",
            "",
        ]
    )
    return "\n".join(lines)


def build_g3_summary_markdown(
    result: dict[str, Any],
    *,
    platform_key: str,
    gate: str,
    source_result: str,
    raw_result_sha256: str,
    created_at: str,
    reproduction_env_status: str | None,
) -> str:
    summary = result["summary"]
    platforms = result.get("platforms", [])
    failures = result.get("failures", [])
    blockers = result.get("blockers", [])
    lines = [
        f"# Gate Zero {gate.upper()} {platform_key} Evidence Summary",
        "",
        f"- Source result: `{source_result}`",
        f"- Source result SHA256: `{raw_result_sha256}`",
        f"- Generated at: `{created_at}`",
        f"- Overall status: `{result['status']}`",
        f"- Platforms: `{', '.join(platforms)}`",
        f"- Corpus: `{result['corpus'].get('id', 'unknown')}`",
        f"- Corpus files compared: `{summary['corpus_files_total']}`",
        f"- Definition: `{result['definition'].get('gates', 'unknown')}`",
        f"- Reproduction command: `reproduction-command.txt`",
        f"- Reproduction env: `reproduction-env.json` (`{reproduction_env_status or 'unknown'}`)",
        f"- Host attestation: `host-attestation.json`",
        "",
        "## Determinism Result",
        "",
        "| Check | Divergences |",
        "| --- | ---: |",
        f"| Stable payload projection hash | {summary['canonical_payload_divergences']} |",
        f"| Document fingerprint | {summary['document_fingerprint_divergences']} |",
        f"| Warning IDs | {summary['warning_id_divergences']} |",
        f"| Corpus binding | {summary['corpus_binding_divergences']} |",
        "",
        "## Platform Inputs",
        "",
        "| Platform | Result | Status | Ethos Status | Runs | SHA256 |",
        "| --- | --- | --- | --- | ---: | --- |",
    ]
    for platform_name, record in result["comparison"]["platform_results"].items():
        lines.append(
            "| "
            f"{platform_name} | "
            f"`{record['path']}` | "
            f"`{record['result_status']}` | "
            f"`{record['ethos_status']}` | "
            f"{record['runs_total']} | "
            f"{short_hash(record['sha256'])} |"
        )

    if failures:
        lines.extend(["", "## Failures", ""])
        for failure in failures:
            lines.append(f"- {failure}")
    if blockers:
        lines.extend(["", "## Blockers", ""])
        for blocker in blockers:
            lines.append(f"- {blocker}")

    lines.extend(
        [
            "",
            "## Interpretation Guardrail",
            "",
            "G3 compares existing G1 Ethos stable payload projection hashes, document "
            "fingerprints, warning IDs, and corpus bindings across required platforms. It does "
            "not run parsers or measure extraction quality.",
            "",
        ]
    )
    return "\n".join(lines)


def build_summary_markdown(
    result: dict[str, Any],
    *,
    platform_key: str,
    gate: str,
    source_result: str,
    raw_result_sha256: str,
    created_at: str,
    reproduction_env_status: str | None,
) -> str:
    if result.get("schema_version") == "ethos-gate-zero-g2-result-v1":
        return build_g2_summary_markdown(
            result,
            platform_key=platform_key,
            gate=gate,
            source_result=source_result,
            raw_result_sha256=raw_result_sha256,
            created_at=created_at,
            reproduction_env_status=reproduction_env_status,
        )
    if result.get("schema_version") == "ethos-gate-zero-g3-result-v1":
        return build_g3_summary_markdown(
            result,
            platform_key=platform_key,
            gate=gate,
            source_result=source_result,
            raw_result_sha256=raw_result_sha256,
            created_at=created_at,
            reproduction_env_status=reproduction_env_status,
        )
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
        f"- Reproduction env: `reproduction-env.json` (`{reproduction_env_status or 'unknown'}`)",
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
            "This summary supports claims about recorded determinism, footprint, measured "
            "latency, and RSS when available for this pinned corpus and host. It does not "
            "claim Ethos is the fastest parser overall.",
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


def competitor_expected_hashes(result: dict[str, Any]) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for adapter in result.get("competitors", {}).get("adapters", []):
        competitor_id = adapter.get("id")
        artifact = adapter.get("artifact", {})
        expected = artifact.get("expected_sha256")
        if isinstance(competitor_id, str) and isinstance(expected, str):
            hashes[competitor_id] = expected
    return hashes


def reproduction_env_specs(result: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    if result.get("schema_version") == "ethos-gate-zero-g2-result-v1":
        return tuple(
            spec for spec in REPRODUCTION_ENV_VARS
            if spec["name"] in G2_REPRODUCTION_ENV_VAR_NAMES
        )
    if result.get("schema_version") == "ethos-gate-zero-g3-result-v1":
        return ()
    return REPRODUCTION_ENV_VARS


def path_metadata(path_value: str, kind: str) -> dict[str, Any]:
    path = Path(path_value)
    exists = path.exists()
    metadata: dict[str, Any] = {
        "path": path_value,
        "exists": exists,
        "path_kind": kind,
        "size_bytes": None,
        "sha256": None,
        "tree_sha256": None,
    }
    if not exists:
        return metadata
    if path.is_file():
        metadata["path_kind"] = "file"
        metadata["size_bytes"] = path.stat().st_size
        metadata["sha256"] = run_gate_zero.sha256_file(path)
        return metadata
    if path.is_dir():
        metadata["path_kind"] = "directory"
        metadata["size_bytes"] = run_gate_zero.path_size_bytes(path)
        metadata["tree_sha256"] = run_gate_zero.output_tree_hash(path)
        return metadata
    metadata["path_kind"] = "other"
    return metadata


def build_reproduction_env(
    result: dict[str, Any],
    environment: Mapping[str, str],
) -> dict[str, Any]:
    expected_hashes = competitor_expected_hashes(result)
    variables: list[dict[str, Any]] = []
    blockers: list[str] = []
    for spec in reproduction_env_specs(result):
        name = spec["name"]
        kind = spec["kind"]
        value = environment.get(name)
        entry: dict[str, Any] = {
            "name": name,
            "role": spec["role"],
            "kind": kind,
            "status": "resolved" if value else "unresolved",
            "value": value if value else None,
            "path": None,
            "exists": None,
            "path_kind": None,
            "size_bytes": None,
            "sha256": None,
            "tree_sha256": None,
            "expected_sha256": None,
            "hash_matches_expected": None,
            "notes": [],
        }
        competitor_id = spec.get("competitor_id")
        if isinstance(competitor_id, str):
            entry["competitor_id"] = competitor_id
        if spec.get("artifact") and isinstance(competitor_id, str):
            entry["expected_sha256"] = expected_hashes.get(competitor_id)
        if not value:
            blockers.append(f"{name} is not set")
            variables.append(entry)
            continue
        if kind in {"file", "directory"}:
            metadata = path_metadata(value, kind)
            entry.update(metadata)
            if not metadata["exists"]:
                blockers.append(f"{name} path does not exist: {value}")
            expected_sha256 = entry["expected_sha256"]
            if expected_sha256 and metadata["sha256"]:
                entry["hash_matches_expected"] = metadata["sha256"] == expected_sha256
                if not entry["hash_matches_expected"]:
                    blockers.append(f"{name} sha256 does not match expected artifact hash")
        variables.append(entry)

    status = "complete" if not blockers else "incomplete"
    return {
        "schema_version": "ethos-gate-zero-reproduction-env-v1",
        "status": status,
        "source": "environment",
        "blockers": blockers,
        "variables": variables,
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
    reproduction_env: dict[str, Any] | None = None,
    environment: Mapping[str, str] | None = None,
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
    if reproduction_env is None:
        reproduction_env = build_reproduction_env(result, environment or {})
    else:
        validate_reproduction_env(reproduction_env, Path("<in-memory-reproduction-env>"))
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
        reproduction_env_status=reproduction_env.get("status"),
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

    reproduction_env_path = bundle_dir / "reproduction-env.json"
    write_json(reproduction_env_path, reproduction_env)

    host_path = bundle_dir / "host-attestation.json"
    write_json(host_path, host_attestation)

    summary_path = bundle_dir / "SUMMARY.md"
    write_text(summary_path, summary_text)

    manifest_path = bundle_dir / "evidence-manifest.json"
    preliminary_artifacts = [host_path, raw_path, reproduction_env_path, reproduction_path, summary_path]
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
        "definition_sha256": result.get("definition", {}).get("definition_sha256"),
        "reproduction_env_status": reproduction_env.get("status"),
        "reproduction_env_blockers": reproduction_env.get("blockers", []),
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
    parser.add_argument("--reproduction-env-file", type=Path)
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
        reproduction_env = read_reproduction_env(args.reproduction_env_file)
        report = build_evidence_bundle(
            repo_root=args.repo_root,
            result_path=args.result,
            out_root=args.out_root,
            platform_key=args.platform,
            gate=args.gate,
            timestamp=args.timestamp,
            reproduction_command=reproduction_command,
            reproduction_env=reproduction_env,
            environment=dict(os.environ),
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
