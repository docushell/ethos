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

"""Public Python API for local Ethos CLI operations."""

from ._cli import (
    EthosCli,
    EthosCommandError,
    CorruptPdfError,
    EthosNotFoundError,
    EthosOutputError,
    EthosPythonSurfaceError,
    EthosTimeoutError,
    InvalidPdfError,
    ParseTimeoutError,
    PdfiumNotFoundError,
    anchor,
    app_answer_release_decision,
    crop_element,
    parse_pdf_json,
    parse_pdf_markdown,
    parse_pdf_text,
    proof_summary,
    verify,
)
from .emit import (
    CitationEmissionError,
    build_citation_emission,
    build_evidence_citation_emission,
    build_evidence_handle_context,
    build_langchain_context,
    build_llamaindex_context,
    citation_json_bytes,
    emit_langchain_citations,
    emit_llamaindex_citations,
    hydrate_citations,
    hydrate_evidence_citations,
    project_evidence_states,
)

__version__ = "0.6.0"

__all__ = [
    "EthosCli",
    "EthosCommandError",
    "CorruptPdfError",
    "EthosNotFoundError",
    "EthosOutputError",
    "EthosPythonSurfaceError",
    "EthosTimeoutError",
    "InvalidPdfError",
    "ParseTimeoutError",
    "PdfiumNotFoundError",
    "CitationEmissionError",
    "anchor",
    "app_answer_release_decision",
    "build_citation_emission",
    "build_evidence_citation_emission",
    "build_evidence_handle_context",
    "build_langchain_context",
    "build_llamaindex_context",
    "citation_json_bytes",
    "crop_element",
    "emit_langchain_citations",
    "emit_llamaindex_citations",
    "hydrate_citations",
    "hydrate_evidence_citations",
    "project_evidence_states",
    "parse_pdf_json",
    "parse_pdf_markdown",
    "parse_pdf_text",
    "proof_summary",
    "verify",
]
