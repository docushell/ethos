#!/usr/bin/env python3

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "scripts/build-windows-verify-candidate.py"


class WindowsVerifyCandidateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.work = Path(self.temp.name)
        self.binary = self.work / "ethos.exe"
        self.binary.write_bytes(b"fixture windows executable\n")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def command(self, out_dir: Path) -> list[str]:
        return [
            "python3",
            str(BUILDER),
            "--ethos-binary",
            str(self.binary),
            "--version",
            "test",
            "--out-dir",
            str(out_dir),
        ]

    def test_double_run_is_byte_identical_and_verify_only(self) -> None:
        first = self.work / "first"
        second = self.work / "second"
        subprocess.run(self.command(first), cwd=ROOT, check=True, capture_output=True, text=True)
        subprocess.run(self.command(second), cwd=ROOT, check=True, capture_output=True, text=True)

        archive_name = "ethos-windows-x64.zip"
        first_archive = first / archive_name
        second_archive = second / archive_name
        self.assertEqual(first_archive.read_bytes(), second_archive.read_bytes())
        self.assertEqual(
            (first / f"{archive_name}.sha256").read_bytes(),
            (second / f"{archive_name}.sha256").read_bytes(),
        )

        root = "ethos-windows-x64"
        with zipfile.ZipFile(first_archive) as archive:
            names = set(archive.namelist())
            for required in (
                f"{root}/ethos.exe",
                f"{root}/LICENSE",
                f"{root}/NOTICE",
                f"{root}/PDFIUM-MANUAL-SETUP.md",
                f"{root}/VERIFY-QUICKSTART.txt",
                f"{root}/verify-example/document.json",
                f"{root}/verify-example/citations.json",
                f"{root}/artifact-manifest.json",
            ):
                self.assertIn(required, names)
                self.assertEqual((1980, 1, 1, 0, 0, 0), archive.getinfo(required).date_time)
            manifest = json.loads(archive.read(f"{root}/artifact-manifest.json"))
            quickstart = archive.read(f"{root}/VERIFY-QUICKSTART.txt").decode("utf-8")
            self.assertEqual("verify-only", manifest["artifact_scope"])
            self.assertFalse(manifest["pdfium_included"])
            self.assertEqual("blocked", manifest["publication"])
            self.assertIn("--fail-on-ungrounded", quickstart)
            self.assertIn("not semantic truth", quickstart)

    def test_missing_binary_fails_closed(self) -> None:
        self.binary.unlink()
        result = subprocess.run(
            self.command(self.work / "out"), cwd=ROOT, capture_output=True, text=True
        )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("missing regular Windows Ethos binary", result.stderr)


if __name__ == "__main__":
    unittest.main()
