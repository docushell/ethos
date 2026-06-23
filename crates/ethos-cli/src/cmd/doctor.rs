/*
 * Copyright 2026 The Ethos maintainers
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

use std::path::PathBuf;
use std::time::Duration;

use ethos_core::error::{ErrorCode, EthosError};
use ethos_pdf::PDFIUM_LIBRARY_PATH_ENV;

use crate::worker::probe_pdfium_with_worker;
use crate::{write_output, DoctorArgs, Failure, INTERNAL_PDFIUM_LOAD_PROBE_ENV};

const DOCTOR_PDFIUM_PROBE_TIMEOUT: Duration = Duration::from_secs(5);
const NPM_VENDOR_MANIFEST: &str =
    include_str!("../../../../packages/npm/ethos-pdf/vendor/manifest.json");

pub(crate) fn doctor(args: DoctorArgs) -> Result<(), Failure> {
    let platform = current_platform();
    let supported = packaged_target_status(&platform);
    let pdfium = pdfium_status();
    let text = doctor_output(&platform, &supported, &pdfium);
    write_output(None, text.as_bytes())?;
    if args.require_pdfium && !matches!(pdfium.kind, PdfiumStatusKind::Usable) {
        return Err(pdfium_error(pdfium.message));
    }
    Ok(())
}

pub(crate) fn pdfium_load_probe() -> Result<(), Failure> {
    if std::env::var(INTERNAL_PDFIUM_LOAD_PROBE_ENV).as_deref() != Ok("1") {
        return Err(Failure::Usage(format!(
            "__pdfium-load-probe requires {INTERNAL_PDFIUM_LOAD_PROBE_ENV}=1"
        )));
    }
    let backend = ethos_pdf::PdfiumBackend::default();
    backend.probe_library()?;
    Ok(())
}

fn pdfium_status() -> PdfiumStatus {
    let Some(path) = std::env::var_os(PDFIUM_LIBRARY_PATH_ENV).map(PathBuf::from) else {
        return PdfiumStatus::warning(format!(
            "{PDFIUM_LIBRARY_PATH_ENV} is unset; set it to the caller-provided PDFium dynamic library path before PDFium-backed commands"
        ));
    };
    if !path.is_file() {
        return PdfiumStatus::warning(format!(
            "{PDFIUM_LIBRARY_PATH_ENV} does not point to a file; configured PDFium is not usable by Ethos"
        ));
    }
    match probe_pdfium_with_worker(DOCTOR_PDFIUM_PROBE_TIMEOUT) {
        Ok(()) => PdfiumStatus {
            kind: PdfiumStatusKind::Usable,
            message: "configured PDFium is usable by Ethos".to_string(),
        },
        Err(Failure::Ethos(error)) => PdfiumStatus::warning(format!(
            "configured PDFium is not usable by Ethos: {}",
            error.message
        )),
        Err(Failure::Usage(message)) => {
            PdfiumStatus::warning(format!("configured PDFium probe did not run: {message}"))
        }
        Err(Failure::EthosWithDiagnostics { error, .. }) => PdfiumStatus::warning(format!(
            "configured PDFium is not usable by Ethos: {}",
            error.message
        )),
        Err(Failure::Ungrounded) => PdfiumStatus::warning(
            "configured PDFium probe returned an unexpected verification status".to_string(),
        ),
    }
}

fn doctor_output(platform: &str, supported: &str, pdfium: &PdfiumStatus) -> String {
    format!(
        "\
Ethos doctor
version: ethos {}
platform: {platform}
packaged target: {supported}
PDFium:
  {PDFIUM_LIBRARY_PATH_ENV}: {}
  status: {}
  message: {}
  note: Ethos checks whether the operator-configured PDFium is usable; it does not vet untrusted dynamic libraries.
",
        env!("CARGO_PKG_VERSION"),
        pdfium.env_status(),
        pdfium.label(),
        pdfium.message,
    )
}

fn current_platform() -> String {
    let os = match std::env::consts::OS {
        "macos" => "darwin",
        other => other,
    };
    let arch = match std::env::consts::ARCH {
        "aarch64" => "arm64",
        "x86_64" => "x64",
        other => other,
    };
    format!("{os}:{arch}")
}

fn packaged_target_status(platform: &str) -> String {
    if manifest_targets().iter().any(|target| target == platform) {
        "supported by the approved npm vendor manifest".to_string()
    } else {
        "not listed in the approved npm vendor manifest".to_string()
    }
}

fn manifest_targets() -> Vec<String> {
    let value: serde_json::Value =
        serde_json::from_str(NPM_VENDOR_MANIFEST).expect("npm vendor manifest is valid JSON");
    value["targets"]
        .as_object()
        .expect("npm vendor manifest targets are an object")
        .keys()
        .cloned()
        .collect()
}

fn pdfium_error(message: String) -> Failure {
    Failure::Ethos(EthosError::new(ErrorCode::InternalError, message))
}

#[derive(Clone, Copy)]
enum PdfiumStatusKind {
    Warning,
    Usable,
}

struct PdfiumStatus {
    kind: PdfiumStatusKind,
    message: String,
}

impl PdfiumStatus {
    fn warning(message: String) -> Self {
        PdfiumStatus {
            kind: PdfiumStatusKind::Warning,
            message,
        }
    }

    fn env_status(&self) -> &'static str {
        match std::env::var_os(PDFIUM_LIBRARY_PATH_ENV) {
            Some(_) => "set",
            None => "unset",
        }
    }

    fn label(&self) -> &'static str {
        match self.kind {
            PdfiumStatusKind::Warning => "warning",
            PdfiumStatusKind::Usable => "usable",
        }
    }
}
