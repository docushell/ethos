const assert = require("node:assert/strict");
const fs = require("node:fs/promises");
const os = require("node:os");
const path = require("node:path");
const { generateTypes } = require("../dev/generate-types");

const PACKAGE_ROOT = path.resolve(__dirname, "..");
const EXPECTED_FILES = [
  "answer-release.d.ts",
  "citation-emission-v2.d.ts",
  "citation-emission.d.ts",
  "evidence-handle-context.d.ts",
  "grounding-source.d.ts",
  "grounding-validation-report.d.ts",
  "index.d.ts",
  "verification-report.d.ts",
];

async function readOutput(directory) {
  const files = (await fs.readdir(directory)).sort();
  assert.deepEqual(files, EXPECTED_FILES);
  return Promise.all(files.map((file) => fs.readFile(path.join(directory, file))));
}

async function main() {
  const temporaryRoot = await fs.mkdtemp(path.join(os.tmpdir(), "ethos-types-"));
  try {
    const first = path.join(temporaryRoot, "first");
    const second = path.join(temporaryRoot, "second");
    await generateTypes(first);
    await generateTypes(second);

    const firstOutput = await readOutput(first);
    const secondOutput = await readOutput(second);
    const committedOutput = await readOutput(path.join(PACKAGE_ROOT, "types"));
    assert.deepEqual(firstOutput, secondOutput, "generated declarations differ across runs");
    assert.deepEqual(firstOutput, committedOutput, "checked-in declarations are stale");

    const packageJson = JSON.parse(
      await fs.readFile(path.join(PACKAGE_ROOT, "package.json"), "utf8"),
    );
    assert.equal(packageJson.types, "./types/index.d.ts");
    assert(packageJson.files.includes("types/"));
  } finally {
    await fs.rm(temporaryRoot, { recursive: true, force: true });
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
