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
#

from __future__ import annotations

import json
import unittest
from pathlib import Path

import gate_zero_gates


ROOT = Path(__file__).resolve().parents[2]
GATES = ROOT / "benchmarks" / "gate-zero" / "gates.json"
MANIFEST = ROOT / "benchmarks" / "gate-zero" / "manifest.json"
COMPETITORS = ROOT / "benchmarks" / "competitors.lock.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class GateZeroGateDefinitionTests(unittest.TestCase):
    def test_g2_footprint_thresholds_match_prd_contract(self) -> None:
        gates = load_json(GATES)
        g2 = gates["gates"]["g2"]

        self.assertEqual(g2["status"], "defined-not-run")
        self.assertEqual(g2["thresholds"]["max_install_size_bytes"], 30_000_000)
        self.assertEqual(g2["thresholds"]["max_install_size_label"], "30 MB decimal")
        self.assertEqual(g2["claim_thresholds"]["opendataloader_ratio_max"], 0.1)
        self.assertEqual(g2["thresholds"]["comparison_reference"], "opendataloader-pdf")
        self.assertIn("claim threshold", g2["claim_thresholds"]["logic"])
        self.assertIn("PDFium sidecar or static payload", " ".join(g2["measurement_scope"]["includes"]))
        self.assertIn("bundled deterministic font assets", g2["measurement_scope"]["includes"])
        self.assertIn("PDFium build has V8 enabled", g2["measurement_scope"]["auto_fail"])
        self.assertIn("PDFium build has XFA enabled", g2["measurement_scope"]["auto_fail"])

    def test_g2_reference_competitor_exists_in_lock(self) -> None:
        gates = load_json(GATES)
        competitors = load_json(COMPETITORS)
        reference_id = gates["gates"]["g2"]["thresholds"]["comparison_reference"]
        entries = {entry["id"]: entry for entry in competitors["gate_zero"]}

        self.assertIn(reference_id, entries)
        self.assertIn("G1/G2 reference", entries[reference_id]["role"])
        self.assertTrue(entries[reference_id]["pinned"])

    def test_g3_determinism_scope_matches_manifest(self) -> None:
        gates = load_json(GATES)
        manifest = load_json(MANIFEST)
        g3 = gates["gates"]["g3"]

        self.assertEqual(g3["status"], "defined-not-run")
        self.assertEqual(g3["platforms"], manifest["determinism_platforms"])
        self.assertEqual(g3["platforms"], ["macos-arm64", "linux-x64"])
        self.assertEqual(g3["corpus_scope"], "full frozen Gate Zero manifest")
        self.assertEqual(g3["thresholds"]["canonical_payload_divergences_allowed"], 0)
        self.assertEqual(g3["thresholds"]["document_fingerprint_divergences_allowed"], 0)
        self.assertIn("cannot pass from a single platform result", g3["completion_policy"])
        self.assertIn("equal warning_ids", " ".join(g3["required_evidence"]))

    def test_g2_or_g3_failure_forces_fallback_decision_rule(self) -> None:
        gates = load_json(GATES)

        self.assertEqual(gates["schema_version"], "ethos-gate-zero-gates-v1")
        self.assertIn("G2 or G3 fails", gates["decision_rule"]["g2_or_g3_fail"])
        self.assertIn("parser-core expansion stops", gates["decision_rule"]["g2_or_g3_fail"])
        self.assertIn("G1 fails while G2 and G3 pass", gates["decision_rule"]["g1_only_fail"])

    def test_g2_evaluator_enforces_byte_boundary_and_reports_ratio_claim(self) -> None:
        gates = load_json(GATES)
        g2_thresholds = gates["gates"]["g2"]["thresholds"]
        claim_thresholds = gates["gates"]["g2"]["claim_thresholds"]
        max_bytes = g2_thresholds["max_install_size_bytes"]
        ratio = claim_thresholds["opendataloader_ratio_max"]

        self.assertEqual(
            gate_zero_gates.evaluate_g2_footprint(
                ethos_install_size_bytes=max_bytes,
                opendataloader_install_size_bytes=max_bytes * 10,
                max_install_size_bytes=max_bytes,
                opendataloader_ratio_max=ratio,
                pdfium_v8_enabled=False,
                pdfium_xfa_enabled=False,
            )["status"],
            gate_zero_gates.PASS,
        )
        self.assertEqual(
            gate_zero_gates.evaluate_g2_footprint(
                ethos_install_size_bytes=max_bytes + 1,
                opendataloader_install_size_bytes=(max_bytes + 1) * 10,
                max_install_size_bytes=max_bytes,
                opendataloader_ratio_max=ratio,
                pdfium_v8_enabled=False,
                pdfium_xfa_enabled=False,
            )["status"],
            gate_zero_gates.FAIL,
        )
        ratio_miss = gate_zero_gates.evaluate_g2_footprint(
            ethos_install_size_bytes=101,
            opendataloader_install_size_bytes=1000,
            max_install_size_bytes=max_bytes,
            opendataloader_ratio_max=ratio,
            pdfium_v8_enabled=False,
            pdfium_xfa_enabled=False,
        )
        self.assertEqual(ratio_miss["status"], gate_zero_gates.PASS)
        self.assertFalse(ratio_miss["claims"]["one_tenth_opendataloader_footprint_supported"])

    def test_g2_evaluator_blocks_missing_reference_and_auto_fails_v8_xfa(self) -> None:
        gates = load_json(GATES)
        thresholds = gates["gates"]["g2"]["thresholds"]
        claim_thresholds = gates["gates"]["g2"]["claim_thresholds"]

        blocked = gate_zero_gates.evaluate_g2_footprint(
            ethos_install_size_bytes=1,
            opendataloader_install_size_bytes=0,
            max_install_size_bytes=thresholds["max_install_size_bytes"],
            opendataloader_ratio_max=claim_thresholds["opendataloader_ratio_max"],
            pdfium_v8_enabled=False,
            pdfium_xfa_enabled=False,
        )
        self.assertEqual(blocked["status"], gate_zero_gates.BLOCKED)
        self.assertIn("OpenDataLoader install size is missing or invalid", blocked["blockers"])

        failed = gate_zero_gates.evaluate_g2_footprint(
            ethos_install_size_bytes=1,
            opendataloader_install_size_bytes=100,
            max_install_size_bytes=thresholds["max_install_size_bytes"],
            opendataloader_ratio_max=claim_thresholds["opendataloader_ratio_max"],
            pdfium_v8_enabled=True,
            pdfium_xfa_enabled=True,
        )
        self.assertEqual(failed["status"], gate_zero_gates.FAIL)
        self.assertIn("PDFium V8 is enabled", failed["failures"])
        self.assertIn("PDFium XFA is enabled", failed["failures"])

    def test_g3_evaluator_requires_full_platform_and_corpus_binding(self) -> None:
        result = self._g3_result("macos-arm64", "payload-a", "fp-a", ["W001"])

        blocked = gate_zero_gates.evaluate_g3_determinism(
            platform_results={"macos-arm64": result},
            required_platforms=["macos-arm64", "linux-x64"],
            corpus_ids=["sample"],
            manifest_sha256="manifest-sha",
            deterministic_profile_sha256="profile-sha",
        )

        self.assertEqual(blocked["status"], gate_zero_gates.BLOCKED)
        self.assertIn("missing required platform result: linux-x64", blocked["blockers"])

    def test_g3_evaluator_fails_payload_fingerprint_and_warning_divergence(self) -> None:
        mac = self._g3_result("macos-arm64", "payload-a", "fp-a", ["W001"])
        linux = self._g3_result("linux-x64", "payload-b", "fp-b", ["W002"])

        report = gate_zero_gates.evaluate_g3_determinism(
            platform_results={"macos-arm64": mac, "linux-x64": linux},
            required_platforms=["macos-arm64", "linux-x64"],
            corpus_ids=["sample"],
            manifest_sha256="manifest-sha",
            deterministic_profile_sha256="profile-sha",
        )

        self.assertEqual(report["status"], gate_zero_gates.FAIL)
        self.assertIn("sample stable payload differs on linux-x64", report["failures"])
        self.assertIn("sample document fingerprint differs on linux-x64", report["failures"])
        self.assertIn("sample warning ids differ on linux-x64", report["failures"])

    def test_gate_zero_decision_rule_never_retries_g2_or_g3_failure(self) -> None:
        self.assertEqual(
            gate_zero_gates.gate_zero_decision(
                gate_zero_gates.PASS,
                gate_zero_gates.PASS,
                gate_zero_gates.PASS,
            ),
            gate_zero_gates.PROCEED,
        )
        self.assertEqual(
            gate_zero_gates.gate_zero_decision(
                gate_zero_gates.FAIL,
                gate_zero_gates.PASS,
                gate_zero_gates.PASS,
            ),
            gate_zero_gates.G1_RETRY_OR_FALLBACK,
        )
        self.assertEqual(
            gate_zero_gates.gate_zero_decision(
                gate_zero_gates.PASS,
                gate_zero_gates.FAIL,
                gate_zero_gates.PASS,
            ),
            gate_zero_gates.FALLBACK,
        )
        self.assertEqual(
            gate_zero_gates.gate_zero_decision(
                gate_zero_gates.PASS,
                gate_zero_gates.PASS,
                gate_zero_gates.BLOCKED,
            ),
            gate_zero_gates.INCONCLUSIVE,
        )

    def _g3_result(
        self,
        platform: str,
        payload_sha256: str,
        document_fingerprint: str,
        warning_ids: list[str],
    ) -> dict:
        return {
            "corpus": {"manifest_sha256": "manifest-sha"},
            "deterministic_profile_sha256": "profile-sha",
            "host": {"selected": {"platform": platform}},
            "runs": [
                {
                    "corpus_file": {
                        "actual_sha256": "sample-sha",
                        "file": "benchmarks/gate-zero/corpus/sample.pdf",
                        "id": "sample",
                        "sha256": "sample-sha",
                    },
                    "document_fingerprint": document_fingerprint,
                    "output_sha256": "raw-output-" + platform,
                    "payload_sha256": payload_sha256,
                    "warning_ids": warning_ids,
                }
            ],
        }


if __name__ == "__main__":
    unittest.main()
