# Windows x64 Verify-Only Draft

Status: NIP-5.3 draft artifact contract. No Windows artifact is published or approved by this
document.

The Windows x64 archive provides the JSON citation-verification path without bundling PDFium.
After downloading `ethos-windows-x64.zip`, the bundled grounded example runs in two PowerShell
commands:

```powershell
Expand-Archive .\ethos-windows-x64.zip -DestinationPath .
.\ethos-windows-x64\ethos.exe verify .\ethos-windows-x64\verify-example\document.json --citations .\ethos-windows-x64\verify-example\citations.json --fail-on-ungrounded
```

Exit `0` means every required check grounded against the supplied source representation. Exit `1`
means an ungrounded report was produced; exit `2` or greater is an error and must fail closed.
Ethos verifies citation grounding against the supplied source representation, not semantic truth.

## Artifact Boundary

The deterministic ZIP contains:

- `ethos.exe`;
- project `LICENSE` and `NOTICE`;
- `PDFIUM-MANUAL-SETUP.md` and `VERIFY-QUICKSTART.txt`;
- the grounded document/citations example;
- a canonical `artifact-manifest.json` marked `draft_not_release_ready`, `verify-only`, and
  `publication: blocked`.

It contains no PDFium DLL. `ethos doc parse` therefore exits with the stable missing-capability
code `12` unless a caller separately configures `ETHOS_PDFIUM_LIBRARY_PATH`. Windows-with-PDFium
packaging remains outside NIP-5.3 and follows the ADR-0015 decision.

## Build and Validation

`.github/workflows/release.yml` builds the Windows CLI on `windows-latest`, assembles the ZIP
twice, rejects differing bytes, runs the bundled verification fixture twice, checks byte-identical
reports, and confirms missing PDFium fails closed. The workflow uploads draft CI evidence only;
it does not create or edit a GitHub Release.
