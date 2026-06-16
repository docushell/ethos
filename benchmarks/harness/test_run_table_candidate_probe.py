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
import tempfile
import textwrap
import unittest
from pathlib import Path

import run_table_candidate_probe


def write_text(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


class TableCandidateProbeHarnessTests(unittest.TestCase):
    def test_probe_runs_parse_then_internal_table_probe_and_compares_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pdf_root = root / "pdfs"
            write_text(pdf_root / "sample.pdf", "%PDF-1.7\n")
            expected = root / "expected"
            write_text(expected / "sample.md", "| A | B |\n")
            fake_ethos = write_text(
                root / "ethos",
                textwrap.dedent(
                    """\
                    #!/usr/bin/env python3
                    import json
                    import os
                    import sys
                    from pathlib import Path

                    if sys.argv[1:3] == ["doc", "parse"]:
                        out = Path(sys.argv[sys.argv.index("--out") + 1])
                        out.parent.mkdir(parents=True, exist_ok=True)
                        out.write_text(json.dumps({"fake": "document"}) + "\\n")
                        raise SystemExit(0)

                    if sys.argv[1] == "__table-candidate-probe":
                        if os.environ.get("ETHOS_INTERNAL_TABLE_CANDIDATE_PROBE") != "1":
                            raise SystemExit(9)
                        out = Path(sys.argv[sys.argv.index("--out") + 1])
                        out.parent.mkdir(parents=True, exist_ok=True)
                        out.write_text(json.dumps({
                            "summary": {"tables_total": 1},
                            "tables": [{"markdown": "| A | B |\\n"}],
                        }) + "\\n")
                        raise SystemExit(0)

                    raise SystemExit(2)
                    """
                ),
            )
            fake_ethos.chmod(0o755)

            args = run_table_candidate_probe.parse_args(
                [
                    "--ethos-bin",
                    str(fake_ethos),
                    "--pdf-root",
                    str(pdf_root),
                    "--doc-id",
                    "sample",
                    "--out",
                    str(root / "report.json"),
                    "--work-dir",
                    str(root / "work"),
                    "--expected-markdown-dir",
                    str(expected),
                ]
            )
            report = run_table_candidate_probe.build_report(args)

        self.assertEqual(report["summary"]["documents_total"], 1)
        self.assertEqual(report["summary"]["documents_passed"], 1)
        self.assertEqual(report["summary"]["candidate_tables_total"], 1)
        self.assertEqual(report["summary"]["expected_markdown_compared"], 1)
        self.assertEqual(report["summary"]["expected_markdown_exact_matches"], 1)
        self.assertEqual(report["documents"][0]["status"], "pass")
        self.assertTrue(report["documents"][0]["expected_markdown"]["exact_match"])

    def test_parse_failure_is_reported_without_probe(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pdf_root = root / "pdfs"
            write_text(pdf_root / "sample.pdf", "%PDF-1.7\n")
            fake_ethos = write_text(
                root / "ethos",
                textwrap.dedent(
                    """\
                    #!/usr/bin/env python3
                    import sys
                    if sys.argv[1:3] == ["doc", "parse"]:
                        print("parse failed", file=sys.stderr)
                        raise SystemExit(7)
                    raise SystemExit(2)
                    """
                ),
            )
            fake_ethos.chmod(0o755)

            args = run_table_candidate_probe.parse_args(
                [
                    "--ethos-bin",
                    str(fake_ethos),
                    "--pdf-root",
                    str(pdf_root),
                    "--doc-id",
                    "sample",
                    "--out",
                    str(root / "report.json"),
                    "--work-dir",
                    str(root / "work"),
                ]
            )
            report = run_table_candidate_probe.build_report(args)

        self.assertEqual(report["summary"]["documents_passed"], 0)
        self.assertEqual(report["summary"]["documents_failed"], 1)
        self.assertEqual(report["documents"][0]["status"], "fail")
        self.assertEqual(report["documents"][0]["stage"], "parse")
        self.assertIn("parse failed", report["documents"][0]["stderr"])


if __name__ == "__main__":
    unittest.main()
