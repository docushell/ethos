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

"""Schema/example validation gate (ci.yml: schema-validate job).

Checks, in order:
1. every schema is itself a valid JSON Schema draft 2020-12;
2. every example validates against its schema (JSONL = every line);
3. the deterministic profile artifact validates against the profile schema;
4. referential integrity inside the document example (every *_ref resolves).

Exit 0 = green. Any failure prints the offending file/pointer and exits 1.
"""
import json
import sys
from pathlib import Path

from font_policy_validation import diagnose_font_policy
from security_report_validation import (
    DEFAULT_CHUNK_EXCLUDED_CODES,
    FINDING_MESSAGE_TEMPLATES,
    INVENTORY_BACKED_FINDING_CODES,
    TEXT_BACKED_FINDING_CODES,
    diagnose_security_report_example,
    deterministic_preview,
)
from table_model_validation import diagnose_table_model

try:
    from jsonschema import Draft202012Validator as Validator
    DIALECT = "2020-12"
except ImportError:  # pragma: no cover
    try:
        # Older jsonschema (<4): the contract schemas deliberately use only keywords shared by
        # draft-7 and 2020-12 ($defs refs are plain JSON pointers), so draft-7 validation is a
        # faithful local approximation. CI pins jsonschema>=4.18 and validates the real dialect.
        from jsonschema import Draft7Validator as Validator
        DIALECT = "draft-7 fallback (CI runs 2020-12)"
    except ImportError:
        print(
            "FAIL  Python package 'jsonschema' is required for schema/example validation. "
            "Install jsonschema>=4.18 or run with a Python environment that provides it.",
            file=sys.stderr,
        )
        sys.exit(1)
print(f"dialect: {DIALECT}")

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS = ROOT / "schemas"
EXAMPLES = SCHEMAS / "examples"

PAIRS = [
    ("ethos-document.schema.json", [EXAMPLES / "document.example.json"]),
    ("ethos-chunks.schema.json", [EXAMPLES / "chunks.example.jsonl"]),
    ("ethos-citations.schema.json", [
        EXAMPLES / "citations.example.json",
        EXAMPLES / "citations-array.example.json",
    ]),
    ("ethos-security-report.schema.json", [
        EXAMPLES / "security-report.example.json",
        EXAMPLES / "security-report.full.example.json",
    ]),
    ("ethos-verification-report.schema.json", [
        EXAMPLES / "verification-report.example.json",
        EXAMPLES / "verification-report-negative.example.json",
    ]),
    ("ethos-verification-config.schema.json", [EXAMPLES / "verification-config.example.json"]),
    ("ethos-crop-descriptor.schema.json", [EXAMPLES / "crop-descriptor.example.json"]),
    ("ethos-crop-element-request.schema.json", [
        EXAMPLES / "crop-element-request.example.json",
    ]),
    ("ethos-verify-citations-contract.schema.json", [
        ROOT / "examples" / "verify" / "verify_citations_v1_contract.json",
    ]),
    ("ethos-claim-kind-boundary-contract.schema.json", [
        ROOT / "examples" / "verify" / "claim_kind_boundary_v1_contract.json",
    ]),
    ("ethos-grounding-source-contract.schema.json", [
        ROOT / "examples" / "verify" / "grounding_source_v1_contract.json",
    ]),
    ("ethos-capability-downgrade-contract.schema.json", [
        ROOT / "examples" / "verify" / "capability_downgrade_v1_contract.json",
    ]),
    ("ethos-opendataloader-adapter-shape-contract.schema.json", [
        ROOT / "examples" / "verify" / "opendataloader_adapter_shape_v1_contract.json",
    ]),
    ("ethos-crop-element-contract.schema.json", [
        ROOT / "examples" / "crop" / "crop_element_v1_contract.json",
    ]),
    ("ethos-crop-element-surface-shape-contract.schema.json", [
        ROOT / "examples" / "crop" / "crop_element_surface_shape_v1_contract.json",
    ]),
    ("ethos-sandbox-subprocess-request.schema.json", [
        EXAMPLES / "sandbox-subprocess-doc-parse-request.example.json",
        EXAMPLES / "sandbox-subprocess-doc-parse-timeout-request.example.json",
        EXAMPLES / "sandbox-subprocess-doc-parse-diagnostics-request.example.json",
        EXAMPLES / "sandbox-subprocess-fingerprint-timeout-request.example.json",
    ]),
    ("ethos-sandbox-subprocess-contract.schema.json", [
        ROOT / "examples" / "sandbox" / "sandbox_subprocess_v1_contract.json",
    ]),
    ("ethos-milestone-e-fixture-candidates.schema.json", [
        ROOT / "docs" / "milestone-e-fixture-candidates.json",
    ]),
    ("ethos-milestone-e-fixture-promotion-criteria.schema.json", [
        ROOT / "docs" / "milestone-e-fixture-promotion-criteria.json",
    ]),
    ("ethos-deterministic-profile.schema.json", [ROOT / "profiles" / "ethos-deterministic-v1.json"]),
]

failures = 0


def fail(msg: str) -> None:
    global failures
    failures += 1
    print(f"FAIL  {msg}")


def validate_instance(validator, instance, label: str) -> None:
    errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path))
    if errors:
        for e in errors[:8]:
            ptr = "/" + "/".join(str(p) for p in e.absolute_path)
            fail(f"{label} at '{ptr}': {e.message}")
    else:
        print(f"ok    {label}")


for schema_name, example_paths in PAIRS:
    schema_path = SCHEMAS / schema_name
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    if DIALECT != "2020-12":
        # jsonschema 3.x cannot resolve refs against a URN base URI. All contract refs are
        # local '#/...' pointers, so dropping $id is semantics-preserving for validation.
        schema.pop("$id", None)
    try:
        Validator.check_schema(schema)
        print(f"ok    {schema_name} is a valid schema ({DIALECT})")
    except Exception as exc:  # noqa: BLE001
        fail(f"{schema_name} is not a valid schema: {exc}")
        continue
    validator = Validator(schema)
    for example in example_paths:
        if not example.exists():
            fail(f"{example} missing")
            continue
        if example.suffix == ".jsonl":
            for i, line in enumerate(example.read_text(encoding="utf-8").splitlines(), 1):
                if not line.strip():
                    continue
                validate_instance(validator, json.loads(line), f"{example.name}:{i}")
        else:
            validate_instance(validator, json.loads(example.read_text(encoding="utf-8")), example.name)

# --- referential integrity inside the document example -------------------------------
doc = json.loads((EXAMPLES / "document.example.json").read_text(encoding="utf-8"))
p = doc["payload"]
ids = {
    "page": {x["id"] for x in p["pages"]},
    "element": {x["id"] for x in p["elements"]},
    "span": {x["id"] for x in p["spans"]},
    "table": {x["id"] for x in p["tables"]},
    "region": {x["id"] for x in p["regions"]},
    "warning": {w["id"] for w in p["security_warnings"] + p["parser_warnings"]},
}


def check_ref(kind: str, ref: str, ctx: str) -> None:
    if ref not in ids[kind]:
        fail(f"document.example.json: {ctx} references unknown {kind} '{ref}'")


for el in p["elements"]:
    check_ref("page", el["page"], f"element {el['id']}")
    for r in el.get("span_refs", []):
        check_ref("span", r, f"element {el['id']}")
    for r in el.get("warning_refs", []):
        check_ref("warning", r, f"element {el['id']}")
    if "table_ref" in el:
        check_ref("table", el["table_ref"], f"element {el['id']}")
    if "region_ref" in el:
        check_ref("region", el["region_ref"], f"element {el['id']}")
for sp in p["spans"]:
    check_ref("page", sp["page"], f"span {sp['id']}")
    for r in sp.get("warning_refs", []):
        check_ref("warning", r, f"span {sp['id']}")
for t in p["tables"]:
    for r in t["page_refs"]:
        check_ref("page", r, f"table {t['id']}")
    for r in t.get("warning_refs", []):
        check_ref("warning", r, f"table {t['id']}")
    for c in t["cells"]:
        cell_ctx = f"table {t['id']} cell ({c['row']},{c['col']})"
        for r in c.get("span_refs", []):
            check_ref("span", r, cell_ctx)
        for r in c.get("element_refs", []):
            check_ref("element", r, cell_ctx)
for ch in p["chunks"]:
    for r in ch["element_refs"]:
        check_ref("element", r, f"chunk {ch['id']}")
    for r in ch["page_refs"]:
        check_ref("page", r, f"chunk {ch['id']}")
    for b in ch["bboxes"]:
        check_ref("page", b["page"], f"chunk {ch['id']} bbox")
for w in p["security_warnings"] + p["parser_warnings"]:
    if "page" in w:
        check_ref("page", w["page"], f"warning {w['id']}")
    if "element_ref" in w:
        check_ref("element", w["element_ref"], f"warning {w['id']}")
    if "span_ref" in w:
        check_ref("span", w["span_ref"], f"warning {w['id']}")
    if "region_ref" in w:
        check_ref("region", w["region_ref"], f"warning {w['id']}")

for diagnostic in diagnose_table_model(p):
    fail(diagnostic)

# --- derivability: chunks.example.jsonl must be EXACTLY what `ethos rag chunk` derives
# from document.example.json (PRD §7: every derived artifact is reproducible from the
# canonical JSON + config). Catches drift between examples (P2 reviewer finding).
def c14n_line(v) -> str:
    return json.dumps(v, separators=(",", ":"), sort_keys=True, ensure_ascii=False)


def c14n_value(v) -> str:
    return json.dumps(v, separators=(",", ":"), sort_keys=True, ensure_ascii=False)


wcodes = {w["id"]: w["code"] for w in p["security_warnings"] + p["parser_warnings"]}
expected_lines = []
for ch in p["chunks"]:
    for warning_ref in ch.get("warning_refs", []):
        code = wcodes[warning_ref]
        if code in DEFAULT_CHUNK_EXCLUDED_CODES:
            fail(
                "document.example.json: "
                f"chunk {ch['id']} references default-excluded warning_ref {warning_ref} ({code})"
            )
    expected_lines.append(c14n_line({
        "schema_version": doc["schema_version"],
        "document_fingerprint": doc["fingerprint"],
        "source_fingerprint": doc["source"]["fingerprint"],
        "config_sha256": doc["config_sha256"],
        "id": ch["id"],
        "text": ch["text"],
        "element_refs": ch["element_refs"],
        "page_refs": ch["page_refs"],
        "bboxes": ch["bboxes"],
        "token_estimate": ch["token_estimate"],
        "warnings": [wcodes[r] for r in ch.get("warning_refs", [])],
    }))
actual_lines = [
    c14n_line(json.loads(l))
    for l in (EXAMPLES / "chunks.example.jsonl").read_text(encoding="utf-8").splitlines()
    if l.strip()
]
if expected_lines != actual_lines:
    fail("chunks.example.jsonl is not derivable from document.example.json "
         f"({len(actual_lines)} lines vs {len(expected_lines)} derived)")
else:
    print(f"ok    chunks.example.jsonl derivable from document example ({len(actual_lines)} chunks)")

spans = {span["id"]: span for span in p["spans"]}
security_warnings = sorted(
    p["security_warnings"],
    key=lambda warning: (
        warning["code"],
        warning.get("page", ""),
        warning.get("element_ref", ""),
        warning.get("span_ref", ""),
        warning.get("region_ref", ""),
        warning.get("message", ""),
    ),
)
summary = {}
findings = []
for index, warning in enumerate(security_warnings, 1):
    if warning["code"] not in FINDING_MESSAGE_TEMPLATES:
        continue
    if warning["code"] in INVENTORY_BACKED_FINDING_CODES:
        fail(
            "document.example.json: security-report.example.json cannot derive "
            f"inventory-backed warning {warning['id']} ({warning['code']}) "
            "from source-only document warnings"
        )
        continue
    summary[warning["code"]] = summary.get(warning["code"], 0) + 1
    finding = {
        "id": f"f{index:04}",
        "code": warning["code"],
        "message": warning["message"],
        "excluded_from_default_chunks": warning["code"] in DEFAULT_CHUNK_EXCLUDED_CODES,
    }
    for field in ("page", "element_ref", "span_ref"):
        if field in warning:
            finding[field] = warning[field]
    if warning["code"] in TEXT_BACKED_FINDING_CODES:
        span_ref = warning.get("span_ref")
        if span_ref is None or span_ref not in spans:
            fail(
                "document.example.json: security-report.example.json cannot derive "
                f"text-backed warning {warning['id']} without a valid span_ref"
            )
        else:
            finding["bbox"] = spans[span_ref]["bbox"]
            finding["text_preview"] = deterministic_preview(spans[span_ref]["text"])
    findings.append(finding)

expected_security_report = {
    "schema_version": doc["schema_version"],
    "document_fingerprint": doc["fingerprint"],
    "source_fingerprint": doc["source"]["fingerprint"],
    "profile": {
        "id": doc["profile"]["id"],
        "sha256": doc["profile"]["sha256"],
    },
    "summary": summary,
    "findings": findings,
    "inventories": {
        "annotations": [],
        "actions": [],
        "attachments": [],
        "scripts": [],
        "links": [],
    },
}
actual_security_report = json.loads(
    (EXAMPLES / "security-report.example.json").read_text(encoding="utf-8")
)
if c14n_value(expected_security_report) != c14n_value(actual_security_report):
    fail(
        "security-report.example.json is not derivable from document.example.json "
        f"({len(actual_security_report.get('findings', []))} findings vs "
        f"{len(findings)} derived)"
    )
else:
    finding_label = "finding" if len(findings) == 1 else "findings"
    print(
        "ok    security-report.example.json derivable from document example "
        f"({len(findings)} {finding_label})"
    )

# fingerprint coherence across example artifacts
sec = actual_security_report
sec_full = json.loads((EXAMPLES / "security-report.full.example.json").read_text(encoding="utf-8"))
ver = json.loads((EXAMPLES / "verification-report.example.json").read_text(encoding="utf-8"))
citations = json.loads((EXAMPLES / "citations.example.json").read_text(encoding="utf-8"))
crop = json.loads((EXAMPLES / "crop-descriptor.example.json").read_text(encoding="utf-8"))
for label, got in [
    ("security-report.document_fingerprint", sec["document_fingerprint"]),
    ("security-report.source_fingerprint", sec["source_fingerprint"]),
    ("security-report-full.document_fingerprint", sec_full["document_fingerprint"]),
    ("security-report-full.source_fingerprint", sec_full["source_fingerprint"]),
    ("verification-report.document_fingerprint", ver["document_fingerprint"]),
    ("crop-descriptor.document_fingerprint", crop["document_fingerprint"]),
]:
    want = doc["source"]["fingerprint"] if label.endswith("source_fingerprint") else doc["fingerprint"]
    if got != want:
        fail(f"{label} diverges from document example")
print("ok    example fingerprints coherent across artifacts")

security_report_diagnostics = diagnose_security_report_example(doc, sec)
security_report_full_diagnostics = diagnose_security_report_example(
    doc,
    sec_full,
    ctx="security-report.full.example.json",
)
if security_report_diagnostics or security_report_full_diagnostics:
    for diagnostic in security_report_diagnostics:
        fail(diagnostic)
    for diagnostic in security_report_full_diagnostics:
        fail(diagnostic)
else:
    print("ok    security report examples findings are grounded in document example")

# Milestone D verify_citations v1 contract fixture: the minimal citation input example and
# grounded report example must describe the same ordered claims over the document example.
verify_citations_failures_before = failures
if citations["document_fingerprint"] != doc["fingerprint"]:
    fail("citations.example.json document_fingerprint diverges from document example")
if ver["document_fingerprint"] != citations["document_fingerprint"]:
    fail("verification-report.example.json document_fingerprint diverges from citations example")
claims = citations["claims"]
checks = ver["checks"]
if len(checks) != len(claims):
    fail(
        "verification-report.example.json checks do not match citations.example.json claims "
        f"({len(checks)} checks vs {len(claims)} claims)"
    )
else:
    for index, (claim, check) in enumerate(zip(claims, checks), 1):
        expected_id = f"v{index:04}"
        if check["id"] != expected_id:
            fail(f"verification-report.example.json check {index} id is not {expected_id}")
        if c14n_value(check["claim"]) != c14n_value(claim):
            fail(
                "verification-report.example.json check "
                f"{check['id']} does not echo citations.example.json claim {index}"
            )
        if check["status"] != "grounded":
            fail(f"verification-report.example.json check {check['id']} is not grounded")
        if check["semantic_unverified"]:
            fail(f"verification-report.example.json check {check['id']} is semantically unverified")
if not ver["all_evidence_grounded"]:
    fail("verification-report.example.json all_evidence_grounded is not true")
if ver["unsupported_claim_kinds"]:
    fail("verification-report.example.json unexpectedly has unsupported claim kinds")
if failures == verify_citations_failures_before:
    print("ok    verify_citations v1 example pair coherent")

# deterministic profile font-policy artifact checks
profile = json.loads(
    (ROOT / "profiles" / "ethos-deterministic-v1.json").read_text(encoding="utf-8")
)
font_policy_diagnostics = diagnose_font_policy(ROOT, profile)
if font_policy_diagnostics:
    for diagnostic in font_policy_diagnostics:
        fail(diagnostic)
else:
    print("ok    deterministic profile font policy artifact pins coherent")

# bbox sanity (schema cannot express x0<=x1, y0<=y1)
def walk_bboxes(label, node, ctx):
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "bbox" and isinstance(v, list) and len(v) == 4:
                x0, y0, x1, y1 = v
                if x0 > x1 or y0 > y1:
                    fail(f"{label}: malformed bbox {v} at {ctx}.{k}")
            else:
                walk_bboxes(label, v, f"{ctx}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk_bboxes(label, v, f"{ctx}[{i}]")


walk_bboxes("document.example.json", p, "payload")
walk_bboxes("crop-descriptor.example.json", crop, "root")

if failures:
    print(f"\n{failures} failure(s)")
    sys.exit(1)
print("\nAll schema/example checks green.")
