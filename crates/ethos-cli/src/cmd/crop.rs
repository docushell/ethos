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

use ethos_core::crop_element::{resolve_crop_element_descriptor, CropElementRequest};
use ethos_core::error::EthosError;

use crate::{read_document, read_file_limited, write_output, CropElementArgs, Failure};

pub(crate) fn crop_element(args: CropElementArgs) -> Result<(), Failure> {
    let document = read_document(&args.input)?;
    let request = read_crop_element_request(&args.request)?;
    let descriptor =
        resolve_crop_element_descriptor(&document, &request, &args.check_id).map_err(|error| {
            Failure::Usage(format!(
                "crop_element request failed: {}",
                error.diagnostic()
            ))
        })?;
    let mut bytes = ethos_core::c14n::c14n_bytes(
        &serde_json::to_value(descriptor)
            .map_err(|_| EthosError::internal("crop_element descriptor serialization failed"))?,
    )
    .map_err(|error| EthosError::internal(error.message))?;
    bytes.push(b'\n');
    write_output(args.out, &bytes)
}

fn read_crop_element_request(path: &std::path::Path) -> Result<CropElementRequest, Failure> {
    let bytes = read_file_limited(path, crate::default_max_input_bytes())?;
    serde_json::from_slice(&bytes)
        .map_err(|error| Failure::Usage(format!("crop_element request is invalid: {error}")))
}
