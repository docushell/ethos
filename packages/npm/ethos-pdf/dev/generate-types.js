#!/usr/bin/env node

const fs = require("node:fs/promises");
const path = require("node:path");
const { compile } = require("json-schema-to-typescript");

const PACKAGE_ROOT = path.resolve(__dirname, "..");
const REPOSITORY_ROOT = path.resolve(PACKAGE_ROOT, "../../..");
const BANNER = [
  "// Generated from the Ethos JSON Schemas. Do not edit by hand.",
  "// Runtime JSON Schema validation remains authoritative.",
  "// Ethos verifies citation grounding, not semantic truth.",
].join("\n");

const CONTRACTS = [
  {
    input: "schemas/ethos-verification-report.schema.json",
    name: "EthosVerificationReport",
    output: "verification-report.d.ts",
    definitions: {
      fingerprint: "EthosVerificationFingerprint",
      bbox: "EthosVerificationBbox",
      check_reason: "EthosVerificationCheckReason",
      warning_code: "EthosVerificationWarningCode",
    },
  },
  {
    input: "schemas/ethos-llm-citation-output.schema.json",
    name: "EthosLlmCitationOutput",
    output: "citation-emission.d.ts",
    definitions: {
      source_id: "EthosCitationSourceId",
      text: "EthosCitationText",
      cell: "EthosCitationCell",
      quote: "EthosCitationQuote",
      value: "EthosCitationValue",
      presence: "EthosCitationPresence",
      table_cell: "EthosCitationTableCell",
      claim: "EthosCitationClaim",
    },
  },
  {
    input: "schemas/ethos-evidence-handle-context.schema.json",
    name: "EthosEvidenceHandleContext",
    output: "evidence-handle-context.d.ts",
    definitions: {
      id: "EthosEvidenceHandleId",
      cell: "EthosEvidenceHandleCell",
      locator: "EthosEvidenceHandleLocator",
      evidence: "EthosEvidenceHandle",
    },
  },
  {
    input: "schemas/ethos-llm-citation-output-v2.schema.json",
    name: "EthosLlmCitationOutputV2",
    output: "citation-emission-v2.d.ts",
    definitions: {
      id: "EthosEvidenceHandleCitationId",
      text: "EthosEvidenceHandleCitationText",
      textual: "EthosEvidenceHandleTextualCitation",
      presence: "EthosEvidenceHandlePresenceCitation",
      claim: "EthosEvidenceHandleCitationClaim",
    },
  },
  {
    input: "schemas/ethos-app-answer-release-decision.schema.json",
    name: "EthosAppAnswerReleaseDecision",
    output: "answer-release.d.ts",
    definitions: {
      proof_status: "EthosProofStatus",
      proof_limitation: "EthosProofLimitation",
      app_status: "EthosAppStatus",
      question_relevance: "EthosQuestionRelevance",
      claim_type: "EthosClaimType",
      claim_support: "EthosClaimSupport",
      release_action: "EthosReleaseAction",
      release_reason: "EthosReleaseReason",
      claim_decision: "EthosClaimDecision",
    },
  },
  {
    input: "schemas/ethos-grounding-source.schema.json",
    name: "EthosGroundingSource",
    output: "grounding-source.d.ts",
    definitions: {
      bbox: "EthosGroundingBbox",
      capabilities: "EthosGroundingCapabilities",
      cell: "EthosGroundingCell",
      coordinate_system: "EthosGroundingCoordinateSystem",
      element: "EthosGroundingElement",
      id: "EthosGroundingId",
      page: "EthosGroundingPage",
      producer: "EthosGroundingProducer",
      sha256: "EthosGroundingSha256",
      source: "EthosGroundingSourceMetadata",
      span: "EthosGroundingSpan",
      table: "EthosGroundingTable",
    },
  },
  {
    input: "schemas/ethos-grounding-validation-report.schema.json",
    name: "EthosGroundingValidationReport",
    output: "grounding-validation-report.d.ts",
    definitions: { error: "EthosGroundingValidationError" },
  },
];

function expandCitationLocators(schema) {
  for (const name of ["quote", "value", "presence"]) {
    const definition = schema.$defs[name];
    const variants = ["element_id", "span_id", "page"].map((locator) => {
      const allowed = new Set(["kind", "text", "page", locator]);
      const variant = {
        ...definition,
        required: [...definition.required, locator],
        properties: Object.fromEntries(
          Object.entries(definition.properties).filter(([property]) => allowed.has(property)),
        ),
      };
      delete variant.allOf;
      return variant;
    });
    schema.$defs[name] = { oneOf: variants };
  }
  delete schema.$defs.text_locator;
}

function projectReportConditions(schema) {
  const versionCondition = schema.allOf?.[0];
  const versions = [
    versionCondition?.then?.properties?.schema_version?.const,
    versionCondition?.else?.properties?.schema_version?.const,
  ].filter(Boolean);
  if (versions.length !== 2) {
    throw new Error("verification report schema version condition changed");
  }
  schema.properties.schema_version = { enum: versions.sort() };
  delete schema.allOf;
}

function projectAnswerReleaseConditions(schema) {
  delete schema.$defs.claim_decision.allOf;
}

function renameDefinitions(schema, names) {
  const renamed = new Set(Object.values(names));
  schema.$defs = Object.fromEntries(
    Object.entries(schema.$defs).map(([name, definition]) => [names[name], definition]),
  );
  const visit = (value) => {
    if (Array.isArray(value)) {
      value.forEach(visit);
      return;
    }
    if (!value || typeof value !== "object") return;
    if (typeof value.$ref === "string" && value.$ref.startsWith("#/$defs/")) {
      const oldName = value.$ref.slice("#/$defs/".length);
      if (renamed.has(oldName)) return;
      if (!names[oldName]) throw new Error(`unmapped schema definition: ${oldName}`);
      value.$ref = `#/$defs/${names[oldName]}`;
    }
    Object.values(value).forEach(visit);
  };
  visit(schema);
}

async function generateTypes(outputDirectory = path.join(PACKAGE_ROOT, "types")) {
  await fs.mkdir(outputDirectory, { recursive: true });
  for (const contract of CONTRACTS) {
    const schema = JSON.parse(
      await fs.readFile(path.join(REPOSITORY_ROOT, contract.input), "utf8"),
    );
    schema.title = contract.name;
    if (contract.name === "EthosVerificationReport") projectReportConditions(schema);
    if (contract.name === "EthosLlmCitationOutput") expandCitationLocators(schema);
    if (contract.name === "EthosAppAnswerReleaseDecision") {
      projectAnswerReleaseConditions(schema);
    }
    renameDefinitions(schema, contract.definitions);
    const declaration = await compile(schema, contract.name, {
      bannerComment: BANNER,
      format: true,
      unreachableDefinitions: false,
    });
    await fs.writeFile(path.join(outputDirectory, contract.output), declaration, "utf8");
  }
  const runtimeTypeImports = `import type { EthosLlmCitationOutput } from "./citation-emission";\nimport type { EthosVerificationReport } from "./verification-report";\nimport type { EthosGroundingValidationReport } from "./grounding-validation-report";\n`;
  await fs.writeFile(
    path.join(outputDirectory, "index.d.ts"),
    `${BANNER}\n\n${runtimeTypeImports}\nexport * from "./verification-report";\nexport * from "./citation-emission";\nexport * from "./evidence-handle-context";\nexport * from "./citation-emission-v2";\nexport * from "./answer-release";\nexport * from "./grounding-source";\nexport * from "./grounding-validation-report";\n\nexport interface EthosCommandResult<T> {\n  exitCode: number;\n  artifact: T | null;\n  reason: string | null;\n}\n\nexport interface CheckGroundingOptions {\n  inputPath: string;\n  outputPath?: string;\n  sourceArtifactPath?: string;\n  timeoutMs?: number;\n  signal?: AbortSignal;\n}\n\nexport interface VerifyClaimsOptions {\n  inputPath: string;\n  citationsPath?: string;\n  citations?: EthosLlmCitationOutput;\n  sourceArtifactPath?: string;\n  configPath?: string;\n  outputPath?: string;\n  failOnUngrounded?: boolean;\n  grounding?: "opendataloader-json";\n  timeoutMs?: number;\n  signal?: AbortSignal;\n}\n\nexport function checkGrounding(options: CheckGroundingOptions): Promise<EthosCommandResult<EthosGroundingValidationReport>>;\nexport function verifyClaims(options: VerifyClaimsOptions): Promise<EthosCommandResult<EthosVerificationReport>>;\n`,
    "utf8",
  );
}

if (require.main === module) {
  generateTypes().catch((error) => {
    console.error(error instanceof Error ? error.message : String(error));
    process.exitCode = 1;
  });
}

module.exports = { generateTypes };
