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
from typing import Any, Dict, Mapping, Optional, Sequence, Union

PathLike = Union[str, os.PathLike[str]]

_DOC_PARSE_FORMATS = frozenset(("json", "markdown", "text"))
_DEFAULT_CROP_CHECK_ID = "v0001"


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
        cwd: Optional[PathLike] = None,
        env: Optional[Mapping[str, str]] = None,
    ) -> None:
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

    def _run(
        self,
        command: Sequence[str],
        *,
        timeout_seconds: Optional[float],
    ) -> str:
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
        if completed.returncode != 0:
            raise EthosCommandError(command, completed.returncode, stdout, stderr)
        return stdout


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


def _validate_timeout_seconds(timeout_seconds: Optional[float]) -> None:
    if timeout_seconds is not None and timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be greater than zero when provided")


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


def _decode_utf8(data: bytes, command: Sequence[str], stream: str) -> str:
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise EthosOutputError(
            f"ethos returned non-UTF-8 {stream}",
            command,
            data.decode("utf-8", errors="replace"),
        ) from exc
