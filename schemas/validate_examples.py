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
    ("ethos-security-report.schema.json", [EXAMPLES / "security-report.example.json"]),
    ("ethos-verification-report.schema.json", [
        EXAMPLES / "verification-report.example.json",
        EXAMPLES / "verification-report-negative.example.json",
    ]),
    ("ethos-verification-config.schema.json", [EXAMPLES / "verification-config.example.json"]),
    ("ethos-crop-descriptor.schema.json", [EXAMPLES / "crop-descriptor.example.json"]),
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
    for c in t["cells"]:
        for r in c.get("element_refs", []):
            check_ref("element", r, f"table {t['id']} cell ({c['row']},{c['col']})")
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

# --- derivability: chunks.example.jsonl must be EXACTLY what `ethos rag chunk` derives
# from document.example.json (PRD §7: every derived artifact is reproducible from the
# canonical JSON + config). Catches drift between examples (P2 reviewer finding).
def c14n_line(v) -> str:
    return json.dumps(v, separators=(",", ":"), sort_keys=True, ensure_ascii=False)


wcodes = {w["id"]: w["code"] for w in p["security_warnings"] + p["parser_warnings"]}
expected_lines = []
for ch in p["chunks"]:
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

# fingerprint coherence across example artifacts
sec = json.loads((EXAMPLES / "security-report.example.json").read_text(encoding="utf-8"))
ver = json.loads((EXAMPLES / "verification-report.example.json").read_text(encoding="utf-8"))
crop = json.loads((EXAMPLES / "crop-descriptor.example.json").read_text(encoding="utf-8"))
for label, got in [
    ("security-report.document_fingerprint", sec["document_fingerprint"]),
    ("security-report.source_fingerprint", sec["source_fingerprint"]),
    ("verification-report.document_fingerprint", ver["document_fingerprint"]),
    ("crop-descriptor.document_fingerprint", crop["document_fingerprint"]),
]:
    want = doc["source"]["fingerprint"] if label.endswith("source_fingerprint") else doc["fingerprint"]
    if got != want:
        fail(f"{label} diverges from document example")
print("ok    example fingerprints coherent across artifacts")

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
