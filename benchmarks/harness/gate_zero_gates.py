#!/usr/bin/env python3
"""Pure Gate Zero G2/G3 definition evaluators.

These helpers intentionally do not run parsers or measure the filesystem. They
only encode pass/fail semantics from benchmarks/gate-zero/gates.json so result
runners can be tested before benchmark execution exists.
"""

from __future__ import annotations

from typing import Any


PASS = "pass"
FAIL = "fail"
BLOCKED = "blocked"
PROCEED = "PROCEED"
FALLBACK = "FALLBACK"
G1_RETRY_OR_FALLBACK = "G1_RETRY_OR_FALLBACK"
INCONCLUSIVE = "INCONCLUSIVE"


def evaluate_g2_footprint(
    *,
    ethos_install_size_bytes: int | None,
    opendataloader_install_size_bytes: int | None,
    max_install_size_bytes: int,
    opendataloader_ratio_max: float,
    pdfium_v8_enabled: bool | None,
    pdfium_xfa_enabled: bool | None,
) -> dict[str, Any]:
    blockers: list[str] = []
    failures: list[str] = []
    if ethos_install_size_bytes is None or ethos_install_size_bytes < 0:
        blockers.append("ethos install size is missing or invalid")
    if opendataloader_install_size_bytes is None or opendataloader_install_size_bytes <= 0:
        blockers.append("OpenDataLoader install size is missing or invalid")
    if pdfium_v8_enabled is None:
        blockers.append("PDFium V8 setting is unverifiable")
    elif pdfium_v8_enabled:
        failures.append("PDFium V8 is enabled")
    if pdfium_xfa_enabled is None:
        blockers.append("PDFium XFA setting is unverifiable")
    elif pdfium_xfa_enabled:
        failures.append("PDFium XFA is enabled")
    if blockers:
        return {"status": BLOCKED, "blockers": blockers, "failures": failures}

    assert ethos_install_size_bytes is not None
    assert opendataloader_install_size_bytes is not None
    max_by_reference = opendataloader_install_size_bytes * opendataloader_ratio_max
    if ethos_install_size_bytes > max_install_size_bytes:
        failures.append("ethos install size exceeds max byte threshold")
    if ethos_install_size_bytes > max_by_reference:
        failures.append("ethos install size exceeds OpenDataLoader ratio threshold")
    return {
        "status": FAIL if failures else PASS,
        "blockers": [],
        "failures": failures,
        "thresholds": {
            "max_install_size_bytes": max_install_size_bytes,
            "opendataloader_ratio_max": opendataloader_ratio_max,
            "opendataloader_ratio_max_bytes": max_by_reference,
        },
    }


def run_index(runs: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for run in runs:
        corpus_file = run.get("corpus_file", {})
        corpus_id = corpus_file.get("id")
        if isinstance(corpus_id, str):
            indexed[corpus_id] = run
    return indexed


def evaluate_g3_determinism(
    *,
    platform_results: dict[str, dict[str, Any]],
    required_platforms: list[str],
    corpus_ids: list[str],
    manifest_sha256: str,
    deterministic_profile_sha256: str,
) -> dict[str, Any]:
    blockers: list[str] = []
    failures: list[str] = []
    for platform in required_platforms:
        if platform not in platform_results:
            blockers.append(f"missing required platform result: {platform}")
    if blockers:
        return {"status": BLOCKED, "blockers": blockers, "failures": failures}

    indexed_by_platform = {
        platform: run_index(platform_results[platform].get("runs", []))
        for platform in required_platforms
    }
    for platform in required_platforms:
        result = platform_results[platform]
        corpus = result.get("corpus", {})
        if corpus.get("manifest_sha256") != manifest_sha256:
            blockers.append(f"{platform} manifest sha256 does not match")
        if result.get("deterministic_profile_sha256") != deterministic_profile_sha256:
            blockers.append(f"{platform} deterministic profile sha256 does not match")
        for corpus_id in corpus_ids:
            if corpus_id not in indexed_by_platform[platform]:
                blockers.append(f"{platform} missing corpus entry: {corpus_id}")
    if blockers:
        return {"status": BLOCKED, "blockers": blockers, "failures": failures}

    baseline_platform = required_platforms[0]
    baseline_runs = indexed_by_platform[baseline_platform]
    for corpus_id in corpus_ids:
        baseline = baseline_runs[corpus_id]
        for platform in required_platforms[1:]:
            candidate = indexed_by_platform[platform][corpus_id]
            if candidate.get("output_sha256") != baseline.get("output_sha256"):
                failures.append(f"{corpus_id} canonical payload differs on {platform}")
            if candidate.get("document_fingerprint") != baseline.get("document_fingerprint"):
                failures.append(f"{corpus_id} document fingerprint differs on {platform}")
            if candidate.get("warning_ids") != baseline.get("warning_ids"):
                failures.append(f"{corpus_id} warning ids differ on {platform}")
            if candidate.get("corpus_file") != baseline.get("corpus_file"):
                failures.append(f"{corpus_id} corpus binding differs on {platform}")
    return {"status": FAIL if failures else PASS, "blockers": [], "failures": failures}


def gate_zero_decision(g1_status: str, g2_status: str, g3_status: str) -> str:
    if BLOCKED in {g1_status, g2_status, g3_status}:
        return INCONCLUSIVE
    if g2_status == FAIL or g3_status == FAIL:
        return FALLBACK
    if g1_status == PASS and g2_status == PASS and g3_status == PASS:
        return PROCEED
    if g1_status == FAIL and g2_status == PASS and g3_status == PASS:
        return G1_RETRY_OR_FALLBACK
    return INCONCLUSIVE
