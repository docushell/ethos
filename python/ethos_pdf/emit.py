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

"""Pure-Python helpers for citation-emission v1.

The framework adapters are deliberately duck typed. Importing or using this module does not
require LangChain, LlamaIndex, the Ethos CLI, or PDFium.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from typing import Any, Dict, Iterable, List, Optional, Tuple


EMISSION_SCHEMA_VERSION = "1.0.0"
EVIDENCE_HANDLE_CONTEXT_SCHEMA_VERSION = "1.0.0"
EVIDENCE_HANDLE_EMISSION_SCHEMA_VERSION = "2.0.0"
DEFAULT_MAX_CLAIMS = 256
_SOURCE_ID_LIMIT = 256
_CLAIM_KINDS = frozenset(("quote", "value", "presence", "table_cell"))
_FINGERPRINT = re.compile(r"^sha256:[0-9a-f]{64}$")


class CitationEmissionError(ValueError):
    """A stable, fail-closed citation construction or hydration error."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        claim_index: Optional[int] = None,
        record_index: Optional[int] = None,
    ) -> None:
        self.code = code
        self.claim_index = claim_index
        self.record_index = record_index
        prefix = ""
        if claim_index is not None:
            prefix = f"claim {claim_index}: "
        elif record_index is not None:
            prefix = f"record {record_index}: "
        super().__init__(f"{prefix}{code}: {message}")


def citation_json_bytes(value: Mapping[str, Any]) -> bytes:
    """Serialize an emission or hydrated citation artifact byte-identically."""

    if not isinstance(value, Mapping):
        raise CitationEmissionError("invalid_artifact", "expected a mapping")
    try:
        return (json.dumps(value, ensure_ascii=True, indent=2) + "\n").encode("utf-8")
    except (TypeError, ValueError) as error:
        raise CitationEmissionError("invalid_artifact", str(error)) from error


def build_citation_emission(
    answer: str,
    claims: Iterable[Mapping[str, Any]],
    *,
    max_claims: int = DEFAULT_MAX_CLAIMS,
) -> Dict[str, Any]:
    """Build and validate a citation-emission v1 model/callback artifact."""

    payload = {
        "schema_version": EMISSION_SCHEMA_VERSION,
        "answer": answer,
        "claims": _copy_claims(claims),
    }
    _validate_emission(payload, max_claims=max_claims)
    return payload


def build_langchain_context(documents: Iterable[Any]) -> Dict[str, Any]:
    """Build trusted citation vocabulary from LangChain-style Documents."""

    records = []
    for index, document in enumerate(_materialize_records(documents), 1):
        if isinstance(document, Mapping):
            metadata = document.get("metadata")
        else:
            metadata = getattr(document, "metadata", None)
        records.append(_metadata_mapping(metadata, index))
    return _build_context(records)


def build_llamaindex_context(nodes: Iterable[Any]) -> Dict[str, Any]:
    """Build trusted citation vocabulary from LlamaIndex-style nodes/results."""

    records = []
    for index, result in enumerate(_materialize_records(nodes), 1):
        if isinstance(result, Mapping):
            node = result.get("node", result)
        else:
            node = getattr(result, "node", result)
        if isinstance(node, Mapping):
            metadata = node.get("metadata")
        else:
            metadata = getattr(node, "metadata", None)
        records.append(_metadata_mapping(metadata, index))
    return _build_context(records)


def hydrate_citations(
    emission: Mapping[str, Any],
    context: Mapping[str, Any],
    *,
    max_claims: int = DEFAULT_MAX_CLAIMS,
) -> Dict[str, Any]:
    """Hydrate callback output into ``ethos-citations`` input without guessing."""

    _validate_emission(emission, max_claims=max_claims)
    trusted = _validate_context(context)
    claims = []

    for index, emitted in enumerate(emission["claims"], 1):
        citation: Dict[str, Any] = {}
        page = emitted.get("page")
        if page is not None:
            _require_shown(page, trusted["pages"], "page", index)
            citation["page"] = page

        element_id = emitted.get("element_id")
        if element_id is not None:
            _require_shown(element_id, trusted["elements"], "element_id", index)
            citation["element_id"] = element_id

        span_id = emitted.get("span_id")
        if span_id is not None:
            _require_shown(span_id, trusted["spans"], "span_id", index)
            citation["span_id"] = span_id

        table_id = emitted.get("table_id")
        if table_id is not None:
            cell = emitted["cell"]
            locator = (table_id, cell["row"], cell["col"])
            if locator not in trusted["table_cells"]:
                raise CitationEmissionError(
                    "out_of_vocabulary",
                    f"table_cell {table_id}[{cell['row']},{cell['col']}] was not shown",
                    claim_index=index,
                )
            citation["table_id"] = table_id
            citation["cell"] = {"row": cell["row"], "col": cell["col"]}

        claim = {"kind": emitted["kind"]}
        if "text" in emitted:
            claim["text"] = emitted["text"]
        claim["citation"] = citation
        claims.append(claim)

    return {
        "document_fingerprint": trusted["document_fingerprint"],
        "claims": claims,
    }


def build_evidence_handle_context(records: Iterable[Mapping[str, Any]]) -> Dict[str, Any]:
    """Build a trusted single-document evidence-handle context without locator inference."""
    items = _materialize_records(records)
    fingerprint = None
    evidence = []
    seen = set()
    for index, record in enumerate(items, 1):
        if not isinstance(record, Mapping) or set(record) - {"document_fingerprint", "evidence_id", "locator", "display", "excerpt"}:
            raise CitationEmissionError("invalid_evidence_record", "record fields do not match context v1", record_index=index)
        current = record.get("document_fingerprint")
        _require_nonblank(current, "document_fingerprint", code="missing_document_fingerprint", record_index=index)
        if _FINGERPRINT.fullmatch(current) is None:
            raise CitationEmissionError("invalid_document_fingerprint", "expected sha256 fingerprint", record_index=index)
        if fingerprint is None: fingerprint = current
        elif fingerprint != current: raise CitationEmissionError("mixed_document_fingerprints", "all evidence must name one document", record_index=index)
        evidence_id = record.get("evidence_id")
        _require_source_id(evidence_id, "evidence_id", record_index=index)
        if evidence_id in seen: raise CitationEmissionError("duplicate_evidence_id", "evidence_id must be unique", record_index=index)
        seen.add(evidence_id)
        locator = _validate_handle_locator(record.get("locator"), index)
        item = {"evidence_id": evidence_id, "locator": locator}
        for field, limit in (("display", 512), ("excerpt", 4096)):
            if field in record:
                _require_nonblank(record[field], field, code="invalid_evidence_record", record_index=index)
                if len(record[field]) > limit: raise CitationEmissionError("invalid_evidence_record", f"{field} exceeds {limit} characters", record_index=index)
                item[field] = record[field]
        evidence.append(item)
    if len(evidence) > 1024: raise CitationEmissionError("evidence_limit_exceeded", "received more than 1024 evidence entries")
    return {"artifact_type": "ethos.evidence_handle_context.v1", "schema_version": EVIDENCE_HANDLE_CONTEXT_SCHEMA_VERSION, "document_fingerprint": fingerprint, "evidence": evidence}


def build_evidence_citation_emission(answer: str, claims: Iterable[Mapping[str, Any]]) -> Dict[str, Any]:
    """Build model output v2 whose handles are opaque and non-authoritative until hydration."""
    payload = {"schema_version": EVIDENCE_HANDLE_EMISSION_SCHEMA_VERSION, "answer": answer, "claims": _copy_claims(claims)}
    _validate_handle_emission(payload)
    return payload


def hydrate_evidence_citations(emission: Mapping[str, Any], context: Mapping[str, Any]) -> Dict[str, Any]:
    """Resolve every model handle solely through a validated trusted context."""
    _validate_handle_emission(emission)
    validated = _validate_handle_context(context)
    claims = []
    for index, claim in enumerate(emission["claims"], 1):
        locator = validated.get(claim["evidence_id"])
        if locator is None:
            raise CitationEmissionError("out_of_vocabulary", "evidence_id was not shown", claim_index=index)
        item = {"kind": claim["kind"], "citation": dict(locator)}
        if "text" in claim: item["text"] = claim["text"]
        claims.append(item)
    return {"document_fingerprint": context["document_fingerprint"], "claims": claims}


def project_evidence_states(
    context: Mapping[str, Any], emission: Mapping[str, Any], report: Mapping[str, Any]
) -> Dict[str, Any]:
    """Project noncanonical handle states only from a report bound to trusted hydration."""
    hydrated = hydrate_evidence_citations(emission, context)
    if not isinstance(report, Mapping) or report.get("schema_version") not in {"1.0.0", "1.1.0"}:
        raise CitationEmissionError("unsupported_report", "report schema_version is not supported")
    if report.get("document_fingerprint") != hydrated["document_fingerprint"] or report.get("fingerprint_stale") is not False:
        raise CitationEmissionError("report_context_mismatch", "report fingerprint does not bind the context")
    checks = report.get("checks")
    if not isinstance(checks, list) or len(checks) != len(hydrated["claims"]):
        raise CitationEmissionError("report_context_mismatch", "report checks do not match hydrated claims")
    supported = []
    for index, (check, claim) in enumerate(zip(checks, hydrated["claims"]), 1):
        if not isinstance(check, Mapping) or check.get("id") != f"v{index:04d}" or check.get("claim") != claim:
            raise CitationEmissionError("report_context_mismatch", "report check order or claim differs from hydration")
        if not isinstance(check.get("semantic_unverified"), bool) or not isinstance(check.get("status"), str):
            raise CitationEmissionError("invalid_report", "report check is malformed")
        if check["status"] != "unsupported_claim_kind": supported.append(check)
    recomputed = bool(supported) and all(check["status"] == "grounded" for check in supported) and all(not check["semantic_unverified"] for check in checks) and not report.get("unsupported_claim_kinds", [])
    if report.get("all_evidence_grounded") is not recomputed:
        raise CitationEmissionError("invalid_report", "report all_evidence_grounded is inconsistent")
    by_handle = {entry["evidence_id"]: [] for entry in context["evidence"]}
    for index, (claim, check) in enumerate(zip(emission["claims"], checks), 1):
        by_handle[claim["evidence_id"]].append((index, check))
    states = []
    for entry in context["evidence"]:
        linked = by_handle[entry["evidence_id"]]
        statuses = [check["status"] == "grounded" and not check["semantic_unverified"] for _, check in linked]
        state = "unreferenced" if not linked else "grounded" if all(statuses) else "partially_grounded" if any(statuses) else "ungrounded"
        item = {"evidence_id": entry["evidence_id"], "state": state, "claim_indexes": [index for index, _ in linked], "check_ids": [check["id"] for _, check in linked]}
        if "display" in entry: item["display"] = entry["display"]
        states.append(item)
    return {"document_fingerprint": hydrated["document_fingerprint"], "all_evidence_grounded": recomputed, "states": states}


def emit_langchain_citations(
    documents: Iterable[Any],
    answer: str,
    claims: Iterable[Mapping[str, Any]],
    *,
    max_claims: int = DEFAULT_MAX_CLAIMS,
) -> Dict[str, Any]:
    """Build and hydrate citations using only the supplied LangChain retrieval results."""

    emission = build_citation_emission(answer, claims, max_claims=max_claims)
    return hydrate_citations(
        emission,
        build_langchain_context(documents),
        max_claims=max_claims,
    )


def emit_llamaindex_citations(
    nodes: Iterable[Any],
    answer: str,
    claims: Iterable[Mapping[str, Any]],
    *,
    max_claims: int = DEFAULT_MAX_CLAIMS,
) -> Dict[str, Any]:
    """Build and hydrate citations using only the supplied LlamaIndex retrieval results."""

    emission = build_citation_emission(answer, claims, max_claims=max_claims)
    return hydrate_citations(
        emission,
        build_llamaindex_context(nodes),
        max_claims=max_claims,
    )


def _copy_claims(claims: Iterable[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    if isinstance(claims, (str, bytes, Mapping)):
        raise CitationEmissionError("invalid_claims", "claims must be an iterable of mappings")
    try:
        materialized = list(claims)
    except TypeError as error:
        raise CitationEmissionError("invalid_claims", "claims must be iterable") from error

    copied = []
    for index, claim in enumerate(materialized, 1):
        if not isinstance(claim, Mapping):
            raise CitationEmissionError(
                "invalid_claim", "expected a mapping", claim_index=index
            )
        item = dict(claim)
        if isinstance(item.get("cell"), Mapping):
            item["cell"] = dict(item["cell"])
        copied.append(item)
    return copied


def _validate_emission(emission: Mapping[str, Any], *, max_claims: int) -> None:
    if not isinstance(emission, Mapping):
        raise CitationEmissionError("invalid_emission", "expected a mapping")
    if set(emission) != {"schema_version", "answer", "claims"}:
        raise CitationEmissionError("invalid_emission", "top-level fields do not match v1")
    if emission["schema_version"] != EMISSION_SCHEMA_VERSION:
        raise CitationEmissionError("unsupported_schema_version", "expected 1.0.0")
    _require_nonblank(emission["answer"], "answer", code="invalid_emission")
    if (
        isinstance(max_claims, bool)
        or not isinstance(max_claims, int)
        or not 1 <= max_claims <= 256
    ):
        raise CitationEmissionError("invalid_claim_limit", "max_claims must be in 1..256")
    claims = emission["claims"]
    if not isinstance(claims, list):
        raise CitationEmissionError("invalid_claims", "claims must be an array")
    if not claims:
        raise CitationEmissionError("invalid_claims", "at least one claim is required")
    if len(claims) > max_claims:
        raise CitationEmissionError(
            "claim_limit_exceeded", f"received {len(claims)} claims; limit is {max_claims}"
        )
    for index, claim in enumerate(claims, 1):
        _validate_claim(claim, index)


def _validate_claim(claim: Any, index: int) -> None:
    if not isinstance(claim, Mapping):
        raise CitationEmissionError("invalid_claim", "expected a mapping", claim_index=index)
    kind = claim.get("kind")
    if not isinstance(kind, str) or kind not in _CLAIM_KINDS:
        raise CitationEmissionError("invalid_claim", "unsupported kind", claim_index=index)

    if kind == "table_cell":
        allowed = {"kind", "text", "page", "table_id", "cell"}
        if set(claim) - allowed or not {"kind", "text", "table_id", "cell"} <= set(claim):
            raise CitationEmissionError(
                "invalid_claim", "table_cell fields do not match v1", claim_index=index
            )
        _require_nonblank(claim["text"], "text", claim_index=index)
        _require_source_id(claim["table_id"], "table_id", index)
        if "page" in claim:
            _require_source_id(claim["page"], "page", index)
        cell = claim["cell"]
        if not isinstance(cell, Mapping) or set(cell) != {"row", "col"}:
            raise CitationEmissionError(
                "invalid_claim", "cell must contain only row and col", claim_index=index
            )
        for axis in ("row", "col"):
            value = cell[axis]
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise CitationEmissionError(
                    "invalid_claim",
                    f"cell.{axis} must be a non-negative integer",
                    claim_index=index,
                )
        return

    allowed = {"kind", "page", "element_id", "span_id"}
    if kind in ("quote", "value"):
        allowed.add("text")
        if "text" not in claim:
            raise CitationEmissionError("invalid_claim", "text is required", claim_index=index)
        _require_nonblank(claim["text"], "text", claim_index=index)
    elif "text" in claim:
        raise CitationEmissionError(
            "invalid_claim", "presence must not contain text", claim_index=index
        )
    if set(claim) - allowed:
        raise CitationEmissionError(
            "invalid_claim", "claim contains forbidden fields", claim_index=index
        )
    for field in ("page", "element_id", "span_id"):
        if field in claim:
            _require_source_id(claim[field], field, index)
    primary = sum(field in claim for field in ("element_id", "span_id"))
    if primary > 1:
        raise CitationEmissionError(
            "locator_conflict", "multiple primary locators", claim_index=index
        )
    if primary == 0 and "page" not in claim:
        raise CitationEmissionError("locator_missing", "no source locator", claim_index=index)


def _materialize_records(records: Iterable[Any]) -> List[Any]:
    if isinstance(records, (str, bytes, Mapping)):
        raise CitationEmissionError("invalid_retrieval_results", "expected an iterable of records")
    try:
        materialized = list(records)
    except TypeError as error:
        raise CitationEmissionError(
            "invalid_retrieval_results", "records must be iterable"
        ) from error
    if not materialized:
        raise CitationEmissionError("empty_retrieval_results", "at least one record is required")
    return materialized


def _metadata_mapping(metadata: Any, index: int) -> Mapping[str, Any]:
    if not isinstance(metadata, Mapping):
        raise CitationEmissionError(
            "missing_metadata", "metadata mapping is required", record_index=index
        )
    return metadata


def _build_context(records: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    fingerprint = None
    pages: List[str] = []
    elements: List[str] = []
    spans: List[str] = []
    table_cells: List[Dict[str, Any]] = []
    seen_pages = set()
    seen_elements = set()
    seen_spans = set()
    seen_cells = set()

    for index, metadata in enumerate(records, 1):
        current = metadata.get("document_fingerprint")
        _require_nonblank(
            current,
            "document_fingerprint",
            code="missing_document_fingerprint",
            record_index=index,
        )
        if _FINGERPRINT.fullmatch(current) is None:
            raise CitationEmissionError(
                "invalid_document_fingerprint",
                "expected sha256 followed by 64 lowercase hexadecimal characters",
                record_index=index,
            )
        if fingerprint is None:
            fingerprint = current
        elif current != fingerprint:
            raise CitationEmissionError(
                "mixed_document_fingerprints",
                "all retrieval records must name the same document",
                record_index=index,
            )

        record_locator_count = 0
        record_locator_count += _append_source_ids(
            metadata.get("page_refs", []), "page_refs", pages, seen_pages, index
        )
        record_locator_count += _append_source_ids(
            metadata.get("element_refs", []), "element_refs", elements, seen_elements, index
        )
        record_locator_count += _append_source_ids(
            metadata.get("span_refs", []), "span_refs", spans, seen_spans, index
        )
        record_locator_count += _append_table_cells(
            metadata.get("table_cells", []), table_cells, seen_cells, index
        )
        if record_locator_count == 0:
            raise CitationEmissionError(
                "missing_source_ids",
                "metadata must expose page_refs, element_refs, span_refs, or table_cells",
                record_index=index,
            )

    return {
        "document_fingerprint": fingerprint,
        "pages": pages,
        "elements": elements,
        "spans": spans,
        "table_cells": table_cells,
    }


def _append_source_ids(
    values: Any,
    field: str,
    output: List[str],
    seen: set,
    record_index: int,
) -> int:
    if not isinstance(values, list):
        raise CitationEmissionError(
            "invalid_source_ids", f"{field} must be an array", record_index=record_index
        )
    for value in values:
        _require_source_id(value, field, record_index=record_index)
        if value not in seen:
            seen.add(value)
            output.append(value)
    return len(values)


def _append_table_cells(
    values: Any,
    output: List[Dict[str, Any]],
    seen: set,
    record_index: int,
) -> int:
    if not isinstance(values, list):
        raise CitationEmissionError(
            "invalid_table_cells", "table_cells must be an array", record_index=record_index
        )
    for value in values:
        if not isinstance(value, Mapping) or set(value) != {"table_id", "row", "col"}:
            raise CitationEmissionError(
                "invalid_table_cells",
                "each table cell must contain only table_id, row, and col",
                record_index=record_index,
            )
        _require_source_id(value["table_id"], "table_id", record_index=record_index)
        for axis in ("row", "col"):
            coordinate = value[axis]
            if isinstance(coordinate, bool) or not isinstance(coordinate, int) or coordinate < 0:
                raise CitationEmissionError(
                    "invalid_table_cells",
                    f"{axis} must be a non-negative integer",
                    record_index=record_index,
                )
        locator = (value["table_id"], value["row"], value["col"])
        if locator not in seen:
            seen.add(locator)
            output.append({"table_id": locator[0], "row": locator[1], "col": locator[2]})
    return len(values)


def _validate_context(context: Mapping[str, Any]) -> Dict[str, Any]:
    if not isinstance(context, Mapping):
        raise CitationEmissionError("invalid_context", "expected a mapping")
    if set(context) != {"document_fingerprint", "pages", "elements", "spans", "table_cells"}:
        raise CitationEmissionError("invalid_context", "context fields do not match v1")
    fingerprint = context["document_fingerprint"]
    _require_nonblank(fingerprint, "document_fingerprint", code="missing_document_fingerprint")
    if _FINGERPRINT.fullmatch(fingerprint) is None:
        raise CitationEmissionError(
            "invalid_document_fingerprint",
            "expected sha256 followed by 64 lowercase hexadecimal characters",
        )
    normalized = _build_context([
        {
            "document_fingerprint": fingerprint,
            "page_refs": context["pages"],
            "element_refs": context["elements"],
            "span_refs": context["spans"],
            "table_cells": context["table_cells"],
        }
    ])
    return {
        "document_fingerprint": normalized["document_fingerprint"],
        "pages": frozenset(normalized["pages"]),
        "elements": frozenset(normalized["elements"]),
        "spans": frozenset(normalized["spans"]),
        "table_cells": frozenset(
            (cell["table_id"], cell["row"], cell["col"])
            for cell in normalized["table_cells"]
        ),
    }


def _validate_handle_locator(locator: Any, index: int) -> Dict[str, Any]:
    if not isinstance(locator, Mapping): raise CitationEmissionError("invalid_locator", "locator must be a mapping", record_index=index)
    allowed = {"page", "element_id", "span_id", "table_id", "cell"}
    if set(locator) - allowed: raise CitationEmissionError("invalid_locator", "locator contains forbidden fields", record_index=index)
    anchors = ("element_id", "span_id", "table_id")
    primary = sum(field in locator for field in anchors)
    if primary > 1 or (primary == 0 and "page" not in locator): raise CitationEmissionError("invalid_locator", "locator must contain exactly one primary anchor", record_index=index)
    if "table_id" in locator:
        cell = locator.get("cell")
        if not isinstance(cell, Mapping) or set(cell) != {"row", "col"}: raise CitationEmissionError("invalid_locator", "table locator requires cell", record_index=index)
        for axis in ("row", "col"):
            if isinstance(cell[axis], bool) or not isinstance(cell[axis], int) or cell[axis] < 0: raise CitationEmissionError("invalid_locator", f"cell.{axis} must be non-negative", record_index=index)
    elif "cell" in locator: raise CitationEmissionError("invalid_locator", "cell requires table_id", record_index=index)
    for field in ("page", "element_id", "span_id", "table_id"):
        if field in locator: _require_source_id(locator[field], field, record_index=index)
    result = dict(locator)
    if isinstance(result.get("cell"), Mapping): result["cell"] = dict(result["cell"])
    return result


def _validate_handle_context(context: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    if not isinstance(context, Mapping) or set(context) != {"artifact_type", "schema_version", "document_fingerprint", "evidence"}:
        raise CitationEmissionError("invalid_evidence_context", "context fields do not match v1")
    if context["artifact_type"] != "ethos.evidence_handle_context.v1" or context["schema_version"] != EVIDENCE_HANDLE_CONTEXT_SCHEMA_VERSION:
        raise CitationEmissionError("unsupported_schema_version", "expected evidence context 1.0.0")
    rebuilt = build_evidence_handle_context([{**entry, "document_fingerprint": context["document_fingerprint"]} for entry in context["evidence"]])
    return {entry["evidence_id"]: entry["locator"] for entry in rebuilt["evidence"]}


def _validate_handle_emission(emission: Mapping[str, Any]) -> None:
    if not isinstance(emission, Mapping) or set(emission) != {"schema_version", "answer", "claims"} or emission["schema_version"] != EVIDENCE_HANDLE_EMISSION_SCHEMA_VERSION:
        raise CitationEmissionError("unsupported_schema_version", "expected evidence citation output 2.0.0")
    _require_nonblank(emission["answer"], "answer", code="invalid_emission")
    claims = emission["claims"]
    if not isinstance(claims, list) or not 1 <= len(claims) <= DEFAULT_MAX_CLAIMS: raise CitationEmissionError("invalid_claims", "claims must contain 1 to 256 entries")
    for index, claim in enumerate(claims, 1):
        if not isinstance(claim, Mapping) or set(claim) - {"kind", "text", "evidence_id"} or not {"kind", "evidence_id"} <= set(claim):
            raise CitationEmissionError("invalid_claim", "claim fields do not match v2", claim_index=index)
        if claim.get("kind") not in _CLAIM_KINDS: raise CitationEmissionError("invalid_claim", "unsupported kind", claim_index=index)
        _require_source_id(claim.get("evidence_id"), "evidence_id", claim_index=index)
        if claim["kind"] == "presence":
            if "text" in claim: raise CitationEmissionError("invalid_claim", "presence must not contain text", claim_index=index)
        elif "text" not in claim: raise CitationEmissionError("invalid_claim", "text is required", claim_index=index)
        else: _require_nonblank(claim["text"], "text", claim_index=index)


def _require_shown(value: str, vocabulary: frozenset, field: str, claim_index: int) -> None:
    if value not in vocabulary:
        raise CitationEmissionError(
            "out_of_vocabulary", f"{field} {value} was not shown", claim_index=claim_index
        )


def _require_nonblank(
    value: Any,
    field: str,
    *,
    code: str = "invalid_claim",
    claim_index: Optional[int] = None,
    record_index: Optional[int] = None,
) -> None:
    if not isinstance(value, str) or not value.strip():
        raise CitationEmissionError(
            code,
            f"{field} must be a non-blank string",
            claim_index=claim_index,
            record_index=record_index,
        )


def _require_source_id(
    value: Any,
    field: str,
    claim_index: Optional[int] = None,
    *,
    record_index: Optional[int] = None,
) -> None:
    _require_nonblank(
        value,
        field,
        code="invalid_source_id",
        claim_index=claim_index,
        record_index=record_index,
    )
    if len(value) > _SOURCE_ID_LIMIT:
        raise CitationEmissionError(
            "invalid_source_id",
            f"{field} exceeds {_SOURCE_ID_LIMIT} characters",
            claim_index=claim_index,
            record_index=record_index,
        )


__all__ = [
    "CitationEmissionError",
    "build_citation_emission",
    "build_evidence_handle_context",
    "build_evidence_citation_emission",
    "build_langchain_context",
    "build_llamaindex_context",
    "citation_json_bytes",
    "emit_langchain_citations",
    "emit_llamaindex_citations",
    "hydrate_citations",
    "hydrate_evidence_citations",
    "project_evidence_states",
]
