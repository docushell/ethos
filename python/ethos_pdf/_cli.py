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
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Sequence, Type, Union

PathLike = Union[str, os.PathLike[str]]

_DOC_PARSE_FORMATS = frozenset(("json", "markdown", "text"))
_DEFAULT_CROP_CHECK_ID = "v0001"
_CAPABILITY_LIMITED = "capability_limited"
_GROUNDED = "grounded"
_ANSWER_RELEVANT = frozenset(("direct_answer", "supports_answer"))
_ANSWER_IRRELEVANT = frozenset(("background_only", "unrelated"))
_QUESTION_RELEVANCE = _ANSWER_RELEVANT | _ANSWER_IRRELEVANT
_CLAIM_TYPES = frozenset(("source_fact", "synthesis", "unsupported"))
_PROOF_STATUSES = frozenset(("verified", "partially_verified", "unverified"))
_PROOF_LIMITATIONS = frozenset(
    (
        "capability_limited",
        "stale_fingerprint",
        "unsupported_claim_kind",
        "non_grounded_checks",
        "semantic_unverified",
    )
)


class EthosPythonSurfaceError(Exception):
    """Base class for Python surface errors."""


class EthosNotFoundError(EthosPythonSurfaceError):
    """Raised when the configured local ethos binary cannot be executed."""

    def __init__(self, ethos_bin: str) -> None:
        super().__init__(f"ethos binary not found: {ethos_bin}")
        self.ethos_bin = ethos_bin


class EthosTimeoutError(EthosPythonSurfaceError):
    """Raised when the local ethos command exceeds the caller's timeout."""

    def __init__(self, command: Sequence[str], timeout_seconds: float) -> None:
        super().__init__(
            f"ethos command timed out after {timeout_seconds:g}s: {' '.join(command)}"
        )
        self.command = tuple(command)
        self.timeout_seconds = timeout_seconds


class EthosCommandError(EthosPythonSurfaceError):
    """Raised when the local ethos command exits non-zero."""

    def __init__(
        self,
        command: Sequence[str],
        returncode: int,
        stdout: str,
        stderr: str,
    ) -> None:
        super().__init__(
            f"ethos command exited {returncode}: {' '.join(command)}"
        )
        self.command = tuple(command)
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class PdfiumNotFoundError(EthosCommandError):
    """Raised when the CLI reports missing caller-provided PDFium."""


class InvalidPdfError(EthosCommandError):
    """Raised when the CLI reports `invalid_pdf`."""


class CorruptPdfError(EthosCommandError):
    """Raised when the CLI reports `corrupt_pdf`."""


class ParseTimeoutError(EthosCommandError):
    """Raised when the CLI reports `parse_timeout`."""


class EthosOutputError(EthosPythonSurfaceError):
    """Raised when a successful local ethos command returns unusable output."""

    def __init__(self, message: str, command: Sequence[str], stdout: str) -> None:
        super().__init__(message)
        self.command = tuple(command)
        self.stdout = stdout


class EthosCli:
    """Small local wrapper around the Ethos CLI.

    The wrapper is deliberately explicit about the binary it runs. It does not
    discover, download, or bundle Ethos; callers provide a local command path or
    rely on their own PATH.
    """

    def __init__(
        self,
        ethos_bin: PathLike = "ethos",
        *,
        binary: Optional[PathLike] = None,
        cwd: Optional[PathLike] = None,
        env: Optional[Mapping[str, str]] = None,
    ) -> None:
        if binary is not None and os.fspath(ethos_bin) != "ethos":
            raise ValueError("provide either ethos_bin or binary, not both")
        if binary is not None:
            ethos_bin = binary
        self.ethos_bin = os.fspath(ethos_bin)
        self.cwd = None if cwd is None else os.fspath(cwd)
        self.env = None if env is None else dict(env)

    def parse_pdf_json(
        self,
        input_pdf: PathLike,
        *,
        pages: Optional[str] = None,
        diagnostics: bool = False,
        timeout_seconds: Optional[float] = None,
    ) -> Any:
        """Parse a PDF and return the canonical JSON value."""

        return self.parse_pdf(
            input_pdf,
            output_format="json",
            pages=pages,
            diagnostics=diagnostics,
            timeout_seconds=timeout_seconds,
        )

    def parse_pdf_markdown(
        self,
        input_pdf: PathLike,
        *,
        pages: Optional[str] = None,
        diagnostics: bool = False,
        timeout_seconds: Optional[float] = None,
    ) -> str:
        """Parse a PDF and return Markdown output as UTF-8 text."""

        return self.parse_pdf(
            input_pdf,
            output_format="markdown",
            pages=pages,
            diagnostics=diagnostics,
            timeout_seconds=timeout_seconds,
        )

    def parse_pdf_text(
        self,
        input_pdf: PathLike,
        *,
        pages: Optional[str] = None,
        diagnostics: bool = False,
        timeout_seconds: Optional[float] = None,
    ) -> str:
        """Parse a PDF and return plain-text output as UTF-8 text."""

        return self.parse_pdf(
            input_pdf,
            output_format="text",
            pages=pages,
            diagnostics=diagnostics,
            timeout_seconds=timeout_seconds,
        )

    def parse_pdf(
        self,
        input_pdf: PathLike,
        *,
        output_format: str = "json",
        pages: Optional[str] = None,
        diagnostics: bool = False,
        timeout_seconds: Optional[float] = None,
    ) -> Any:
        """Run `ethos doc parse` for one local PDF.

        `output_format` must be one of `json`, `markdown`, or `text`. JSON output
        is decoded and returned as a Python value. Markdown and text outputs are
        returned exactly as UTF-8 strings, including the CLI's trailing newline.
        """

        if output_format not in _DOC_PARSE_FORMATS:
            allowed = ", ".join(sorted(_DOC_PARSE_FORMATS))
            raise ValueError(f"output_format must be one of: {allowed}")
        if pages is not None and not pages:
            raise ValueError("pages must be non-empty when provided")
        _validate_timeout_seconds(timeout_seconds)

        pdf_path = _existing_file_path(input_pdf)

        command = self._doc_parse_command(
            pdf_path,
            output_format=output_format,
            pages=pages,
            diagnostics=diagnostics,
        )
        stdout = self._run(command, timeout_seconds=timeout_seconds)
        if output_format == "json":
            return _load_json_stdout(stdout, command)
        return stdout

    def crop_element(
        self,
        input_document: PathLike,
        request: PathLike,
        *,
        check_id: str = _DEFAULT_CROP_CHECK_ID,
        crop_source_pdf: Optional[PathLike] = None,
        crop_dir: Optional[PathLike] = None,
        timeout_seconds: Optional[float] = None,
    ) -> Any:
        """Run `ethos crop_element` for one native document element."""

        if not check_id:
            raise ValueError("check_id must be non-empty")
        if (crop_source_pdf is None) != (crop_dir is None):
            raise ValueError("crop_source_pdf and crop_dir must be provided together")
        _validate_timeout_seconds(timeout_seconds)

        document_path = _existing_file_path(input_document)
        request_path = _existing_file_path(request)
        source_pdf_path = (
            None if crop_source_pdf is None else _existing_file_path(crop_source_pdf)
        )
        crop_dir_path = None if crop_dir is None else Path(crop_dir)

        command = self._crop_element_command(
            document_path,
            request_path,
            check_id=check_id,
            crop_source_pdf=source_pdf_path,
            crop_dir=crop_dir_path,
        )
        stdout = self._run(command, timeout_seconds=timeout_seconds)
        return _load_json_stdout(stdout, command)

    def verify(
        self,
        source: PathLike,
        *,
        citations: PathLike,
        grounding: Optional[str] = None,
        config: Optional[PathLike] = None,
        fail_on_ungrounded: bool = False,
        output_format: str = "json",
        timeout: Optional[float] = 30.0,
    ) -> Any:
        """Run `ethos verify` and return the JSON verification report.

        This wrapper intentionally supports JSON output only. Missing source,
        citations, or config paths raise the built-in `FileNotFoundError`
        before invoking the CLI.

        A verify exit code of `1` is a normal enforcement verdict when
        `--fail-on-ungrounded` was requested and the CLI still writes a JSON
        report. Usage, IO, malformed input, and infrastructure failures still
        raise `EthosCommandError` or a more specific subclass.
        """

        if output_format != "json":
            raise ValueError("output_format must be 'json'")
        _validate_optional_adapter_id(grounding)
        _validate_timeout_seconds(timeout)

        source_path = _existing_file_path(source)
        citations_path = _existing_file_path(citations)
        config_path = None if config is None else _existing_file_path(config)

        command = self._verify_command(
            source_path,
            citations_path,
            grounding=grounding,
            config=config_path,
            fail_on_ungrounded=fail_on_ungrounded,
            output_format=output_format,
        )
        return self._run_json_report(
            command,
            timeout_seconds=timeout,
            report_returncodes={0, 1} if fail_on_ungrounded else {0},
        )

    def anchor(
        self,
        source: PathLike,
        *,
        evidence_refs: PathLike,
        grounding: Optional[str] = None,
        output_format: str = "json",
        timeout: Optional[float] = 30.0,
    ) -> Any:
        """Run `ethos evidence anchor` and return the JSON anchor report.

        This wrapper intentionally supports JSON output only. Missing source or
        evidence-ref paths raise the built-in `FileNotFoundError` before
        invoking the CLI.
        """

        if output_format != "json":
            raise ValueError("output_format must be 'json'")
        _validate_optional_adapter_id(grounding)
        _validate_timeout_seconds(timeout)

        source_path = _existing_file_path(source)
        evidence_refs_path = _existing_file_path(evidence_refs)

        command = self._anchor_command(
            source_path,
            evidence_refs_path,
            grounding=grounding,
        )
        return self._run_json_report(
            command,
            timeout_seconds=timeout,
            report_returncodes={0},
        )

    def _doc_parse_command(
        self,
        pdf_path: Path,
        *,
        output_format: str,
        pages: Optional[str],
        diagnostics: bool,
    ) -> Sequence[str]:
        command = [
            self.ethos_bin,
            "doc",
            "parse",
            os.fspath(pdf_path),
            "--format",
            output_format,
        ]
        if pages is not None:
            command.extend(["--pages", pages])
        if diagnostics:
            command.append("--diagnostics")
        return tuple(command)

    def _crop_element_command(
        self,
        document_path: Path,
        request_path: Path,
        *,
        check_id: str,
        crop_source_pdf: Optional[Path],
        crop_dir: Optional[Path],
    ) -> Sequence[str]:
        command = [
            self.ethos_bin,
            "crop_element",
            os.fspath(document_path),
            "--request",
            os.fspath(request_path),
            "--check-id",
            check_id,
        ]
        if crop_source_pdf is not None and crop_dir is not None:
            command.extend(
                [
                    "--crop-source-pdf",
                    os.fspath(crop_source_pdf),
                    "--crop-dir",
                    os.fspath(crop_dir),
                ]
            )
        return tuple(command)

    def _verify_command(
        self,
        source_path: Path,
        citations_path: Path,
        *,
        grounding: Optional[str],
        config: Optional[Path],
        fail_on_ungrounded: bool,
        output_format: str,
    ) -> Sequence[str]:
        command = [
            self.ethos_bin,
            "verify",
            os.fspath(source_path),
            "--citations",
            os.fspath(citations_path),
        ]
        if grounding is not None:
            command.extend(["--grounding", grounding])
        if config is not None:
            command.extend(["--config", os.fspath(config)])
        if fail_on_ungrounded:
            command.append("--fail-on-ungrounded")
        command.extend(["--format", output_format])
        return tuple(command)

    def _anchor_command(
        self,
        source_path: Path,
        evidence_refs_path: Path,
        *,
        grounding: Optional[str],
    ) -> Sequence[str]:
        command = [
            self.ethos_bin,
            "evidence",
            "anchor",
            os.fspath(source_path),
            "--evidence-refs",
            os.fspath(evidence_refs_path),
        ]
        if grounding is not None:
            command.extend(["--grounding", grounding])
        return tuple(command)

    def _run(
        self,
        command: Sequence[str],
        *,
        timeout_seconds: Optional[float],
    ) -> str:
        returncode, stdout, stderr = self._run_completed(
            command,
            timeout_seconds=timeout_seconds,
        )
        if returncode != 0:
            error_class = _command_error_class(returncode, stderr)
            raise error_class(command, returncode, stdout, stderr)
        return stdout

    def _run_json_report(
        self,
        command: Sequence[str],
        *,
        timeout_seconds: Optional[float],
        report_returncodes: set[int],
    ) -> Any:
        returncode, stdout, stderr = self._run_completed(
            command,
            timeout_seconds=timeout_seconds,
        )
        if returncode not in report_returncodes:
            error_class = _command_error_class(returncode, stderr)
            raise error_class(command, returncode, stdout, stderr)
        if returncode != 0 and not stdout.strip():
            error_class = _command_error_class(returncode, stderr)
            raise error_class(command, returncode, stdout, stderr)
        return _load_json_stdout(stdout, command)

    def _run_completed(
        self,
        command: Sequence[str],
        *,
        timeout_seconds: Optional[float],
    ) -> tuple[int, str, str]:
        run_env: Optional[Dict[str, str]] = None
        if self.env is not None:
            run_env = dict(os.environ)
            run_env.update(self.env)

        try:
            completed = subprocess.run(
                command,
                cwd=self.cwd,
                env=run_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=timeout_seconds,
            )
        except FileNotFoundError as exc:
            raise EthosNotFoundError(self.ethos_bin) from exc
        except subprocess.TimeoutExpired as exc:
            timeout = timeout_seconds if timeout_seconds is not None else 0.0
            raise EthosTimeoutError(command, timeout) from exc

        stdout = _decode_utf8(completed.stdout, command, "stdout")
        stderr = _decode_utf8(completed.stderr, command, "stderr")
        return completed.returncode, stdout, stderr


def parse_pdf_json(
    input_pdf: PathLike,
    *,
    ethos_bin: PathLike = "ethos",
    pages: Optional[str] = None,
    diagnostics: bool = False,
    timeout_seconds: Optional[float] = None,
    env: Optional[Mapping[str, str]] = None,
) -> Any:
    """Parse a PDF through a local ethos binary and return JSON."""

    return EthosCli(ethos_bin, env=env).parse_pdf_json(
        input_pdf,
        pages=pages,
        diagnostics=diagnostics,
        timeout_seconds=timeout_seconds,
    )


def parse_pdf_markdown(
    input_pdf: PathLike,
    *,
    ethos_bin: PathLike = "ethos",
    pages: Optional[str] = None,
    diagnostics: bool = False,
    timeout_seconds: Optional[float] = None,
    env: Optional[Mapping[str, str]] = None,
) -> str:
    """Parse a PDF through a local ethos binary and return Markdown."""

    return EthosCli(ethos_bin, env=env).parse_pdf_markdown(
        input_pdf,
        pages=pages,
        diagnostics=diagnostics,
        timeout_seconds=timeout_seconds,
    )


def parse_pdf_text(
    input_pdf: PathLike,
    *,
    ethos_bin: PathLike = "ethos",
    pages: Optional[str] = None,
    diagnostics: bool = False,
    timeout_seconds: Optional[float] = None,
    env: Optional[Mapping[str, str]] = None,
) -> str:
    """Parse a PDF through a local ethos binary and return plain text."""

    return EthosCli(ethos_bin, env=env).parse_pdf_text(
        input_pdf,
        pages=pages,
        diagnostics=diagnostics,
        timeout_seconds=timeout_seconds,
    )


def crop_element(
    input_document: PathLike,
    request: PathLike,
    *,
    ethos_bin: PathLike = "ethos",
    check_id: str = _DEFAULT_CROP_CHECK_ID,
    crop_source_pdf: Optional[PathLike] = None,
    crop_dir: Optional[PathLike] = None,
    timeout_seconds: Optional[float] = None,
    env: Optional[Mapping[str, str]] = None,
) -> Any:
    """Resolve a crop element through a local ethos binary."""

    return EthosCli(ethos_bin, env=env).crop_element(
        input_document,
        request,
        check_id=check_id,
        crop_source_pdf=crop_source_pdf,
        crop_dir=crop_dir,
        timeout_seconds=timeout_seconds,
    )


def verify(
    source: PathLike,
    *,
    citations: PathLike,
    ethos_bin: PathLike = "ethos",
    grounding: Optional[str] = None,
    config: Optional[PathLike] = None,
    fail_on_ungrounded: bool = False,
    output_format: str = "json",
    timeout: Optional[float] = 30.0,
    env: Optional[Mapping[str, str]] = None,
) -> Any:
    """Verify citations through a local ethos binary and return JSON.

    Missing source, citations, or config paths raise the built-in
    `FileNotFoundError` before invoking the CLI.
    """

    return EthosCli(ethos_bin, env=env).verify(
        source,
        citations=citations,
        grounding=grounding,
        config=config,
        fail_on_ungrounded=fail_on_ungrounded,
        output_format=output_format,
        timeout=timeout,
    )


def anchor(
    source: PathLike,
    *,
    evidence_refs: PathLike,
    ethos_bin: PathLike = "ethos",
    grounding: Optional[str] = None,
    output_format: str = "json",
    timeout: Optional[float] = 30.0,
    env: Optional[Mapping[str, str]] = None,
) -> Any:
    """Anchor evidence refs through a local ethos binary and return JSON.

    Missing source or evidence-ref paths raise the built-in `FileNotFoundError`
    before invoking the CLI.
    """

    return EthosCli(ethos_bin, env=env).anchor(
        source,
        evidence_refs=evidence_refs,
        grounding=grounding,
        output_format=output_format,
        timeout=timeout,
    )


def proof_summary(report: Mapping[str, Any]) -> Dict[str, Any]:
    """Derive product-facing proof status from a verification report.

    This mirrors the Rust `VerificationReport::proof_summary()` helper without
    changing the canonical JSON report. `request_certified` mirrors
    `all_evidence_grounded`; reusable grounded checks exclude report-level stale
    fingerprints and claim-level `semantic_unverified` cases.
    """

    checks = _list_value(report.get("checks"))
    fingerprint_stale = bool(report.get("fingerprint_stale", False))
    reusable_grounded_check_ids = []
    needs_review_check_ids = []

    for check in checks:
        if not isinstance(check, Mapping):
            continue
        check_id = check.get("id")
        if not isinstance(check_id, str):
            continue
        if _is_reusable_grounded_check(check, fingerprint_stale):
            reusable_grounded_check_ids.append(check_id)
        else:
            needs_review_check_ids.append(check_id)

    request_certified = bool(report.get("all_evidence_grounded", False))
    if request_certified:
        status = "verified"
    elif reusable_grounded_check_ids:
        status = "partially_verified"
    else:
        status = "unverified"

    limitations = []
    if _has_capability_limit(report, checks):
        limitations.append(_CAPABILITY_LIMITED)
    if fingerprint_stale:
        limitations.append("stale_fingerprint")
    if _list_value(report.get("unsupported_claim_kinds")):
        limitations.append("unsupported_claim_kind")
    if any(
        isinstance(check, Mapping) and check.get("status") != _GROUNDED
        for check in checks
    ):
        limitations.append("non_grounded_checks")
    if any(
        isinstance(check, Mapping) and bool(check.get("semantic_unverified", False))
        for check in checks
    ):
        limitations.append("semantic_unverified")

    return {
        "proof_status": status,
        "request_certified": request_certified,
        "reusable_grounded_check_ids": reusable_grounded_check_ids,
        "needs_review_check_ids": needs_review_check_ids,
        "proof_limitations": limitations,
    }


def app_answer_release_decision(
    question: str,
    proof: Mapping[str, Any],
    claims: Sequence[Mapping[str, Any]],
    *,
    verification_report_ref: str = "verification_report.json",
    notes: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    """Build a non-canonical app answer release decision envelope.

    The caller owns `question_relevance` and `claim_type` labels. This helper
    only applies the app-release policy from
    `docs/app-answer-release-contract.md` against an Ethos proof summary or a
    canonical verification report. It never judges relevance or synthesis by
    itself.
    """

    if not isinstance(question, str) or not question.strip():
        raise ValueError("question must be a non-empty string")
    if not isinstance(verification_report_ref, str) or not verification_report_ref:
        raise ValueError("verification_report_ref must be a non-empty string")
    if not isinstance(claims, Sequence) or isinstance(claims, (str, bytes)):
        raise ValueError("claims must be a sequence of mappings")

    grounding = _coerce_proof_summary(proof)
    reusable = set(grounding["reusable_grounded_check_ids"])
    needs_review = set(grounding["needs_review_check_ids"])

    decisions = [
        _app_claim_decision(claim, reusable, needs_review)
        for claim in claims
    ]
    final_ids = [
        claim["id"] for claim in decisions if claim["release_action"] == "show_final"
    ]
    review_ids = [
        claim["id"] for claim in decisions if claim["release_action"] == "needs_review"
    ]
    blocked_ids = [
        claim["id"] for claim in decisions if claim["release_action"] == "block"
    ]

    envelope: Dict[str, Any] = {
        "artifact_type": "ethos.app_answer_release_decision.v1",
        "schema_version": "1.0.0",
        "question": question,
        "grounding": {
            "verification_report_ref": verification_report_ref,
            **grounding,
        },
        "app_status": _app_status(decisions),
        "claims": decisions,
        "final_answer_claim_ids": final_ids,
        "review_claim_ids": review_ids,
        "blocked_claim_ids": blocked_ids,
    }
    if notes is not None:
        envelope["notes"] = _string_list(notes, "notes")
    return envelope


def _validate_timeout_seconds(timeout_seconds: Optional[float]) -> None:
    if timeout_seconds is not None and timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be greater than zero when provided")


def _validate_optional_adapter_id(adapter_id: Optional[str]) -> None:
    if adapter_id is not None and not adapter_id:
        raise ValueError("grounding must be non-empty when provided")


def _existing_file_path(path: PathLike) -> Path:
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(os.fspath(path))
    return file_path


def _load_json_stdout(stdout: str, command: Sequence[str]) -> Any:
    try:
        return json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise EthosOutputError(
            f"ethos returned invalid JSON: {exc.msg}",
            command,
            stdout,
        ) from exc


def _is_reusable_grounded_check(
    check: Mapping[str, Any], fingerprint_stale: bool
) -> bool:
    return (
        not fingerprint_stale
        and check.get("status") == _GROUNDED
        and not bool(check.get("semantic_unverified", False))
    )


def _has_capability_limit(
    report: Mapping[str, Any], checks: Sequence[Any]
) -> bool:
    if _list_value(report.get("capability_limits")):
        return True
    if _CAPABILITY_LIMITED in _list_value(report.get("warnings")):
        return True
    return any(
        isinstance(check, Mapping)
        and _CAPABILITY_LIMITED in _list_value(check.get("warnings"))
        for check in checks
    )


def _coerce_proof_summary(proof: Mapping[str, Any]) -> Dict[str, Any]:
    if not isinstance(proof, Mapping):
        raise ValueError("proof must be a verification report or proof summary mapping")
    if "proof_status" not in proof and "all_evidence_grounded" in proof:
        proof = proof_summary(proof)

    status = proof.get("proof_status")
    if status not in _PROOF_STATUSES:
        raise ValueError("proof_status must be verified, partially_verified, or unverified")
    request_certified = proof.get("request_certified")
    if not isinstance(request_certified, bool):
        raise ValueError("request_certified must be a boolean")
    reusable = _string_list(
        proof.get("reusable_grounded_check_ids"),
        "reusable_grounded_check_ids",
    )
    needs_review = _string_list(
        proof.get("needs_review_check_ids"),
        "needs_review_check_ids",
    )
    limitations = _string_list(proof.get("proof_limitations"), "proof_limitations")
    unknown_limitations = [
        limitation for limitation in limitations if limitation not in _PROOF_LIMITATIONS
    ]
    if unknown_limitations:
        raise ValueError(f"unknown proof_limitations: {', '.join(unknown_limitations)}")
    return {
        "proof_status": status,
        "request_certified": request_certified,
        "reusable_grounded_check_ids": reusable,
        "needs_review_check_ids": needs_review,
        "proof_limitations": limitations,
    }


def _app_claim_decision(
    claim: Mapping[str, Any],
    reusable_check_ids: set[str],
    needs_review_check_ids: set[str],
) -> Dict[str, Any]:
    if not isinstance(claim, Mapping):
        raise ValueError("each claim must be a mapping")

    claim_id = _required_string(claim, "id")
    text = _required_string(claim, "text")
    relevance = _required_string(claim, "question_relevance")
    if relevance not in _QUESTION_RELEVANCE:
        raise ValueError(f"unknown question_relevance for claim {claim_id}: {relevance}")
    claim_type = _required_string(claim, "claim_type")
    if claim_type not in _CLAIM_TYPES:
        raise ValueError(f"unknown claim_type for claim {claim_id}: {claim_type}")

    check_ids = _claim_check_ids(claim, claim_id)
    citation_grounded = _claim_citation_grounded(
        claim,
        claim_id,
        check_ids,
        reusable_check_ids,
        needs_review_check_ids,
    )
    if claim_type == "unsupported" and citation_grounded:
        raise ValueError(f"unsupported claim {claim_id} cannot be citation_grounded")

    release_action, release_reason = _release_decision(
        citation_grounded,
        relevance,
        claim_type,
    )
    decision: Dict[str, Any] = {
        "id": claim_id,
        "text": text,
        "citation_grounded": citation_grounded,
        "question_relevance": relevance,
        "claim_type": claim_type,
        "release_action": release_action,
        "release_reason": release_reason,
    }
    if check_ids:
        decision["check_ids"] = check_ids
    return decision


def _required_string(value: Mapping[str, Any], field: str) -> str:
    item = value.get(field)
    if not isinstance(item, str) or not item:
        raise ValueError(f"{field} must be a non-empty string")
    return item


def _string_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, (list, tuple)):
        raise ValueError(f"{field} must be a list of strings")
    result = []
    for item in value:
        if not isinstance(item, str) or not item:
            raise ValueError(f"{field} must be a list of non-empty strings")
        result.append(item)
    if len(set(result)) != len(result):
        raise ValueError(f"{field} must not contain duplicates")
    return result


def _claim_check_ids(claim: Mapping[str, Any], claim_id: str) -> list[str]:
    has_check_id = "check_id" in claim
    has_check_ids = "check_ids" in claim
    if has_check_id and has_check_ids:
        raise ValueError(f"claim {claim_id} must use either check_id or check_ids, not both")
    if has_check_id:
        return [_required_string(claim, "check_id")]
    if has_check_ids:
        check_ids = _string_list(claim.get("check_ids"), "check_ids")
        if not check_ids:
            raise ValueError(f"claim {claim_id} check_ids must not be empty")
        return check_ids
    return []


def _claim_citation_grounded(
    claim: Mapping[str, Any],
    claim_id: str,
    check_ids: Sequence[str],
    reusable_check_ids: set[str],
    needs_review_check_ids: set[str],
) -> bool:
    provided = claim.get("citation_grounded")
    if provided is not None and not isinstance(provided, bool):
        raise ValueError(f"citation_grounded for claim {claim_id} must be a boolean")

    if check_ids:
        known = reusable_check_ids | needs_review_check_ids
        unknown = [check_id for check_id in check_ids if check_id not in known]
        if unknown:
            raise ValueError(
                f"claim {claim_id} references unknown check ids: {', '.join(unknown)}"
            )
        computed = all(check_id in reusable_check_ids for check_id in check_ids)
        if provided is not None and provided != computed:
            raise ValueError(
                f"citation_grounded for claim {claim_id} conflicts with proof summary"
            )
        return computed

    if provided is None:
        raise ValueError(
            f"claim {claim_id} without check_id/check_ids must set citation_grounded"
        )
    return provided


def _release_decision(
    citation_grounded: bool,
    relevance: str,
    claim_type: str,
) -> tuple[str, str]:
    if (
        citation_grounded
        and relevance in _ANSWER_RELEVANT
        and claim_type == "source_fact"
    ):
        return "show_final", "certified"
    if (
        citation_grounded
        and relevance in _ANSWER_RELEVANT
        and claim_type == "synthesis"
    ):
        return "needs_review", "supported_synthesis_needs_review"
    if citation_grounded and relevance in _ANSWER_IRRELEVANT:
        return "block", "grounded_but_irrelevant"
    return "block", "cannot_answer_from_sources"


def _app_status(claims: Sequence[Mapping[str, Any]]) -> str:
    has_final = any(claim["release_action"] == "show_final" for claim in claims)
    has_review = any(claim["release_action"] == "needs_review" for claim in claims)
    has_blocked = any(claim["release_action"] == "block" for claim in claims)
    if has_final and not has_review and not has_blocked:
        return "certified"
    if has_final:
        return "partial_certified"
    if has_review:
        return "supported_synthesis_needs_review"
    if any(claim["release_reason"] == "grounded_but_irrelevant" for claim in claims):
        return "grounded_but_irrelevant"
    return "cannot_answer_from_sources"


def _list_value(value: Any) -> Sequence[Any]:
    if isinstance(value, list):
        return value
    return ()


def _decode_utf8(data: bytes, command: Sequence[str], stream: str) -> str:
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise EthosOutputError(
            f"ethos returned non-UTF-8 {stream}",
            command,
            data.decode("utf-8", errors="replace"),
        ) from exc


def _command_error_class(returncode: int, stderr: str) -> Type[EthosCommandError]:
    error_code = _stable_error_code(stderr)
    if error_code == "invalid_pdf":
        return InvalidPdfError
    if error_code == "corrupt_pdf":
        return CorruptPdfError
    if error_code == "parse_timeout":
        return ParseTimeoutError
    if "ETHOS_PDFIUM_LIBRARY_PATH" in stderr or "PDFium not found" in stderr:
        return PdfiumNotFoundError
    return {
        3: InvalidPdfError,
        4: CorruptPdfError,
        10: ParseTimeoutError,
    }.get(returncode, EthosCommandError)


def _stable_error_code(stderr: str) -> Optional[str]:
    try:
        envelope = json.loads(stderr)
    except json.JSONDecodeError:
        return None
    if not isinstance(envelope, dict):
        return None
    error = envelope.get("error")
    if not isinstance(error, dict):
        return None
    code = error.get("code")
    if isinstance(code, str):
        return code
    return None
