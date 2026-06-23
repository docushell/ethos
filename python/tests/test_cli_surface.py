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

import os
import stat
import tempfile
import textwrap
import unittest
from pathlib import Path

from ethos_pdf import (
    CorruptPdfError,
    EthosCli,
    EthosCommandError,
    EthosNotFoundError,
    EthosOutputError,
    EthosTimeoutError,
    InvalidPdfError,
    ParseTimeoutError,
    PdfiumNotFoundError,
    crop_element,
    parse_pdf_json,
)


FAKE_ETHOS = """\
#!/usr/bin/env python3
import json
import os
import sys
import time

mode = os.environ.get("ETHOS_FAKE_MODE", "ok")
if mode == "fail":
    sys.stdout.write("partial output\\n")
    sys.stderr.write("usage: fake ethos failure\\n")
    raise SystemExit(2)
if mode == "sleep":
    time.sleep(10)
    raise SystemExit(0)
if mode == "invalid-json":
    sys.stdout.write("not-json\\n")
    raise SystemExit(0)
if mode == "missing-pdfium":
    sys.stderr.write(
        "PDFium not found: set ETHOS_PDFIUM_LIBRARY_PATH to the caller-provided PDFium dynamic library path. Run ethos doctor for setup diagnostics, run ethos doctor --require-pdfium after setting it, and see docs/pdfium-manual-setup.md.\\n"
    )
    raise SystemExit(1)
if mode == "invalid-pdf":
    sys.stderr.write("invalid_pdf: not a PDF\\n")
    raise SystemExit(3)
if mode == "invalid-pdf-envelope":
    sys.stderr.write(json.dumps({"error": {"code": "invalid_pdf", "message": "not a PDF"}}) + "\\n")
    raise SystemExit(3)
if mode == "corrupt-pdf":
    sys.stderr.write("corrupt_pdf: broken xref\\n")
    raise SystemExit(4)
if mode == "parse-timeout":
    sys.stderr.write("parse_timeout: parse exceeded wall-time limit\\n")
    raise SystemExit(10)

if sys.argv[1:2] == ["crop_element"]:
    if "--request" not in sys.argv or "--check-id" not in sys.argv:
        sys.stderr.write("missing crop arguments\\n")
        raise SystemExit(2)
    sys.stdout.write(
        json.dumps(
            {
                "artifact_type": "ethos.crop_descriptor.v1",
                "argv": sys.argv[1:],
                "ok": True,
            },
            sort_keys=True,
        )
        + "\\n"
    )
    raise SystemExit(0)

if sys.argv[1:3] != ["doc", "parse"]:
    sys.stderr.write("unexpected command\\n")
    raise SystemExit(2)

output_format = "json"
if "--format" in sys.argv:
    output_format = sys.argv[sys.argv.index("--format") + 1]

if output_format == "json":
    sys.stdout.write(json.dumps({"argv": sys.argv[1:], "ok": True}, sort_keys=True) + "\\n")
elif output_format == "markdown":
    sys.stdout.write("# Alpha\\n\\nTrust loop\\n")
elif output_format == "text":
    sys.stdout.write("Alpha trust loop\\n")
else:
    sys.stderr.write("unsupported format\\n")
    raise SystemExit(2)
"""


class PythonSurfaceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.fake_ethos = self.root / "ethos"
        self.fake_ethos.write_text(textwrap.dedent(FAKE_ETHOS), encoding="utf-8")
        self.fake_ethos.chmod(
            stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP
        )
        self.pdf = self.root / "document.pdf"
        self.pdf.write_bytes(b"%PDF-1.7\n")
        self.document = self.root / "document.ethos.json"
        self.document.write_text("{}", encoding="utf-8")
        self.crop_request = self.root / "crop-request.json"
        self.crop_request.write_text("{}", encoding="utf-8")
        self.crop_source_pdf = self.root / "source.pdf"
        self.crop_source_pdf.write_bytes(b"%PDF-1.7\n")
        self.crop_dir = self.root / "crops"

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_parse_pdf_json_invokes_doc_parse_with_pages_and_diagnostics(self) -> None:
        result = parse_pdf_json(
            self.pdf,
            ethos_bin=self.fake_ethos,
            pages="1-2",
            diagnostics=True,
        )

        self.assertTrue(result["ok"])
        self.assertEqual(
            result["argv"],
            [
                "doc",
                "parse",
                str(self.pdf),
                "--format",
                "json",
                "--pages",
                "1-2",
                "--diagnostics",
            ],
        )

    def test_parse_pdf_text_preserves_cli_stdout(self) -> None:
        result = EthosCli(self.fake_ethos).parse_pdf_text(self.pdf)

        self.assertEqual(result, "Alpha trust loop\n")

    def test_parse_pdf_markdown_preserves_cli_stdout(self) -> None:
        result = EthosCli(self.fake_ethos).parse_pdf_markdown(self.pdf)

        self.assertEqual(result, "# Alpha\n\nTrust loop\n")

    def test_command_failure_raises_with_exit_code_and_streams(self) -> None:
        cli = EthosCli(self.fake_ethos, env={"ETHOS_FAKE_MODE": "fail"})

        with self.assertRaises(EthosCommandError) as caught:
            cli.parse_pdf_json(self.pdf)

        self.assertEqual(caught.exception.returncode, 2)
        self.assertIn("partial output", caught.exception.stdout)
        self.assertIn("fake ethos failure", caught.exception.stderr)

    def test_missing_pdfium_setup_error_is_specific_and_preserves_stderr(self) -> None:
        cli = EthosCli(self.fake_ethos, env={"ETHOS_FAKE_MODE": "missing-pdfium"})

        with self.assertRaises(PdfiumNotFoundError) as caught:
            cli.parse_pdf_json(self.pdf)

        self.assertIsInstance(caught.exception, EthosCommandError)
        self.assertEqual(caught.exception.returncode, 1)
        self.assertIn("PDFium not found", caught.exception.stderr)
        self.assertIn("ETHOS_PDFIUM_LIBRARY_PATH", caught.exception.stderr)
        self.assertIn("ethos doctor", caught.exception.stderr)
        self.assertIn("ethos doctor --require-pdfium", caught.exception.stderr)
        self.assertIn("docs/pdfium-manual-setup.md", caught.exception.stderr)

    def test_invalid_pdf_exit_code_maps_to_specific_exception(self) -> None:
        cli = EthosCli(self.fake_ethos, env={"ETHOS_FAKE_MODE": "invalid-pdf"})

        with self.assertRaises(InvalidPdfError) as caught:
            cli.parse_pdf_json(self.pdf)

        self.assertIsInstance(caught.exception, EthosCommandError)
        self.assertEqual(caught.exception.returncode, 3)

    def test_stable_error_envelope_maps_to_specific_exception(self) -> None:
        cli = EthosCli(self.fake_ethos, env={"ETHOS_FAKE_MODE": "invalid-pdf-envelope"})

        with self.assertRaises(InvalidPdfError) as caught:
            cli.parse_pdf_json(self.pdf)

        self.assertIn('"code": "invalid_pdf"', caught.exception.stderr)

    def test_corrupt_pdf_exit_code_maps_to_specific_exception(self) -> None:
        cli = EthosCli(self.fake_ethos, env={"ETHOS_FAKE_MODE": "corrupt-pdf"})

        with self.assertRaises(CorruptPdfError) as caught:
            cli.parse_pdf_json(self.pdf)

        self.assertEqual(caught.exception.returncode, 4)

    def test_parse_timeout_exit_code_maps_to_specific_exception(self) -> None:
        cli = EthosCli(self.fake_ethos, env={"ETHOS_FAKE_MODE": "parse-timeout"})

        with self.assertRaises(ParseTimeoutError) as caught:
            cli.parse_pdf_json(self.pdf)

        self.assertEqual(caught.exception.returncode, 10)

    def test_missing_binary_raises_not_found(self) -> None:
        cli = EthosCli(self.root / "missing-ethos")

        with self.assertRaises(EthosNotFoundError):
            cli.parse_pdf_json(self.pdf)

    def test_timeout_raises_timeout_error(self) -> None:
        cli = EthosCli(self.fake_ethos, env={"ETHOS_FAKE_MODE": "sleep"})

        with self.assertRaises(EthosTimeoutError):
            cli.parse_pdf_json(self.pdf, timeout_seconds=0.01)

    def test_invalid_format_is_rejected_before_command_execution(self) -> None:
        with self.assertRaises(ValueError):
            EthosCli(self.fake_ethos).parse_pdf(self.pdf, output_format="html")

    def test_empty_pages_is_rejected_before_command_execution(self) -> None:
        with self.assertRaises(ValueError):
            EthosCli(self.fake_ethos).parse_pdf_json(self.pdf, pages="")

    def test_non_positive_timeout_is_rejected_before_command_execution(self) -> None:
        with self.assertRaises(ValueError):
            EthosCli(self.fake_ethos).parse_pdf_json(self.pdf, timeout_seconds=0)

    def test_missing_input_pdf_raises_file_not_found(self) -> None:
        with self.assertRaises(FileNotFoundError):
            EthosCli(self.fake_ethos).parse_pdf_json(self.root / "missing.pdf")

    def test_invalid_json_stdout_raises_output_error(self) -> None:
        cli = EthosCli(self.fake_ethos, env={"ETHOS_FAKE_MODE": "invalid-json"})

        with self.assertRaises(EthosOutputError) as caught:
            cli.parse_pdf_json(self.pdf)

        self.assertIn("invalid JSON", str(caught.exception))
        self.assertEqual(caught.exception.stdout, "not-json\n")

    def test_crop_element_invokes_descriptor_cli_with_request_and_check_id(self) -> None:
        result = crop_element(
            self.document,
            self.crop_request,
            ethos_bin=self.fake_ethos,
            check_id="v0002",
        )

        self.assertTrue(result["ok"])
        self.assertEqual(result["artifact_type"], "ethos.crop_descriptor.v1")
        self.assertEqual(
            result["argv"],
            [
                "crop_element",
                str(self.document),
                "--request",
                str(self.crop_request),
                "--check-id",
                "v0002",
            ],
        )

    def test_crop_element_method_uses_default_check_id(self) -> None:
        result = EthosCli(self.fake_ethos).crop_element(self.document, self.crop_request)

        self.assertEqual(result["argv"][-2:], ["--check-id", "v0001"])

    def test_crop_element_rejects_empty_check_id_before_command_execution(self) -> None:
        with self.assertRaises(ValueError):
            EthosCli(self.fake_ethos).crop_element(
                self.document,
                self.crop_request,
                check_id="",
            )

    def test_crop_element_missing_request_raises_file_not_found(self) -> None:
        with self.assertRaises(FileNotFoundError):
            EthosCli(self.fake_ethos).crop_element(
                self.document,
                self.root / "missing-request.json",
            )

    def test_crop_element_invalid_json_stdout_raises_output_error(self) -> None:
        cli = EthosCli(self.fake_ethos, env={"ETHOS_FAKE_MODE": "invalid-json"})

        with self.assertRaises(EthosOutputError) as caught:
            cli.crop_element(self.document, self.crop_request)

        self.assertIn("invalid JSON", str(caught.exception))
        self.assertEqual(caught.exception.stdout, "not-json\n")

    def test_crop_element_passes_rendered_artifact_arguments(self) -> None:
        result = EthosCli(self.fake_ethos).crop_element(
            self.document,
            self.crop_request,
            crop_source_pdf=self.crop_source_pdf,
            crop_dir=self.crop_dir,
        )

        self.assertEqual(
            result["argv"][-4:],
            [
                "--crop-source-pdf",
                str(self.crop_source_pdf),
                "--crop-dir",
                str(self.crop_dir),
            ],
        )

    def test_crop_element_rejects_partial_rendered_arguments(self) -> None:
        with self.assertRaises(ValueError):
            EthosCli(self.fake_ethos).crop_element(
                self.document,
                self.crop_request,
                crop_source_pdf=self.crop_source_pdf,
            )


if __name__ == "__main__":
    unittest.main()
