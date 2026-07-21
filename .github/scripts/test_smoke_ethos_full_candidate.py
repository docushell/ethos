#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SMOKE = ROOT / ".github/scripts/smoke_ethos_full_candidate.py"


class SmokeEthosFullCandidateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "ethos-full-test-linux-x64"
        (self.root / "bin").mkdir(parents=True)
        (self.root / "lib").mkdir()
        for name in ("LICENSE", "NOTICE"):
            (self.root / name).write_text(name)
        (self.root / "lib/libpdfium.so").write_bytes(b"runtime")
        (self.root / "artifact-manifest.json").write_text(json.dumps({"target":"linux-x64", "pdfium":{"runtime_library_path":"lib/libpdfium.so"}}))
        binary = self.root / "bin/ethos"
        binary.write_text("#!/bin/sh\nroot=$(CDPATH= cd -P -- \"$(dirname \"$0\")/..\" && pwd)\n[ \"$ETHOS_PDFIUM_LIBRARY_PATH\" = \"$root/lib/libpdfium.so\" ] || exit 9\ncase \"$1\" in --version) echo 'ethos test';; doctor) exit 0;; doc) echo '{\"document\":true}';; esac\n")
        binary.chmod(0o755)
        launcher = self.root / "ethos"
        launcher.write_text("#!/bin/sh\nroot=$(CDPATH= cd -P -- \"$(dirname \"$0\")\" && pwd)\nexport ETHOS_PDFIUM_LIBRARY_PATH=\"$root/lib/libpdfium.so\"\nexec \"$root/bin/ethos\" \"$@\"\n")
        launcher.chmod(0o755)
        self.fixture = self.root / "fixture.pdf"
        self.fixture.write_bytes(b"fixture")

    def tearDown(self) -> None: self.temp.cleanup()

    def test_smoke_records_deterministic_parse_evidence(self) -> None:
        out = self.root / "smoke.json"
        result = subprocess.run(["python3", str(SMOKE), "--root", str(self.root), "--expected-version", "ethos test", "--fixture", str(self.fixture), "--out", str(out)], capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stderr)
        evidence = json.loads(out.read_text())
        self.assertEqual("linux-x64", evidence["target"])
        self.assertIn("parse_stdout_sha256", evidence)


if __name__ == "__main__": unittest.main()
