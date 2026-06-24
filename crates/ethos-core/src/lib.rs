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

//! # ethos-core
//!
//! The Ethos product contract in Rust: canonical document model, deterministic
//! serialization (c14n v1), fingerprints, stable error/warning codes, page-range
//! configuration, and the trait boundaries between crates.
//!
//! Normative references: `schemas/*.json` and `docs/determinism-contract.md`.
//! Contract changes happen only via `contract-change` PRs with version bumps.
//!
//! ## Feature layers (invariant 4: verify portability)
//!
//! - `grounding` — the [`grounding::GroundingSource`] trait module alone. `ethos-verify`
//!   depends on `ethos-core` with `default-features = false, features = ["grounding", "verify-types"]`
//!   and therefore can never see parser internals. CI builds it that way to prove it.
//! - `verify-types` — verification report/config schema types + stable warning codes.
//! - `full` (default) — canonical model, c14n, fingerprints, geometry, config, traits.
//! - `crop-element` — source-only pre-alpha crop descriptor API, intentionally opt-in.

#![forbid(unsafe_code)]
#![warn(missing_docs)]

#[cfg(feature = "grounding")]
pub mod grounding;

#[cfg(feature = "verify-types")]
pub mod codes;
#[cfg(feature = "verify-types")]
pub mod evidence_anchor;
#[cfg(feature = "verify-types")]
pub mod verify_types;

#[cfg(feature = "full")]
pub mod c14n;
#[cfg(feature = "full")]
pub mod config;
#[cfg(feature = "crop-element")]
pub mod crop_element;
#[cfg(feature = "full")]
pub mod error;
#[cfg(feature = "full")]
pub mod fingerprint;
#[cfg(feature = "full")]
pub mod geom;
#[cfg(feature = "full")]
pub mod ids;
#[cfg(feature = "full")]
pub mod model;
#[cfg(feature = "full")]
pub mod traits;

/// Canonical schema version emitted by this crate (all five schemas move in lockstep).
pub const SCHEMA_VERSION: &str = "1.0.0";

/// The deterministic profile this crate is built to honor.
pub const PROFILE_ID: &str = "ethos-deterministic-v1";

/// c14n algorithm version implemented by [`c14n`] (when the `full` feature is on).
pub const C14N_VERSION: &str = "c14n-v1";

/// ID scheme version implemented by [`ids`] (when the `full` feature is on).
pub const ID_SCHEME_VERSION: &str = "ids-v1";
