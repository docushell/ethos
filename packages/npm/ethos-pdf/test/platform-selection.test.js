"use strict";

const assert = require("assert");
const path = require("path");
const { SUPPORTED_TARGETS, resolveBinary, targetKey } = require("../bin/ethos-pdf");

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

console.log("platform selection ok");
