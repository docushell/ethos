# Security Policy

Ethos treats PDFs as hostile input. The parser core is C++ (PDFium) behind a Rust boundary;
hosted/service deployments must use sandbox/subprocess mode (CPU/memory/wall-time/fd/output
limits, no network, no child processes, no shell, narrow IPC). In-process parsing is for
local/offline CLI use with an explicit threat model. See PRD §6.3 and §10.

## Reporting a vulnerability

Use **GitHub private vulnerability reporting** (Security → Report a vulnerability) on this
repository. Do not open public issues for vulnerabilities.

- Acknowledgement target: 48 hours.
- Coordinated disclosure: we will agree on a timeline with you; default 90 days.
- In-scope: parser memory safety, sandbox escapes, path traversal in CLI/MCP surfaces,
  implemented hidden-content exclusion bypasses, determinism-contract violations exploitable for
  cache poisoning, dependency advisories in the base tree.
- Out-of-scope until the relevant surface ships: hosted services (none exist; Ethos is OSS-only).

## Hardening guarantees (base build)

- No embedded JavaScript execution; V8 and XFA disabled in the PDFium build (ADR-0002).
- No external link following; no external resource fetches; **no network APIs in base crates**
  (enforced three ways: dependency policy, clippy disallowed-API lints, runtime no-egress test).
- Resource limits: max file size, page count, parse time; stable failure codes — a PDF that
  cannot be parsed safely fails with a stable error code, never a panic.
- Current `security_report.json` findings are limited to warnings emitted by the canonical
  document. Image-only pages are surfaced today. Hidden, off-page, low-contrast text and PDF object
  inventories (annotations, actions, attachments, scripts, links) are not detected by the base
  parser yet; treat parsed document text and empty inventory arrays as untrusted, not as a clean
  bill of health.

## Supported versions

Pre-release: only `main` receives fixes. From the first public release, the latest minor
release line is supported; security regressions are release blockers (OpenSSF Scorecard is
tracked monthly after launch).
