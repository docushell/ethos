# v0.6.0 Public Wording Request

Status: **approved 2026-07-31; applied at publication only.** Nothing here is on a public surface
yet, and `test_v0_6_0_version_activation.py` keeps every install command naming the published
0.5.0 until v0.6.0 reaches the registries.

## Revision clause

This wording may be revised without a fresh approval from scratch when either of these happens:

- the outsider clean-room walkthrough finds the mapper guide unclear, or
- business need changes how Ethos should be described.

Revisions go through the normal claims lane: update `README.md` and
`docs/public-boundary-claims.json` together, keep the claims gates green, and note the change in
`CHANGELOG.md`. The claims registry has been revised at v0.2, v0.3, and v0.5, so this is the
established path rather than an exception.

What a revision may **not** do is widen the claim past the "What this request does NOT claim"
section below. Removing one of those limits is a new approval, not a revision.

## Why approving before the walkthrough is sound

The two answer different questions. This wording claims a **capability** — that any parser can
reach the verifier by writing one mapper — and that is already evidenced by the JavaScript, Python,
and DocuShell mappers, none of which needed PDFium. The walkthrough tests **documentation
quality**: whether a stranger can follow the guide.

A poor walkthrough result means the guide needs work. It does not make the capability claim false.

The walkthrough still gates **publication**, because release-prep §5.1 makes an undocumented step a
release blocker. It does not gate this approval.

Release-prep §12 requires that exact public wording be separately approved. This document is the
request. It proposes the minimum wording change v0.6.0 needs, and states plainly what it does not
claim.

## Why a change is needed

`README.md` currently tells readers:

> Grounding JSON is a proposal, not a current feature.

If v0.6.0 publishes, that sentence becomes false. The WP-0 posture request explicitly withheld
Grounding JSON and npm SDK availability wording, so it has to be requested rather than assumed.

## Apply only at publication

These edits land when v0.6.0 artifacts are live on crates.io, PyPI, npm, and GitHub Releases —
never before. `test_v0_6_0_version_activation.py` enforces that install commands keep naming the
published 0.5.0 until then.

## Requested changes

### 1. Replace the "Proposed for v0.6.0" section

Current text presents Grounding JSON as a proposal. Proposed replacement:

> ### Any language, via Grounding JSON
>
> Emit one strict JSON file and any parser can reach the verifier, with no Rust involved:
>
> ```text
> your parser output -> one mapper -> Grounding JSON -> ethos grounding check -> ethos verify
> ```
>
> Writing that mapper is real work, and Ethos does not pretend otherwise. Your mapper owns stable
> IDs and reading order, coordinate conversion, and honest capability declarations. Ethos rejects
> unknown or incomplete input rather than guessing.
>
> Grounding JSON validation and verification never require PDFium.
>
> Start with [Writing a Grounding JSON Mapper](docs/writing-a-mapper.md). Worked JavaScript and
> Python examples ship in the npm package.

### 2. Add Grounding JSON to the supported-sources table

| Source | How to use it |
| --- | --- |
| Grounding JSON (`ethos.grounding.v1`) | Any parser, via one mapper. `ethos grounding check` then `ethos verify` |

### 3. Update the "Supported today" row

Change the foreign-parser row from OpenDataLoader-only to: *"OpenDataLoader-style JSON adapter, or
`ethos.grounding.v1` from any parser."*

### 4. Answer the existing FAQ question accurately

"Can Ethos verify output from other parsers?" currently points at the plan. It should say Grounting
JSON is available, and link the mapper guide.

### 5. Note the npm functions

The npm package gains `checkGrounding` and `verifyClaims`. One sentence in the npm README, no
separate marketing.

## What this request does NOT claim

Stated explicitly so approval cannot be read wider than intended:

- **Not** that Ethos supports every parser automatically. Every integration writes one mapper.
- **Not** that text-only parsers are supported. Geometry is required, and §6.6 says so.
- **Not** any parser-quality or extraction-fidelity claim. A source-hash match proves only that the
  mapper declared the hash of the PDF supplied.
- **Not** that `grounded` means true, relevant, complete, or fresh.
- **Not** production positioning. Public-beta status stays.
- **Not** hosted surfaces, Windows artifacts, benchmark claims, or OCR.

## Honest limitations the wording keeps

The replacement text keeps three uncomfortable facts rather than hiding them, because they are
what makes the claim credible:

1. A mapper is required. "Plug and play" would be false.
2. Geometry is mandatory, so some parsers cannot use this profile honestly.
3. Ethos rejects rather than repairs.

## Evidence behind the claim

| Claim | Evidence |
| --- | --- |
| Any language can reach the verifier | JavaScript and Python mappers, byte-identical output |
| No PDFium needed | Full path exercised on a host with no usable PDFium |
| A stranger can write a mapper | **Pending** — outsider walkthrough |
| A real consumer uses public surfaces only | DocuShell `cc652ec` |

The third row is documentation quality, not capability. It gates publication under §5.1 and feeds
the revision clause above; it does not gate this approval.

## Decision

**Approved as written — decider, 2026-07-31.**

Approval covers the wording in this document only, applied at publication, subject to the revision
clause above. It does not approve production positioning, hosted surfaces, Windows artifacts,
benchmark claims, OCR, or any widening of the limits recorded in "What this request does NOT
claim".
