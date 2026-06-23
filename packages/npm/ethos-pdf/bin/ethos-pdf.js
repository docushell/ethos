#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");

const SUPPORTED_TARGETS = new Map([
  ["darwin:arm64", "ethos-darwin-arm64"],
  ["linux:x64", "ethos-linux-x64"]
]);

function targetKey(platform = process.platform, arch = process.arch) {
  return `${platform}:${arch}`;
}

function resolveBinary(platform = process.platform, arch = process.arch) {
  const binaryName = SUPPORTED_TARGETS.get(targetKey(platform, arch));
  if (!binaryName) {
    throw new Error(
      `Unsupported Ethos npm binary target: ${platform} ${arch}. ` +
        "Supported targets are macOS arm64 and Linux x64."
    );
  }
  return path.join(__dirname, "..", "vendor", binaryName);
}

function main(argv = process.argv.slice(2)) {
  let binaryPath;
  try {
    binaryPath = resolveBinary();
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
  SUPPORTED_TARGETS,
  resolveBinary,
  targetKey
};
