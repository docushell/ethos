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

use ethos_core::error::EthosError;
use ethos_core::evidence_anchor::{EvidenceAnchorReport, EvidenceAnchorRequest};

use crate::grounding::load_source;
use crate::{default_max_input_bytes, read_file_limited, write_output, EvidenceAnchorArgs, Failure};

pub(crate) fn evidence_anchor(args: EvidenceAnchorArgs) -> Result<(), Failure> {
    let max_input_bytes = default_max_input_bytes();
    let request_bytes = read_file_limited(&args.evidence_refs, max_input_bytes)?;
    let request: EvidenceAnchorRequest = serde_json::from_slice(&request_bytes).map_err(|_| {
        Failure::Usage("evidence refs file does not match the evidence anchor request shape".into())
    })?;

    let source = load_source(&args.input, args.grounding.as_deref())?;
    let report = ethos_verify::anchor_evidence(&source, request)
        .map_err(|error| Failure::Usage(error.to_string()))?;

    write_anchor_report(args.out, &report)
}

fn write_anchor_report(
    out: Option<std::path::PathBuf>,
    report: &EvidenceAnchorReport,
) -> Result<(), Failure> {
    let value = serde_json::to_value(report).map_err(|e| EthosError::internal(e.to_string()))?;
    let mut bytes =
        ethos_core::c14n::c14n_bytes(&value).map_err(|e| EthosError::internal(e.message))?;
    bytes.push(b'\n');
    write_output(out, &bytes)
}
