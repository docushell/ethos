"use strict";

const assert = require("assert");
const path = require("path");
const { spawnSync } = require("child_process");

const packageRoot = path.resolve(__dirname, "..");
const environment = { ...process.env };
delete environment.ETHOS_PDFIUM_LIBRARY_PATH;

const result = spawnSync(process.execPath, ["scripts/postinstall.js"], {
  cwd: packageRoot,
  encoding: "utf8",
  env: environment
});

assert.strictEqual(result.status, 0, result.stderr);
assert.strictEqual(result.stdout, "");
for (const required of [
  "scripts/fetch-pdfium.sh",
  "ETHOS_PDFIUM_LIBRARY_PATH export",
  "ethos doctor --require-pdfium",
  "pinned archive and runtime sha256 values",
  "never runs automatically",
  "docs/pdfium-manual-setup.md"
]) {
  assert.ok(result.stderr.includes(required), required);
}

console.log("setup guidance ok");
