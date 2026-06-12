#!/usr/bin/env python3
"""Generate Gate Zero G2 footprint results.

G2 is a footprint gate, not a parser execution benchmark. It measures the
explicit base-parser artifact set supplied by the benchmark runner and evaluates
that measurement against the contract encoded in benchmarks/gate-zero/gates.json.
"""

from __future__ import annotations

import argparse
import json
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
DEFAULT_OUT = ROOT / "benchmarks" / "results" / "gate-zero" / "macos-arm64" / "g2.json"


def path_measurement(repo_root: Path, path: Path, role: str) -> dict[str, Any]:
    resolved = path.resolve()
    measurement: dict[str, Any] = {
        "role": role,
        "path": run_gate_zero.report_path(repo_root, path),
        "exists": resolved.exists(),
        "path_kind": None,
        "size_bytes": None,
        "sha256": None,
        "tree_sha256": None,
    }
    if not resolved.exists():
        return measurement
    if resolved.is_file():
        measurement["path_kind"] = "file"
        measurement["size_bytes"] = resolved.stat().st_size
        measurement["sha256"] = run_gate_zero.sha256_file(resolved)
    elif resolved.is_dir():
        measurement["path_kind"] = "directory"
        measurement["size_bytes"] = run_gate_zero.path_size_bytes(resolved)
        measurement["tree_sha256"] = run_gate_zero.output_tree_hash(resolved)
    else:
        measurement["path_kind"] = "other"
    return measurement


def overlapping_paths(paths: list[Path]) -> list[str]:
    overlaps: list[str] = []
    existing = [path.resolve() for path in paths if path.exists()]
    for index, left in enumerate(existing):
        for right in existing[index + 1:]:
            if left == right or left in right.parents or right in left.parents:
                overlaps.append(f"footprint paths overlap: {left} and {right}")
    return overlaps


def measure_footprint(
    repo_root: Path,
    items: list[tuple[str, Path]],
) -> tuple[list[dict[str, Any]], int | None, list[str]]:
    blockers: list[str] = []
    if not items:
        return [], None, ["at least one Ethos footprint path is required"]
    blockers.extend(overlapping_paths([path for _, path in items]))
    measurements = [
        path_measurement(repo_root, path, role)
        for role, path in items
    ]
    total = 0
    for measurement in measurements:
        if not measurement["exists"]:
            blockers.append(f"{measurement['role']} path does not exist: {measurement['path']}")
            continue
        if measurement["path_kind"] not in {"file", "directory"}:
            blockers.append(f"{measurement['role']} path is not a file or directory: {measurement['path']}")
            continue
        size = measurement["size_bytes"]
        if not isinstance(size, int) or size < 0:
            blockers.append(f"{measurement['role']} size is invalid: {measurement['path']}")
            continue
        total += size
    return measurements, None if blockers else total, blockers


def pdfium_policy(profile: dict[str, Any]) -> dict[str, Any]:
    backend = profile.get("backend", {})
    flags = backend.get("build_flags", {})
    v8_text = backend.get("v8")
    xfa_text = backend.get("xfa")
    flag_v8 = flags.get("pdf_enable_v8")
    flag_xfa = flags.get("pdf_enable_xfa")
    v8_enabled = None
    xfa_enabled = None
    if isinstance(flag_v8, bool):
        v8_enabled = flag_v8
    elif isinstance(v8_text, str):
        v8_enabled = v8_text.lower() != "disabled"
    if isinstance(flag_xfa, bool):
        xfa_enabled = flag_xfa
    elif isinstance(xfa_text, str):
        xfa_enabled = xfa_text.lower() != "disabled"
    return {
        "backend_id": backend.get("id"),
        "backend_version": backend.get("version"),
        "upstream_version": backend.get("upstream_version"),
        "v8": v8_text,
        "xfa": xfa_text,
        "pdf_enable_v8": flag_v8,
        "pdf_enable_xfa": flag_xfa,
        "v8_enabled": v8_enabled,
        "xfa_enabled": xfa_enabled,
    }


def artifact_hash_record(
    path: Path | None,
    expected_sha256: str | None,
    repo_root: Path,
    label: str,
) -> tuple[dict[str, Any] | None, list[str]]:
    blockers: list[str] = []
    if path is None:
        return None, blockers
    record = path_measurement(repo_root, path, label)
    record["expected_sha256"] = expected_sha256
    record["hash_matches_expected"] = None
    if not record["exists"]:
        blockers.append(f"{label} path does not exist: {record['path']}")
    elif record["path_kind"] != "file":
        blockers.append(f"{label} path is not a file: {record['path']}")
    elif expected_sha256 and record["sha256"]:
        record["hash_matches_expected"] = record["sha256"] == expected_sha256
        if not record["hash_matches_expected"]:
            blockers.append(f"{label} sha256 does not match expected hash")
    return record, blockers


def selected_pdfium_artifact(profile: dict[str, Any], platform_key: str) -> dict[str, Any] | None:
    backend = profile.get("backend", {})
    artifacts = backend.get("platform_artifacts")
    if isinstance(artifacts, dict):
        artifact = artifacts.get(platform_key)
        if isinstance(artifact, dict):
            return artifact
    return None


def build_g2_result(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = args.repo_root.resolve()
    manifest_path = args.manifest.resolve()
    competitors_path = args.competitors_lock.resolve()
    gates_path = args.gates.resolve()
    profile_path = args.deterministic_profile.resolve()

    manifest = run_gate_zero.load_json(manifest_path)
    competitors = run_gate_zero.load_json(competitors_path)
    gates = run_gate_zero.load_json(gates_path)
    profile = run_gate_zero.load_json(profile_path) if profile_path.is_file() else {}
    host = run_gate_zero.select_host(manifest, args.host_id)
    platform_key = args.platform or (
        host.get("platform") if isinstance(host, dict) else run_gate_zero.current_platform_key()
    )

    blockers: list[str] = []
    if host is None:
        blockers.append("no matching performance host for this runner")
    if not profile_path.is_file():
        blockers.append("deterministic profile is missing")

    g2 = gates.get("gates", {}).get("g2", {})
    thresholds = g2.get("thresholds", {})
    reference_id = thresholds.get("comparison_reference")
    if reference_id != "opendataloader-pdf":
        blockers.append("G2 comparison reference is not opendataloader-pdf")

    footprint_items = [
        (item.role, item.path)
        for item in args.ethos_footprint
    ]
    ethos_items, ethos_size, footprint_blockers = measure_footprint(repo_root, footprint_items)
    blockers.extend(footprint_blockers)

    odl_install = path_measurement(repo_root, args.opendataloader_install_path, "opendataloader-install")
    odl_size = odl_install["size_bytes"] if odl_install["exists"] else None
    if not odl_install["exists"]:
        blockers.append(f"OpenDataLoader install path does not exist: {odl_install['path']}")
    elif odl_install["path_kind"] not in {"file", "directory"}:
        blockers.append(f"OpenDataLoader install path is not a file or directory: {odl_install['path']}")

    odl_entry = run_gate_zero.competitor_lock_entry(competitors, "opendataloader-pdf")
    expected_odl_hash = run_gate_zero.lock_artifact_hash(odl_entry, platform_key)
    odl_artifact, artifact_blockers = artifact_hash_record(
        args.opendataloader_artifact,
        expected_odl_hash,
        repo_root,
        "opendataloader-artifact",
    )
    blockers.extend(artifact_blockers)

    policy = pdfium_policy(profile)
    pdfium_expected = selected_pdfium_artifact(profile, platform_key) or {}
    pdfium_library, pdfium_library_blockers = artifact_hash_record(
        args.pdfium_library_path,
        pdfium_expected.get("runtime_library_sha256"),
        repo_root,
        "pdfium-library",
    )
    blockers.extend(pdfium_library_blockers)
    platform_hashes = profile.get("backend", {}).get("platform_hashes", {})
    pdfium_artifact, pdfium_artifact_blockers = artifact_hash_record(
        args.pdfium_artifact,
        platform_hashes.get(platform_key) if isinstance(platform_hashes, dict) else None,
        repo_root,
        "pdfium-artifact",
    )
    blockers.extend(pdfium_artifact_blockers)

    evaluation = gate_zero_gates.evaluate_g2_footprint(
        ethos_install_size_bytes=ethos_size,
        opendataloader_install_size_bytes=odl_size if isinstance(odl_size, int) else None,
        max_install_size_bytes=thresholds.get("max_install_size_bytes", 30_000_000),
        opendataloader_ratio_max=thresholds.get("opendataloader_ratio_max", 0.1),
        pdfium_v8_enabled=policy["v8_enabled"],
        pdfium_xfa_enabled=policy["xfa_enabled"],
    )
    if blockers:
        status = gate_zero_gates.BLOCKED
    else:
        status = evaluation["status"]
    failures = evaluation.get("failures", []) if not blockers else []

    ratio = (
        ethos_size / odl_size
        if isinstance(ethos_size, int) and isinstance(odl_size, int) and odl_size > 0
        else None
    )
    summary = {
        "status": status,
        "ethos_install_size_bytes": ethos_size,
        "opendataloader_install_size_bytes": odl_size,
        "ethos_to_opendataloader_ratio": ratio,
        "max_install_size_bytes": thresholds.get("max_install_size_bytes"),
        "opendataloader_ratio_max": thresholds.get("opendataloader_ratio_max"),
        "pdfium_v8_enabled": policy["v8_enabled"],
        "pdfium_xfa_enabled": policy["xfa_enabled"],
    }

    return {
        "schema_version": "ethos-gate-zero-g2-result-v1",
        "gate": "g2",
        "status": status,
        "platform": platform_key,
        "corpus": {
            "id": manifest.get("corpus_id", "gate-zero-v1"),
            "manifest": str(manifest_path.relative_to(repo_root)),
            "manifest_sha256": run_gate_zero.sha256_file(manifest_path),
        },
        "definition": {
            "gates": str(gates_path.relative_to(repo_root)),
            "definition_sha256": run_gate_zero.sha256_file(gates_path),
            "gate_status": g2.get("status"),
            "thresholds": thresholds,
            "measurement_scope": g2.get("measurement_scope"),
        },
        "host": {
            "selected": host,
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
            "deterministic_profile_sha256": run_gate_zero.sha256_c14n_file(profile_path)
            if profile_path.is_file()
            else None,
            "gates": str(gates_path.relative_to(repo_root)),
            "gates_sha256": run_gate_zero.sha256_file(gates_path),
            "manifest": str(manifest_path.relative_to(repo_root)),
            "manifest_sha256": run_gate_zero.sha256_file(manifest_path),
        },
        "measurements": {
            "ethos": {
                "install_size_bytes": ethos_size,
                "items": ethos_items,
            },
            "opendataloader-pdf": {
                "install_size_bytes": odl_size,
                "install_path": odl_install,
                "artifact": odl_artifact,
            },
            "pdfium": {
                "policy": policy,
                "platform_artifact": pdfium_expected,
                "library": pdfium_library,
                "artifact": pdfium_artifact,
            },
        },
        "evaluation": evaluation,
        "blockers": [*blockers, *evaluation.get("blockers", [])],
        "failures": failures,
        "summary": summary,
    }


def parse_footprint(value: str) -> argparse.Namespace:
    if "=" not in value:
        raise argparse.ArgumentTypeError("footprint path must use role=path")
    role, path = value.split("=", 1)
    role = role.strip()
    path = path.strip()
    if not role or not path:
        raise argparse.ArgumentTypeError("footprint path must use role=path")
    return argparse.Namespace(role=role, path=Path(path))


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--competitors-lock", type=Path, default=DEFAULT_COMPETITORS)
    parser.add_argument("--gates", type=Path, default=DEFAULT_GATES)
    parser.add_argument("--deterministic-profile", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument("--platform")
    parser.add_argument("--host-id")
    parser.add_argument(
        "--ethos-footprint",
        action="append",
        type=parse_footprint,
        default=[],
        metavar="ROLE=PATH",
    )
    parser.add_argument("--opendataloader-install-path", type=Path, required=True)
    parser.add_argument("--opendataloader-artifact", type=Path)
    parser.add_argument("--pdfium-library-path", type=Path)
    parser.add_argument("--pdfium-artifact", type=Path)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--stdout", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        result = build_g2_result(args)
    except Exception as exc:
        print(f"Gate Zero G2: {exc}", file=sys.stderr)
        return 2
    if args.stdout:
        run_gate_zero.write_json(None, result)
    else:
        run_gate_zero.write_json(args.out, result)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
