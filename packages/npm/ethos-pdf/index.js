"use strict";

const fs = require("node:fs/promises");
const os = require("node:os");
const path = require("node:path");
const { spawn } = require("node:child_process");

const {
  resolveBinary,
  validateVendorManifest,
  SUPPORTED_TARGETS,
  targetKey,
  VENDOR_DIR
} = require("./bin/ethos-pdf");

const MAX_OUTPUT_BYTES = 8 * 1024 * 1024;
const MAX_CITATIONS_BYTES = 8 * 1024 * 1024;
const DEFAULT_TIMEOUT_MS = 120000;

class EthosSdkError extends Error {
  constructor(code, message) {
    super(message);
    this.name = "EthosSdkError";
    this.code = code;
  }
}

function checkGrounding(options) {
  return execute("checkGrounding", options, (value) => {
    const inputPath = requiredPath(value.inputPath, "inputPath");
    const args = ["grounding", "check", inputPath];
    appendOption(args, "--source-artifact", value.sourceArtifactPath);
    appendOption(args, "--out", value.outputPath);
    return { args, outputPath: value.outputPath };
  });
}

function verifyClaims(options) {
  return execute("verifyClaims", options, async (value) => {
    const inputPath = requiredPath(value.inputPath, "inputPath");
    const hasPath = value.citationsPath !== undefined;
    const hasObject = value.citations !== undefined;
    if (hasPath === hasObject) {
      throw new EthosSdkError(
        "invalid_options",
        "verifyClaims requires exactly one of citationsPath or citations",
      );
    }
    if (value.grounding !== undefined && value.grounding !== "opendataloader-json") {
      throw new EthosSdkError("invalid_options", "grounding must be opendataloader-json");
    }
    let temporaryRoot = null;
    let citationsPath = value.citationsPath;
    if (hasObject) {
      if (!value.citations || typeof value.citations !== "object" || Array.isArray(value.citations)) {
        throw new EthosSdkError("invalid_options", "citations must be a bounded object");
      }
      const citationsBytes = Buffer.from(JSON.stringify(value.citations), "utf8");
      if (citationsBytes.length > MAX_CITATIONS_BYTES) {
        throw new EthosSdkError("invalid_options", "citations exceed the SDK size limit");
      }
      temporaryRoot = await fs.mkdtemp(path.join(os.tmpdir(), "ethos-citations-"));
      citationsPath = path.join(temporaryRoot, "citations.json");
      await fs.writeFile(citationsPath, citationsBytes);
    }

    const args = ["verify", inputPath, "--citations", requiredPath(citationsPath, "citationsPath")];
    appendOption(args, "--config", value.configPath);
    appendOption(args, "--out", value.outputPath);
    if (value.grounding !== undefined) {
      args.push("--grounding", value.grounding);
    }
    if (value.failOnUngrounded === true) args.push("--fail-on-ungrounded");
    return { args, outputPath: value.outputPath, temporaryRoot };
  });
}

// Resolve the packaged binary, converting launcher errors into one typed SDK error. An
// unsupported platform or a missing/invalid vendor payload must fail before anything can be
// mistaken for a verification result.
function resolveBinaryOrThrowTyped() {
  if (!SUPPORTED_TARGETS.has(targetKey())) {
    throw new EthosSdkError(
      "unsupported_platform",
      `Unsupported Ethos npm binary target: ${process.platform} ${process.arch}. ` +
        "Supported targets are macOS arm64 and Linux x64. No verification was performed."
    );
  }
  try {
    validateVendorManifest();
    return resolveBinary();
  } catch (error) {
    throw new EthosSdkError("vendor_invalid", error.message);
  }
}

async function execute(operation, options, build) {
  if (!options || typeof options !== "object" || Array.isArray(options)) {
    throw new EthosSdkError("invalid_options", `${operation} options must be an object`);
  }
  const plan = await build(options);
  try {
    const binaryPath = resolveBinaryOrThrowTyped();
    const result = await run(binaryPath, plan.args, options);
    const artifactBytes = plan.outputPath
      ? await readOutputFile(plan.outputPath)
      : result.stdout;
    if (!artifactBytes.length) {
      throw new EthosSdkError("invalid_output", `${operation} returned no report artifact`);
    }
    let artifact;
    try {
      artifact = JSON.parse(artifactBytes.toString("utf8"));
    } catch {
      throw new EthosSdkError("invalid_output", `${operation} returned invalid JSON`);
    }
    return {
      exitCode: result.exitCode,
      artifact,
      reason: result.stderr.toString("utf8").trim() || null,
    };
  } finally {
    if (plan.temporaryRoot) await fs.rm(plan.temporaryRoot, { recursive: true, force: true });
  }
}

function run(binaryPath, args, options) {
  const timeoutMs = options.timeoutMs === undefined ? DEFAULT_TIMEOUT_MS : options.timeoutMs;
  if (!Number.isInteger(timeoutMs) || timeoutMs <= 0) {
    return Promise.reject(new EthosSdkError("invalid_options", "timeoutMs must be a positive integer"));
  }
  return new Promise((resolve, reject) => {
    let child;
    try {
      child = spawn(binaryPath, args, { cwd: VENDOR_DIR, stdio: ["ignore", "pipe", "pipe"] });
    } catch (error) {
      reject(new EthosSdkError("launch_failed", error.message));
      return;
    }
    const stdout = [];
    const stderr = [];
    let stdoutBytes = 0;
    let stderrBytes = 0;
    let settled = false;
    const timer = setTimeout(() => finishError("timeout", "Ethos command timed out"), timeoutMs);
    const abort = () => finishError("cancelled", "Ethos command was cancelled");
    if (options.signal) {
      if (options.signal.aborted) return abort();
      options.signal.addEventListener("abort", abort, { once: true });
    }
    const collect = (chunks, limitName) => (chunk) => {
      const next = (limitName === "stdout" ? stdoutBytes : stderrBytes) + chunk.length;
      if (next > MAX_OUTPUT_BYTES) {
        finishError("output_limit", "Ethos command output exceeded the SDK limit");
        return;
      }
      chunks.push(chunk);
      if (limitName === "stdout") stdoutBytes = next;
      else stderrBytes = next;
    };
    child.stdout.on("data", collect(stdout, "stdout"));
    child.stderr.on("data", collect(stderr, "stderr"));
    child.on("error", (error) => finishError("launch_failed", error.message));
    child.on("close", (code, signal) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      cleanupSignal();
      resolve({ exitCode: code === null ? 1 : code, signal, stdout: Buffer.concat(stdout), stderr: Buffer.concat(stderr) });
    });

    function finishError(code, message) {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      cleanupSignal();
      child.kill("SIGTERM");
      reject(new EthosSdkError(code, message));
    }

    function cleanupSignal() {
      options.signal?.removeEventListener("abort", abort);
    }
  });
}

async function readOutputFile(outputPath) {
  try {
    const stat = await fs.stat(outputPath);
    if (!stat.isFile() || stat.size > MAX_OUTPUT_BYTES) {
      throw new EthosSdkError("invalid_output", "Ethos report file is missing or too large");
    }
    return await fs.readFile(outputPath);
  } catch (error) {
    if (error instanceof EthosSdkError) throw error;
    throw new EthosSdkError("invalid_output", "Ethos report file is missing");
  }
}

function requiredPath(value, name) {
  if (typeof value !== "string" || value.length === 0) {
    throw new EthosSdkError("invalid_options", `${name} must be a non-empty path`);
  }
  return value;
}

function appendOption(args, flag, value) {
  if (value !== undefined) args.push(flag, requiredPath(value, flag));
}

module.exports = { EthosSdkError, checkGrounding, verifyClaims };
