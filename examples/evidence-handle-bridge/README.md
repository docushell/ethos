# Evidence Handle Bridge

This dependency-free walkthrough turns trusted retrieval records into opaque evidence handles,
hydrates recorded structured model output, and projects states from a pinned verification report.
It makes no model, API, CLI, network, or PDFium call. The report is a recorded fixture bound to the
hydrated citations; Ethos verifies citation grounding, not semantic truth.

Run `PYTHONPATH=python python3 examples/evidence-handle-bridge/run.py --out-dir target/example`.

Structured `claims[].evidence_id` values are the only citation channel. The model-authored
`answer` is inert prose: consumers must not parse `[ev_...]`-like tokens, link them, or style them
as verified. A deterministic presentation sanitizer may remove such tokens, but must never
reconcile them with structured claims. Display and excerpt mutations cannot affect hydration or
projected state.

The offline Python suite covers grounded and failed claims, dangling and duplicate handles,
stale and mismatched fingerprints, ambiguous locators, uncited retrieved evidence, repeated
handle use, display/excerpt mutation, conflicting handle-shaped prose, and byte-identical
projection. This example itself is executed twice by the Python release gate against the
repository's canonical verification-report fixture.
