# First Public Release Artifact Evidence Validation - 2026-06-23

- Validated source HEAD before this record: `7c99a33`

Release-candidate source commit: `7c99a338819d580dd0537af9062d069c052944ac`

Release-candidate source tree: `7f7952c001256a493b3fce81ad7a1851a495a34a`

Status: **artifact evidence recorded; public artifact publication remains blocked**

This record captures local first public release artifact evidence after
`make release-candidate-prep PYTHON=/private/tmp/ethos-jsonschema-venv-main/bin/python` passed on
the release-candidate source state. It does not approve publication to GitHub Releases, PyPI, npm,
or any hosted surface, and it does not approve launch wording.

## Release-Candidate Validation

Command:

```sh
make release-candidate-prep PYTHON=/private/tmp/ethos-jsonschema-venv-main/bin/python
```

Result: **pass**

Covered:

- public-surface posture guard;
- claims gate;
- schema/example validation;
- first public release scope decision guard;
- Python public API policy guard;
- Python wrapper tests;
- npm binary package scaffold guard;
- npm platform-selection test;
- PDFium manual setup contract guard;
- draft release artifact workflow guard;
- release-candidate prep guard;
- release reproducibility scaffold guard;
- launch-copy approval scaffold guard;
- targeted CLI smoke test;
- diff hygiene.

## macOS arm64 CLI Draft Artifact Evidence

Artifact: `ethos-macos-arm64.tar.gz`

SHA256: `35c7cc19ea51231edb1a0cfb6d160d3a2e620ba9357d116ef071f66ebc5e236f`

Inventory:

```json
{
  "artifact": "ethos-macos-arm64.tar.gz",
  "artifact_class": "github-release-binary",
  "pdfium_policy": "caller-provided",
  "publication": "blocked",
  "required_notices": [
    "LICENSE",
    "NOTICE",
    "docs/pdfium-manual-setup.md"
  ],
  "schema": "ethos.release_artifact_inventory.v1",
  "sha256": "35c7cc19ea51231edb1a0cfb6d160d3a2e620ba9357d116ef071f66ebc5e236f",
  "status": "draft_not_release_ready",
  "target": "macos-arm64"
}
```

Smoke evidence:

- archive contains `LICENSE`, `NOTICE`, `ethos`, and `pdfium-manual-setup.md`;
- `ethos --version` prints `ethos 0.1.0`;
- `ethos --help` lists the expected command groups;
- missing PDFium check exits non-zero and reports
  `PDFium not found: set ETHOS_PDFIUM_LIBRARY_PATH to the caller-provided PDFium dynamic library path`;
- missing PDFium check returned `exit_code=12`.

Build caveat:

- release build emitted an existing warning for unused import `Write` in
  `crates/ethos-cli/src/worker.rs`; this should be cleaned before final release approval.

## Python Wheel Evidence

Wheel: `ethos_pdf-0.1.0-py3-none-any.whl`

Result: **build, local install, import, version, and API smoke passed**

Observed:

- `python3 -m build --wheel` built `ethos_pdf-0.1.0-py3-none-any.whl`;
- local install with `python3 -m pip install --force-reinstall --no-deps` succeeded;
- import smoke reported `version 0.1.0`;
- API smoke reported `EthosCli` and `EthosCommandError`.

Packaging caveats to resolve before final release approval:

- Setuptools warned that `project.license` as a TOML table is deprecated.
- Setuptools warned that license classifiers are deprecated in favor of SPDX license expressions.

## npm Package Evidence

Package: `@docushell/ethos-pdf@0.1.0`

Tarball: `docushell-ethos-pdf-0.1.0.tgz`

Result: **pack, local install, metadata, and platform-selection smoke passed**

Observed:

- `npm pack` produced `docushell-ethos-pdf-0.1.0.tgz`;
- package size was `1.7 kB`;
- npm shasum was `cf83c7e0196d451f169f3dcbee26e4d009e5da82`;
- local install succeeded;
- metadata smoke reported `@docushell/ethos-pdf 0.1.0`;
- macOS arm64 and Linux x64 binary paths resolved;
- Windows x64 was rejected as unsupported.

npm caveat to resolve before final release approval:

- The tarball contains no `vendor/` binary payload yet. Final npm publication remains blocked until
  binary payload inclusion is implemented and validated, or a later decider record explicitly keeps
  npm publication blocked.

## Retained Blockers

- Public artifact publication remains blocked.
- Launch wording remains blocked.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- Windows x64 packaged artifacts remain blocked.
- Bundled project-maintained PDFium builds remain blocked.
- `ethos-doc` remains blocked.
- `ethos-rag` remains blocked.

## Result

The local release-candidate evidence is sufficient to continue toward final approval preparation,
but it is not sufficient to publish public artifacts or use launch wording. Final approval still
requires resolving the recorded caveats or explicitly retaining the affected surfaces as blocked.
