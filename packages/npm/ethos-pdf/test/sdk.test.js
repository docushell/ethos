const assert = require("node:assert/strict");
const childProcess = require("node:child_process");
const { EventEmitter } = require("node:events");
const fs = require("node:fs/promises");
const path = require("node:path");

const calls = [];
const originalSpawn = childProcess.spawn;

childProcess.spawn = (binary, args) => {
  const child = new EventEmitter();
  child.stdout = new EventEmitter();
  child.stderr = new EventEmitter();
  child.kill = () => {};
  calls.push({ binary, args });
  process.nextTick(async () => {
    if (args[0] === "verify") {
      const citations = await fs.readFile(args[args.indexOf("--citations") + 1], "utf8");
      assert.match(citations, /"checks"/);
    }
    child.stdout.emit(
      "data",
      Buffer.from(JSON.stringify({ artifact_type: "ethos.test", schema_version: "1.0.0" })),
    );
    child.emit("close", 0, null);
  });
  return child;
};

const { EthosSdkError, checkGrounding, verifyClaims } = require("..");

const inputPath = path.resolve(__dirname, "../../../schemas/examples/grounding-source.example.json");

async function main() {
  const checked = await checkGrounding({ inputPath });
  assert.equal(checked.exitCode, 0);
  assert.equal(checked.artifact.artifact_type, "ethos.test");
  assert.deepEqual(calls[0].args.slice(0, 3), ["grounding", "check", inputPath]);

  const verified = await verifyClaims({
    inputPath,
    citations: { schema_version: "1.0.0", checks: [] },
  });
  assert.equal(verified.exitCode, 0);
  assert.deepEqual(calls[1].args.slice(0, 3), ["verify", inputPath, "--citations"]);
  await assert.rejects(
    () => verifyClaims({ inputPath, citations: {}, citationsPath: inputPath }),
    (error) => error instanceof EthosSdkError && error.code === "invalid_options",
  );
  await assert.rejects(
    () => verifyClaims({ inputPath, citationsPath: inputPath, grounding: "opendataloader-json", sourceArtifactPath: inputPath }),
    (error) => error instanceof EthosSdkError && error.code === "invalid_options",
  );
}

main()
  .finally(() => {
    childProcess.spawn = originalSpawn;
  })
  .catch((error) => {
    console.error(error);
    process.exitCode = 1;
  });
