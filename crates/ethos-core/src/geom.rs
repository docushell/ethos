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

//! Quantized geometry (determinism contract §4). Invariant 1: extraction emits these
//! types — raw `f64` tuples cannot cross the backend boundary.

use serde::de::Error as _;
use serde::{Deserialize, Deserializer, Serialize, Serializer};

/// Largest magnitude allowed in canonical values (2^53 − 1, ecosystem-safe).
pub const MAX_SAFE_INT: i64 = 9_007_199_254_740_991;

/// Quantization failure (NaN/∞ input or out-of-range result).
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct QuantizeError;

impl core::fmt::Display for QuantizeError {
    fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
        f.write_str("non-finite or out-of-range coordinate")
    }
}
impl std::error::Error for QuantizeError {}

/// Quantize a point-space coordinate to integer quanta:
/// `round_half_away_from_zero(pts × quantum_per_point)`.
///
/// This is the only permitted float math on the canonical path; IEEE-754 double
/// multiply + floor/ceil on identical inputs is identical across supported platforms.
pub fn quantize(pts: f64, quantum_per_point: u32) -> Result<i64, QuantizeError> {
    if !pts.is_finite() {
        return Err(QuantizeError);
    }
    let scaled = pts * f64::from(quantum_per_point);
    if !scaled.is_finite() {
        return Err(QuantizeError);
    }
    let rounded = if scaled >= 0.0 {
        (scaled + 0.5).floor()
    } else {
        (scaled - 0.5).ceil()
    };
    if rounded.abs() > MAX_SAFE_INT as f64 {
        return Err(QuantizeError);
    }
    Ok(rounded as i64)
}

/// A point in quanta, top-left origin.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct QPoint {
    /// x in quanta.
    pub x: i64,
    /// y in quanta (grows downward).
    pub y: i64,
}

/// An axis-aligned rectangle in quanta, top-left origin, `x0 ≤ x1`, `y0 ≤ y1`.
/// Serializes as the contract bbox array `[x0, y0, x1, y1]`.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct QRect {
    /// Left edge.
    pub x0: i64,
    /// Top edge.
    pub y0: i64,
    /// Right edge.
    pub x1: i64,
    /// Bottom edge.
    pub y1: i64,
}

impl QRect {
    /// Construct with ordering validation.
    pub fn new(x0: i64, y0: i64, x1: i64, y1: i64) -> Result<Self, QuantizeError> {
        if x0 > x1 || y0 > y1 {
            return Err(QuantizeError);
        }
        Ok(QRect { x0, y0, x1, y1 })
    }

    /// As the contract array form.
    pub fn to_array(self) -> [i64; 4] {
        [self.x0, self.y0, self.x1, self.y1]
    }

    /// True when `other` is contained in `self` expanded by `tolerance_q` on every side.
    pub fn contains_with_tolerance(self, other: QRect, tolerance_q: i64) -> bool {
        other.x0 >= self.x0 - tolerance_q
            && other.y0 >= self.y0 - tolerance_q
            && other.x1 <= self.x1 + tolerance_q
            && other.y1 <= self.y1 + tolerance_q
    }
}

impl Serialize for QRect {
    fn serialize<S: Serializer>(&self, s: S) -> Result<S::Ok, S::Error> {
        self.to_array().serialize(s)
    }
}

impl<'de> Deserialize<'de> for QRect {
    fn deserialize<D: Deserializer<'de>>(d: D) -> Result<Self, D::Error> {
        let [x0, y0, x1, y1] = <[i64; 4]>::deserialize(d)?;
        QRect::new(x0, y0, x1, y1).map_err(|_| D::Error::custom("malformed bbox: x0>x1 or y0>y1"))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use proptest::prelude::*;

    #[test]
    fn rounding_is_half_away_from_zero() {
        // 0.005pt @ q=100 → 0.5 quanta → 1; -0.005 → -1
        assert_eq!(quantize(0.005, 100).unwrap(), 1);
        assert_eq!(quantize(-0.005, 100).unwrap(), -1);
        assert_eq!(quantize(0.004, 100).unwrap(), 0);
        assert_eq!(quantize(-0.004, 100).unwrap(), 0);
        assert_eq!(quantize(612.0, 100).unwrap(), 61200);
        assert_eq!(quantize(0.0, 100).unwrap(), 0);
        // -0.0 normalizes to 0 (no negative zero in canonical values)
        assert_eq!(quantize(-0.0, 100).unwrap(), 0);
    }

    #[test]
    fn rejects_non_finite_and_overflow() {
        assert!(quantize(f64::NAN, 100).is_err());
        assert!(quantize(f64::INFINITY, 100).is_err());
        assert!(quantize(1e17, 100).is_err());
    }

    #[test]
    fn qrect_validates_and_serializes_as_array() {
        assert!(QRect::new(5, 5, 4, 9).is_err());
        let r = QRect::new(1, 2, 3, 4).unwrap();
        assert_eq!(serde_json::to_string(&r).unwrap(), "[1,2,3,4]");
        let back: QRect = serde_json::from_str("[1,2,3,4]").unwrap();
        assert_eq!(back, r);
        assert!(serde_json::from_str::<QRect>("[5,5,4,9]").is_err());
    }

    proptest! {
        #[test]
        fn quantization_of_integers_is_exact(n in -1_000_000i64..1_000_000i64) {
            // integer points quantize to exactly n*q (idempotence basis)
            prop_assert_eq!(quantize(n as f64, 100).unwrap(), n * 100);
        }

        #[test]
        fn quantize_is_monotonic(a in -10_000.0f64..10_000.0, b in -10_000.0f64..10_000.0) {
            let (lo, hi) = if a <= b { (a, b) } else { (b, a) };
            prop_assert!(quantize(lo, 100).unwrap() <= quantize(hi, 100).unwrap());
        }
    }
}
