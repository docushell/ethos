#!/usr/bin/env python3
from __future__ import annotations

import gzip
import hashlib
import io
import json
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SMOKE = ROOT / ".github/scripts/smoke_ethos_full_candidate.py"


class SmokeEthosFullCandidateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.work = Path(self.temp.name)
        self.fixture = self.work / "fixture.pdf"
        self.fixture.write_bytes(b"fixture")
        self.archive = self.work / "ethos-full-test-linux-x64.tar.gz"
        self.checksum = self.archive.with_suffix(".tar.gz.sha256")
        self.inventory = self.work / "ethos-full-test-linux-x64.inventory.json"
        self.write_candidate()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_candidate(self, extra_name: str | None = None) -> None:
        root = "ethos-full-test-linux-x64"
        files = {
            "LICENSE": b"LICENSE\n", "NOTICE": b"NOTICE\n", "lib/libpdfium.so": b"runtime",
            "artifact-manifest.json": json.dumps({"target": "linux-x64", "pdfium": {"runtime_library_path": "lib/libpdfium.so"}}).encode(),
            "bin/ethos": b'#!/bin/sh\nroot=$(CDPATH= cd -P -- "$(dirname "$0")/.." && pwd)\n[ "$ETHOS_PDFIUM_LIBRARY_PATH" = "$root/lib/libpdfium.so" ] || exit 9\ncase "$1" in --version) echo "ethos test";; doctor) exit 0;; doc) echo "{\\"document\\":true}";; esac\n',
            "ethos": b'#!/bin/sh\nroot=$(CDPATH= cd -P -- "$(dirname "$0")" && pwd)\nexport ETHOS_PDFIUM_LIBRARY_PATH="$root/lib/libpdfium.so"\nexec "$root/bin/ethos" "$@"\n',
        }
        with self.archive.open("wb") as raw:
            with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
                with tarfile.open(fileobj=compressed, mode="w") as bundle:
                    for name, data in sorted(files.items()):
                        info = tarfile.TarInfo(f"{root}/{name}"); info.size = len(data); info.mode = 0o755 if name in {"ethos", "bin/ethos"} else 0o644; info.mtime = 0
                        bundle.addfile(info, io.BytesIO(data))
                    if extra_name:
                        info = tarfile.TarInfo(extra_name); info.size = 1; info.mtime = 0; bundle.addfile(info, io.BytesIO(b"x"))
        digest = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        self.checksum.write_text(f"{digest}  {self.archive.name}\n")
        self.inventory.write_text(json.dumps({"schema": "ethos.full_candidate_inventory.v1", "status": "release_candidate_pending_target_smoke", "publication": "not_publishable_pending_release_gates", "artifact": self.archive.name, "sha256": digest, "size_bytes": self.archive.stat().st_size, "target": "linux-x64"}))

    def command(self, extract: Path, out: Path | None = None) -> list[str]:
        command = ["python3", str(SMOKE), "--archive", str(self.archive), "--checksum", str(self.checksum), "--inventory", str(self.inventory), "--extract-dir", str(extract), "--expected-version", "ethos test", "--fixture", str(self.fixture)]
        return command + (["--out", str(out)] if out else [])

    def test_smoke_validates_candidate_metadata_before_runtime(self) -> None:
        out = self.work / "smoke.json"
        result = subprocess.run(self.command(self.work / "extracted", out), capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stderr)
        evidence = json.loads(out.read_text())
        self.assertEqual(self.archive.name, evidence["artifact"])
        self.assertEqual(hashlib.sha256(self.archive.read_bytes()).hexdigest(), evidence["archive_sha256"])
        self.assertIn("parse_stdout_sha256", evidence)

    def test_rejects_checksum_and_inventory_mismatches_before_extraction(self) -> None:
        self.checksum.write_text("0" * 64 + f"  {self.archive.name}\n")
        result = subprocess.run(self.command(self.work / "bad-checksum"), capture_output=True, text=True)
        self.assertNotEqual(0, result.returncode); self.assertIn("checksum", result.stderr); self.assertFalse((self.work / "bad-checksum").exists())
        self.write_candidate()
        record = json.loads(self.inventory.read_text()); record["sha256"] = "0" * 64; self.inventory.write_text(json.dumps(record))
        result = subprocess.run(self.command(self.work / "bad-inventory"), capture_output=True, text=True)
        self.assertNotEqual(0, result.returncode); self.assertIn("inventory sha256", result.stderr); self.assertFalse((self.work / "bad-inventory").exists())

    def test_rejects_unsafe_archive_member_before_payload_execution(self) -> None:
        self.write_candidate("../escape")
        result = subprocess.run(self.command(self.work / "unsafe"), capture_output=True, text=True)
        self.assertNotEqual(0, result.returncode); self.assertIn("unsafe member path", result.stderr)


if __name__ == "__main__": unittest.main()
