#!/usr/bin/env node
"use strict";

if (!process.env.ETHOS_PDFIUM_LIBRARY_PATH) {
  console.warn(
    "ethos-pdf: PDFium-backed commands require ETHOS_PDFIUM_LIBRARY_PATH. " +
      "This install-time warning is non-blocking; set it at runtime before PDF commands. " +
      "See QUICKSTART.md for caller-provided PDFium setup."
  );
}
