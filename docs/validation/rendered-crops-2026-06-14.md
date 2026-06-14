# Rendered Crop Validation - 2026-06-14

## Purpose

Validate the alpha rendered-crop artifact path for `ethos verify --crop-dir
--crop-source-pdf`.

This record answers two separate questions:

1. Are rendered crop artifacts repeatable across two runs on the same host with pinned PDFium?
2. Are rendered crop artifacts byte-identical across macOS arm64 and Linux x64?

## Subject

- Validation subject commit: `64541dd799cb0fbf1e66fb34be956e64ed6b8429`
- Short commit: `64541dd`
- Bundle used for Linux transfer: `/tmp/ethos-64541dd.bundle`
- Bundle SHA-256: `0d32451b1f0ca5932ad50d10e8e409aaf7779ee2bdf13b6bb2a5529ba04e2737`

The comparison helper was added later in commit `c76dbc9` and was used to classify the
same archived macOS/Linux outputs. It does not change the rendered-crop output produced by
`64541dd`.

## macOS arm64 Environment

- Repo path: `/Users/<private-user-pattern>/Desktop/Stuff/project/repo/ethos`
- Validated commit: `64541dd`
- Local unrelated dirty files at validation time: `README.md`,
  `docs/benchmark-plan.md`
- PDFium library: `/private/tmp/ethos-pdfium/lib/libpdfium.dylib`
- PDFium library SHA-256:
  `1bc45b15466b34cef96641ce25c77a876e70010c6b114f909dda2f5325fc5bd7`
- PDFium artifact: `/private/tmp/ethos-pdfium-mac-arm64.tgz`
- PDFium artifact SHA-256:
  `52e94ca5aa8847934330daf3f8150c190682c5ca93831468794f8b90d4392e40`
- `ETHOS_PDFIUM_VERSION`: `chromium/7881`

Command:

```bash
export ETHOS_PDFIUM_LIBRARY_PATH=/private/tmp/ethos-pdfium/lib/libpdfium.dylib
export ETHOS_PDFIUM_VERSION=chromium/7881
export ETHOS_PDFIUM_ARTIFACT_PATH=/private/tmp/ethos-pdfium-mac-arm64.tgz

make verify-rendered-crops
```

Outcome:

```text
ok    parsed document JSON is byte-identical across runs
ok    verification report JSON is byte-identical across runs
ok    crop descriptors crop-17348b1d50b795bd31b8cc4d64bf7b3df8e2fc799a602373d6a2c4d25df7cadd.json is byte-identical across runs
ok    rendered PNG crops crop-17348b1d50b795bd31b8cc4d64bf7b3df8e2fc799a602373d6a2c4d25df7cadd.png is byte-identical across runs
ok    rendered descriptors bind report, source PDF fingerprint, and PNG hashes

rendered crop determinism checks passed
```

macOS run details:

```text
document_fingerprint sha256:7164f43f104dc248193f12ea828e0ab857eae194210114c6f6c0160fd643c87b
source_fingerprint   sha256:f2f6ab91c696a4dffd96512456184451634fda22e19face9f636f3b69c6286f3
payload_sha256       db600b33362c6897c2755e74c0236d97f98eee9898c527baad1c6938dbaa191e
document_json_sha256 93e9f4d066da206fdf9e375689a903279a61330666e00081e993735b8696a1b2
report_json_sha256   59280703296739ac56c41c1b0d9fe48e8d79afce652217bfba90e1a236528c84
evidence_bbox        [7392, 5482, 19378, 7226]
descriptor_ref       crop-17348b1d50b795bd31b8cc4d64bf7b3df8e2fc799a602373d6a2c4d25df7cadd.json
descriptor_sha256    44de475e48358a0127e8d568d023644dd50febecf8367b3521f970c4cf726bd6
rendered_ref         crop-17348b1d50b795bd31b8cc4d64bf7b3df8e2fc799a602373d6a2c4d25df7cadd.png
rendered_sha256      adff168dc8cc7aa78d498a166141fdce545a233ad367e615d84dff27a0ca84a6
rendered_size_px     121 x 19
png_file_size        9283
```

## Linux x64 Environment

- Repo path: `/scratch/<private-user-pattern>/ethos-rendered-crop-64541dd`
- Validated commit: `64541dd`
- Working tree at validation time: clean
- Host architecture: `x86_64`
- `rustc`: `1.87.0 (17067e9ac 2025-05-09)`
- `cargo`: `1.87.0 (99624be96 2025-05-06)`
- `python3`: `3.13.13`
- GNU Make: `4.2.1`
- PDFium library: `/home/<private-user-pattern>/ethos-bench/pdfium/lib/libpdfium.so`
- PDFium library SHA-256:
  `f728930966f503652b92acc89b9374a2eeca00ce42e26dccd3e4b5c5161b2d64`
- PDFium artifact: `/home/<private-user-pattern>/ethos-bench/artifacts/pdfium-linux-x64.tgz`
- PDFium artifact SHA-256:
  `1470e21b8b4a3b4ad7f85684e2da11d94f3b69a86d81dee11b9b6709d927ac1d`
- Debug binary: `target/debug/ethos`
- Debug binary SHA-256:
  `0054dce0802f29f55f03bde6b7f8540eadd6db3e16c184e8650e6da05002063b`
- `ETHOS_PDFIUM_VERSION`: `chromium/7881`

Command:

```bash
export ETHOS_PDFIUM_LIBRARY_PATH=/home/<private-user-pattern>/ethos-bench/pdfium/lib/libpdfium.so
export ETHOS_PDFIUM_VERSION=chromium/7881
export ETHOS_PDFIUM_ARTIFACT_PATH=/home/<private-user-pattern>/ethos-bench/artifacts/pdfium-linux-x64.tgz

make verify-rendered-crops
```

Outcome:

```text
ok    parsed document JSON is byte-identical across runs
ok    verification report JSON is byte-identical across runs
ok    crop descriptors crop-338ee9490833980141deb5be0fc9cb1f669f60f3ca9552b58aabb227194c74b9.json is byte-identical across runs
ok    rendered PNG crops crop-338ee9490833980141deb5be0fc9cb1f669f60f3ca9552b58aabb227194c74b9.png is byte-identical across runs
ok    rendered descriptors bind report, source PDF fingerprint, and PNG hashes

rendered crop determinism checks passed
```

Linux run details:

```text
document_fingerprint sha256:7164f43f104dc248193f12ea828e0ab857eae194210114c6f6c0160fd643c87b
source_fingerprint   sha256:f2f6ab91c696a4dffd96512456184451634fda22e19face9f636f3b69c6286f3
payload_sha256       db600b33362c6897c2755e74c0236d97f98eee9898c527baad1c6938dbaa191e
document_json_sha256 4815053f08a8b40fb5e25eabce09f23a8a8eb46387f546e74fab11f2d138ff26
report_json_sha256   e9e69f28ad8f639d002b75fc51cf63d896857827c1b5db2c69b4e22ff1a1d8e9
evidence_bbox        [7385, 5477, 19385, 7234]
descriptor_ref       crop-338ee9490833980141deb5be0fc9cb1f669f60f3ca9552b58aabb227194c74b9.json
descriptor_sha256    338a00377c401124f024cfe618e12e31382e6102db6102b636adefd6789a81ee
rendered_ref         crop-338ee9490833980141deb5be0fc9cb1f669f60f3ca9552b58aabb227194c74b9.png
rendered_sha256      88de1db03898ecfffeada4c4cc93e5ce7e79c8d05aacece492f0f43a04ecc7e5
rendered_size_px     121 x 19
png_file_size        9283
```

Transferred Linux artifact:

```text
/tmp/ethos-rendered-crops-linux-x64-64541dd.tgz
SHA-256 514ced8bc9f45315a1fdc11ebea2d8982aafa148e79fee914012f5f7099ecc26
```

## Cross-Platform Comparison

Comparison command shape:

```bash
python3 examples/verify/compare_rendered_crop_runs.py \
  --left-run target/verify-rendered-crops/run1 \
  --left-label macos-arm64 \
  --right-run /tmp/ethos-rendered-crops-linux-x64-64541dd-extract/verify-rendered-crops/run1 \
  --right-label linux-x64
```

Logical identity passed:

```text
document_fingerprint      equal
source_fingerprint        equal
payload_sha256            equal
report_document_fingerprint equal
all_evidence_grounded     equal
check id/status/page      equal
descriptor_count          equal
rendered_size             equal
png_count                 equal
png_file_size             equal
```

Rendered artifact equality failed:

```text
macOS evidence_bbox       [7392, 5482, 19378, 7226]
Linux evidence_bbox       [7385, 5477, 19385, 7234]

macOS descriptor_ref      crop-17348b1d50b795bd31b8cc4d64bf7b3df8e2fc799a602373d6a2c4d25df7cadd.json
Linux descriptor_ref      crop-338ee9490833980141deb5be0fc9cb1f669f60f3ca9552b58aabb227194c74b9.json

macOS rendered_sha256     adff168dc8cc7aa78d498a166141fdce545a233ad367e615d84dff27a0ca84a6
Linux rendered_sha256     88de1db03898ecfffeada4c4cc93e5ce7e79c8d05aacece492f0f43a04ecc7e5
```

The divergence starts before PNG encoding: the evidence bbox differs slightly across
platforms. Since crop descriptor names and PNG names are derived from crop identity, they also
differ.

## Conclusion

Same-host rendered crop repeatability with pinned PDFium: **pass** on macOS arm64 and Linux
x64.

Cross-platform rendered crop byte identity: **fail** on this fixture.

The supported claim is:

```text
Ethos rendered crop artifacts are same-host repeatable with pinned PDFium.
Cross-platform rendered crop bit-identical output is not currently proven.
```

Do not claim cross-platform bit-identical rendered crops from this evidence.

## Follow-Up

- Keep rendered crops as source-bound audit artifacts, not part of the core cross-platform
  deterministic payload claim.
- Decide whether crop artifact filenames should be derived from logical evidence identity
  instead of raw bbox-derived identity. That could make references more stable across hosts,
  while descriptors still record exact platform-specific bbox and PNG hashes.
- Do not chase cross-platform PNG equality unless a product requirement depends on it.
