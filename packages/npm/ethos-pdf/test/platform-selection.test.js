"use strict";

const assert = require("assert");
const path = require("path");
const { main, SUPPORTED_TARGETS, resolveBinary, targetKey } = require("../bin/ethos-pdf");

assert.strictEqual(targetKey("darwin", "arm64"), "darwin:arm64");
assert.strictEqual(targetKey("linux", "x64"), "linux:x64");

assert.deepStrictEqual(
  Array.from(SUPPORTED_TARGETS.keys()).sort(),
  ["darwin:arm64", "linux:x64"]
);

assert.strictEqual(
  resolveBinary("darwin", "arm64"),
  path.join(__dirname, "..", "vendor", "ethos-darwin-arm64")
);
assert.strictEqual(
  resolveBinary("linux", "x64"),
  path.join(__dirname, "..", "vendor", "ethos-linux-x64")
);

assert.throws(
  () => resolveBinary("win32", "x64"),
  /Unsupported Ethos npm binary target/
);

const originalError = console.error;
const errors = [];
console.error = (message) => errors.push(String(message));
try {
  assert.strictEqual(main(["--version"]), 1);
} finally {
  console.error = originalError;
}
assert.match(errors.join("\n"), /Ethos binary is missing from this package/);

console.log("platform selection ok");
