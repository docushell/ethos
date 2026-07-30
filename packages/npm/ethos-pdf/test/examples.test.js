const assert = require("node:assert/strict");
const fs = require("node:fs/promises");
const os = require("node:os");
const path = require("node:path");
const { spawnSync } = require("node:child_process");

const PACKAGE_ROOT = path.resolve(__dirname, "..");
const FIXTURES = path.join(PACKAGE_ROOT, "examples", "fixtures");

async function main() {
  const temporaryRoot = await fs.mkdtemp(path.join(os.tmpdir(), "ethos-mappers-"));
  try {
    const jsOutput = path.join(temporaryRoot, "javascript.json");
    const pythonOutput = path.join(temporaryRoot, "python.json");
    const inputs = [
      path.join(FIXTURES, "parser-output.json"),
      path.join(FIXTURES, "page-metadata.json"),
    ];
    const js = spawnSync(process.execPath, [path.join(PACKAGE_ROOT, "examples", "map-grounding.js"), ...inputs, jsOutput], { encoding: "utf8" });
    assert.equal(js.status, 0, js.stderr);
    const python = spawnSync(process.env.PYTHON || "python3", [path.join(PACKAGE_ROOT, "examples", "map_grounding.py"), ...inputs, pythonOutput], { encoding: "utf8" });
    assert.equal(python.status, 0, python.stderr);
    const expected = await fs.readFile(path.join(FIXTURES, "grounding.json"));
    const first = await fs.readFile(jsOutput);
    const second = await fs.readFile(pythonOutput);
    assert.deepEqual(first, second, "JavaScript and Python mapper bytes differ");
    assert.deepEqual(first, expected, "committed grounding fixture is stale");
  } finally {
    await fs.rm(temporaryRoot, { recursive: true, force: true });
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
