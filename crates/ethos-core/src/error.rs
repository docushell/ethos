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

//! Stable error codes (PRD §10) and their CLI exit codes (docs/architecture.md).
//! A PDF that cannot be parsed safely fails with one of these — never a panic.
//! Code changes are `contract-change` events; exit codes are public API.

use serde::{Deserialize, Serialize};

/// The 10 stable error codes. Wire format is snake_case.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ErrorCode {
    /// Not a PDF / unparseable header.
    InvalidPdf,
    /// Structurally corrupt PDF.
    CorruptPdf,
    /// Encrypted/password-protected input.
    PasswordProtected,
    /// Page count exceeds the configured limit.
    PageLimitExceeded,
    /// File size exceeds the configured limit.
    FileTooLarge,
    /// No extractable text — OCR would be required (out of Release 1 base).
    OcrRequired,
    /// PDF feature outside the supported profile.
    UnsupportedPdfFeature,
    /// Wall-time limit exceeded.
    ParseTimeout,
    /// Memory budget exceeded.
    MemoryLimitExceeded,
    /// Any internal failure (incl. ID-width overflow, c14n errors at runtime).
    InternalError,
}

impl ErrorCode {
    /// All codes, in contract order.
    pub const ALL: [ErrorCode; 10] = [
        ErrorCode::InvalidPdf,
        ErrorCode::CorruptPdf,
        ErrorCode::PasswordProtected,
        ErrorCode::PageLimitExceeded,
        ErrorCode::FileTooLarge,
        ErrorCode::OcrRequired,
        ErrorCode::UnsupportedPdfFeature,
        ErrorCode::ParseTimeout,
        ErrorCode::MemoryLimitExceeded,
        ErrorCode::InternalError,
    ];

    /// Stable wire string (snake_case).
    pub fn as_str(self) -> &'static str {
        match self {
            ErrorCode::InvalidPdf => "invalid_pdf",
            ErrorCode::CorruptPdf => "corrupt_pdf",
            ErrorCode::PasswordProtected => "password_protected",
            ErrorCode::PageLimitExceeded => "page_limit_exceeded",
            ErrorCode::FileTooLarge => "file_too_large",
            ErrorCode::OcrRequired => "ocr_required",
            ErrorCode::UnsupportedPdfFeature => "unsupported_pdf_feature",
            ErrorCode::ParseTimeout => "parse_timeout",
            ErrorCode::MemoryLimitExceeded => "memory_limit_exceeded",
            ErrorCode::InternalError => "internal_error",
        }
    }

    /// Public CLI exit code (docs/architecture.md). 0 = success, 2 = usage error (clap).
    pub fn exit_code(self) -> i32 {
        match self {
            ErrorCode::InvalidPdf => 3,
            ErrorCode::CorruptPdf => 4,
            ErrorCode::PasswordProtected => 5,
            ErrorCode::PageLimitExceeded => 6,
            ErrorCode::FileTooLarge => 7,
            ErrorCode::OcrRequired => 8,
            ErrorCode::UnsupportedPdfFeature => 9,
            ErrorCode::ParseTimeout => 10,
            ErrorCode::MemoryLimitExceeded => 11,
            ErrorCode::InternalError => 12,
        }
    }
}

impl core::fmt::Display for ErrorCode {
    fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
        f.write_str(self.as_str())
    }
}

/// The Ethos error type: stable code + deterministic message.
/// Messages follow fixed templates (determinism contract §8) — no paths, no timestamps.
#[derive(Debug, Clone, PartialEq, Eq, thiserror::Error, Serialize, Deserialize)]
#[error("{code}: {message}")]
pub struct EthosError {
    /// Stable code.
    pub code: ErrorCode,
    /// Deterministic, template-derived message.
    pub message: String,
}

impl EthosError {
    /// Construct with a template-derived message.
    pub fn new(code: ErrorCode, message: impl Into<String>) -> Self {
        EthosError {
            code,
            message: message.into(),
        }
    }

    /// Internal error helper.
    pub fn internal(message: impl Into<String>) -> Self {
        EthosError::new(ErrorCode::InternalError, message)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn exit_codes_are_dense_and_disjoint() {
        let mut seen = std::collections::BTreeSet::new();
        for code in ErrorCode::ALL {
            assert!(seen.insert(code.exit_code()), "duplicate exit code");
        }
        assert_eq!(*seen.first().unwrap(), 3);
        assert_eq!(*seen.last().unwrap(), 12);
        assert_eq!(seen.len(), 10);
    }

    #[test]
    fn wire_format_round_trips() {
        for code in ErrorCode::ALL {
            let json = serde_json::to_string(&code).unwrap();
            assert_eq!(json, format!("\"{}\"", code.as_str()));
            assert_eq!(serde_json::from_str::<ErrorCode>(&json).unwrap(), code);
        }
    }
}
