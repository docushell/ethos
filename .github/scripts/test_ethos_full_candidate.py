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
BUILDER = ROOT / "scripts/build-ethos-full-candidate.py"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class EthosFullCandidateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.work = Path(self.temp.name)
        self.binary = self.work / "ethos-bin"
        self.binary.write_bytes(b"fixture ethos binary\n")
        self.binary.chmod(0o755)
        self.runtime = b"fixture pdfium runtime\n"
        self.pdfium_archive = self.work / "pdfium.tgz"
        self.write_pdfium_archive(self.runtime, include_pdfium_notice=True)
        self.profile = self.work / "profile.json"
        self.write_profile(sha256(self.runtime))

    def write_pdfium_archive(self, runtime: bytes, include_pdfium_notice: bool) -> None:
        files = {
            "LICENSE": b"PDFium package license\n",
            "lib/libpdfium.dylib": runtime,
            "licenses/zlib.txt": b"zlib notice\n",
        }
        if include_pdfium_notice:
            files["licenses/pdfium.txt"] = b"PDFium BSD notice\n"
        with self.pdfium_archive.open("wb") as raw:
            with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
                with tarfile.open(fileobj=compressed, mode="w") as archive:
                    for name, data in sorted(files.items()):
                        info = tarfile.TarInfo(name)
                        info.size = len(data)
                        info.mtime = 0
                        archive.addfile(info, io.BytesIO(data))

    def write_profile(self, runtime_hash: str) -> None:
        self.profile.write_text(
            json.dumps(
                {
                    "backend": {
                        "id": "pdfium",
                        "phase": 1,
                        "version": "fixture/1",
                        "upstream_version": "fixture",
                        "distribution": {"source": "fixture"},
                        "build_flags": {"pdf_enable_v8": False, "pdf_enable_xfa": False},
                        "platform_hashes": {
                            "macos-arm64": sha256(self.pdfium_archive.read_bytes())
                        },
                        "platform_artifacts": {
                            "macos-arm64": {
                                "runtime_library_path": "lib/libpdfium.dylib",
                                "runtime_library_sha256": runtime_hash,
                            }
                        },
                    }
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def command(self, out_dir: Path) -> list[str]:
        return [
            "python3",
            str(BUILDER),
            "--target",
            "macos-arm64",
            "--version",
            "test",
            "--ethos-binary",
            str(self.binary),
            "--pdfium-archive",
            str(self.pdfium_archive),
            "--out-dir",
            str(out_dir),
            "--profile",
            str(self.profile),
            "--project-license",
            str(ROOT / "LICENSE"),
            "--project-notice",
            str(ROOT / "NOTICE"),
        ]

    def test_double_run_is_byte_identical_and_complete(self) -> None:
        first = self.work / "first"
        second = self.work / "second"
        subprocess.run(self.command(first), cwd=ROOT, check=True, capture_output=True, text=True)
        subprocess.run(self.command(second), cwd=ROOT, check=True, capture_output=True, text=True)

        archive_name = "ethos-full-test-macos-arm64.tar.gz"
        first_archive = first / archive_name
        second_archive = second / archive_name
        self.assertEqual(first_archive.read_bytes(), second_archive.read_bytes())
        self.assertEqual(
            (first / f"{archive_name}.sha256").read_bytes(),
            (second / f"{archive_name}.sha256").read_bytes(),
        )
        self.assertEqual(
            (first / "ethos-full-test-macos-arm64.inventory.json").read_bytes(),
            (second / "ethos-full-test-macos-arm64.inventory.json").read_bytes(),
        )

        root = "ethos-full-test-macos-arm64"
        with tarfile.open(first_archive, "r:gz") as archive:
            names = set(archive.getnames())
            for required in (
                f"{root}/ethos",
                f"{root}/bin/ethos",
                f"{root}/lib/libpdfium.dylib",
                f"{root}/LICENSE",
                f"{root}/NOTICE",
                f"{root}/third-party/pdfium/LICENSE",
                f"{root}/third-party/pdfium/licenses/pdfium.txt",
                f"{root}/artifact-manifest.json",
            ):
                self.assertIn(required, names)
            manifest = json.load(archive.extractfile(f"{root}/artifact-manifest.json"))
            launcher = archive.extractfile(f"{root}/ethos").read().decode("utf-8")
            self.assertEqual("release_candidate_pending_target_smoke", manifest["status"])
            self.assertEqual("not_publishable_pending_release_gates", manifest["publication"])
            self.assertEqual(sha256(self.binary.read_bytes()), manifest["input_sha256"]["ethos_binary"])
            self.assertEqual(sha256(self.pdfium_archive.read_bytes()), manifest["input_sha256"]["pdfium_archive"])
            self.assertIn('ETHOS_PDFIUM_LIBRARY_PATH="$root/lib/libpdfium.dylib"', launcher)

    def test_hash_mismatch_fails_closed(self) -> None:
        self.write_pdfium_archive(b"wrong runtime\n", include_pdfium_notice=True)
        self.write_profile(sha256(self.runtime))
        result = subprocess.run(
            self.command(self.work / "out"), cwd=ROOT, capture_output=True, text=True
        )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("PDFium runtime sha256 mismatch", result.stderr)

    def test_missing_notice_fails_closed(self) -> None:
        self.write_pdfium_archive(self.runtime, include_pdfium_notice=False)
        self.write_profile(sha256(self.runtime))
        result = subprocess.run(
            self.command(self.work / "out"), cwd=ROOT, capture_output=True, text=True
        )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("must include licenses/pdfium.txt", result.stderr)


if __name__ == "__main__":
    unittest.main()
