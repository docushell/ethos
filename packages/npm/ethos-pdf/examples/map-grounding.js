#!/usr/bin/env node
"use strict";

const fs = require("node:fs");

function centipoints(value) {
  return Math.round(Number(value) * 100);
}

function mapGrounding(parser, metadata) {
  const page = metadata.pages[0];
  const elements = parser.kids.map((item) => {
    const [left, bottom, right, top] = item["bounding box"];
    return {
      id: `element-${item.id}`,
      page: `page-${item["page number"]}`,
      bbox: [
        centipoints(left),
        centipoints(page.height - top),
        centipoints(right),
        centipoints(page.height - bottom),
      ],
      kind: item.type === "heading" ? "heading" : "text_block",
      text: item.content,
    };
  });
  return {
    artifact_type: "ethos.grounding.v1",
    schema_version: "1.0.0",
    source: {
      media_type: "application/pdf",
      sha256: `sha256:${metadata.source_pdf_sha256}`,
    },
    producer: { name: "opendataloader-mapper-example", version: "1.0.0" },
    capabilities: { spans: false, char_offsets: false, tables: false },
    coordinate_system: { unit: "centipoint", origin: "top-left" },
    pages: metadata.pages.map((entry) => ({
      id: `page-${entry.index}`,
      index: entry.index,
      width: centipoints(entry.width),
      height: centipoints(entry.height),
      rotation: entry.rotation,
    })),
    elements,
  };
}

function main(argv = process.argv.slice(2)) {
  if (argv.length !== 3) {
    console.error("usage: map-grounding.js parser-output.json page-metadata.json output.json");
    return 2;
  }
  const parser = JSON.parse(fs.readFileSync(argv[0], "utf8"));
  const metadata = JSON.parse(fs.readFileSync(argv[1], "utf8"));
  const output = JSON.stringify(mapGrounding(parser, metadata));
  fs.writeFileSync(argv[2], output);
  return 0;
}

if (require.main === module) process.exitCode = main();

module.exports = { mapGrounding };
