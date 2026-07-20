# Ethos Verify Action

This source-only Action runs the checksum-pinned public Ethos CLI on Linux x64 and turns
ungrounded citations into pull-request annotations. Ethos checks citation grounding against the
supplied source representation; it does not establish semantic truth.

```yaml
- uses: docushell/ethos/actions/verify@<full-commit-sha>
  with:
    source: document.json
    citations: citations.json
    grounding: native
```

The Action writes `ethos-verification-report.json`, fails on ungrounded citations (CLI exit `1`),
and fails on operational errors (CLI exit `>=2`). It supports GitHub-hosted Linux x64 runners;
other platforms fail explicitly. The Action downloads only the fixed v0.3.0 Linux x64 release
archive and verifies both its archive and executable SHA256 values before execution.

Pin the Action itself to a full Ethos commit SHA. Marketplace publication is deferred; this
subdirectory form is consumed directly from the Ethos repository.
