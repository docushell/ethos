import { z } from "zod";
import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";
import { runEthos, type EthosResult } from "./ethos.js";

/**
 * Turn an Ethos CLI result into an MCP tool result.
 *
 * The canonical Ethos report (JSON on stdout) is returned as the primary text
 * block. A nonzero exit code is surfaced but is NOT automatically treated as an
 * error for `verify`, where exit 1 means "ungrounded evidence found" and the
 * report itself is the deliverable. `isError` is reserved for spawn failures and
 * for tools where a nonzero exit is genuinely a failure.
 */
function toResult(res: EthosResult, opts?: { nonzeroIsError?: boolean }): CallToolResult {
  if (res.spawnError) {
    return {
      isError: true,
      content: [
        {
          type: "text",
          text:
            `Failed to run the Ethos CLI: ${res.spawnError}\n\n` +
            `Ensure @docushell/ethos-pdf is installed for this platform, or set ` +
            `ETHOS_BIN to a valid ethos executable.`,
        },
      ],
    };
  }

  const body = res.stdout.trim().length > 0 ? res.stdout : res.stderr;
  const isError = opts?.nonzeroIsError ? res.exitCode !== 0 : false;

  const content: CallToolResult["content"] = [{ type: "text", text: body }];
  if (res.stderr.trim().length > 0 && res.stdout.trim().length > 0) {
    content.push({ type: "text", text: `stderr:\n${res.stderr.trim()}` });
  }
  content.push({ type: "text", text: `exit_code: ${res.exitCode}` });

  return { isError, content };
}

/** Append `--flag value` when the value is defined and non-empty. */
function opt(args: string[], flag: string, value?: string | null): void {
  if (value !== undefined && value !== null && `${value}`.length > 0) {
    args.push(flag, `${value}`);
  }
}

export function registerTools(server: McpServer): void {
  server.registerTool(
    "ethos_verify",
    {
      title: "Verify citations against a source document",
      description:
        "Check that cited evidence actually exists in a parsed source document. " +
        "Returns a deterministic verification report naming each check's status " +
        "(grounded, not_found, mismatch, stale_fingerprint, capability_limited). " +
        "Use this to catch fabricated or unsupported citations.",
      inputSchema: {
        input: z
          .string()
          .describe(
            "Path to the grounding input: a canonical Ethos document (*.ethos.json), " +
              "or a foreign parser output when `grounding` is set.",
          ),
        citations: z
          .string()
          .describe(
            "Path to the citations JSON file. Accepts an array of claims or " +
              '{"document_fingerprint": "...", "claims": [...]}.',
          ),
        grounding: z
          .string()
          .optional()
          .describe("Foreign grounding adapter id, e.g. 'opendataloader-json'."),
        config: z
          .string()
          .optional()
          .describe("Path to a verification config JSON. Defaults to the pinned 'default-v1'."),
        format: z
          .enum(["json", "summary"])
          .optional()
          .describe("Report format: 'json' (canonical) or 'summary' (compact text). Default json."),
        fail_on_ungrounded: z
          .boolean()
          .optional()
          .describe("Exit 1 when any requested evidence is not grounded (report is still returned)."),
      },
    },
    async (a) => {
      const args = ["verify", a.input, "--citations", a.citations];
      opt(args, "--grounding", a.grounding);
      opt(args, "--config", a.config);
      opt(args, "--format", a.format);
      if (a.fail_on_ungrounded) args.push("--fail-on-ungrounded");
      // A nonzero exit here means "ungrounded found"; the report is the value.
      return toResult(await runEthos(args), { nonzeroIsError: false });
    },
  );

  server.registerTool(
    "ethos_doc_parse",
    {
      title: "Parse a PDF into the canonical document graph",
      description:
        "Parse a born-digital PDF into Ethos's canonical, deterministic document graph " +
        "(JSON, Markdown, or text). PDFium-backed: requires ETHOS_PDFIUM_LIBRARY_PATH.",
      inputSchema: {
        input: z.string().describe("Path to the input PDF."),
        format: z
          .enum(["json", "markdown", "text"])
          .optional()
          .describe("Output format. Default json (canonical)."),
        out: z
          .string()
          .optional()
          .describe("Output path (file or directory). Omit to return output on stdout."),
        pages: z
          .string()
          .optional()
          .describe("Page selection, e.g. '1-5,9' (1-based, inclusive). Affects the canonical config."),
      },
    },
    async (a) => {
      const args = ["doc", "parse", a.input];
      opt(args, "--format", a.format);
      opt(args, "--out", a.out);
      opt(args, "--pages", a.pages);
      return toResult(await runEthos(args), { nonzeroIsError: true });
    },
  );

  server.registerTool(
    "ethos_rag_chunk",
    {
      title: "Derive retrieval-ready chunks",
      description:
        "Deterministically derive chunks.jsonl from a canonical Ethos document for RAG pipelines.",
      inputSchema: {
        input: z.string().describe("Path to a canonical Ethos document (*.ethos.json)."),
        out: z.string().optional().describe("Output path for chunks.jsonl. Omit for stdout."),
      },
    },
    async (a) => {
      const args = ["rag", "chunk", a.input];
      opt(args, "--out", a.out);
      return toResult(await runEthos(args), { nonzeroIsError: true });
    },
  );

  server.registerTool(
    "ethos_security_report",
    {
      title: "Derive a security report",
      description:
        "Derive security_report.json from the security warnings captured in a canonical Ethos document.",
      inputSchema: {
        input: z.string().describe("Path to a canonical Ethos document (*.ethos.json)."),
        out: z.string().optional().describe("Output path for security_report.json. Omit for stdout."),
      },
    },
    async (a) => {
      const args = ["security", "report", a.input];
      opt(args, "--out", a.out);
      return toResult(await runEthos(args), { nonzeroIsError: true });
    },
  );

  server.registerTool(
    "ethos_evidence_anchor",
    {
      title: "Anchor caller-provided evidence refs",
      description:
        "Check caller-provided evidence references against the source evidence in a document.",
      inputSchema: {
        input: z
          .string()
          .describe("Grounding input: a canonical Ethos document, or foreign output with `grounding`."),
        evidence_refs: z.string().describe("Path to the evidence refs request JSON."),
        grounding: z
          .string()
          .optional()
          .describe("Grounding adapter id: 'ethos-json' (default) or 'opendataloader-json'."),
        out: z
          .string()
          .optional()
          .describe("Output path for evidence_anchor_report.json. Omit for stdout."),
      },
    },
    async (a) => {
      const args = ["evidence", "anchor", a.input, "--evidence-refs", a.evidence_refs];
      opt(args, "--grounding", a.grounding);
      opt(args, "--out", a.out);
      return toResult(await runEthos(args), { nonzeroIsError: true });
    },
  );

  server.registerTool(
    "ethos_fingerprint",
    {
      title: "Recompute and check a document fingerprint",
      description:
        "Recompute the deterministic fingerprint for a canonical document (or a PDF parsed under " +
        "the deterministic profile) and check it.",
      inputSchema: {
        input: z
          .string()
          .describe("Path to a canonical document (*.ethos.json) or a PDF to parse deterministically."),
      },
    },
    async (a) => {
      const args = ["fingerprint", a.input];
      return toResult(await runEthos(args), { nonzeroIsError: true });
    },
  );

  server.registerTool(
    "ethos_doctor",
    {
      title: "Diagnose the local Ethos and PDFium setup",
      description:
        "Diagnose the local Ethos install and caller-provided PDFium configuration. " +
        "Use before PDFium-backed commands to confirm ETHOS_PDFIUM_LIBRARY_PATH is usable.",
      inputSchema: {
        require_pdfium: z
          .boolean()
          .optional()
          .describe("Fail if caller-provided PDFium is not configured and usable."),
      },
    },
    async (a) => {
      const args = ["doctor"];
      if (a.require_pdfium) args.push("--require-pdfium");
      return toResult(await runEthos(args), { nonzeroIsError: true });
    },
  );
}
