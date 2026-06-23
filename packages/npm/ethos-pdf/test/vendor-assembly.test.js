"use strict";

const assert = require("assert");
const crypto = require("crypto");
const fs = require("fs");
const os = require("os");
const path = require("path");
const { spawnSync } = require("child_process");
const { prepareVendor, sha256File } = require("../scripts/prepare-vendor");

function writeFixtureArchive(root, assetName, nestedDir, binaryText) {
  const sourceDir = path.join(root, "src", nestedDir);
  fs.mkdirSync(sourceDir, { recursive: true });
  const binary = path.join(sourceDir, "ethos");
  fs.writeFileSync(binary, binaryText, { mode: 0o755 });
  const archive = path.join(root, "artifacts", assetName);
  fs.mkdirSync(path.dirname(archive), { recursive: true });
  const result = spawnSync("tar", ["-czf", archive, "-C", path.join(root, "src"), nestedDir], {
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"]
  });
  assert.strictEqual(result.status, 0, result.stderr);
  return archive;
}

const temp = fs.mkdtempSync(path.join(os.tmpdir(), "ethos-vendor-assembly-"));
try {
  const macArchive = writeFixtureArchive(
    temp,
    "ethos-macos-arm64.tar.gz",
    "ethos-macos-arm64",
    "#!/usr/bin/env sh\necho mac\n"
  );
  const linuxArchive = writeFixtureArchive(
    temp,
    "ethos-linux-x64.tar.gz",
    "ethos-linux-x64",
    "#!/usr/bin/env sh\necho linux\n"
  );
  const manifestPath = path.join(temp, "manifest.json");
  fs.writeFileSync(
    manifestPath,
    JSON.stringify(
      {
        version: 1,
        targets: {
          "darwin:arm64": {
            binary: "ethos-darwin-arm64",
            release_asset: path.basename(macArchive),
            release_asset_sha256: sha256File(macArchive)
          },
          "linux:x64": {
            binary: "ethos-linux-x64",
            release_asset: path.basename(linuxArchive),
            release_asset_sha256: sha256File(linuxArchive)
          }
        }
      },
      null,
      2
    )
  );

  const vendorDir = path.join(temp, "vendor");
  const prepared = prepareVendor({
    artifactDir: path.join(temp, "artifacts"),
    vendorDir,
    manifestPath
  });

  assert.deepStrictEqual(
    prepared.map((file) => path.basename(file)).sort(),
    ["ethos-darwin-arm64", "ethos-linux-x64"]
  );
  assert.strictEqual(fs.readFileSync(path.join(vendorDir, "ethos-darwin-arm64"), "utf8"), "#!/usr/bin/env sh\necho mac\n");
  assert.strictEqual(fs.readFileSync(path.join(vendorDir, "ethos-linux-x64"), "utf8"), "#!/usr/bin/env sh\necho linux\n");
  assert.ok((fs.statSync(path.join(vendorDir, "ethos-linux-x64")).mode & 0o111) !== 0);
  assert.match(sha256File(path.join(vendorDir, "ethos-linux-x64")), /^[a-f0-9]{64}$/);

  const badManifest = path.join(temp, "bad-manifest.json");
  fs.writeFileSync(
    badManifest,
    JSON.stringify({
      targets: {
        "linux:x64": {
          binary: "ethos-linux-x64",
          release_asset: "ethos-linux-x64.tar.gz",
          release_asset_sha256: crypto.createHash("sha256").update("wrong").digest("hex")
        }
      }
    })
  );
  assert.throws(
    () =>
      prepareVendor({
        artifactDir: path.join(temp, "artifacts"),
        vendorDir: path.join(temp, "bad-vendor"),
        manifestPath: badManifest
      }),
    /Checksum mismatch/
  );

  const missingManifest = path.join(temp, "missing-manifest.json");
  fs.writeFileSync(
    missingManifest,
    JSON.stringify({
      targets: {
        "linux:x64": {
          binary: "ethos-linux-x64",
          release_asset: "missing.tar.gz",
          release_asset_sha256: sha256File(linuxArchive)
        }
      }
    })
  );
  assert.throws(
    () =>
      prepareVendor({
        artifactDir: path.join(temp, "artifacts"),
        vendorDir: path.join(temp, "missing-vendor"),
        manifestPath: missingManifest
      }),
    /Missing release asset/
  );
} finally {
  fs.rmSync(temp, { recursive: true, force: true });
}

console.log("vendor assembly ok");
