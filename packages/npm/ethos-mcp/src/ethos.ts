import { execFile } from "node:child_process";
import { createRequire } from "node:module";
import path from "node:path";

const require = createRequire(import.meta.url);

/**
 * Result of an Ethos CLI invocation.
 *
 * `exitCode` is preserved faithfully: the Ethos CLI uses a nonzero exit as a
 * meaningful signal (for example `verify --fail-on-ungrounded` exits 1 while
 * still writing a full, auditable report to stdout). Callers must inspect the
 * report, not just the exit code.
 */
export interface EthosResult {
  stdout: string;
  stderr: string;
  exitCode: number;
  /** Set when the process could not be spawned at all (e.g. binary missing). */
  spawnError?: string;
}

/**
 * Resolve how to invoke the Ethos CLI.
 *
 * Order of preference:
 *   1. ETHOS_BIN env var pointing directly at an `ethos` executable.
 *   2. The launcher shipped by the `@docushell/ethos-pdf` npm package, which
 *      selects the correct vendored platform binary. We run it through the
 *      current Node executable so no PATH setup is required.
 */
function resolveLauncher(): { command: string; prefixArgs: string[] } {
  const override = process.env.ETHOS_BIN;
  if (override && override.trim().length > 0) {
    return { command: override, prefixArgs: [] };
  }

  const pkgJsonPath = require.resolve("@docushell/ethos-pdf/package.json");
  const pkgDir = path.dirname(pkgJsonPath);
  const launcher = path.join(pkgDir, "bin", "ethos-pdf.js");
  return { command: process.execPath, prefixArgs: [launcher] };
}

const MAX_BUFFER = 128 * 1024 * 1024; // 128 MiB: parse output can be large.

/**
 * Run the Ethos CLI with the given argument vector.
 *
 * Never rejects on a nonzero exit code — the exit code is returned so tool
 * handlers can surface it. Only genuine spawn failures set `spawnError`.
 */
export function runEthos(args: string[]): Promise<EthosResult> {
  const { command, prefixArgs } = resolveLauncher();
  const fullArgs = [...prefixArgs, ...args];

  return new Promise((resolve) => {
    execFile(
      command,
      fullArgs,
      { maxBuffer: MAX_BUFFER, env: process.env },
      (err, stdout, stderr) => {
        if (err) {
          const code = (err as NodeJS.ErrnoException).code;
          // execFile sets `code` to the numeric exit code for a nonzero exit,
          // or to a string errno (e.g. "ENOENT") for a spawn failure.
          if (typeof code === "number") {
            resolve({ stdout: stdout ?? "", stderr: stderr ?? "", exitCode: code });
            return;
          }
          resolve({
            stdout: stdout ?? "",
            stderr: stderr ?? "",
            exitCode: -1,
            spawnError: `${code ?? "spawn error"}: ${err.message}`,
          });
          return;
        }
        resolve({ stdout: stdout ?? "", stderr: stderr ?? "", exitCode: 0 });
      },
    );
  });
}

/** Return the resolved CLI command line, for diagnostics/logging. */
export function describeLauncher(): string {
  const { command, prefixArgs } = resolveLauncher();
  return [command, ...prefixArgs].join(" ");
}
