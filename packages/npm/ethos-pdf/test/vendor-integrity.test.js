"use strict";

const assert = require("assert");
const fs = require("fs");
const os = require("os");
const path = require("path");
const {
  DEFAULT_MANIFEST,
  DEFAULT_VENDOR_DIR,
  readManifest,
  verifyBinaryChecksum
} = require("../scripts/prepare-vendor");

const manifest = readManifest(DEFAULT_MANIFEST);
for (const [targetKey, target] of Object.entries(manifest.targets || {})) {
  const binaryPath = path.join(DEFAULT_VENDOR_DIR, target.binary);
  assert.ok(fs.existsSync(binaryPath), `missing vendored binary for ${targetKey}`);
  assert.strictEqual(verifyBinaryChecksum(targetKey, target, binaryPath), true);
}

const temp = fs.mkdtempSync(path.join(os.tmpdir(), "ethos-vendor-integrity-"));
try {
  const binaryPath = path.join(temp, "ethos-linux-x64");
  fs.writeFileSync(binaryPath, "tampered");
  assert.throws(
    () => verifyBinaryChecksum("linux:x64", manifest.targets["linux:x64"], binaryPath),
    /Binary checksum mismatch/
  );
  assert.throws(
    () => verifyBinaryChecksum("linux:x64", { binary: "ethos-linux-x64" }, binaryPath),
    /Binary checksum is missing or invalid/
  );
} finally {
  fs.rmSync(temp, { recursive: true, force: true });
}

console.log("vendor integrity ok");
