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

//! Stable warning codes (PRD §10). New codes are `contract-change` events; renames are
//! breaking. Error codes live in [`crate::error`] (full feature) because only the parser
//! emits them; warning codes are shared with verification reports (verify-types feature).

use serde::{Deserialize, Serialize};

/// The 11 stable warning codes. Wire format is snake_case.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum WarningCode {
    /// Reading-order heuristic below confidence threshold.
    LowConfidenceReadingOrder,
    /// Table-structure heuristic below confidence threshold.
    LowConfidenceTableStructure,
    /// Hidden text detected (excluded from default chunks).
    HiddenTextDetected,
    /// Text positioned off the page box (excluded from default chunks).
    OffPageTextDetected,
    /// Low-contrast (e.g. white-on-white) text detected (excluded from default chunks).
    LowContrastTextDetected,
    /// Annotations present on a page.
    AnnotationsPresent,
    /// External links present (never followed).
    ExternalLinksPresent,
    /// Page has no extractable text (image-only).
    ImageOnlyPage,
    /// Annotation subtype not supported.
    UnsupportedAnnotation,
    /// Parse completed partially (e.g. a page-level failure inside limits).
    PartialParse,
    /// A grounding/verification capability was missing; result downgraded explicitly.
    CapabilityLimited,
}

impl WarningCode {
    /// All codes, in contract order.
    pub const ALL: [WarningCode; 11] = [
        WarningCode::LowConfidenceReadingOrder,
        WarningCode::LowConfidenceTableStructure,
        WarningCode::HiddenTextDetected,
        WarningCode::OffPageTextDetected,
        WarningCode::LowContrastTextDetected,
        WarningCode::AnnotationsPresent,
        WarningCode::ExternalLinksPresent,
        WarningCode::ImageOnlyPage,
        WarningCode::UnsupportedAnnotation,
        WarningCode::PartialParse,
        WarningCode::CapabilityLimited,
    ];

    /// Stable wire string (snake_case), identical to the serde form.
    pub fn as_str(self) -> &'static str {
        match self {
            WarningCode::LowConfidenceReadingOrder => "low_confidence_reading_order",
            WarningCode::LowConfidenceTableStructure => "low_confidence_table_structure",
            WarningCode::HiddenTextDetected => "hidden_text_detected",
            WarningCode::OffPageTextDetected => "off_page_text_detected",
            WarningCode::LowContrastTextDetected => "low_contrast_text_detected",
            WarningCode::AnnotationsPresent => "annotations_present",
            WarningCode::ExternalLinksPresent => "external_links_present",
            WarningCode::ImageOnlyPage => "image_only_page",
            WarningCode::UnsupportedAnnotation => "unsupported_annotation",
            WarningCode::PartialParse => "partial_parse",
            WarningCode::CapabilityLimited => "capability_limited",
        }
    }

    /// Security-class codes route to `security_warnings` / the security report;
    /// the rest are parser warnings (determinism contract §8).
    pub fn is_security(self) -> bool {
        matches!(
            self,
            WarningCode::HiddenTextDetected
                | WarningCode::OffPageTextDetected
                | WarningCode::LowContrastTextDetected
                | WarningCode::AnnotationsPresent
                | WarningCode::ExternalLinksPresent
                | WarningCode::UnsupportedAnnotation
                | WarningCode::ImageOnlyPage
        )
    }

    /// Security-report codes that currently require inventory data not present in the
    /// canonical document warning lane.
    pub fn is_inventory_backed_security(self) -> bool {
        matches!(
            self,
            WarningCode::AnnotationsPresent
                | WarningCode::ExternalLinksPresent
                | WarningCode::UnsupportedAnnotation
        )
    }

    /// Security-report codes backed by text spans and excluded from default chunks.
    pub fn is_text_backed_security(self) -> bool {
        matches!(
            self,
            WarningCode::HiddenTextDetected
                | WarningCode::OffPageTextDetected
                | WarningCode::LowContrastTextDetected
        )
    }

    /// Security-report codes that require a page reference.
    pub fn is_page_backed_security(self) -> bool {
        self.is_text_backed_security() || matches!(self, WarningCode::ImageOnlyPage)
    }

    /// Warning codes that must never appear in default chunk artifacts.
    pub fn excludes_from_default_chunks(self) -> bool {
        self.is_text_backed_security()
    }

    /// Fixed message template for security-report findings.
    pub fn security_report_message_template(self) -> Option<&'static str> {
        match self {
            WarningCode::HiddenTextDetected => {
                Some("hidden text detected: excluded from default chunks")
            }
            WarningCode::OffPageTextDetected => {
                Some("off-page text detected: excluded from default chunks")
            }
            WarningCode::LowContrastTextDetected => {
                Some("low-contrast text detected: excluded from default chunks")
            }
            WarningCode::AnnotationsPresent => Some("annotations present on page"),
            WarningCode::ExternalLinksPresent => Some("external links present on page"),
            WarningCode::UnsupportedAnnotation => Some("unsupported annotation ignored"),
            WarningCode::ImageOnlyPage => Some("image-only page"),
            _ => None,
        }
    }
}

impl core::fmt::Display for WarningCode {
    fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
        f.write_str(self.as_str())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn wire_format_is_snake_case_and_stable() {
        for code in WarningCode::ALL {
            let json = serde_json::to_string(&code).unwrap();
            assert_eq!(json, format!("\"{}\"", code.as_str()));
            let back: WarningCode = serde_json::from_str(&json).unwrap();
            assert_eq!(back, code);
        }
    }

    #[test]
    fn security_split_matches_contract() {
        let security: Vec<_> = WarningCode::ALL
            .iter()
            .filter(|c| c.is_security())
            .map(|c| c.as_str())
            .collect();
        assert_eq!(
            security,
            vec![
                "hidden_text_detected",
                "off_page_text_detected",
                "low_contrast_text_detected",
                "annotations_present",
                "external_links_present",
                "image_only_page",
                "unsupported_annotation",
            ]
        );
    }

    #[test]
    fn security_report_warning_policy_matches_contract() {
        let inventory_backed: Vec<_> = WarningCode::ALL
            .iter()
            .filter(|c| c.is_inventory_backed_security())
            .map(|c| c.as_str())
            .collect();
        assert_eq!(
            inventory_backed,
            vec![
                "annotations_present",
                "external_links_present",
                "unsupported_annotation",
            ]
        );

        let text_backed: Vec<_> = WarningCode::ALL
            .iter()
            .filter(|c| c.is_text_backed_security())
            .map(|c| c.as_str())
            .collect();
        assert_eq!(
            text_backed,
            vec![
                "hidden_text_detected",
                "off_page_text_detected",
                "low_contrast_text_detected",
            ]
        );

        let page_backed: Vec<_> = WarningCode::ALL
            .iter()
            .filter(|c| c.is_page_backed_security())
            .map(|c| c.as_str())
            .collect();
        assert_eq!(
            page_backed,
            vec![
                "hidden_text_detected",
                "off_page_text_detected",
                "low_contrast_text_detected",
                "image_only_page",
            ]
        );

        let default_chunk_excluded: Vec<_> = WarningCode::ALL
            .iter()
            .filter(|c| c.excludes_from_default_chunks())
            .map(|c| c.as_str())
            .collect();
        assert_eq!(default_chunk_excluded, text_backed);
    }

    #[test]
    fn security_report_message_templates_match_contract() {
        let templates: Vec<_> = WarningCode::ALL
            .iter()
            .filter_map(|c| {
                c.security_report_message_template()
                    .map(|template| (c.as_str(), template))
            })
            .collect();
        assert_eq!(
            templates,
            vec![
                (
                    "hidden_text_detected",
                    "hidden text detected: excluded from default chunks",
                ),
                (
                    "off_page_text_detected",
                    "off-page text detected: excluded from default chunks",
                ),
                (
                    "low_contrast_text_detected",
                    "low-contrast text detected: excluded from default chunks",
                ),
                ("annotations_present", "annotations present on page"),
                ("external_links_present", "external links present on page"),
                ("image_only_page", "image-only page"),
                ("unsupported_annotation", "unsupported annotation ignored"),
            ]
        );
    }
}
