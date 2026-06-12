#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

import build_gate_zero_evidence
import gate_zero_gates
import run_gate_zero
import run_gate_zero_g2


HEX = "a" * 64


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def write_bytes(path: Path, size: int, byte: bytes = b"x") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(byte * size)
    return path


def fake_manifest(root: Path) -> Path:
    path = root / "benchmarks" / "gate-zero" / "manifest.json"
    write_json(
        path,
        {
            "corpus_id": "gate-zero-test",
            "hardware": [
                {
                    "id": "mac-m4pro-arm64",
                    "role": "performance",
                    "platform": "macos-arm64",
                    "model": "Mac",
                    "cpu": "Apple",
                    "ram": "48 GB",
                    "os": "macOS",
                    "kernel": "Darwin",
                    "runner": "local",
                }
            ],
        },
    )
    return path


def fake_gates(root: Path, *, max_bytes: int = 1_000, ratio: float = 0.1) -> Path:
    path = root / "benchmarks" / "gate-zero" / "gates.json"
    write_json(
        path,
        {
            "schema_version": "ethos-gate-zero-gates-v1",
            "gates": {
                "g2": {
                    "status": "defined-not-run",
                    "thresholds": {
                        "comparison_reference": "opendataloader-pdf",
                        "max_install_size_bytes": max_bytes,
                        "max_install_size_label": "30 MB decimal",
                        "logic": "PASS when max footprint is respected.",
                    },
                    "claim_thresholds": {
                        "claim": "one tenth OpenDataLoader footprint",
                        "logic": "Record whether ratio claim is supported.",
                        "opendataloader_ratio_max": ratio,
                    },
                    "measurement_scope": {
                        "includes": [],
                        "excludes": [],
                        "auto_fail": [],
                    },
                }
            },
        },
    )
    return path


def fake_competitors(root: Path, odl_artifact: Path) -> Path:
    path = root / "benchmarks" / "competitors.lock.json"
    write_json(
        path,
        {
            "status": "FROZEN",
            "gate_zero": [
                {
                    "id": "opendataloader-pdf",
                    "version": "2.4.7",
                    "artifact_sha256": run_gate_zero.sha256_file(odl_artifact),
                    "pinned": True,
                }
            ],
        },
    )
    return path


def fake_profile(root: Path, pdfium_library: Path, pdfium_artifact: Path, *, v8: bool = False, xfa: bool = False) -> Path:
    path = root / "profiles" / "ethos-deterministic-v1.json"
    write_json(
        path,
        {
            "backend": {
                "id": "pdfium",
                "version": "chromium/7881",
                "upstream_version": "PDFium 151.0.7881.0",
                "v8": "enabled" if v8 else "disabled",
                "xfa": "enabled" if xfa else "disabled",
                "build_flags": {
                    "pdf_enable_v8": v8,
                    "pdf_enable_xfa": xfa,
                },
                "platform_hashes": {
                    "macos-arm64": run_gate_zero.sha256_file(pdfium_artifact),
                },
                "platform_artifacts": {
                    "macos-arm64": {
                        "runtime_library_sha256": run_gate_zero.sha256_file(pdfium_library),
                    }
                },
            }
        },
    )
    return path


def fake_args(
    root: Path,
    *,
    ethos_items: list[tuple[str, Path]],
    odl_install: Path,
    odl_artifact: Path,
    pdfium_library: Path,
    pdfium_artifact: Path,
    profile: Path,
    manifest: Path,
    competitors: Path,
    gates: Path,
) -> Namespace:
    return Namespace(
        repo_root=root,
        manifest=manifest,
        competitors_lock=competitors,
        gates=gates,
        deterministic_profile=profile,
        platform="macos-arm64",
        host_id="mac-m4pro-arm64",
        ethos_footprint=[
            Namespace(role=role, path=path)
            for role, path in ethos_items
        ],
        opendataloader_install_path=odl_install,
        opendataloader_artifact=odl_artifact,
        pdfium_library_path=pdfium_library,
        pdfium_artifact=pdfium_artifact,
        out=root / "g2.json",
        stdout=False,
    )


class GateZeroG2ResultTests(unittest.TestCase):
    def test_g2_result_passes_when_footprint_is_within_thresholds(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ethos_cli = write_bytes(root / "target" / "release" / "ethos", 100)
            pdfium_library = write_bytes(root / "pdfium" / "libpdfium.dylib", 100)
            pdfium_artifact = write_bytes(root / "pdfium-mac-arm64.tgz", 50)
            odl_install = root / "odl"
            write_bytes(odl_install / "payload.bin", 3_000)
            odl_artifact = write_bytes(root / "opendataloader.whl", 30)
            manifest = fake_manifest(root)
            gates = fake_gates(root)
            competitors = fake_competitors(root, odl_artifact)
            profile = fake_profile(root, pdfium_library, pdfium_artifact)

            result = run_gate_zero_g2.build_g2_result(
                fake_args(
                    root,
                    ethos_items=[("ethos-cli", ethos_cli), ("pdfium-library", pdfium_library)],
                    odl_install=odl_install,
                    odl_artifact=odl_artifact,
                    pdfium_library=pdfium_library,
                    pdfium_artifact=pdfium_artifact,
                    profile=profile,
                    manifest=manifest,
                    competitors=competitors,
                    gates=gates,
                )
            )

        self.assertEqual(result["status"], gate_zero_gates.PASS)
        self.assertEqual(result["summary"]["ethos_install_size_bytes"], 200)
        self.assertEqual(result["summary"]["opendataloader_install_size_bytes"], 3000)
        self.assertTrue(result["summary"]["opendataloader_ratio_claim_supported"])
        self.assertEqual(result["blockers"], [])
        self.assertEqual(result["failures"], [])

    def test_g2_result_passes_but_marks_ratio_claim_unsupported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ethos_cli = write_bytes(root / "target" / "release" / "ethos", 201)
            pdfium_library = write_bytes(root / "pdfium" / "libpdfium.dylib", 100)
            pdfium_artifact = write_bytes(root / "pdfium-mac-arm64.tgz", 50)
            odl_install = root / "odl"
            write_bytes(odl_install / "payload.bin", 3_000)
            odl_artifact = write_bytes(root / "opendataloader.whl", 30)
            manifest = fake_manifest(root)
            gates = fake_gates(root)
            competitors = fake_competitors(root, odl_artifact)
            profile = fake_profile(root, pdfium_library, pdfium_artifact)

            result = run_gate_zero_g2.build_g2_result(
                fake_args(
                    root,
                    ethos_items=[("ethos-cli", ethos_cli), ("pdfium-library", pdfium_library)],
                    odl_install=odl_install,
                    odl_artifact=odl_artifact,
                    pdfium_library=pdfium_library,
                    pdfium_artifact=pdfium_artifact,
                    profile=profile,
                    manifest=manifest,
                    competitors=competitors,
                    gates=gates,
                )
            )

        self.assertEqual(result["status"], gate_zero_gates.PASS)
        self.assertFalse(result["summary"]["opendataloader_ratio_claim_supported"])
        self.assertEqual(result["failures"], [])

    def test_g2_result_blocks_overlapping_footprint_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = root / "bundle"
            nested = write_bytes(bundle / "ethos", 10)
            pdfium_library = write_bytes(root / "pdfium" / "libpdfium.dylib", 10)
            pdfium_artifact = write_bytes(root / "pdfium-mac-arm64.tgz", 10)
            odl_install = root / "odl"
            write_bytes(odl_install / "payload.bin", 1_000)
            odl_artifact = write_bytes(root / "opendataloader.whl", 10)
            manifest = fake_manifest(root)
            gates = fake_gates(root)
            competitors = fake_competitors(root, odl_artifact)
            profile = fake_profile(root, pdfium_library, pdfium_artifact)

            result = run_gate_zero_g2.build_g2_result(
                fake_args(
                    root,
                    ethos_items=[("ethos-bundle", bundle), ("ethos-cli", nested)],
                    odl_install=odl_install,
                    odl_artifact=odl_artifact,
                    pdfium_library=pdfium_library,
                    pdfium_artifact=pdfium_artifact,
                    profile=profile,
                    manifest=manifest,
                    competitors=competitors,
                    gates=gates,
                )
            )

        self.assertEqual(result["status"], gate_zero_gates.BLOCKED)
        self.assertTrue(any("footprint paths overlap" in blocker for blocker in result["blockers"]))

    def test_g2_result_fails_when_pdfium_v8_or_xfa_is_enabled(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ethos_cli = write_bytes(root / "target" / "release" / "ethos", 1)
            pdfium_library = write_bytes(root / "pdfium" / "libpdfium.dylib", 1)
            pdfium_artifact = write_bytes(root / "pdfium-mac-arm64.tgz", 1)
            odl_install = root / "odl"
            write_bytes(odl_install / "payload.bin", 1_000)
            odl_artifact = write_bytes(root / "opendataloader.whl", 1)
            manifest = fake_manifest(root)
            gates = fake_gates(root)
            competitors = fake_competitors(root, odl_artifact)
            profile = fake_profile(root, pdfium_library, pdfium_artifact, v8=True, xfa=True)

            result = run_gate_zero_g2.build_g2_result(
                fake_args(
                    root,
                    ethos_items=[("ethos-cli", ethos_cli), ("pdfium-library", pdfium_library)],
                    odl_install=odl_install,
                    odl_artifact=odl_artifact,
                    pdfium_library=pdfium_library,
                    pdfium_artifact=pdfium_artifact,
                    profile=profile,
                    manifest=manifest,
                    competitors=competitors,
                    gates=gates,
                )
            )

        self.assertEqual(result["status"], gate_zero_gates.FAIL)
        self.assertIn("PDFium V8 is enabled", result["failures"])
        self.assertIn("PDFium XFA is enabled", result["failures"])

    def test_evidence_builder_accepts_g2_result_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ethos_cli = write_bytes(root / "target" / "release" / "ethos", 100)
            pdfium_library = write_bytes(root / "pdfium" / "libpdfium.dylib", 100)
            pdfium_artifact = write_bytes(root / "pdfium-mac-arm64.tgz", 50)
            odl_install = root / "odl"
            write_bytes(odl_install / "payload.bin", 3_000)
            odl_artifact = write_bytes(root / "opendataloader.whl", 30)
            manifest = fake_manifest(root)
            gates = fake_gates(root)
            competitors = fake_competitors(root, odl_artifact)
            profile = fake_profile(root, pdfium_library, pdfium_artifact)
            result = run_gate_zero_g2.build_g2_result(
                fake_args(
                    root,
                    ethos_items=[("ethos-cli", ethos_cli), ("pdfium-library", pdfium_library)],
                    odl_install=odl_install,
                    odl_artifact=odl_artifact,
                    pdfium_library=pdfium_library,
                    pdfium_artifact=pdfium_artifact,
                    profile=profile,
                    manifest=manifest,
                    competitors=competitors,
                    gates=gates,
                )
            )
            result_path = root / "benchmarks" / "results" / "gate-zero" / "macos-arm64" / "g2.json"
            write_json(result_path, result)

            report = build_gate_zero_evidence.build_evidence_bundle(
                repo_root=root,
                result_path=result_path,
                out_root=root / "benchmarks" / "results" / "gate-zero",
                platform_key="macos-arm64",
                gate="g2",
                timestamp="20260612T120000Z",
                reproduction_command="python3 benchmarks/harness/run_gate_zero_g2.py ...",
                environment={
                    "ETHOS_PDFIUM_LIBRARY_PATH": str(pdfium_library),
                    "ETHOS_PDFIUM_VERSION": "chromium/7881",
                    "ETHOS_PDFIUM_ARTIFACT_PATH": str(pdfium_artifact),
                    "ETHOS_OPENDATALOADER_PDF_ARTIFACT": str(odl_artifact),
                    "ETHOS_OPENDATALOADER_PDF_INSTALL_PATH": str(odl_install),
                },
                benchmark_commit="c" * 40,
            )
            bundle_dir = Path(report["bundle_dir"])
            summary = (bundle_dir / "SUMMARY.md").read_text(encoding="utf-8")

        self.assertIn("## Footprint Result", summary)
        self.assertIn("Ethos base parser footprint", summary)
        self.assertEqual(report["manifest"]["definition_sha256"], result["definition"]["definition_sha256"])
        self.assertEqual(report["manifest"]["reproduction_env_status"], "complete")


if __name__ == "__main__":
    unittest.main()
