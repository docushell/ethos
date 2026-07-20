#!/usr/bin/env python3
"""Generate the deterministic NIP-3.1 synthetic trust corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


SCHEMA_VERSION = "1.0.0"
PROFILE_ID = "ethos-deterministic-v1"
PROFILE_SHA256 = "d6145b9210845db39ad592ea549788432b52a649778c9947f5b2d91173e38070"
CONFIG_SHA256 = "68cc61753d299917cc7773f069c18aca31c8ac68f43736a94cb57eee05144084"
CATEGORIES = (
    "grounded",
    "fabricated-quote",
    "wrong-page",
    "paraphrase-drift",
    "split-quote",
    "stale-fingerprint",
    "capability-limited",
)


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def pdf_string(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def make_pdf(number: int, exact: str, split_a: str, split_b: str, second_page: str) -> bytes:
    streams = [
        (
            "BT /F1 12 Tf 72 720 Td "
            f"({pdf_string(exact)}) Tj 0 -28 Td "
            f"({pdf_string(split_a)}) Tj "
            f"({pdf_string(split_b)}) Tj ET\n"
        ).encode(),
        f"BT /F1 12 Tf 72 720 Td ({pdf_string(second_page)}) Tj ET\n".encode(),
    ]
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R 4 0 R] /Count 2 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 5 0 R >> >> /Contents 6 0 R >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 5 0 R >> >> /Contents 7 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length %d >>\nstream\n%sstream-end-placeholder" % (len(streams[0]), streams[0]),
        b"<< /Length %d >>\nstream\n%sstream-end-placeholder" % (len(streams[1]), streams[1]),
    ]
    objects[5] = objects[5].replace(b"stream-end-placeholder", b"endstream")
    objects[6] = objects[6].replace(b"stream-end-placeholder", b"endstream")
    output = bytearray(b"%%PDF-1.4\n%%\xe2\xe3\xcf\xd3\n%% Ethos synthetic trust benchmark %02d\n" % number)
    offsets = [0]
    for object_id, body in enumerate(objects, 1):
        offsets.append(len(output))
        output.extend(f"{object_id} 0 obj\n".encode())
        output.extend(body)
        output.extend(b"\nendobj\n")
    xref = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode())
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode())
    output.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    )
    return bytes(output)


def without_geometry(value: object) -> object:
    if isinstance(value, dict):
        return {key: without_geometry(item) for key, item in value.items() if key not in {"bbox", "bboxes"}}
    if isinstance(value, list):
        return [without_geometry(item) for item in value]
    return value


def make_document(number: int, pdf: bytes, exact: str, split_a: str, split_b: str, second_page: str) -> dict:
    texts = (exact, split_a, split_b, second_page)
    pages = [
        {"height": 79200, "id": "p0001", "index": 1, "rotation": 0, "width": 61200},
        {"height": 79200, "id": "p0002", "index": 2, "rotation": 0, "width": 61200},
    ]
    boxes = ([7200, 7200, 54000, 8600], [7200, 10000, 26000, 11400], [26000, 10000, 54000, 11400], [7200, 7200, 54000, 8600])
    elements = []
    spans = []
    for index, (text, box) in enumerate(zip(texts, boxes), 1):
        page = "p0002" if index == 4 else "p0001"
        element_id = f"e{index:06d}"
        span_id = f"s{index:06d}"
        elements.append({
            "bbox": list(box), "id": element_id, "page": page,
            "span_refs": [span_id], "text": text, "type": "text_block",
        })
        spans.append({
            "bbox": list(box), "char_end": len(text), "char_start": 0,
            "font_id": "embedded:Helvetica", "font_size_q": 1200,
            "id": span_id, "page": page, "text": text,
        })
    payload = {
        "chunks": [],
        "coordinate_system": {"origin": "top-left", "quantum_per_point": 100, "unit": "quantum"},
        "elements": elements,
        "pages": pages,
        "parser_warnings": [],
        "regions": [],
        "security_warnings": [],
        "spans": spans,
        "tables": [],
    }
    payload_sha = sha256(canonical_bytes(without_geometry(payload)))
    source_fingerprint = f"sha256:{sha256(pdf)}"
    manifest = {
        "config_sha256": CONFIG_SHA256,
        "payload_sha256": payload_sha,
        "profile_id": PROFILE_ID,
        "profile_sha256": PROFILE_SHA256,
        "schema_version": SCHEMA_VERSION,
        "source_fingerprint": source_fingerprint,
    }
    return {
        "config_sha256": CONFIG_SHA256,
        "fingerprint": f"sha256:{sha256(canonical_bytes(manifest))}",
        "parser": {"name": "ethos", "version": "0.3.0"},
        "payload": payload,
        "payload_sha256": payload_sha,
        "profile": {"id": PROFILE_ID, "sha256": PROFILE_SHA256},
        "schema_version": SCHEMA_VERSION,
        "source": {"bytes": len(pdf), "fingerprint": source_fingerprint},
    }


def claim(category: str, kind: str, text: str | None, citation: dict, status: str, reason: str | None = None) -> dict:
    value = {
        "category": category,
        "citation": citation,
        "expected_reason": reason,
        "expected_status": status,
        "kind": kind,
    }
    if text is not None:
        value["text"] = text
    return value


def make_checks(number: int, exact: str, split_a: str, split_b: str, second_page: str) -> list[dict]:
    split = split_a + split_b
    return [
        claim("grounded", "quote", exact, {"element_id": "e000001"}, "grounded"),
        claim("grounded", "presence", None, {"element_id": "e000004"}, "grounded"),
        claim("fabricated-quote", "quote", f"Document {number:02d} states that lunar revenue doubled.", {"element_id": "e000001"}, "mismatch", "text_mismatch"),
        claim("wrong-page", "quote", exact, {"page": "p0002"}, "mismatch", "text_mismatch"),
        claim("paraphrase-drift", "quote", f"Record {number:02d} approves deterministic evidence checks.", {"element_id": "e000001"}, "mismatch", "text_mismatch"),
        claim("paraphrase-drift", "value", f"secondary value {number + 100}", {"element_id": "e000004"}, "mismatch", "text_mismatch"),
        claim("split-quote", "quote", split, {"element_id": "e000002"}, "grounded"),
        claim("split-quote", "quote", split, {"element_id": "e000003"}, "grounded"),
        claim("stale-fingerprint", "quote", exact, {"element_id": "e000001"}, "stale", "stale_fingerprint"),
        claim("capability-limited", "quote", second_page, {"element_id": "e000004"}, "grounded"),
    ]


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value) + b"\n")


def generate(output: Path) -> None:
    documents = []
    for number in range(1, 21):
        doc_id = f"synthetic-{number:02d}"
        exact = f"Ethos record {number:02d} requires deterministic citation evidence."
        split_a = f"Split record {number:02d} joins "
        split_b = "adjacent born-digital text."
        second_page = f"Secondary value {number:02d} is independently citable."
        pdf = make_pdf(number, exact, split_a, split_b, second_page)
        document = make_document(number, pdf, exact, split_a, split_b, second_page)
        directory = output / "documents" / doc_id
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "document.pdf").write_bytes(pdf)
        write_json(directory / "ethos.json", document)
        documents.append({
            "checks": make_checks(number, exact, split_a, split_b, second_page),
            "document_fingerprint": document["fingerprint"],
            "id": doc_id,
            "license": "Apache-2.0",
            "page_count": 2,
            "pdf_sha256": sha256(pdf),
            "provenance": "Ethos-authored deterministic synthetic born-digital PDF",
            "source": f"documents/{doc_id}/ethos.json",
            "source_pdf": f"documents/{doc_id}/document.pdf",
        })
    write_json(output / "manifest.json", {
        "categories": list(CATEGORIES),
        "check_count": 200,
        "corpus_id": "ethos-synthetic-trust-v1",
        "document_count": 20,
        "documents": documents,
        "schema_version": "1.0.0",
        "warning": "Ethos-authored synthetic corpus; not a neutral benchmark suite.",
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    generate(args.output)


if __name__ == "__main__":
    main()
