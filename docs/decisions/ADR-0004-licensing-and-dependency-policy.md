# ADR-0004: Licensing and Dependency Policy

- Status: Accepted (recorded from PRD v3.5 §12, §15)
- Date: 2026-06-11
- Governs: IMPLEMENTATION_PLAN §2 row 0.6, §4 invariant 6; PRD §12

## Context

Apache-2.0 maximizes enterprise and OSS adoption; restrictive licenses would reduce adoption and ecosystem trust. The base install must stay free of copyleft and model-license-restricted dependencies, including via optional modules' default features.

## Decision

- **License: Apache-2.0** for Ethos Core (all crates in this workspace).
- **Contribution governance: DCO**, not CLA. CI enforces `Signed-off-by` on every commit.
- **Base dependency allowlist** (enforced by `deny.toml`): Apache-2.0, MIT, BSD-2-Clause, BSD-3-Clause, ISC, Zlib, Unicode-DFS-2016, CC0-1.0, MPL-2.0.
- **Denied in the base tree** (including optional modules' default features): GPL, AGPL, LGPL, source-available, custom-condition, and model-license-restricted licenses.
- Optional OCR/VLM/layout-ML integrations needing restricted dependencies live behind explicit **non-default features or separate packages** and publish license manifests.
- **Exceptions only by ADR before merge.**
- **`NOTICE`** is maintained and includes at minimum PDFium BSD-3 notices and Liberation SIL OFL 1.1 notices (added when those assets land in WS-ENGINE).
- Network-capable crates (`reqwest`, `hyper`, `ureq`, `curl`, socket-bearing crates) are banned from base crates via `deny.toml` bans + review (invariant 5a).

## Consequences

- `deny.toml` at the workspace root implements this policy; `ci.yml` runs `cargo-deny` on every PR.
- Generated third-party notices are reviewed at release; the release pipeline publishes the license/NOTICE manifest with artifacts.
- MuPDF (AGPL) and Poppler (GPL) are structurally excluded as base backends (PRD §6.2).
