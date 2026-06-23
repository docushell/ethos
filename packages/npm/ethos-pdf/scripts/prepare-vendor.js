#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const os = require("os");
const path = require("path");
const { spawnSync } = require("child_process");

const PACKAGE_ROOT = path.join(__dirname, "..");
const DEFAULT_MANIFEST = path.join(PACKAGE_ROOT, "vendor", "manifest.json");
const DEFAULT_VENDOR_DIR = path.join(PACKAGE_ROOT, "vendor");

function sha256File(filePath) {
  const hash = crypto.createHash("sha256");
  hash.update(fs.readFileSync(filePath));
  return hash.digest("hex");
}

function readManifest(manifestPath = DEFAULT_MANIFEST) {
  return JSON.parse(fs.readFileSync(manifestPath, "utf8"));
}

function findEthosBinary(root) {
  const stack = [root];
  while (stack.length > 0) {
    const current = stack.pop();
    for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
      const entryPath = path.join(current, entry.name);
      if (entry.isDirectory()) {
        stack.push(entryPath);
      } else if (entry.isFile() && entry.name === "ethos") {
        return entryPath;
      }
    }
  }
  throw new Error(`No ethos binary found in extracted archive ${root}`);
}

function extractTarGz(archivePath, destination) {
  fs.mkdirSync(destination, { recursive: true });
  const result = spawnSync("tar", ["-xzf", archivePath, "-C", destination], {
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"]
  });
  if (result.status !== 0) {
    throw new Error(result.stderr || `tar failed for ${archivePath}`);
  }
}

function prepareVendor({
  artifactDir,
  vendorDir = DEFAULT_VENDOR_DIR,
  manifestPath = DEFAULT_MANIFEST
}) {
  if (!artifactDir) {
    throw new Error("Usage: node scripts/prepare-vendor.js <release-artifact-dir>");
  }

  const manifest = readManifest(manifestPath);
  const targets = manifest.targets || {};
  fs.mkdirSync(vendorDir, { recursive: true });

  const prepared = [];
  for (const [targetKey, target] of Object.entries(targets)) {
    const archivePath = path.join(artifactDir, target.release_asset);
    if (!fs.existsSync(archivePath)) {
      throw new Error(`Missing release asset for ${targetKey}: ${archivePath}`);
    }

    const actualSha256 = sha256File(archivePath);
    if (actualSha256 !== target.release_asset_sha256) {
      throw new Error(
        `Checksum mismatch for ${target.release_asset}: expected ${target.release_asset_sha256}, got ${actualSha256}`
      );
    }

    const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), `ethos-${targetKey.replace(":", "-")}-`));
    try {
      extractTarGz(archivePath, tempDir);
      const sourceBinary = findEthosBinary(tempDir);
      const vendorBinary = path.join(vendorDir, target.binary);
      fs.copyFileSync(sourceBinary, vendorBinary);
      fs.chmodSync(vendorBinary, 0o755);
      prepared.push(vendorBinary);
    } finally {
      fs.rmSync(tempDir, { recursive: true, force: true });
    }
  }

  return prepared;
}

function main(argv = process.argv.slice(2)) {
  try {
    const prepared = prepareVendor({ artifactDir: argv[0] });
    for (const file of prepared) {
      console.log(`prepared ${path.relative(PACKAGE_ROOT, file)}`);
    }
    return 0;
  } catch (error) {
    console.error(error.message);
    return 1;
  }
}

if (require.main === module) {
  process.exitCode = main();
}

module.exports = {
  DEFAULT_MANIFEST,
  DEFAULT_VENDOR_DIR,
  findEthosBinary,
  main,
  prepareVendor,
  readManifest,
  sha256File
};
