# NIP-5.2 `ethos-full` Build Evidence — 2026-07-20

Status: superseded feasibility evidence. ADR-0015 is Accepted for the v0.5.0 release candidate;
publication, target smoke, release gates, registry actions, tags, GitHub Release changes, and
public wording remain blocked until the accepted candidate passes them.

## Inputs

- Candidate builder: `scripts/build-ethos-full-candidate.py`
- Packaging fixture CLI version: published `ethos 0.3.0` macOS arm64 and Linux x64 binaries
  already vendored under `packages/npm/ethos-pdf/vendor/`
- Profile: `profiles/ethos-deterministic-v1.json`
- PDFium: `chromium/7881` / PDFium `151.0.7881.0`, V8 disabled, XFA disabled
- macOS archive sha256:
  `52e94ca5aa8847934330daf3f8150c190682c5ca93831468794f8b90d4392e40`
- Linux archive sha256:
  `1470e21b8b4a3b4ad7f85684e2da11d94f3b69a86d81dee11b9b6709d927ac1d`
- macOS runtime sha256:
  `1bc45b15466b34cef96641ce25c77a876e70010c6b114f909dda2f5325fc5bd7`
- Linux runtime sha256:
  `f728930966f503652b92acc89b9374a2eeca00ce42e26dccd3e4b5c5161b2d64`

The Linux archive was downloaded from the exact profile-pinned URL and verified before
extraction. The builder itself performs no network access.

## Double-Run Results

Each target was assembled twice into separate output directories. `cmp` passed for both the
archive and adjacent inventory.

| Target | Candidate sha256 | Size bytes | Result |
| --- | --- | ---: | --- |
| macOS arm64 | `efd089d5303f2e064ed1d89b4d2605e8da967493a0ae65cc7cc150d48c2d5c97` | 4,266,676 | two builds byte-identical |
| Linux x64 | `6ee170293756309a00a48ef820753a7e8624beac55055b88693ba8170a06d5e5` | 4,510,646 | two builds byte-identical |

Every archive contains the project license/NOTICE, upstream PDFium package license, all files
from the upstream `licenses/` directory, the verified runtime, a relative-path launcher, and a
canonical manifest marked as proposal evidence. The v0.5 builder now produces a separate
release-candidate status and remains non-publishable pending target smoke and release gates.

## Smoke and Fail-Closed Evidence

On macOS arm64, the extracted launcher reported `ethos 0.3.0` and parsed
`fixtures/synthetic/simple-text/document.pdf` twice without an externally configured PDFium
path. The outputs were byte-identical with sha256
`e6e70e38e07d8087dae5d1323410d6fcd08eda7b976d33bf34387c872c58341a`.

Linux execution was not claimed from the macOS host. ADR-0015 requires a Linux x64 smoke before
any Linux candidate can become publishable.

Focused automated tests verify:

- archive, checksum, and inventory double-run byte identity;
- required payload and license-notice coverage;
- proposal-only status and publication blocker;
- runtime path binding in the launcher;
- fail-closed behavior for a runtime hash mismatch or missing PDFium notice.

No registry or release action ran, and no approved public claim string changed.
