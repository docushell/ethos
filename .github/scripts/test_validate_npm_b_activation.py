from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from validate_npm_b_activation import validate


class ValidateNpmBActivationTests(unittest.TestCase):
    def fixture(self, version: str = "0.5.0") -> tuple[Path, Path]:
        root = Path(tempfile.mkdtemp())
        package = root / "package"
        vendor = package / "vendor"
        vendor.mkdir(parents=True)
        (package / "package.json").write_text(json.dumps({"version": version}), encoding="utf-8")
        (package / "package-lock.json").write_text(json.dumps({"version": version, "packages": {"": {"version": version}}}), encoding="utf-8")
        (vendor / "manifest.json").write_text(json.dumps({"cli_version": version}), encoding="utf-8")
        targets = {}
        for target in ("macos-arm64", "linux-x64"):
            archive = root / f"{target}.tar.gz"
            archive.write_bytes(target.encode())
            digest = hashlib.sha256(archive.read_bytes()).hexdigest()
            checksum = root / f"{target}.sha256"
            checksum.write_text(f"{digest}  {archive.name}\n", encoding="utf-8")
            inventory = root / f"{target}.inventory.json"
            inventory.write_text(json.dumps({"schema": "ethos.full_candidate_inventory.v1", "status": "release_candidate_pending_target_smoke", "publication": "not_publishable_pending_release_gates", "target": target, "sha256": digest}), encoding="utf-8")
            smoke = root / f"{target}.smoke.json"
            smoke.write_text(json.dumps({"schema": "ethos.full_candidate_smoke.v1", "target": target, "archive_sha256": digest, "version_stdout": version}), encoding="utf-8")
            targets[target] = {"archive": archive.name, "checksum": checksum.name, "inventory": inventory.name, "smoke": smoke.name}
        evidence = root / "evidence.json"
        evidence.write_text(json.dumps({"schema": "ethos.npm_b_activation_evidence.v1", "core_version": version, "core_commit": "a" * 40, "targets": targets}), encoding="utf-8")
        return evidence, package

    def test_accepts_complete_frozen_core_a_evidence(self) -> None:
        evidence, package = self.fixture()
        validate(evidence, package)

    def test_rejects_current_published_payload(self) -> None:
        evidence, package = self.fixture(version="0.4.0")
        with self.assertRaises(SystemExit):
            validate(evidence, package)

    def test_rejects_unsafe_evidence_path(self) -> None:
        evidence, package = self.fixture()
        data = json.loads(evidence.read_text(encoding="utf-8"))
        data["targets"]["linux-x64"]["archive"] = "../outside"
        evidence.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises(SystemExit):
            validate(evidence, package)


if __name__ == "__main__":
    unittest.main()
