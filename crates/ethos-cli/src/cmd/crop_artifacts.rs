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

use std::path::{Path, PathBuf};

use ethos_core::crop_element::CropElementDescriptor;
use ethos_core::error::EthosError;
use ethos_core::fingerprint::source_fingerprint;
use ethos_core::geom::QRect;
use ethos_core::model::Document;
use ethos_pdf::PdfiumBackend;

use crate::{default_max_input_bytes, read_file_limited, Failure};

pub(crate) struct CropSourcePdf {
    pub(crate) bytes: Vec<u8>,
    pub(crate) fingerprint: String,
}

pub(crate) fn load_bound_crop_source_pdf(
    doc: &Document,
    source_pdf: &Path,
) -> Result<CropSourcePdf, Failure> {
    let bytes = read_file_limited(source_pdf, default_max_input_bytes())?;
    if !bytes[..bytes.len().min(1024)]
        .windows(5)
        .any(|window| window == b"%PDF-")
    {
        return Err(Failure::Usage(
            "crop source PDF does not contain a PDF header".to_string(),
        ));
    }
    let actual = source_fingerprint(&bytes);
    if actual != doc.source.fingerprint {
        return Err(Failure::Usage(
            "crop source PDF fingerprint does not match document source fingerprint".to_string(),
        ));
    }
    Ok(CropSourcePdf {
        bytes,
        fingerprint: actual,
    })
}

pub(crate) fn write_crop_descriptor_artifact(
    crop_dir: &Path,
    descriptor: &CropElementDescriptor,
) -> Result<(), Failure> {
    let path = crop_descriptor_path(crop_dir, &descriptor.crop_ref)?;
    let mut bytes = crop_descriptor_bytes(descriptor)?;
    bytes.push(b'\n');
    std::fs::write(&path, bytes).map_err(|_| {
        Failure::Usage(format!(
            "cannot write crop descriptor artifact: {}",
            path.display()
        ))
    })
}

pub(crate) fn write_rendered_crop_artifact(
    crop_dir: &Path,
    descriptor: &mut CropElementDescriptor,
    source_pdf: &CropSourcePdf,
) -> Result<(), Failure> {
    let rendered = render_crop_png(source_pdf, descriptor)?;
    let rendered_ref = rendered_ref_for(&descriptor.crop_ref)?;
    let rendered_path = crop_artifact_path(crop_dir, &rendered_ref)?;
    std::fs::write(&rendered_path, &rendered.bytes).map_err(|_| {
        Failure::Usage(format!(
            "cannot write rendered crop artifact: {}",
            rendered_path.display()
        ))
    })?;
    descriptor.source_pdf_fingerprint = Some(source_pdf.fingerprint.clone());
    descriptor.rendered_ref = Some(rendered_ref);
    descriptor.rendered_format = Some("png".to_string());
    descriptor.rendered_sha256 = Some(ethos_core::c14n::sha256_hex_bytes(&rendered.bytes));
    descriptor.rendered_width_px = Some(rendered.width_px);
    descriptor.rendered_height_px = Some(rendered.height_px);
    Ok(())
}

fn crop_descriptor_path(crop_dir: &Path, crop_ref: &str) -> Result<PathBuf, Failure> {
    crop_artifact_path(crop_dir, crop_ref)
}

fn crop_artifact_path(crop_dir: &Path, crop_ref: &str) -> Result<PathBuf, Failure> {
    let path = Path::new(crop_ref);
    if path.components().count() != 1
        || path.file_name().and_then(|name| name.to_str()) != Some(crop_ref)
    {
        return Err(Failure::Ethos(EthosError::internal(
            "crop_ref is not a safe artifact filename",
        )));
    }
    Ok(crop_dir.join(path))
}

fn crop_descriptor_bytes(descriptor: &CropElementDescriptor) -> Result<Vec<u8>, Failure> {
    let descriptor_value =
        serde_json::to_value(descriptor).map_err(|e| EthosError::internal(e.to_string()))?;
    ethos_core::c14n::c14n_bytes(&descriptor_value)
        .map_err(|e| Failure::Ethos(EthosError::internal(e.message)))
}

struct RenderedCrop {
    width_px: u32,
    height_px: u32,
    bytes: Vec<u8>,
}

fn render_crop_png(
    source_pdf: &CropSourcePdf,
    descriptor: &CropElementDescriptor,
) -> Result<RenderedCrop, Failure> {
    let page_index = native_page_index(&descriptor.page)?;
    let bbox = QRect::new(
        descriptor.bbox[0],
        descriptor.bbox[1],
        descriptor.bbox[2],
        descriptor.bbox[3],
    )
    .map_err(|_| Failure::Ethos(EthosError::internal("crop descriptor bbox is malformed")))?;
    let raw = PdfiumBackend::default().render_crop_raw(&source_pdf.bytes, page_index, bbox)?;
    let bytes = png_from_bgra(raw.width_px, raw.height_px, raw.stride, &raw.bytes)?;
    Ok(RenderedCrop {
        width_px: raw.width_px,
        height_px: raw.height_px,
        bytes,
    })
}

fn native_page_index(page: &str) -> Result<u32, Failure> {
    let Some(digits) = page.strip_prefix('p') else {
        return Err(Failure::Ethos(EthosError::internal(
            "crop descriptor page is not a native Ethos page id",
        )));
    };
    if digits.len() != 4 || !digits.as_bytes().iter().all(u8::is_ascii_digit) {
        return Err(Failure::Ethos(EthosError::internal(
            "crop descriptor page is not a native Ethos page id",
        )));
    }
    let page_index = digits
        .parse::<u32>()
        .map_err(|_| EthosError::internal("crop descriptor page index overflow"))?;
    if page_index == 0 {
        return Err(Failure::Ethos(EthosError::internal(
            "crop descriptor page index must be positive",
        )));
    }
    Ok(page_index)
}

fn rendered_ref_for(crop_ref: &str) -> Result<String, Failure> {
    let Some(stem) = crop_ref.strip_suffix(".json") else {
        return Err(Failure::Ethos(EthosError::internal(
            "crop_ref is not a descriptor filename",
        )));
    };
    Ok(format!("{stem}.png"))
}

fn png_from_bgra(
    width_px: u32,
    height_px: u32,
    stride: u32,
    bgra: &[u8],
) -> Result<Vec<u8>, Failure> {
    let width =
        usize::try_from(width_px).map_err(|_| EthosError::internal("PNG width overflow"))?;
    let height =
        usize::try_from(height_px).map_err(|_| EthosError::internal("PNG height overflow"))?;
    let stride =
        usize::try_from(stride).map_err(|_| EthosError::internal("PNG stride overflow"))?;
    let row_bytes = width
        .checked_mul(4)
        .ok_or_else(|| EthosError::internal("PNG row width overflow"))?;
    if stride < row_bytes {
        return Err(Failure::Ethos(EthosError::internal(
            "rendered crop stride is smaller than row width",
        )));
    }
    let expected_len = stride
        .checked_mul(height)
        .ok_or_else(|| EthosError::internal("rendered crop buffer length overflow"))?;
    if bgra.len() != expected_len {
        return Err(Failure::Ethos(EthosError::internal(
            "rendered crop buffer length mismatch",
        )));
    }

    let scanline_bytes = row_bytes
        .checked_add(1)
        .and_then(|row| row.checked_mul(height))
        .ok_or_else(|| EthosError::internal("PNG scanline buffer length overflow"))?;
    let mut scanlines = Vec::with_capacity(scanline_bytes);
    for row in 0..height {
        scanlines.push(0);
        let row_start = row
            .checked_mul(stride)
            .ok_or_else(|| EthosError::internal("PNG source row offset overflow"))?;
        for pixel in bgra[row_start..row_start + row_bytes].chunks_exact(4) {
            scanlines.extend_from_slice(&[pixel[2], pixel[1], pixel[0], pixel[3]]);
        }
    }

    let mut png = Vec::new();
    png.extend_from_slice(b"\x89PNG\r\n\x1a\n");
    let mut ihdr = Vec::with_capacity(13);
    ihdr.extend_from_slice(&width_px.to_be_bytes());
    ihdr.extend_from_slice(&height_px.to_be_bytes());
    ihdr.extend_from_slice(&[8, 6, 0, 0, 0]);
    write_png_chunk(&mut png, b"IHDR", &ihdr)?;
    let idat = zlib_store(&scanlines)?;
    write_png_chunk(&mut png, b"IDAT", &idat)?;
    write_png_chunk(&mut png, b"IEND", &[])?;
    Ok(png)
}

fn zlib_store(data: &[u8]) -> Result<Vec<u8>, Failure> {
    let mut out = Vec::new();
    out.extend_from_slice(&[0x78, 0x01]);
    let mut remaining = data;
    while !remaining.is_empty() {
        let len = remaining.len().min(u16::MAX as usize);
        let final_block = len == remaining.len();
        out.push(if final_block { 0x01 } else { 0x00 });
        let len_u16 = u16::try_from(len)
            .map_err(|_| Failure::Ethos(EthosError::internal("PNG zlib block length overflow")))?;
        out.extend_from_slice(&len_u16.to_le_bytes());
        out.extend_from_slice(&(!len_u16).to_le_bytes());
        out.extend_from_slice(&remaining[..len]);
        remaining = &remaining[len..];
    }
    if data.is_empty() {
        out.push(0x01);
        out.extend_from_slice(&0u16.to_le_bytes());
        out.extend_from_slice(&u16::MAX.to_le_bytes());
    }
    out.extend_from_slice(&adler32(data).to_be_bytes());
    Ok(out)
}

fn write_png_chunk(out: &mut Vec<u8>, kind: &[u8; 4], data: &[u8]) -> Result<(), Failure> {
    let len = u32::try_from(data.len()).map_err(|_| EthosError::internal("PNG chunk too large"))?;
    out.extend_from_slice(&len.to_be_bytes());
    out.extend_from_slice(kind);
    out.extend_from_slice(data);
    let mut crc_input = Vec::with_capacity(kind.len() + data.len());
    crc_input.extend_from_slice(kind);
    crc_input.extend_from_slice(data);
    out.extend_from_slice(&crc32(&crc_input).to_be_bytes());
    Ok(())
}

fn adler32(data: &[u8]) -> u32 {
    const MOD_ADLER: u32 = 65_521;
    let mut a = 1u32;
    let mut b = 0u32;
    for byte in data {
        a = (a + u32::from(*byte)) % MOD_ADLER;
        b = (b + a) % MOD_ADLER;
    }
    (b << 16) | a
}

fn crc32(data: &[u8]) -> u32 {
    let mut crc = 0xFFFF_FFFFu32;
    for byte in data {
        crc ^= u32::from(*byte);
        for _ in 0..8 {
            let mask = 0u32.wrapping_sub(crc & 1);
            crc = (crc >> 1) ^ (0xEDB8_8320 & mask);
        }
    }
    !crc
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn png_from_bgra_writes_png_signature_and_dimensions() {
        let bgra = [
            0, 0, 255, 255, // red, opaque
            0, 255, 0, 128, // green, half alpha
        ];
        let png = match png_from_bgra(2, 1, 8, &bgra) {
            Ok(png) => png,
            Err(_) => panic!("PNG encoding should succeed"),
        };

        assert!(png.starts_with(b"\x89PNG\r\n\x1a\n"));
        assert_eq!(&png[12..16], b"IHDR");
        assert_eq!(u32::from_be_bytes(png[16..20].try_into().unwrap()), 2);
        assert_eq!(u32::from_be_bytes(png[20..24].try_into().unwrap()), 1);
        assert_eq!(&png[png.len() - 8..png.len() - 4], b"IEND");
    }

    #[test]
    fn png_from_bgra_rejects_mismatched_buffer_length() {
        let err = png_from_bgra(2, 1, 8, &[0, 0, 0, 255]).unwrap_err();
        match err {
            Failure::Ethos(error) => {
                assert_eq!(error.message, "rendered crop buffer length mismatch");
            }
            _ => panic!("expected ethos failure"),
        }
    }

    #[test]
    fn zlib_store_splits_blocks_larger_than_u16_max() {
        let data = vec![0x41; u16::MAX as usize + 1];
        let zlib = zlib_store(&data).unwrap_or_else(|_| panic!("zlib store should encode"));

        assert_eq!(&zlib[..2], &[0x78, 0x01]);
        assert_eq!(zlib[2], 0x00);
        assert_eq!(u16::from_le_bytes([zlib[3], zlib[4]]), u16::MAX);

        let second_block = 2 + 1 + 2 + 2 + u16::MAX as usize;
        assert_eq!(zlib[second_block], 0x01);
        assert_eq!(
            u16::from_le_bytes([zlib[second_block + 1], zlib[second_block + 2]]),
            1
        );
    }

    #[test]
    fn crop_artifact_path_rejects_unsafe_crop_refs() {
        let crop_dir = tempfile::tempdir().unwrap();

        for crop_ref in ["../crop.json", "nested/crop.json", "crop.json/extra"] {
            let err = crop_artifact_path(crop_dir.path(), crop_ref)
                .expect_err("unsafe crop ref must fail");

            match err {
                Failure::Ethos(error) => {
                    assert_eq!(error.message, "crop_ref is not a safe artifact filename");
                }
                _ => panic!("expected ethos failure"),
            }
        }
    }
}
