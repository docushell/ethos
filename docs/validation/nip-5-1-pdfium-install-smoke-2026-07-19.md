# NIP-5.1 PDFium install smoke — 2026-07-19

Acceptance: the decider accepted this isolated macOS `env -i` smoke on 2026-07-20 as sufficient
for NIP-5.1 under `NEXT_IMPLEMENTATION_PLAN.md` revision v1.3. Later platform-specific artifact
tasks retain their own target-platform validation requirements.

Environment: macOS 26.5.1 arm64. The smoke used `env -i`, a fresh `HOME`, and a fresh PDFium
destination under `/tmp`; no preconfigured `ETHOS_PDFIUM_LIBRARY_PATH` was inherited.

```sh
env -i HOME=/tmp/ethos-nip-5-1-clean-home PATH=/usr/bin:/bin:/usr/sbin:/sbin \
  TMPDIR=/tmp scripts/fetch-pdfium.sh /tmp/ethos-nip-5-1-clean-env-pdfium
```

Result: exit `0`; archive sha256 verified before extraction; runtime-library sha256 verified
after extraction; the script printed the exact `ETHOS_PDFIUM_LIBRARY_PATH` export.

```sh
env -i PATH=/usr/bin:/bin:/usr/sbin:/sbin \
  ETHOS_PDFIUM_LIBRARY_PATH=/tmp/ethos-nip-5-1-clean-env-pdfium/lib/libpdfium.dylib \
  target/debug/ethos doctor --require-pdfium
```

Result: exit `0`; doctor reported `usable` and confirmed the pinned runtime sha256.

The license-clean `fixtures/synthetic/simple-text/document.pdf` parse was then run twice under the
same empty environment. `cmp` passed and both outputs had sha256
`e6e70e38e07d8087dae5d1323410d6fcd08eda7b976d33bf34387c872c58341a`.

A wheel was built with `pip wheel --no-deps --no-build-isolation`, installed into a fresh Python
3.12 virtual environment, and `python -m ethos_pdf` printed the same fetch, export, doctor, pin,
and no-auto-download guidance as the npm postinstall test.

Validation also passed:

```text
cargo build --locked --workspace
cargo test --locked --workspace
make verify-alpha
cargo test --locked -p ethos-cli --test doctor
make python-surface-test
python3 .github/scripts/test_pdfium_manual_setup_contract.py
python3 .github/scripts/test_npm_binary_package_scaffold.py
npm --prefix packages/npm/ethos-pdf test
python3 .github/scripts/public_boundary_claims_gate.py
git diff --check
```

No registry action ran. PDFium remains caller-provided and neither package downloads it
automatically.
