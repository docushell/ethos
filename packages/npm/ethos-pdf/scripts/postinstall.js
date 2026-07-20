#!/usr/bin/env node
"use strict";

if (!process.env.ETHOS_PDFIUM_LIBRARY_PATH) {
  console.warn(
    "ethos-pdf: PDFium setup command: scripts/fetch-pdfium.sh. " +
      "Run it from an Ethos source checkout, apply the printed " +
      "ETHOS_PDFIUM_LIBRARY_PATH export, then run ethos doctor --require-pdfium. " +
      "The script verifies pinned archive and runtime sha256 values and never runs " +
      "automatically. See docs/pdfium-manual-setup.md."
  );
}
