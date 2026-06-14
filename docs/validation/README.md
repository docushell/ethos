# Validation Records

This directory stores dated evidence records for validation runs that affect Ethos product
claims or determinism boundaries.

Human-written validation records should avoid private usernames, hostnames, and one-off absolute
paths unless the path itself is the subject under test. Preserve commit ids, hashes, commands,
and pass/fail conclusions. Generated benchmark result files follow the evidence-handling policy
in `docs/public-release-checklist.md`.

Records:

- `rendered-crops-2026-06-14.md` - same-host rendered crop repeatability passed on macOS
  arm64 and Linux x64; cross-platform rendered crop byte identity failed because evidence
  bbox differed slightly across platforms.
