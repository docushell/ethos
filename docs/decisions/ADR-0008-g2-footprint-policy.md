# ADR-0008: Gate Zero G2 Footprint Policy

- Status: **Accepted**
- Date: 2026-06-12
- Decider: Gate Zero decider
- Supersedes: the Gate Zero G2 ratio-as-hard-gate wording in PRD §1.3, IMPLEMENTATION_PLAN §6.4, and ADR-0005's template text.

## Context

The original Gate Zero G2 rule required Ethos' base parser footprint to be both:

- no more than 30 MB, and
- no more than one tenth of the measured OpenDataLoader installed footprint.

The first macOS arm64 G2 run measured the full Phase 1 base parser footprint as:

- Ethos CLI: 1,277,392 bytes
- pinned PDFium dynamic library: 7,732,336 bytes
- total Ethos base parser footprint: 9,009,728 bytes
- OpenDataLoader installed footprint: 35,753,427 bytes
- Ethos/OpenDataLoader ratio: 0.25199620724469296

That result passed the 30 MB cap and the PDFium V8/XFA policy, but failed the one-tenth
OpenDataLoader ratio. Treating that ratio miss as a parser-core kill switch would make the Phase 1
PDFium path fail for a reason that is mostly the required native PDFium payload, not the Ethos
parser itself.

Ethos' product direction is now explicitly a verification and grounding layer with a deterministic
parser underneath. Parser ownership is justified by deterministic canonical output, fingerprints,
provenance, citation inspection, and benchmarked trust, not by footprint alone.

## Decision

Gate Zero G2 remains a hard installed-footprint and security-profile gate, but the one-tenth
OpenDataLoader comparison is now a claim threshold, not a hard parser-core decision threshold.

Hard G2 pass requires:

- measured base parser footprint no more than 30,000,000 bytes,
- PDFium V8 disabled,
- PDFium XFA disabled,
- no required network downloads in the base parser surface,
- full footprint evidence recorded for the exact artifact set being evaluated.

The Ethos/OpenDataLoader ratio is still measured and reported. Ethos may claim "one tenth of
OpenDataLoader's installed footprint" only when the measured ratio is less than or equal to 0.1.

## Consequences

- Existing strict-ratio macOS G2 evidence remains useful historical evidence.
- The Gate Zero G2 runner must report whether the one-tenth OpenDataLoader claim is supported.
- A G2 hard-gate failure still blocks parser-core expansion.
- A G2 claim-threshold miss does not by itself force fallback.
- Public claims must distinguish "under 30 MB" from "one tenth of OpenDataLoader"; the latter is
  unsupported until the measured ratio satisfies the claim threshold.
