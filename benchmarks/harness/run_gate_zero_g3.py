#!/usr/bin/env python3
"""Generate Gate Zero G3 cross-platform determinism results.

G3 compares existing platform-scoped G1 Ethos result files. It does not run
parsers and does not inspect competitor rows; those remain G1 evidence.
"""

from __future__ import annotations

import argparse
import platform
import sys
from pathlib import Path
from typing import Any

import gate_zero_gates
import run_gate_zero


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / "benchmarks" / "gate-zero" / "manifest.json"
DEFAULT_COMPETITORS = ROOT / "benchmarks" / "competitors.lock.json"
DEFAULT_GATES = ROOT / "benchmarks" / "gate-zero" / "gates.json"
DEFAULT_PROFILE = ROOT / "profiles" / "ethos-deterministic-v1.json"
DEFAULT_OUT = ROOT / "benchmarks" / "results" / "gate-zero" / "g3.json"


def parse_platform_result(value: str) -> argparse.Namespace:
    if "=" not in value:
        raise argparse.ArgumentTypeError("platform result must use platform=path")
    platform_key, path = value.split("=", 1)
    platform_key = platform_key.strip()
    path = path.strip()
    if not platform_key or not path:
        raise argparse.ArgumentTypeError("platform result must use platform=path")
    return argparse.Namespace(platform=platform_key, path=Path(path))


def result_platform(result: dict[str, Any]) -> str | None:
    selected = result.get("host", {}).get("selected", {})
    platform_key = selected.get("platform") if isinstance(selected, dict) else None
    return platform_key if isinstance(platform_key, str) else None


def load_g1_result(path: Path) -> dict[str, Any]:
    result = run_gate_zero.load_json(path)
    if result.get("schema_version") != "ethos-gate-zero-result-v1":
        raise ValueError(f"{path} is not a Gate Zero G1 result")
    return result


def default_platform_result_paths(
    repo_root: Path,
    platforms: list[str],
) -> dict[str, Path]:
    base = repo_root / "benchmarks" / "results" / "gate-zero"
    return {
        platform_key: base / platform_key / "g1.json"
        for platform_key in platforms
    }


def configured_platform_result_paths(
    repo_root: Path,
    platforms: list[str],
    configured: list[argparse.Namespace],
) -> dict[str, Path]:
    paths = default_platform_result_paths(repo_root, platforms)
    for item in configured:
        paths[item.platform] = item.path
    return paths


def platform_result_record(
    repo_root: Path,
    platform_key: str,
    path: Path,
    result: dict[str, Any] | None,
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "platform": platform_key,
        "path": run_gate_zero.report_path(repo_root, path),
        "exists": path.is_file(),
        "sha256": run_gate_zero.sha256_file(path) if path.is_file() else None,
        "canonical_sha256": run_gate_zero.sha256_c14n_value(result) if result else None,
        "schema_version": result.get("schema_version") if result else None,
        "result_status": result.get("status") if result else None,
        "ethos_status": result.get("summary", {}).get("status") if result else None,
        "host_id": None,
        "host_platform": result_platform(result) if result else None,
        "runs_total": len(result.get("runs", [])) if result else 0,
    }
    if result:
        selected = result.get("host", {}).get("selected", {})
        if isinstance(selected, dict):
            record["host_id"] = selected.get("id")
    return record


def failure_counts(failures: list[str]) -> dict[str, int]:
    return {
        "canonical_payload_divergences": sum(
            " canonical payload differs " in failure for failure in failures
        ),
        "document_fingerprint_divergences": sum(
            " document fingerprint differs " in failure for failure in failures
        ),
        "warning_id_divergences": sum(
            " warning ids differ " in failure for failure in failures
        ),
        "corpus_binding_divergences": sum(
            " corpus binding differs " in failure for failure in failures
        ),
    }


def build_g3_result(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = args.repo_root.resolve()
    manifest_path = args.manifest.resolve()
    competitors_path = args.competitors_lock.resolve()
    gates_path = args.gates.resolve()
    profile_path = args.deterministic_profile.resolve()

    manifest = run_gate_zero.load_json(manifest_path)
    gates = run_gate_zero.load_json(gates_path)
    g3 = gates.get("gates", {}).get("g3", {})
    required_platforms = list(args.platforms or g3.get("platforms") or manifest.get("determinism_platforms") or [])
    corpus_ids = [entry["id"] for entry in manifest.get("corpus", []) if isinstance(entry.get("id"), str)]

    blockers: list[str] = []
    if not required_platforms:
        blockers.append("G3 required platforms are missing")
    if not corpus_ids:
        blockers.append("Gate Zero manifest corpus is empty")
    if not profile_path.is_file():
        blockers.append("deterministic profile is missing")
    if not gates_path.is_file():
        blockers.append("Gate Zero gates definition is missing")
    if g3.get("id") != "g3":
        blockers.append("Gate Zero G3 definition is missing")

    configured = args.platform_result or []
    result_paths = configured_platform_result_paths(repo_root, required_platforms, configured)
    platform_results: dict[str, dict[str, Any]] = {}
    platform_records: dict[str, dict[str, Any]] = {}
    for platform_key in required_platforms:
        path = result_paths[platform_key].resolve()
        result: dict[str, Any] | None = None
        if not path.is_file():
            blockers.append(f"{platform_key} G1 result does not exist: {run_gate_zero.report_path(repo_root, path)}")
        else:
            try:
                result = load_g1_result(path)
            except Exception as exc:  # noqa: BLE001 - report path-specific blocker.
                blockers.append(f"{platform_key} G1 result is invalid: {exc}")
            else:
                actual_platform = result_platform(result)
                if actual_platform != platform_key:
                    blockers.append(
                        f"{platform_key} G1 result host platform mismatch: {actual_platform}"
                    )
                platform_results[platform_key] = result
        platform_records[platform_key] = platform_result_record(repo_root, platform_key, path, result)

    manifest_sha256 = run_gate_zero.sha256_file(manifest_path)
    deterministic_profile_sha256 = (
        run_gate_zero.sha256_c14n_file(profile_path) if profile_path.is_file() else None
    )
    if deterministic_profile_sha256 is None:
        evaluation = {"status": gate_zero_gates.BLOCKED, "blockers": [], "failures": []}
    else:
        evaluation = gate_zero_gates.evaluate_g3_determinism(
            platform_results=platform_results,
            required_platforms=required_platforms,
            corpus_ids=corpus_ids,
            manifest_sha256=manifest_sha256,
            deterministic_profile_sha256=deterministic_profile_sha256,
        )

    blockers.extend(evaluation.get("blockers", []))
    failures = [] if blockers else evaluation.get("failures", [])
    status = gate_zero_gates.BLOCKED if blockers else evaluation["status"]
    counts = failure_counts(failures)
    summary = {
        "status": status,
        "platforms_total": len(required_platforms),
        "corpus_files_total": len(corpus_ids),
        "blockers_total": len(blockers),
        "failures_total": len(failures),
        **counts,
    }

    return {
        "schema_version": "ethos-gate-zero-g3-result-v1",
        "gate": "g3",
        "status": status,
        "platforms": required_platforms,
        "corpus": {
            "id": manifest.get("corpus_id", "gate-zero-v1"),
            "manifest": str(manifest_path.relative_to(repo_root)),
            "manifest_sha256": manifest_sha256,
            "corpus_ids": corpus_ids,
        },
        "definition": {
            "gates": str(gates_path.relative_to(repo_root)),
            "definition_sha256": run_gate_zero.sha256_file(gates_path),
            "gate_status": g3.get("status"),
            "completion_policy": g3.get("completion_policy"),
            "corpus_scope": g3.get("corpus_scope"),
            "thresholds": g3.get("thresholds"),
            "required_evidence": g3.get("required_evidence"),
        },
        "host": {
            "selected": None,
            "observed": {
                "platform": platform.platform(),
                "machine": platform.machine(),
                "python": platform.python_version(),
                "platform_key": run_gate_zero.current_platform_key(),
            },
        },
        "inputs": {
            "competitors_lock": str(competitors_path.relative_to(repo_root)),
            "competitors_lock_sha256": run_gate_zero.sha256_file(competitors_path),
            "deterministic_profile": str(profile_path.relative_to(repo_root)),
            "deterministic_profile_sha256": deterministic_profile_sha256,
            "gates": str(gates_path.relative_to(repo_root)),
            "gates_sha256": run_gate_zero.sha256_file(gates_path),
            "manifest": str(manifest_path.relative_to(repo_root)),
            "manifest_sha256": manifest_sha256,
            "platform_results": platform_records,
        },
        "comparison": {
            "baseline_platform": required_platforms[0] if required_platforms else None,
            "required_platforms": required_platforms,
            "corpus_ids": corpus_ids,
            "platform_results": platform_records,
        },
        "evaluation": evaluation,
        "blockers": blockers,
        "failures": failures,
        "summary": summary,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--competitors-lock", type=Path, default=DEFAULT_COMPETITORS)
    parser.add_argument("--gates", type=Path, default=DEFAULT_GATES)
    parser.add_argument("--deterministic-profile", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument("--platforms", nargs="+")
    parser.add_argument(
        "--platform-result",
        action="append",
        type=parse_platform_result,
        default=[],
        metavar="PLATFORM=PATH",
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--stdout", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        result = build_g3_result(args)
    except Exception as exc:
        print(f"Gate Zero G3: {exc}", file=sys.stderr)
        return 2
    if args.stdout:
        run_gate_zero.write_json(None, result)
    else:
        run_gate_zero.write_json(args.out, result)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
