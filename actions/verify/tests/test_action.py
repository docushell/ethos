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

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import stat
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ACTION = Path(__file__).resolve().parents[1]
ROOT = ACTION.parents[1]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
PUBLISHED_LINUX_ARCHIVE_SHA256 = "616be562306d64a293554ca4695f19deb6e135dd328e88598a80e76f6f8fb3cd"
PUBLISHED_LINUX_BINARY_SHA256 = "2136dcd349a7b3f73f8df83a1b1e35819f9832043eb264b3eaea341697b739ed"
sys.path.insert(0, str(ACTION))

import install_cli  # noqa: E402
import run_verify  # noqa: E402


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class VerifyActionTests(unittest.TestCase):
    def make_fake_cli(self, root: Path, report: Path, exit_code: int) -> Path:
        cli = root / "ethos"
        cli.write_text(
            "#!/usr/bin/env python3\n"
            "import pathlib, shutil, sys\n"
            f"source = pathlib.Path({str(report)!r})\n"
            "out = pathlib.Path(sys.argv[sys.argv.index('--out') + 1])\n"
            "shutil.copyfile(source, out)\n"
            f"raise SystemExit({exit_code})\n",
            encoding="utf-8",
        )
        cli.chmod(cli.stat().st_mode | stat.S_IXUSR)
        return cli

    def capture_run(self, cli: Path, work: Path) -> tuple[int, bytes]:
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            code = run_verify.run(
                cli,
                "document.json",
                "citations.json",
                "native",
                work / "report.json",
            )
        return code, stream.getvalue().encode("utf-8")

    def test_ungrounded_annotations_are_snapshot_backed_and_deterministic(self) -> None:
        expected = (FIXTURES / "ungrounded.annotations.txt").read_bytes()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            cli = self.make_fake_cli(root, FIXTURES / "ungrounded-report.json", 1)
            first = self.capture_run(cli, root / "run1")
            second = self.capture_run(cli, root / "run2")
        self.assertEqual(1, first[0])
        self.assertEqual(first, second)
        self.assertEqual(expected, first[1])

    def test_operational_exit_fails_with_annotation(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            cli = root / "ethos"
            cli.write_text("#!/bin/sh\necho 'missing capability' >&2\nexit 12\n", encoding="utf-8")
            cli.chmod(cli.stat().st_mode | stat.S_IXUSR)
            code, output = self.capture_run(cli, root)
        self.assertEqual(12, code)
        self.assertEqual(
            b"::error file=document.json,title=Ethos operational error::missing capability\n",
            output,
        )

    def test_missing_report_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            cli = root / "ethos"
            cli.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
            cli.chmod(cli.stat().st_mode | stat.S_IXUSR)
            code, output = self.capture_run(cli, root)
        self.assertEqual(2, code)
        self.assertIn(b"verification report is missing or invalid", output)

    def test_native_grounding_omits_adapter_flag(self) -> None:
        report = {
            "all_evidence_grounded": True,
            "capability_limits": [],
            "checks": [],
        }
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            cli = root / "ethos"
            cli.write_text("fixture", encoding="utf-8")
            with mock.patch("subprocess.run") as subprocess_run:
                subprocess_run.return_value.returncode = 0
                subprocess_run.return_value.stdout = ""
                subprocess_run.return_value.stderr = ""
                report_path = root / "report.json"
                report_path.write_text(json.dumps(report), encoding="utf-8")
                code = run_verify.run(cli, "document.json", "citations.json", "native", report_path)
            command = subprocess_run.call_args.args[0]
        self.assertEqual(0, code)
        self.assertNotIn("--grounding", command)

    def test_installer_checks_archive_and_binary_digests(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            payload = root / "ethos"
            payload.write_bytes(b"fixture executable\n")
            archive = root / "candidate.tar.gz"
            with tarfile.open(archive, "w:gz") as bundle:
                bundle.add(payload, arcname="ethos-linux-x64/ethos")
            out1 = root / "out1" / "ethos"
            out2 = root / "out2" / "ethos"
            with mock.patch("platform.system", return_value="Linux"), mock.patch(
                "platform.machine", return_value="x86_64"
            ):
                for out in (out1, out2):
                    install_cli.install(archive.as_uri(), digest(archive), digest(payload), out)
            self.assertEqual(out1.read_bytes(), out2.read_bytes())

    def test_installer_rejects_checksum_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = root / "candidate.tar.gz"
            archive.write_bytes(b"not the approved archive")
            with mock.patch("platform.system", return_value="Linux"), mock.patch(
                "platform.machine", return_value="x86_64"
            ), self.assertRaisesRegex(SystemExit, "release archive SHA256 mismatch"):
                install_cli.install(archive.as_uri(), "0" * 64, "0" * 64, root / "ethos")

    def test_scratch_repository_fabricated_citation_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp) / "scratch-repo"
            (repo / ".github/workflows").mkdir(parents=True)
            (repo / "document.json").write_text("{}\n", encoding="utf-8")
            (repo / "citations.json").write_text("[]\n", encoding="utf-8")
            (repo / ".github/workflows/verify.yml").write_text(
                "steps:\n"
                "  - uses: docushell/ethos/actions/verify@<full-commit-sha>\n"
                "    with:\n"
                "      source: document.json\n"
                "      citations: citations.json\n",
                encoding="utf-8",
            )
            cli = self.make_fake_cli(repo, FIXTURES / "ungrounded-report.json", 1)
            code, output = self.capture_run(cli, repo)
        self.assertEqual(1, code)
        self.assertEqual((FIXTURES / "ungrounded.annotations.txt").read_bytes(), output)

    def test_action_is_pinned_and_example_is_short(self) -> None:
        action = (ACTION / "action.yml").read_text(encoding="utf-8")
        readme = (ACTION / "README.md").read_text(encoding="utf-8")
        release_state = json.loads((ROOT / "docs/release-state.json").read_text(encoding="utf-8"))
        published_version = release_state["release"]["npm_package"]["version"]
        self.assertIn(
            f"releases/download/v{published_version}/ethos-linux-x64.tar.gz",
            action,
        )
        self.assertIn(PUBLISHED_LINUX_ARCHIVE_SHA256, action)
        self.assertIn(PUBLISHED_LINUX_BINARY_SHA256, action)
        self.assertNotIn("cli-path", action)
        example = readme.split("```yaml\n", 1)[1].split("```", 1)[0]
        self.assertLessEqual(len(example.strip().splitlines()), 10)

    def test_ci_dogfoods_both_readme_fixtures_and_asserts_failure(self) -> None:
        workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        dogfood = workflow.split("  released-cli-action-dogfood:\n", 1)[1].split(
            "\n  verify-portability:", 1
        )[0]
        self.assertEqual(2, dogfood.count("uses: ./actions/verify"))
        self.assertIn("schemas/examples/document.example.json", dogfood)
        self.assertIn("examples/verify/native_grounded_citations.json", dogfood)
        self.assertIn("examples/verify/native_ungrounded_citations.json", dogfood)
        self.assertIn("continue-on-error: true", dogfood)
        self.assertIn("if: always()", dogfood)
        self.assertIn('test "$GROUNDED_OUTCOME" = "success"', dogfood)
        self.assertIn('test "$FABRICATED_OUTCOME" = "failure"', dogfood)


if __name__ == "__main__":
    unittest.main()
