# @docushell/ethos-mcp

A [Model Context Protocol](https://modelcontextprotocol.io) server that exposes the
Ethos document-evidence CLI as callable tools. Any MCP-compatible client — Claude
Desktop, Cursor, Sim, and others — can then verify citations, parse PDFs, and derive
grounding artifacts through Ethos without shelling out manually.

The server is a thin, faithful wrapper: each tool maps to a real `ethos` subcommand
and returns the canonical, deterministic report unchanged. It preserves Ethos's core
contract — same input, same pinned profile, same stable payload and fingerprint.

## Tools

| Tool                    | Ethos command        | Purpose                                                        |
| ----------------------- | -------------------- | -------------------------------------------------------------- |
| `ethos_verify`          | `verify`             | Verify cited evidence exists in the source; catch fabrications |
| `ethos_doc_parse`       | `doc parse`          | Parse a born-digital PDF into the canonical document graph     |
| `ethos_rag_chunk`       | `rag chunk`          | Derive retrieval-ready `chunks.jsonl`                          |
| `ethos_security_report` | `security report`    | Derive `security_report.json` from document warnings           |
| `ethos_evidence_anchor` | `evidence anchor`    | Anchor caller-provided evidence refs against the source        |
| `ethos_fingerprint`     | `fingerprint`        | Recompute and check a document fingerprint                     |
| `ethos_doctor`          | `doctor`             | Diagnose the local Ethos + PDFium setup                        |

`ethos_verify` uses a nonzero exit only as a signal (exit 1 = ungrounded evidence
found); the full report is always returned as the tool result, so it is never
surfaced as a tool error.

## Install & build

```bash
cd packages/npm/ethos-mcp
npm install
npm run build
```

This depends on `@docushell/ethos-pdf`, which vendors the platform `ethos` binary
(macOS arm64, Linux x64). No separate CLI install is required.

## The Ethos CLI it runs

By default the server invokes the `ethos` launcher shipped by `@docushell/ethos-pdf`.
To point at a different build (e.g. a locally compiled `./target/debug/ethos`), set:

```bash
export ETHOS_BIN=/absolute/path/to/ethos
```

### PDFium

Parsing (`ethos_doc_parse`) and rendered crops are PDFium-backed. The package does
**not** bundle PDFium. Provide your own dynamic library:

```bash
export ETHOS_PDFIUM_LIBRARY_PATH=/absolute/path/to/libpdfium.dylib
```

Verifying against checked-in canonical JSON (`ethos_verify` on `*.ethos.json`) does
**not** require PDFium. Run `ethos_doctor` with `require_pdfium: true` to confirm your
setup before PDFium-backed calls.

## Client configuration

### Claude Desktop / Cursor (`mcp.json`)

```json
{
  "mcpServers": {
    "ethos": {
      "command": "node",
      "args": ["/absolute/path/to/ethos/packages/npm/ethos-mcp/dist/index.js"],
      "env": {
        "ETHOS_PDFIUM_LIBRARY_PATH": "/absolute/path/to/libpdfium.dylib"
      }
    }
  }
}
```

After publishing to npm you can instead use `npx`:

```json
{
  "mcpServers": {
    "ethos": {
      "command": "npx",
      "args": ["-y", "@docushell/ethos-mcp"]
    }
  }
}
```

### Sim (simstudioai/sim)

Sim can consume MCP servers as tool sources. Add this server as a custom MCP server
in Sim's tool/integration settings using the same `command` + `args` as above; its
tools then appear as blocks on the canvas. This requires no Sim-specific code and no
change to the Sim repository.

## Example: catch a fabricated citation

With the client connected, ask the model to call `ethos_verify`:

```json
{
  "input": "schemas/examples/document.example.json",
  "citations": "examples/verify/native_ungrounded_citations.json",
  "fail_on_ungrounded": true
}
```

The returned report names each check's status; the fabricated quote comes back as
`not_found` / `mismatch` rather than a bare error.

## License

Apache-2.0. See `LICENSE` and `NOTICE`.
