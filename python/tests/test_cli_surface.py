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
    EthosCli,
    EthosCommandError,
    EthosNotFoundError,
    EthosOutputError,
    EthosTimeoutError,
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


if __name__ == "__main__":
    unittest.main()
