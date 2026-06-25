# v0.2.0 Package Build Evidence Validation - 2026-06-25

Validated source HEAD before this record: `977306e`.

v0.2.0 package/build source commit:
`977306eb19dbd4070a600bff36e6f52a1e26f776`.

v0.2.0 package/build source tree:
`6ad9746f54c75985ad1069b73926e1877bf7d848`.

Status: **local package/build evidence recorded; publication and installable wording remain blocked**

This record captures local package/build checks after v0.2.0 source/package metadata activation and
after the draft CLI artifact workflow smoke expectation was aligned to `ethos 0.2.0`. It does not
approve PyPI upload, `npm publish`, GitHub Release artifact upload, release tags, package tags,
installable `0.2.0` public wording, hosted surfaces, production positioning, Windows packaged
artifacts, bundled project-maintained PDFium builds, public benchmark reports or claims,
`ethos-doc`, or `ethos-rag`.

## Subject

- Repository: `docushell/ethos`
- Lane: v0.2.0 local package/build checks
- Source commit: `977306eb19dbd4070a600bff36e6f52a1e26f776`
- Source tree: `6ad9746f54c75985ad1069b73926e1877bf7d848`
- Python wheel candidate: `ethos_pdf-0.2.0-py3-none-any.whl`
- Python wheel SHA256:
  `5eb6eabb1d3e8a4d6d5f0280741a89103701c13706182e9004d5bf6ec2402ef4`
- macOS arm64 draft CLI archive: `ethos-macos-arm64.tar.gz`
- macOS arm64 draft CLI archive SHA256:
  `2a41e3457cc074394ad0e347c967d8e90e353a1179d8beaa2dda82c2725ad84a`
- npm dry-run package id: `@docushell/ethos-pdf@0.2.0`
- npm dry-run shasum: `42a0d591e6dd55ee0a9b6ed9976e455786b643c0`
- npm dry-run integrity:
  `sha512-98NfgYjTl49v+gahz+lrnOk3BDEvnDGYwHEIAWknksJIiwfZ7thzP0Q2WMZFJpwfVW1C/9oeccG5b5lbwmlFiA==`

## Baseline Gates

Commands:

```sh
python3 .github/scripts/test_release_artifact_workflow_prep.py
cargo build --locked --release -p ethos-cli
make python-surface-test PYTHON=python3
npm test --prefix packages/npm/ethos-pdf
```

Results:

```text
test_release_artifact_workflow_prep.py: PASS (5 tests)
cargo build --locked --release -p ethos-cli: PASS
python-surface-test: PASS (34 tests)
npm test --prefix packages/npm/ethos-pdf: PASS
```

The draft artifact workflow now passes `--expected-version "ethos 0.2.0"` to
`smoke_release_cli_artifact.py`.

## Python Wheel Evidence

Command:

```sh
SOURCE_DATE_EPOCH=0 python3 -m build --wheel --outdir <temp-dist>
```

Result:

```text
Successfully built ethos_pdf-0.2.0-py3-none-any.whl
```

Wheel metadata:

```text
Name: ethos-pdf
Version: 0.2.0
Summary: Python wrapper for the Ethos document evidence CLI.
License-Expression: Apache-2.0
Requires-Python: >=3.8
```

Wheel file list:

```text
ethos_pdf-0.2.0.dist-info/METADATA
ethos_pdf-0.2.0.dist-info/RECORD
ethos_pdf-0.2.0.dist-info/WHEEL
ethos_pdf-0.2.0.dist-info/licenses/LICENSE
ethos_pdf-0.2.0.dist-info/licenses/NOTICE
ethos_pdf-0.2.0.dist-info/top_level.txt
ethos_pdf/__init__.py
ethos_pdf/_cli.py
```

Install and wrapper smoke:

```sh
python3 -m pip install --no-deps --force-reinstall --target <temp-install> ethos_pdf-0.2.0-py3-none-any.whl
PYTHONPATH=<temp-install> python3 -c '<verify-anchor-smoke>'
```

Result:

```text
Successfully installed ethos-pdf-0.2.0
0.2.0
True
bound
```

The wrapper smoke used the local macOS arm64 draft CLI artifact, verified
`examples/verify/native_grounded_citations.json` against `schemas/examples/document.example.json`,
and anchored `schemas/examples/evidence-anchor-request.example.json`.

## CLI Artifact Evidence

Commands:

```sh
cargo build --locked --release -p ethos-cli
tar -C target/release-artifacts -czf target/release-artifacts/ethos-macos-arm64.tar.gz ethos-macos-arm64
shasum -a 256 target/release-artifacts/ethos-macos-arm64.tar.gz
python3 .github/scripts/write_release_artifact_inventory.py --target macos-arm64
python3 .github/scripts/smoke_release_cli_artifact.py --expected-version "ethos 0.2.0" --target macos-arm64
python3 .github/scripts/validate_release_artifact_inventory.py target/release-artifacts/ethos-macos-arm64.inventory.json
```

Inventory result:

```text
schema: ethos.release_artifact_inventory.v1
status: draft_not_release_ready
artifact_class: github-release-binary
target: macos-arm64
artifact: ethos-macos-arm64.tar.gz
sha256: 2a41e3457cc074394ad0e347c967d8e90e353a1179d8beaa2dda82c2725ad84a
pdfium_policy: caller-provided
publication: blocked
```

Smoke result:

```text
schema: ethos.release_artifact_smoke.v1
target: macos-arm64
version_stdout: ethos 0.2.0
missing_pdfium_exit_code: 12
help_command_groups: doc, rag, security, verify, fingerprint
```

Linux x64 CLI artifact evidence remains required before any two-platform GitHub Release artifact
approval or npm vendor refresh decision.

## npm Evidence And Blocker

Commands:

```sh
npm test --prefix packages/npm/ethos-pdf
npm pack --dry-run --json
node packages/npm/ethos-pdf/bin/ethos-pdf.js --version
```

Results:

```text
platform selection ok
vendor assembly ok
name: @docushell/ethos-pdf
version: 0.2.0
filename: docushell-ethos-pdf-0.2.0.tgz
entryCount: 11
size: 1833226
unpackedSize: 3934993
shasum: 42a0d591e6dd55ee0a9b6ed9976e455786b643c0
integrity: sha512-98NfgYjTl49v+gahz+lrnOk3BDEvnDGYwHEIAWknksJIiwfZ7thzP0Q2WMZFJpwfVW1C/9oeccG5b5lbwmlFiA==
node packages/npm/ethos-pdf/bin/ethos-pdf.js --version: ethos 0.1.2
```

The npm package metadata and dry-run package structure are `0.2.0`, but npm artifact candidacy
remains blocked because the checked-in vendored binaries still expose `ethos 0.1.2`. Do not approve
`npm publish` for v0.2.0 until v0.2.0 macOS arm64 and Linux x64 CLI artifacts are both available,
`prepare-vendor` refreshes the payload from those artifacts, and the installed npm CLI smoke reports
`ethos 0.2.0`.

## Boundary

- PyPI upload remains blocked.
- `npm publish` remains blocked.
- GitHub Release `v0.2.0` artifact upload remains blocked.
- Linux x64 draft CLI artifact evidence remains required.
- npm vendor refresh remains blocked until both v0.2.0 CLI artifact payloads exist.
- Release tag creation remains blocked.
- Package tag creation remains blocked.
- Installable `0.2.0` public wording remains blocked.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- Windows packaged artifacts remain blocked.
- Bundled project-maintained PDFium builds remain blocked.
- `ethos-doc` remains blocked.
- `ethos-rag` remains blocked.

## Result

```text
Python wheel local build and wrapper smoke: PASS
macOS arm64 draft CLI artifact local build and smoke: PASS
npm metadata and dry-run package structure: PASS
npm v0.2.0 artifact candidacy: BLOCKED by vendored ethos 0.1.2 payload
```
