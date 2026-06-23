#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");

const SUPPORTED_TARGETS = new Map([
  ["darwin:arm64", "ethos-darwin-arm64"],
  ["linux:x64", "ethos-linux-x64"]
]);
const VENDOR_DIR = path.join(__dirname, "..", "vendor");
const MANIFEST_PATH = path.join(VENDOR_DIR, "manifest.json");

function targetKey(platform = process.platform, arch = process.arch) {
  return `${platform}:${arch}`;
}

function resolveBinary(platform = process.platform, arch = process.arch, vendorDir = VENDOR_DIR) {
  const binaryName = SUPPORTED_TARGETS.get(targetKey(platform, arch));
  if (!binaryName) {
    throw new Error(
      `Unsupported Ethos npm binary target: ${platform} ${arch}. ` +
        "Supported targets are macOS arm64 and Linux x64."
    );
  }
  return path.join(vendorDir, binaryName);
}

function readVendorManifest() {
  return JSON.parse(fs.readFileSync(MANIFEST_PATH, "utf8"));
}

function validateVendorManifest(manifest = readVendorManifest()) {
  const targets = manifest.targets || {};
  const expectedKeys = Array.from(SUPPORTED_TARGETS.keys()).sort();
  const manifestKeys = Object.keys(targets).sort();
  if (JSON.stringify(manifestKeys) !== JSON.stringify(expectedKeys)) {
    throw new Error(
      `Ethos vendor manifest target mismatch: expected ${expectedKeys.join(", ")}.`
    );
  }

  for (const [key, binaryName] of SUPPORTED_TARGETS.entries()) {
    const target = targets[key] || {};
    if (target.binary !== binaryName) {
      throw new Error(`Ethos vendor manifest binary mismatch for ${key}.`);
    }
    if (!/^[a-f0-9]{64}$/.test(String(target.release_asset_sha256 || ""))) {
      throw new Error(`Ethos vendor manifest checksum is invalid for ${key}.`);
    }
  }
  return true;
}

function main(
  argv = process.argv.slice(2),
  platform = process.platform,
  arch = process.arch,
  vendorDir = VENDOR_DIR
) {
  let binaryPath;
  try {
    validateVendorManifest();
    binaryPath = resolveBinary(platform, arch, vendorDir);
  } catch (error) {
    console.error(error.message);
    return 1;
  }

  if (!fs.existsSync(binaryPath)) {
    console.error(
      `Ethos binary is missing from this package: ${binaryPath}. ` +
        "Use a release artifact that includes the platform binary."
    );
    return 1;
  }

  const result = spawnSync(binaryPath, argv, { stdio: "inherit" });
  if (result.error) {
    console.error(result.error.message);
    return 1;
  }
  return result.status === null ? 1 : result.status;
}

if (require.main === module) {
  process.exitCode = main();
}

module.exports = {
  main,
  MANIFEST_PATH,
  SUPPORTED_TARGETS,
  VENDOR_DIR,
  readVendorManifest,
  resolveBinary,
  targetKey,
  validateVendorManifest
};
