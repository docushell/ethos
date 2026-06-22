# First Public Release Launch Copy Audit Template - 2026-06-22

Status: **template only; no launch copy approved**

This template defines the required claim-audit shape for first public release launch copy. It does
not approve launch wording, public artifact publication, hosted surfaces, production positioning, or
public benchmark reports or claims.

## Required Source Binding

- Source commit: `<to be filled by final approval>`
- Source tree: `<to be filled by final approval>`
- CLI artifact checksums: `<to be filled by release-candidate validation>`
- Python package version: `<to be filled by release-candidate validation>`
- npm package version: `<to be filled by release-candidate validation>`

## Candidate Copy Rules

Every sentence in candidate launch copy must be reviewed as one of:

- `approved`: backed by an approved record and allowed on the named public surface;
- `blocked`: not allowed for this release;
- `revise`: requires narrower wording before approval.

Candidate copy must retain these boundaries:

- Ethos remains public beta unless a later decider record approves different wording.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- Windows x64 packaged artifacts remain blocked.
- Bundled project-maintained PDFium builds remain blocked.
- `ethos-doc` remains blocked.
- `ethos-rag` remains blocked.

## Sentence Audit Table

| Sentence | Surface | Evidence record | Status | Required edit |
| --- | --- | --- | --- | --- |
| `<candidate sentence>` | `<README/release notes/package README>` | `<record path>` | `<approved/blocked/revise>` | `<edit or none>` |

## Required Final Approval

Launch copy may be used only after a final approval record binds the exact approved sentence set,
source commit, source tree, artifact checksums, package versions, destinations, and retained
blockers.
