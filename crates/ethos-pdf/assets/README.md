# ethos-pdf assets (WS-ENGINE fills, Milestone A week 2 — ADR-0003)

- `font-substitution-table.json` — versioned missing-font mapping; sha256 goes into
  `profiles/ethos-deterministic-v1.json` → `font_policy.substitution_table.sha256`.
- `ethos-deterministic-v1.json` — crate-local copy of the source-tree deterministic profile used
  by packaged `ethos-pdf` builds. Keep byte-identical to `profiles/ethos-deterministic-v1.json`.
- `fonts/liberation/` — bundled Liberation family (SIL OFL 1.1, ~4 MB); bundle sha256 goes
  into `font_policy.fallback_bundle.sha256`; OFL notice goes into `NOTICE`.

Both hashes are Gate Zero determinism evidence (G3). System-font fallback stays disabled.
