#!/usr/bin/env node
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { registerTools } from "./tools.js";
import { describeLauncher } from "./ethos.js";

async function main(): Promise<void> {
  const server = new McpServer({
    name: "ethos-mcp",
    version: "0.3.0",
  });

  registerTools(server);

  // Diagnostics go to stderr so they never corrupt the stdio JSON-RPC stream.
  console.error(`[ethos-mcp] using CLI: ${describeLauncher()}`);

  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("[ethos-mcp] ready on stdio");
}

main().catch((err) => {
  console.error("[ethos-mcp] fatal:", err);
  process.exit(1);
});
