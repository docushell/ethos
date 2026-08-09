const assert = require("node:assert/strict");
const fs = require("node:fs/promises");
const os = require("node:os");
const path = require("node:path");
const { spawnSync } = require("node:child_process");

const PACKAGE_ROOT = path.resolve(__dirname, "..");

async function main() {
  const temporaryRoot = await fs.mkdtemp(path.join(os.tmpdir(), "ethos-clean-room-"));
  try {
    const npmEnv = { ...process.env, npm_config_cache: path.join(temporaryRoot, "npm-cache") };
    const pack = spawnSync("npm", ["pack", "--json", "--pack-destination", temporaryRoot], {
      cwd: PACKAGE_ROOT,
      env: npmEnv,
      encoding: "utf8",
    });
    assert.equal(pack.status, 0, pack.stderr);
    const tarball = path.join(temporaryRoot, JSON.parse(pack.stdout)[0].filename);
    const project = path.join(temporaryRoot, "project");
    await fs.mkdir(project);
    await fs.writeFile(path.join(project, "package.json"), '{"name":"clean-room","private":true}\n');
    const install = spawnSync("npm", ["install", "--ignore-scripts", "--no-audit", "--no-fund", "--no-package-lock", tarball], {
      cwd: project,
      env: npmEnv,
      encoding: "utf8",
    });
    assert.equal(install.status, 0, install.stderr);

    const installed = require(path.join(project, "node_modules", "@docushell", "ethos-pdf"));
    assert.equal(typeof installed.checkGrounding, "function");
    assert.equal(typeof installed.verifyClaims, "function");
    await fs.access(path.join(project, "node_modules", "@docushell", "ethos-pdf", "examples", "fixtures", "grounding.json"));
  } finally {
    await fs.rm(temporaryRoot, { recursive: true, force: true });
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
