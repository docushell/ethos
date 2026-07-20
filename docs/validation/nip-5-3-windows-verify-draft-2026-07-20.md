# NIP-5.3 Windows Verify-Only Draft — 2026-07-20

Status: blocked pending execution on a Windows x64 runner. Implementation and host-safe validation
are complete, but this record does not claim a linked or executed Windows artifact.

## Implemented Contract

- `scripts/build-windows-verify-candidate.py` emits a deterministic ZIP with fixed timestamps,
  canonical ordering/modes, a blocked inventory manifest, `ethos.exe`, project notices, a
  two-command PowerShell quickstart, and grounded verification fixtures.
- `.github/workflows/release.yml` builds on `windows-latest`, assembles the candidate twice,
  rejects byte differences, runs the bundled verification twice, and confirms PDF parsing exits
  `12` without caller-provided PDFium.
- Inventory validation marks the target `windows-x64`, scope `verify-only`, PDFium absent, and
  publication blocked.
- `docs/windows-verify.md` records the two-command verification path and citation-grounding
  boundary.

## Host-Safe Validation

Passed:

```text
make windows-verify-candidate-contract PYTHON=python3
cargo check --locked -p ethos-cli --target x86_64-pc-windows-msvc
```

The candidate contract builds fixture archives twice and compares the archive and checksum bytes.
It also covers required contents, fixed ZIP timestamps, verify-only/no-PDFium manifest fields, and
fail-closed missing-binary behavior. The release smoke's Windows fixture verifies twice with
byte-identical stdout and observes missing-PDFium exit `12`.

The Windows cross-target check initially identified one Unix-only `CString` import; gating that
import with `#[cfg(unix)]` made the Windows check warning-free.

## Blocker and Exact Unblock

The macOS host has no Windows execution runtime or MSVC linker. A real cross-target build reached
the final link step and stopped with:

```text
error: linker `link.exe` not found
```

To unblock NIP-5.3, run the new `windows-verify-draft-artifact` GitHub Actions job from reviewed
source and retain its green run URL, ZIP checksum/inventory, and smoke JSON. The job supplies the
required Windows linker and executes the actual `.exe`. Only then may the ledger move to `done`.

No registry, tag, or GitHub Release action ran. The workflow uploads draft CI evidence only, no
PDFium DLL is bundled, and no approved public claim string changed.
