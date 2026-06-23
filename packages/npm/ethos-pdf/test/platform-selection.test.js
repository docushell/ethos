"use strict";

const assert = require("assert");
const crypto = require("crypto");
const os = require("os");
const fs = require("fs");
const path = require("path");
const {
  main,
  MANIFEST_PATH,
  SUPPORTED_TARGETS,
  VENDOR_DIR,
  readVendorManifest,
  resolveBinary,
  targetKey,
  validateVendorManifest
} = require("../bin/ethos-pdf");

assert.strictEqual(targetKey("darwin", "arm64"), "darwin:arm64");
assert.strictEqual(targetKey("linux", "x64"), "linux:x64");

assert.deepStrictEqual(
  Array.from(SUPPORTED_TARGETS.keys()).sort(),
  ["darwin:arm64", "linux:x64"]
);

assert.strictEqual(
  resolveBinary("darwin", "arm64"),
  path.join(VENDOR_DIR, "ethos-darwin-arm64")
);
assert.strictEqual(
  resolveBinary("linux", "x64"),
  path.join(VENDOR_DIR, "ethos-linux-x64")
);

assert.throws(
  () => resolveBinary("win32", "x64"),
  /Unsupported Ethos npm binary target/
);
assert.throws(
  () => resolveBinary("darwin", "x64"),
  /Unsupported Ethos npm binary target/
);
assert.throws(
  () => resolveBinary("linux", "arm64"),
  /Unsupported Ethos npm binary target/
);

const manifest = readVendorManifest();
assert.strictEqual(manifest.version, 1);
assert.strictEqual(manifest.package, "@docushell/ethos-pdf");
validateVendorManifest(manifest);
for (const [key, binaryName] of SUPPORTED_TARGETS.entries()) {
  assert.strictEqual(manifest.targets[key].binary, binaryName);
  assert.match(manifest.targets[key].release_asset_sha256, /^[a-f0-9]{64}$/);
}
assert.throws(
  () => validateVendorManifest({ targets: { "linux:x64": manifest.targets["linux:x64"] } }),
  /target mismatch/
);
assert.throws(
  () =>
    validateVendorManifest({
      targets: {
        ...manifest.targets,
        "linux:x64": { ...manifest.targets["linux:x64"], release_asset_sha256: "bad" }
      }
    }),
  /checksum is invalid/
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

const vendorDir = fs.mkdtempSync(path.join(os.tmpdir(), "ethos-npm-vendor-"));
const outputPath = path.join(vendorDir, ".platform-selection-output");
fs.rmSync(outputPath, { force: true });
const created = [];
function writeExecutable(binaryName, message) {
  const binaryPath = path.join(vendorDir, binaryName);
  fs.writeFileSync(
    binaryPath,
    `#!/usr/bin/env node\nrequire("fs").appendFileSync(${JSON.stringify(
      outputPath
    )}, ${JSON.stringify(message)} + "\\n");\n`,
    { mode: 0o755 }
  );
  created.push(binaryPath);
}

try {
  writeExecutable("ethos-darwin-arm64", "darwin-arm64");
  writeExecutable("ethos-linux-x64", "linux-x64");
  assert.strictEqual(main(["--version"], "darwin", "arm64", vendorDir), 0);
  assert.strictEqual(main(["--version"], "linux", "x64", vendorDir), 0);
  assert.deepStrictEqual(fs.readFileSync(outputPath, "utf8").trim().split("\n"), [
    "darwin-arm64",
    "linux-x64"
  ]);
} finally {
  for (const file of created.concat(outputPath)) {
    fs.rmSync(file, { force: true });
  }
  fs.rmSync(vendorDir, { force: true, recursive: true });
}

assert.strictEqual(
  crypto
    .createHash("sha256")
    .update(fs.readFileSync(MANIFEST_PATH))
    .digest("hex").length,
  64
);

console.log("platform selection ok");
