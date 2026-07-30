const assert = require("node:assert/strict");
const childProcess = require("node:child_process");
const { EventEmitter } = require("node:events");
const fs = require("node:fs/promises");
const path = require("node:path");

const calls = [];
const originalSpawn = childProcess.spawn;
let mode = "success";
let killCount = 0;

childProcess.spawn = (binary, args) => {
  const child = new EventEmitter();
  child.stdout = new EventEmitter();
  child.stderr = new EventEmitter();
  child.kill = () => {
    killCount += 1;
  };
  calls.push({ binary, args });
  if (mode === "timeout") return child;
  process.nextTick(async () => {
    if (args[0] === "verify") {
      const citations = await fs.readFile(args[args.indexOf("--citations") + 1], "utf8");
      assert.ok(citations.length > 0);
    }
    if (mode === "output-limit") {
      child.stdout.emit("data", Buffer.alloc(8 * 1024 * 1024 + 1));
      return;
    }
    child.stdout.emit("data", Buffer.from(JSON.stringify({ artifact_type: "ethos.test", schema_version: "1.0.0" })));
    if (mode === "exit-1") child.stderr.emit("data", Buffer.from("ungrounded"));
    child.emit("close", mode === "exit-1" ? 1 : 0, null);
  });
  return child;
};

const { EthosSdkError, checkGrounding, verifyClaims } = require("..");

const inputPath = path.resolve(__dirname, "../../../../schemas/examples/grounding-source.example.json");

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

  mode = "exit-1";
  const ungrounded = await verifyClaims({ inputPath, citationsPath: inputPath, failOnUngrounded: true });
  assert.equal(ungrounded.exitCode, 1);
  assert.equal(ungrounded.artifact.artifact_type, "ethos.test");
  assert.equal(ungrounded.reason, "ungrounded");

  mode = "output-limit";
  await assert.rejects(
    () => checkGrounding({ inputPath }),
    (error) => error instanceof EthosSdkError && error.code === "output_limit",
  );

  mode = "timeout";
  await assert.rejects(
    () => checkGrounding({ inputPath, timeoutMs: 1 }),
    (error) => error instanceof EthosSdkError && error.code === "timeout",
  );

  const controller = new AbortController();
  const cancelled = checkGrounding({ inputPath, timeoutMs: 1000, signal: controller.signal });
  controller.abort();
  await assert.rejects(
    () => cancelled,
    (error) => error instanceof EthosSdkError && error.code === "cancelled",
  );
  assert.equal(killCount, 3);
}

main()
  .finally(() => {
    childProcess.spawn = originalSpawn;
  })
  .catch((error) => {
    console.error(error);
    process.exitCode = 1;
  });
