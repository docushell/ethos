# v0.3.0 Package Build Evidence Validation - 2026-07-01

Validated source HEAD before this record: `4b6d219`.

v0.3.0 package/build evidence source commit:
`4b6d219df1757b6e4728c16c8023bee5c8cf8962`.

v0.3.0 package/build evidence source tree:
`2920f830f92f8290c2bf4cc661874c2641499688`.

Status: **local Rust and Python package evidence recorded; publication and installable wording remain blocked**

This record captures the first local package/build evidence after `v0.3.0` source metadata
activation. It validates that the current source can assemble candidate Rust crate artifacts and a
candidate Python wheel for the app-answer-release contract without publishing anything and without
changing public install wording.

## Subject

- Repository: `docushell/ethos`
- Lane: v0.3.0 local package/build evidence
- Source commit: `4b6d219df1757b6e4728c16c8023bee5c8cf8962`
- Source tree: `2920f830f92f8290c2bf4cc661874c2641499688`
- Rust candidate packages: `ethos-doc-core`, `ethos-verify`, and `ethos-pdf`
- Python candidate package: `ethos-pdf==0.3.0`
- Python candidate wheel: `ethos_pdf-0.3.0-py3-none-any.whl`
- npm package metadata remains `@docushell/ethos-pdf@0.2.1`

## Rust Package Evidence

Command:

```sh
python3 .github/scripts/package_publication_candidate_activation.py --json
```

Result:

```text
status: pass
candidate_version: 0.3.0
candidate_packages: ethos-doc-core, ethos-verify, ethos-pdf
registry_equivalent_consumer_check: pass
package_publication_approved: false
public_installation_approved: false
```

Candidate crate artifacts:

```text
ethos-doc-core-0.3.0.crate
sha256: 7ba41a2ae299a53a4677153beaaec5ed486a07b5da08b2ef13974b9a0be141cb

ethos-verify-0.3.0.crate
sha256: 00f001455ca207e65aaf464551d3ba05945cda0b06e9e1036f49ac587accbb95

ethos-pdf-0.3.0.crate
sha256: c2f4f2ccb6de6e54cd3257597cd28e7f6dec2a6d22befbd230d2c4cf31931cfd
```

The candidate helper assembled the package artifacts in a temporary workspace and ran the
registry-equivalent consumer check offline.

## Python Wheel Evidence

Command:

```sh
SOURCE_DATE_EPOCH=0 python3 -m build --wheel --outdir <temp-dist>
```

Result:

```text
Successfully built ethos_pdf-0.3.0-py3-none-any.whl
```

Wheel SHA256:

```text
9eb106deafcd1d9717e5e7b67dc9413180421aba25a5257266352d09540b3265
```

Wheel metadata:

```text
Name: ethos-pdf
Version: 0.3.0
Summary: Python wrapper for the Ethos document evidence CLI.
License-Expression: Apache-2.0
Requires-Python: >=3.8
Tag: py3-none-any
```

Wheel file list:

```text
ethos_pdf/__init__.py
ethos_pdf/_cli.py
ethos_pdf-0.3.0.dist-info/METADATA
ethos_pdf-0.3.0.dist-info/RECORD
ethos_pdf-0.3.0.dist-info/WHEEL
ethos_pdf-0.3.0.dist-info/licenses/LICENSE
ethos_pdf-0.3.0.dist-info/licenses/NOTICE
ethos_pdf-0.3.0.dist-info/top_level.txt
```

Install and helper smoke:

```sh
python3 -m pip install --no-deps --force-reinstall --target <temp-install> ethos_pdf-0.3.0-py3-none-any.whl
PYTHONPATH=<temp-install> python3 -c '<import-and-app-answer-release-helper-smoke>'
```

Result:

```text
Successfully installed ethos-pdf-0.3.0
0.3.0
EthosCli
True
True
certified
claim-revenue
```

The helper smoke imported `EthosCli`, `proof_summary`, and `app_answer_release_decision` from the
installed wheel, then checked that a direct, grounded `source_fact` claim with a reusable Ethos
check ID returns `app_status: certified`.

## Explicit Out Of Scope

- CLI artifact evidence remains out of scope for this record.
- npm package evidence remains out of scope for this record.
- GitHub Release artifact evidence remains out of scope for this record.
- DocuShell integration evidence remains out of scope for this record.

## Boundary

- This record does not approve `cargo publish`.
- This record does not approve PyPI upload.
- This record does not approve `npm publish`.
- This record does not approve GitHub Release artifact publication.
- This record does not approve release tag creation.
- This record does not approve package tag creation.
- This record does not approve installable `0.3.0` public wording.
- This record does not approve DocuShell integration.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Windows packaged artifacts remain blocked.
- Bundled project-maintained PDFium builds remain blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- `ethos-doc` remains blocked.
- `ethos-rag` remains blocked.
- PDFium remains caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`.

## Commands

```sh
python3 .github/scripts/test_v0_3_0_package_build_evidence.py
make v0-3-release-prep PYTHON=python3
python3 .github/scripts/check_release_boundary_paths.py
python3 .github/scripts/validation_record_integrity.py
git diff --check
```

## Result

```text
v0.3.0 Rust candidate package assembly: PASS
v0.3.0 registry-equivalent Rust consumer check: PASS
v0.3.0 Python wheel build/install/helper smoke: PASS
publication, artifacts, tags, installable wording, npm alignment, and DocuShell integration: BLOCKED
```
