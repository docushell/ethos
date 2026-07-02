#!/usr/bin/env python3
#
# Copyright 2026 The Ethos maintainers
#
# Licensed under the Apache License, Version 2.0 (the "License");
#

from __future__ import annotations

import json
import re
import unittest
import urllib.request
from pathlib import Path

from makefile_guard import target_block
from validation_record_source import assert_record_source_binding


ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "docs/validation/v0-3-0-publication-closeout-validation-2026-07-01.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"
MAKEFILE = ROOT / "Makefile"
NPM_PACKAGE = ROOT / "packages/npm/ethos-pdf/package.json"

SOURCE_SHORT = "681d324"
SOURCE_COMMIT = "681d324653df91a89f6528fbc2a4c685ff0d0114"
SOURCE_TREE = "7480149de77f325bbc051f5babadda13a65ef842"
APPROVAL_SOURCE_COMMIT = "1f6ab3c7294c390d87f70cde6514a02024cf964c"
PACKAGE_EVIDENCE_SOURCE_COMMIT = "4b6d219df1757b6e4728c16c8023bee5c8cf8962"
VERSION = "0.3.0"
CRATES = {
    "ethos-doc-core": "62f179f2dfc07deaae7ee3bca54a8961548b2b6ee33f015ec99b0c5d8423084c",
    "ethos-verify": "4b2339f82d0c9e01f20fbe163433efb990ae7d27abd93d9cdfddd258dbead8fb",
    "ethos-pdf": "a06a33541df16f630865466ea440bfddc5e4d8304ffe0a4c295a6f74fd033a28",
}
CRATE_ARTIFACT_HASHES = (
    "7ba41a2ae299a53a4677153beaaec5ed486a07b5da08b2ef13974b9a0be141cb",
    "00f001455ca207e65aaf464551d3ba05945cda0b06e9e1036f49ac587accbb95",
    "c2f4f2ccb6de6e54cd3257597cd28e7f6dec2a6d22befbd230d2c4cf31931cfd",
)
PYPI_PACKAGE = "ethos-pdf"
WHEEL = "ethos_pdf-0.3.0-py3-none-any.whl"
WHEEL_SHA256 = "9eb106deafcd1d9717e5e7b67dc9413180421aba25a5257266352d09540b3265"
WHEEL_URL = (
    "https://files.pythonhosted.org/packages/31/5c/5aaa1ba4f887f4002593ffe465369cb8c66823ffa9ac540d99e072e4e589/"
    "ethos_pdf-0.3.0-py3-none-any.whl"
)
WHEEL_SIZE = 16575
UPLOAD_TIME = "2026-07-01T15:03:07.368729Z"
FORBIDDEN = (
    "github release artifacts are published",
    "npm package is published",
    "installable 0.3.0 wording approved",
    "public installation wording approved",
    "docushell integration approved",
    "production-ready",
    "hosted surfaces approved",
    "windows packaged artifacts approved",
    "bundled pdfium approved",
    "public benchmark claims approved",
    "ethos-doc approved",
    "ethos-rag approved",
)
PRIVATE_PATH_MARKERS = (
    "/" + "Users/",
    "/" + "private/tmp",
    "/" + "private/var",
    "/" + "var/folders",
    "saumil" + "diwaker",
    "Desktop/" + "Stuff",
    "project/repo/" + "ethos",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalized(path: Path) -> str:
    return re.sub(r"\s+", " ", read(path))


def crates_io_version(crate: str) -> dict:
    request = urllib.request.Request(
        f"https://crates.io/api/v1/crates/{crate}/{VERSION}",
        headers={"User-Agent": "ethos-release-validation"},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)["version"]


def pypi_release_json() -> dict:
    with urllib.request.urlopen(f"https://pypi.org/pypi/{PYPI_PACKAGE}/{VERSION}/json", timeout=30) as response:
        return json.load(response)


class V030PublicationCloseoutTests(unittest.TestCase):
    def test_closeout_record_is_source_bound_and_indexed(self) -> None:
        raw = read(RECORD)
        record = normalized(RECORD)

        assert_record_source_binding(
            self,
            root=ROOT,
            raw_record=raw,
            normalized_record=record,
            validated_head=SOURCE_SHORT,
            source_label="v0.3.0 publication closeout",
            source_commit=SOURCE_COMMIT,
            source_tree=SOURCE_TREE,
        )
        self.assertIn(RECORD.name, normalized(VALIDATION_README))
        self.assertIn("v0.3.0 publication closeout", normalized(VALIDATION_README).lower())
        for path in (EXECUTION_STATUS, PUBLIC_RELEASE_CHECKLIST):
            text = normalized(path)
            self.assertIn(RECORD.name, text, str(path))
            self.assertIn("0.3.0", text, str(path))
            self.assertIn("npm", text.lower(), str(path))
            self.assertIn("blocked", text.lower(), str(path))

    def test_closeout_records_rust_and_python_publication_evidence(self) -> None:
        record = normalized(RECORD)

        self.assertIn(
            "Status: **v0.3.0 Rust crates and Python wheel published; artifact/npm/tag/install wording lanes remain blocked**",
            record,
        )
        for crate, checksum in CRATES.items():
            self.assertIn(f"`{crate} = {VERSION}`", record)
            self.assertIn(f"cargo publish --locked -p {crate}", record)
            self.assertIn(f"Uploaded {crate} v{VERSION} to registry `crates-io`", record)
            self.assertIn(f"Published {crate} v{VERSION} at registry `crates-io`", record)
            self.assertIn(f"checksum: {checksum}", record)
        for digest in CRATE_ARTIFACT_HASHES:
            self.assertIn(digest, record)
        for expected in (
            "`ethos-doc-core` was published first.",
            "`ethos-verify` was published after crates.io reported `ethos-doc-core = 0.3.0`.",
            "`ethos-pdf` was published after crates.io reported `ethos-verify = 0.3.0`.",
            "SOURCE_DATE_EPOCH=0",
            WHEEL,
            WHEEL_SHA256,
            "python3 -m twine upload target/python-pypi-0.3.0/ethos_pdf-0.3.0-py3-none-any.whl",
            "Uploading distributions to https://upload.pypi.org/legacy/",
            "WARNING This environment is not supported for trusted publishing",
            "Uploading ethos_pdf-0.3.0-py3-none-any.whl",
            "View at: https://pypi.org/project/ethos-pdf/0.3.0/",
            WHEEL_URL,
            UPLOAD_TIME,
            "bdist_wheel",
            "py3",
            "yanked: false",
            f"Approval decision source commit: `{APPROVAL_SOURCE_COMMIT}`",
            f"Package evidence source commit: `{PACKAGE_EVIDENCE_SOURCE_COMMIT}`",
        ):
            self.assertIn(expected, record)

    def test_live_crates_io_reports_published_candidates(self) -> None:
        for crate, checksum in CRATES.items():
            data = crates_io_version(crate)
            self.assertEqual(crate, data["crate"])
            self.assertEqual(VERSION, data["num"])
            self.assertEqual(checksum, data["checksum"])
            self.assertFalse(data["yanked"])

    def test_live_pypi_reports_published_candidate(self) -> None:
        data = pypi_release_json()

        self.assertEqual(PYPI_PACKAGE, data["info"]["name"])
        self.assertEqual(VERSION, data["info"]["version"])
        self.assertEqual(">=3.8", data["info"]["requires_python"])
        self.assertEqual(1, len(data["urls"]))
        file = data["urls"][0]
        self.assertEqual(WHEEL, file["filename"])
        self.assertEqual("bdist_wheel", file["packagetype"])
        self.assertEqual("py3", file["python_version"])
        self.assertEqual(WHEEL_SHA256, file["digests"]["sha256"])
        self.assertEqual(WHEEL_URL, file["url"])
        self.assertEqual(WHEEL_SIZE, file["size"])
        self.assertEqual(UPLOAD_TIME, file["upload_time_iso_8601"])
        self.assertFalse(file["yanked"])

    def test_retained_blockers_public_path_hygiene_and_npm_baseline(self) -> None:
        raw = read(RECORD)
        lower = normalized(RECORD).lower()

        self.assertIn(json.loads(read(NPM_PACKAGE))["version"], {"0.2.1", "0.3.0"})
        for expected in (
            "Public installation wording may be updated only in a separate bounded docs lane.",
            "GitHub Release artifact publication remains blocked pending exact v0.3.0 artifact evidence and",
            "npm publication remains blocked pending exact v0.3.0 vendor/package evidence and a later npm",
            "npm package metadata remains at `@docushell/ethos-pdf@0.2.1`",
            "Release tag creation remains blocked pending explicit release-tag approval.",
            "Package tag creation remains blocked pending explicit package-tag approval.",
            "DocuShell integration remains blocked pending closeout or explicit source-dependency integration",
            "Hosted surfaces remain blocked.",
            "Production positioning remains blocked.",
            "Public benchmark reports remain blocked.",
            "Public benchmark claims remain blocked.",
            "Windows packaged artifacts remain blocked.",
            "Bundled project-maintained PDFium builds remain blocked.",
            "`ethos-doc` remains blocked.",
            "`ethos-rag` remains blocked.",
            "PDFium remains caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`.",
        ):
            self.assertIn(expected, raw)
        for forbidden in FORBIDDEN:
            self.assertNotIn(forbidden, lower)
        for marker in PRIVATE_PATH_MARKERS:
            self.assertNotIn(marker, raw)

    def test_v0_3_release_prep_runs_closeout_after_decision_guard(self) -> None:
        makefile = read(MAKEFILE)
        block = target_block("v0-3-release-prep")
        decision_guard = "$(PYTHON) .github/scripts/test_v0_3_0_publication_approval_decision.py"
        closeout_guard = "$(PYTHON) .github/scripts/test_v0_3_0_publication_closeout.py"
        public_surface_guard = "$(PYTHON) .github/scripts/test_public_surface_posture.py"

        self.assertIn(closeout_guard, block)
        self.assertEqual(1, makefile.count(closeout_guard))
        self.assertLess(block.index(decision_guard), block.index(closeout_guard))
        self.assertLess(block.index(closeout_guard), block.index(public_surface_guard))


if __name__ == "__main__":
    unittest.main()
