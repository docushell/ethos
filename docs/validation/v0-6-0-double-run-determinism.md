# v0.6.0 Double-Run Determinism Evidence

Status: **three of four §11.4 rows evidenced; DocuShell mapper outstanding** (2026-07-31).

Covers release-prep §11.4. Recorded on `darwin:x64` against a CLI built from source, with no
PDFium configured.

## Method

Each producer ran twice over identical pinned inputs, and outputs were compared with `cmp`.

```sh
node   examples/map-grounding.js fixtures/parser-output.json fixtures/page-metadata.json out.json
python examples/map_grounding.py fixtures/parser-output.json fixtures/page-metadata.json out.json
ethos  grounding check out.json --source-artifact fixtures/source.pdf --out validation.json
```

## Result

| §11.4 row | Result |
| --- | --- |
| Validation report bytes equal across two runs | **byte-identical** |
| JavaScript mapper bytes equal across two runs | **byte-identical** |
| Python mapper bytes equal across two runs | **byte-identical** |
| DocuShell mapper bytes equal across two runs | **outstanding** — acceptance commit not selected |

Cross-implementation equality, which §11.4 does not require but which the two examples claim:

| Comparison | Result |
| --- | --- |
| JavaScript output vs Python output | **byte-identical** |
| Either output vs the packaged `fixtures/grounding.json` | **byte-identical** |

## Recorded hashes

```text
mapper artifact      sha256:d83a67d1d79f8bc82d36516a548a4a8c46796b071637e3f830e80dbd295bc8b3
validation report    sha256:090a69f3a9ed25de9cd511d27a55e05557d5db9cebccfbc2dbd29f1aaf3251f3
```

The mapper artifact hash equals the `representation_sha256` reported by `grounding check`, which is
the expected identity: that field hashes the exact accepted Grounding JSON bytes. `source_binding`
was `matched` against the pinned `fixtures/source.pdf`.

## Scope

This evidences producer determinism only. It is not a claim about cross-platform reproducibility,
which the project does not make for rendered artifacts, and it does not cover the DocuShell
acceptance mapper. The single-versus-batch verification equality row in §11.4 is covered by the
Rust integration suite rather than here.
