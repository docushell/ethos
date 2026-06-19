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

use std::fmt;
use std::fs::File;
use std::io::{BufReader, Read};
use std::path::{Path, PathBuf};
use std::process::{Command as ProcessCommand, ExitStatus, Output, Stdio};
use std::thread::{self, JoinHandle};
use std::time::{Duration, Instant};

use ethos_core::config::ParseConfig;
use ethos_core::error::{ErrorCode, EthosError};
use ethos_core::model::Document;
use serde::de::{self, Deserializer as _, IgnoredAny, MapAccess, Visitor};
use sha2::{Digest, Sha256};
use tempfile::TempDir;

use crate::{Failure, EXIT_USAGE};

pub(crate) const WORKER_JSON_ARTIFACT_SCHEMA: &str = "ethos-worker-json-artifact-v1";
// Applied independently to stdout and stderr; if a child keeps writing after a reader rejects,
// the existing worker timeout remains the hard stop.
const WORKER_PIPE_MAX_BYTES: usize = 512 * 1024 * 1024;
const WORKER_JSON_ARTIFACT_HEADER_FIELDS: &[&str] = &[
    "schema_version",
    "document_fingerprint",
    "payload_sha256",
    "output_sha256",
    "output_bytes",
];

pub(crate) struct WorkerJsonArtifact {
    _temp_dir: TempDir,
    path: PathBuf,
    document_fingerprint: String,
}

impl WorkerJsonArtifact {
    pub(crate) fn path(&self) -> &Path {
        &self.path
    }

    pub(crate) fn document_fingerprint(&self) -> &str {
        &self.document_fingerprint
    }
}

pub(crate) fn parse_pdf_with_worker(
    input: &Path,
    pages: Option<&str>,
    config: &ParseConfig,
    diagnostics: bool,
) -> Result<Document, Failure> {
    let command = pdfium_worker_command(input, pages, diagnostics)?;

    let output =
        run_worker_with_timeout(command, Duration::from_millis(config.limits.max_parse_ms))?;
    if output.status.success() {
        let doc: Document = serde_json::from_slice(&output.stdout).map_err(|_| {
            EthosError::internal("pdfium worker returned an invalid canonical document")
        })?;
        doc.verify_integrity()?;
        return Ok(doc);
    }

    Err(worker_failure(&output, diagnostics))
}

pub(crate) fn parse_pdf_json_artifact_with_worker(
    input: &Path,
    pages: Option<&str>,
    config: &ParseConfig,
    diagnostics: bool,
) -> Result<WorkerJsonArtifact, Failure> {
    let (temp_dir, artifact_path) = worker_temp_artifact()?;
    let mut command = pdfium_worker_command(input, pages, diagnostics)?;
    command.arg("--json-out").arg(&artifact_path);

    let output =
        run_worker_with_timeout(command, Duration::from_millis(config.limits.max_parse_ms))?;

    if output.status.success() {
        return worker_json_artifact_from_header(&output.stdout, temp_dir, artifact_path);
    }

    Err(worker_failure(&output, diagnostics))
}

pub(crate) fn worker_json_artifact_header_bytes(
    document_fingerprint: &str,
    payload_sha256: &str,
    output_sha256: &str,
    output_bytes: u64,
) -> Result<Vec<u8>, EthosError> {
    let value = serde_json::json!({
        "schema_version": WORKER_JSON_ARTIFACT_SCHEMA,
        "document_fingerprint": document_fingerprint,
        "payload_sha256": payload_sha256,
        "output_sha256": output_sha256,
        "output_bytes": output_bytes,
    });
    let mut bytes =
        ethos_core::c14n::c14n_bytes(&value).map_err(|e| EthosError::internal(e.message))?;
    bytes.push(b'\n');
    Ok(bytes)
}

pub(crate) fn sha256_hex(bytes: &[u8]) -> String {
    hex_lower(&Sha256::digest(bytes))
}

fn pdfium_worker_command(
    input: &Path,
    pages: Option<&str>,
    diagnostics: bool,
) -> Result<ProcessCommand, Failure> {
    let mut command = ProcessCommand::new(
        std::env::current_exe()
            .map_err(|_| EthosError::internal("failed to locate current executable"))?,
    );
    command.arg("__pdfium-worker").arg(input);
    if let Some(pages) = pages {
        command.arg("--pages").arg(pages);
    }
    if diagnostics {
        command.arg("--diagnostics");
    }
    Ok(command)
}

fn worker_failure(output: &Output, diagnostics: bool) -> Failure {
    if output.status.code() == Some(EXIT_USAGE as i32) {
        return Failure::Usage(worker_usage_message(&output.stderr));
    }
    if let Some(error) = worker_ethos_error(&output.stderr) {
        return error.into();
    }
    let error = EthosError::internal("pdfium worker failed");
    if diagnostics {
        return Failure::EthosWithDiagnostics {
            error,
            diagnostics: worker_failure_diagnostics(output),
        };
    }
    error.into()
}

fn worker_json_artifact_from_header(
    stdout: &[u8],
    temp_dir: TempDir,
    path: PathBuf,
) -> Result<WorkerJsonArtifact, Failure> {
    let header = worker_json_artifact_header_from_stdout(stdout)?;
    let schema_version = required_header_string(header.schema_version.as_ref(), "schema_version")?;
    if schema_version != WORKER_JSON_ARTIFACT_SCHEMA {
        return Err(EthosError::internal(
            "pdfium worker returned an unsupported JSON artifact header",
        )
        .into());
    }
    let document_fingerprint =
        required_header_string(header.document_fingerprint.as_ref(), "document_fingerprint")?;
    let payload_sha256 = required_header_string(header.payload_sha256.as_ref(), "payload_sha256")?;
    let output_sha256 = required_header_string(header.output_sha256.as_ref(), "output_sha256")?;
    let output_bytes = required_header_u64(header.output_bytes.as_ref(), "output_bytes")?;

    let (actual_sha256, actual_bytes) = file_sha256(&path)?;
    if actual_bytes != output_bytes || actual_sha256 != output_sha256 {
        return Err(EthosError::internal("pdfium worker JSON artifact hash mismatch").into());
    }
    let envelope = artifact_envelope_from_file(&path)?;
    if envelope.document_fingerprint != document_fingerprint
        || envelope.payload_sha256 != payload_sha256
    {
        return Err(EthosError::internal(
            "pdfium worker JSON artifact header does not match artifact",
        )
        .into());
    }

    Ok(WorkerJsonArtifact {
        _temp_dir: temp_dir,
        path,
        document_fingerprint,
    })
}

#[derive(Default)]
struct WorkerJsonArtifactHeaderFields {
    schema_version: Option<serde_json::Value>,
    document_fingerprint: Option<serde_json::Value>,
    payload_sha256: Option<serde_json::Value>,
    output_sha256: Option<serde_json::Value>,
    output_bytes: Option<serde_json::Value>,
}

fn worker_json_artifact_header_from_stdout(
    stdout: &[u8],
) -> Result<WorkerJsonArtifactHeaderFields, Failure> {
    let mut deserializer = serde_json::Deserializer::from_slice(stdout);
    let header = deserializer
        .deserialize_map(WorkerJsonArtifactHeaderVisitor)
        .map_err(|_| {
            Failure::Ethos(EthosError::internal(
                "pdfium worker returned an invalid JSON artifact header",
            ))
        })?;
    deserializer.end().map_err(|_| {
        Failure::Ethos(EthosError::internal(
            "pdfium worker returned an invalid JSON artifact header",
        ))
    })?;
    Ok(header)
}

struct WorkerJsonArtifactHeaderVisitor;

impl<'de> Visitor<'de> for WorkerJsonArtifactHeaderVisitor {
    type Value = WorkerJsonArtifactHeaderFields;

    fn expecting(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        formatter.write_str("a strict PDF worker JSON artifact header")
    }

    fn visit_map<A>(self, mut map: A) -> Result<Self::Value, A::Error>
    where
        A: MapAccess<'de>,
    {
        let mut header = WorkerJsonArtifactHeaderFields::default();

        while let Some(key) = map.next_key::<String>()? {
            match key.as_str() {
                "schema_version" => {
                    set_header_value(&mut header.schema_version, "schema_version", &mut map)?
                }
                "document_fingerprint" => set_header_value(
                    &mut header.document_fingerprint,
                    "document_fingerprint",
                    &mut map,
                )?,
                "payload_sha256" => {
                    set_header_value(&mut header.payload_sha256, "payload_sha256", &mut map)?
                }
                "output_sha256" => {
                    set_header_value(&mut header.output_sha256, "output_sha256", &mut map)?
                }
                "output_bytes" => {
                    set_header_value(&mut header.output_bytes, "output_bytes", &mut map)?
                }
                _ => {
                    let _ = map.next_value::<IgnoredAny>()?;
                    return Err(de::Error::unknown_field(
                        &key,
                        WORKER_JSON_ARTIFACT_HEADER_FIELDS,
                    ));
                }
            }
        }

        Ok(header)
    }
}

fn set_header_value<'de, A>(
    slot: &mut Option<serde_json::Value>,
    key: &'static str,
    map: &mut A,
) -> Result<(), A::Error>
where
    A: MapAccess<'de>,
{
    if slot.is_some() {
        return Err(de::Error::duplicate_field(key));
    }
    *slot = Some(map.next_value()?);
    Ok(())
}

fn required_header_string(value: Option<&serde_json::Value>, key: &str) -> Result<String, Failure> {
    value
        .and_then(serde_json::Value::as_str)
        .map(ToString::to_string)
        .ok_or_else(|| {
            EthosError::internal(format!("pdfium worker JSON artifact header missing {key}")).into()
        })
}

fn required_header_u64(value: Option<&serde_json::Value>, key: &str) -> Result<u64, Failure> {
    value.and_then(serde_json::Value::as_u64).ok_or_else(|| {
        EthosError::internal(format!("pdfium worker JSON artifact header missing {key}")).into()
    })
}

fn file_sha256(path: &Path) -> Result<(String, u64), Failure> {
    let file = File::open(path)
        .map_err(|_| EthosError::internal("pdfium worker JSON artifact missing"))?;
    let mut reader = BufReader::new(file);
    let mut hasher = Sha256::new();
    let mut total = 0_u64;
    let mut buf = [0_u8; 64 * 1024];
    loop {
        let n = reader
            .read(&mut buf)
            .map_err(|_| EthosError::internal("pdfium worker JSON artifact read failed"))?;
        if n == 0 {
            break;
        }
        hasher.update(&buf[..n]);
        total += n as u64;
    }
    Ok((hex_lower(&hasher.finalize()), total))
}

struct ArtifactEnvelope {
    document_fingerprint: String,
    payload_sha256: String,
}

fn artifact_envelope_from_file(path: &Path) -> Result<ArtifactEnvelope, Failure> {
    let file = File::open(path)
        .map_err(|_| EthosError::internal("pdfium worker JSON artifact missing"))?;
    let reader = BufReader::new(file);
    let mut deserializer = serde_json::Deserializer::from_reader(reader);
    deserializer
        .deserialize_map(ArtifactEnvelopeVisitor)
        .map_err(|_| EthosError::internal("pdfium worker JSON artifact envelope invalid").into())
}

struct ArtifactEnvelopeVisitor;

impl<'de> Visitor<'de> for ArtifactEnvelopeVisitor {
    type Value = ArtifactEnvelope;

    fn expecting(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        formatter.write_str("a canonical Ethos document envelope")
    }

    fn visit_map<A>(self, mut map: A) -> Result<Self::Value, A::Error>
    where
        A: MapAccess<'de>,
    {
        let mut document_fingerprint = None;
        let mut payload_sha256 = None;

        while let Some(key) = map.next_key::<String>()? {
            match key.as_str() {
                "fingerprint" => {
                    if document_fingerprint.is_some() {
                        return Err(de::Error::duplicate_field("fingerprint"));
                    }
                    document_fingerprint = Some(map.next_value()?);
                }
                "payload_sha256" => {
                    if payload_sha256.is_some() {
                        return Err(de::Error::duplicate_field("payload_sha256"));
                    }
                    payload_sha256 = Some(map.next_value()?);
                }
                _ => {
                    let _ = map.next_value::<IgnoredAny>()?;
                }
            }
        }

        Ok(ArtifactEnvelope {
            document_fingerprint: document_fingerprint
                .ok_or_else(|| de::Error::missing_field("fingerprint"))?,
            payload_sha256: payload_sha256
                .ok_or_else(|| de::Error::missing_field("payload_sha256"))?,
        })
    }
}

fn worker_temp_artifact() -> Result<(TempDir, PathBuf), Failure> {
    let temp_dir = tempfile::Builder::new()
        .prefix("ethos-pdfium-worker-")
        .tempdir()
        .map_err(|_| EthosError::internal("failed to create pdfium worker temp directory"))?;
    let path = temp_dir.path().join("document.json");
    Ok((temp_dir, path))
}

fn hex_lower(bytes: &[u8]) -> String {
    const HEX: &[u8; 16] = b"0123456789abcdef";
    let mut out = String::with_capacity(bytes.len() * 2);
    for byte in bytes {
        out.push(HEX[(byte >> 4) as usize] as char);
        out.push(HEX[(byte & 0x0f) as usize] as char);
    }
    out
}

fn run_worker_with_timeout(
    mut command: ProcessCommand,
    timeout: Duration,
) -> Result<Output, Failure> {
    command
        .stdin(Stdio::null())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());
    let mut child = command
        .spawn()
        .map_err(|_| EthosError::internal("failed to spawn pdfium worker"))?;
    let stdout = child
        .stdout
        .take()
        .ok_or_else(|| EthosError::internal("pdfium worker stdout unavailable"))?;
    let stderr = child
        .stderr
        .take()
        .ok_or_else(|| EthosError::internal("pdfium worker stderr unavailable"))?;
    let stdout_handle = thread::spawn(move || read_pipe(stdout));
    let stderr_handle = thread::spawn(move || read_pipe(stderr));

    let start = Instant::now();
    loop {
        if let Some(status) = child
            .try_wait()
            .map_err(|_| EthosError::internal("pdfium worker wait failed"))?
        {
            return collect_worker_output(status, stdout_handle, stderr_handle);
        }
        if start.elapsed() >= timeout {
            if let Some(status) = child
                .try_wait()
                .map_err(|_| EthosError::internal("pdfium worker wait failed"))?
            {
                return collect_worker_output(status, stdout_handle, stderr_handle);
            }
            let _ = child.kill();
            let _ = child.wait();
            let _ = join_reader(stdout_handle);
            let _ = join_reader(stderr_handle);
            return Err(
                EthosError::new(ErrorCode::ParseTimeout, "parse exceeded max_parse_ms").into(),
            );
        }

        let remaining = timeout.saturating_sub(start.elapsed());
        thread::sleep(remaining.min(Duration::from_millis(10)));
    }
}

fn read_pipe<R: Read>(pipe: R) -> Result<Vec<u8>, EthosError> {
    read_pipe_limited(pipe, WORKER_PIPE_MAX_BYTES)
}

fn read_pipe_limited<R: Read>(mut pipe: R, max_bytes: usize) -> Result<Vec<u8>, EthosError> {
    let mut bytes = Vec::new();
    let mut chunk = [0_u8; 64 * 1024];
    loop {
        let n = pipe
            .read(&mut chunk)
            .map_err(|_| EthosError::internal("pdfium worker pipe read failed"))?;
        if n == 0 {
            break;
        }
        if n > max_bytes.saturating_sub(bytes.len()) {
            return Err(EthosError::new(
                ErrorCode::MemoryLimitExceeded,
                "parse exceeded memory limit",
            ));
        }
        bytes.extend_from_slice(&chunk[..n]);
    }
    Ok(bytes)
}

fn collect_worker_output(
    status: ExitStatus,
    stdout_handle: JoinHandle<Result<Vec<u8>, EthosError>>,
    stderr_handle: JoinHandle<Result<Vec<u8>, EthosError>>,
) -> Result<Output, Failure> {
    Ok(Output {
        status,
        stdout: join_reader(stdout_handle)?,
        stderr: join_reader(stderr_handle)?,
    })
}

fn join_reader(handle: JoinHandle<Result<Vec<u8>, EthosError>>) -> Result<Vec<u8>, Failure> {
    handle
        .join()
        .map_err(|_| EthosError::internal("pdfium worker pipe reader failed"))?
        .map_err(Failure::Ethos)
}

fn worker_usage_message(stderr: &[u8]) -> String {
    let raw = String::from_utf8_lossy(stderr);
    let trimmed = raw.trim();
    trimmed
        .strip_prefix("error (usage): ")
        .unwrap_or(trimmed)
        .to_string()
}

fn worker_ethos_error(stderr: &[u8]) -> Option<EthosError> {
    let value: serde_json::Value = serde_json::from_slice(stderr).ok()?;
    let error = value.get("error")?;
    let code: ErrorCode = serde_json::from_value(error.get("code")?.clone()).ok()?;
    let message = error.get("message")?.as_str()?;
    Some(EthosError::new(code, message))
}

fn worker_failure_diagnostics(output: &Output) -> serde_json::Value {
    let mut worker = serde_json::Map::new();
    if let Some(code) = output.status.code() {
        worker.insert("exit_code".to_string(), serde_json::json!(code));
    }
    #[cfg(unix)]
    {
        use std::os::unix::process::ExitStatusExt as _;

        if let Some(signal) = output.status.signal() {
            worker.insert("signal".to_string(), serde_json::json!(signal));
        }
    }
    if !output.stderr.is_empty() {
        worker.insert(
            "stderr".to_string(),
            serde_json::Value::String(String::from_utf8_lossy(&output.stderr).to_string()),
        );
    }
    serde_json::json!({
        "pdfium_worker": serde_json::Value::Object(worker),
    })
}

#[cfg(debug_assertions)]
pub(crate) fn maybe_sleep_for_worker_timeout_test() {
    if let Ok(raw) = std::env::var("ETHOS_INTERNAL_TEST_PDFIUM_WORKER_SLEEP_MS") {
        if let Ok(ms) = raw.parse::<u64>() {
            thread::sleep(Duration::from_millis(ms));
        }
    }
}

#[cfg(not(debug_assertions))]
pub(crate) fn maybe_sleep_for_worker_timeout_test() {}

#[cfg(debug_assertions)]
pub(crate) fn maybe_exit_for_worker_failure_diagnostics_test() {
    if let Ok(stderr) = std::env::var("ETHOS_INTERNAL_TEST_PDFIUM_WORKER_STDERR") {
        eprint!("{stderr}");
        let code = std::env::var("ETHOS_INTERNAL_TEST_PDFIUM_WORKER_EXIT_CODE")
            .ok()
            .and_then(|raw| raw.parse::<i32>().ok())
            .unwrap_or(101);
        std::process::exit(code);
    }
}

#[cfg(not(debug_assertions))]
pub(crate) fn maybe_exit_for_worker_failure_diagnostics_test() {}

#[cfg(debug_assertions)]
pub(crate) fn maybe_fail_for_worker_memory_limit_test() -> Result<(), Failure> {
    if std::env::var_os("ETHOS_INTERNAL_TEST_PDFIUM_WORKER_MEMORY_LIMIT").is_some() {
        return Err(EthosError::new(
            ErrorCode::MemoryLimitExceeded,
            "parse exceeded memory limit",
        )
        .into());
    }
    Ok(())
}

#[cfg(not(debug_assertions))]
pub(crate) fn maybe_fail_for_worker_memory_limit_test() -> Result<(), Failure> {
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    const TEST_FINGERPRINT: &str =
        "sha256:0000000000000000000000000000000000000000000000000000000000000000";
    const TEST_PAYLOAD_SHA256: &str =
        "1111111111111111111111111111111111111111111111111111111111111111";

    fn test_artifact() -> (TempDir, PathBuf) {
        match worker_temp_artifact() {
            Ok(artifact) => artifact,
            Err(_) => panic!("test temp artifact could not be created"),
        }
    }

    fn test_document_bytes(fingerprint: &str, payload_sha256: &str) -> Vec<u8> {
        let value = serde_json::json!({
            "fingerprint": fingerprint,
            "payload": {
                "spans": []
            },
            "payload_sha256": payload_sha256,
        });
        let mut bytes = ethos_core::c14n::c14n_bytes(&value).expect("test value is canonical");
        bytes.push(b'\n');
        bytes
    }

    fn test_header_bytes(value: serde_json::Value) -> Vec<u8> {
        let mut bytes = ethos_core::c14n::c14n_bytes(&value).expect("test value is canonical");
        bytes.push(b'\n');
        bytes
    }

    fn assert_json_artifact_header_rejected(header: Vec<u8>, message: &str) {
        let (temp_dir, path) = test_artifact();
        let bytes = test_document_bytes(TEST_FINGERPRINT, TEST_PAYLOAD_SHA256);
        std::fs::write(&path, &bytes).expect("test artifact can be written");

        let error = match worker_json_artifact_from_header(&header, temp_dir, path.clone()) {
            Ok(_) => panic!("invalid artifact header was accepted"),
            Err(error) => error,
        };

        match error {
            Failure::Ethos(error) => {
                assert_eq!(error.code, ErrorCode::InternalError);
                assert_eq!(error.message, message);
            }
            _ => panic!("expected Ethos failure"),
        }
        assert!(!path.exists(), "temp dir is cleaned up on rejection");
    }

    #[test]
    fn validates_json_artifact_header_against_file_hash() {
        let (temp_dir, path) = test_artifact();
        let bytes = test_document_bytes(TEST_FINGERPRINT, TEST_PAYLOAD_SHA256);
        std::fs::write(&path, &bytes).expect("test artifact can be written");
        let header = worker_json_artifact_header_bytes(
            TEST_FINGERPRINT,
            TEST_PAYLOAD_SHA256,
            &sha256_hex(&bytes),
            bytes.len() as u64,
        )
        .expect("header can be encoded");

        let artifact = match worker_json_artifact_from_header(&header, temp_dir, path.clone()) {
            Ok(artifact) => artifact,
            Err(_) => panic!("artifact header did not validate"),
        };

        assert_eq!(artifact.path(), path.as_path());
        assert_eq!(artifact.document_fingerprint(), TEST_FINGERPRINT);

        drop(artifact);
        assert!(!path.exists(), "artifact is cleaned up on drop");
    }

    #[test]
    fn rejects_json_artifact_header_invalid_json() {
        assert_json_artifact_header_rejected(
            vec![123],
            "pdfium worker returned an invalid JSON artifact header",
        );
    }

    #[test]
    fn rejects_json_artifact_header_unsupported_schema() {
        let header = test_header_bytes(serde_json::json!({
            "schema_version": "unsupported-worker-json-artifact",
        }));

        assert_json_artifact_header_rejected(
            header,
            "pdfium worker returned an unsupported JSON artifact header",
        );
    }

    #[test]
    fn rejects_json_artifact_header_duplicate_field() {
        let header = br#"{"schema_version":"ethos-worker-json-artifact-v1","schema_version":"ethos-worker-json-artifact-v1"}"#.to_vec();

        assert_json_artifact_header_rejected(
            header,
            "pdfium worker returned an invalid JSON artifact header",
        );
    }

    #[test]
    fn rejects_json_artifact_header_unexpected_field() {
        let header = test_header_bytes(serde_json::json!({
            "schema_version": WORKER_JSON_ARTIFACT_SCHEMA,
            "unexpected": true,
        }));

        assert_json_artifact_header_rejected(
            header,
            "pdfium worker returned an invalid JSON artifact header",
        );
    }

    #[test]
    fn rejects_json_artifact_header_trailing_data() {
        let mut header = test_header_bytes(serde_json::json!({
            "schema_version": WORKER_JSON_ARTIFACT_SCHEMA,
        }));
        header.extend_from_slice(br#"{"schema_version":"ethos-worker-json-artifact-v1"}"#);

        assert_json_artifact_header_rejected(
            header,
            "pdfium worker returned an invalid JSON artifact header",
        );
    }

    #[test]
    fn rejects_json_artifact_header_missing_output_bytes() {
        let bytes = test_document_bytes(TEST_FINGERPRINT, TEST_PAYLOAD_SHA256);
        let header = test_header_bytes(serde_json::json!({
            "schema_version": WORKER_JSON_ARTIFACT_SCHEMA,
            "document_fingerprint": TEST_FINGERPRINT,
            "payload_sha256": TEST_PAYLOAD_SHA256,
            "output_sha256": sha256_hex(&bytes),
        }));

        assert_json_artifact_header_rejected(
            header,
            "pdfium worker JSON artifact header missing output_bytes",
        );
    }

    #[test]
    fn rejects_json_artifact_header_missing_document_fingerprint() {
        let header = test_header_bytes(serde_json::json!({
            "schema_version": WORKER_JSON_ARTIFACT_SCHEMA,
        }));

        assert_json_artifact_header_rejected(
            header,
            "pdfium worker JSON artifact header missing document_fingerprint",
        );
    }

    #[test]
    fn rejects_json_artifact_header_missing_payload_sha256() {
        let header = test_header_bytes(serde_json::json!({
            "schema_version": WORKER_JSON_ARTIFACT_SCHEMA,
            "document_fingerprint": TEST_FINGERPRINT,
        }));

        assert_json_artifact_header_rejected(
            header,
            "pdfium worker JSON artifact header missing payload_sha256",
        );
    }

    #[test]
    fn rejects_json_artifact_header_missing_output_sha256() {
        let header = test_header_bytes(serde_json::json!({
            "schema_version": WORKER_JSON_ARTIFACT_SCHEMA,
            "document_fingerprint": TEST_FINGERPRINT,
            "payload_sha256": TEST_PAYLOAD_SHA256,
            "output_bytes": 0,
        }));

        assert_json_artifact_header_rejected(
            header,
            "pdfium worker JSON artifact header missing output_sha256",
        );
    }

    #[test]
    fn rejects_json_artifact_header_hash_mismatch() {
        let (temp_dir, path) = test_artifact();
        let bytes = test_document_bytes(TEST_FINGERPRINT, TEST_PAYLOAD_SHA256);
        std::fs::write(&path, &bytes).expect("test artifact can be written");
        let header = worker_json_artifact_header_bytes(
            TEST_FINGERPRINT,
            TEST_PAYLOAD_SHA256,
            "2222222222222222222222222222222222222222222222222222222222222222",
            bytes.len() as u64,
        )
        .expect("header can be encoded");

        let error = match worker_json_artifact_from_header(&header, temp_dir, path.clone()) {
            Ok(_) => panic!("hash mismatch was accepted"),
            Err(error) => error,
        };

        match error {
            Failure::Ethos(error) => {
                assert_eq!(error.code, ErrorCode::InternalError);
                assert_eq!(error.message, "pdfium worker JSON artifact hash mismatch");
            }
            _ => panic!("expected Ethos failure"),
        }
        assert!(!path.exists(), "temp dir is cleaned up on rejection");
    }

    #[test]
    fn rejects_json_artifact_header_envelope_mismatch() {
        let (temp_dir, path) = test_artifact();
        let bytes = test_document_bytes(
            "sha256:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
            TEST_PAYLOAD_SHA256,
        );
        std::fs::write(&path, &bytes).expect("test artifact can be written");
        let header = worker_json_artifact_header_bytes(
            TEST_FINGERPRINT,
            TEST_PAYLOAD_SHA256,
            &sha256_hex(&bytes),
            bytes.len() as u64,
        )
        .expect("header can be encoded");

        let error = match worker_json_artifact_from_header(&header, temp_dir, path.clone()) {
            Ok(_) => panic!("envelope mismatch was accepted"),
            Err(error) => error,
        };

        match error {
            Failure::Ethos(error) => {
                assert_eq!(error.code, ErrorCode::InternalError);
                assert_eq!(
                    error.message,
                    "pdfium worker JSON artifact header does not match artifact"
                );
            }
            _ => panic!("expected Ethos failure"),
        }
        assert!(!path.exists(), "temp dir is cleaned up on rejection");
    }

    #[test]
    fn worker_pipe_limit_accepts_empty_output() {
        let bytes = read_pipe_limited(std::io::Cursor::new([]), 3)
            .expect("empty worker output is within the pipe limit");

        assert!(bytes.is_empty());
    }

    #[test]
    fn worker_pipe_limit_accepts_limit_sized_output() {
        let bytes = read_pipe_limited(std::io::Cursor::new([1_u8, 2, 3]), 3)
            .expect("limit-sized worker output is accepted");

        assert_eq!(bytes, vec![1_u8, 2, 3]);
    }

    #[test]
    fn worker_pipe_limit_rejects_oversized_output() {
        let error = match read_pipe_limited(std::io::Cursor::new([1_u8, 2, 3, 4]), 3) {
            Ok(_) => panic!("oversized worker output was accepted"),
            Err(error) => error,
        };

        assert_eq!(error.code, ErrorCode::MemoryLimitExceeded);
        assert_eq!(error.message, "parse exceeded memory limit");
    }

    #[test]
    fn worker_error_envelope_parses_stable_error() {
        let error = worker_ethos_error(
            br#"{"error":{"code":"invalid_pdf","message":"input does not contain a PDF header"}}"#,
        )
        .expect("stable worker error envelope is parsed");

        assert_eq!(error.code, ErrorCode::InvalidPdf);
        assert_eq!(error.message, "input does not contain a PDF header");
    }

    #[test]
    fn worker_error_envelope_rejects_invalid_json() {
        assert!(worker_ethos_error(&[123]).is_none());
    }

    #[test]
    fn worker_error_envelope_rejects_missing_code() {
        assert!(worker_ethos_error(br#"{"error":{"message":"missing code"}}"#).is_none());
    }

    #[test]
    fn worker_error_envelope_rejects_unknown_code() {
        assert!(worker_ethos_error(
            br#"{"error":{"code":"unsupported_worker_code","message":"unknown code"}}"#
        )
        .is_none());
    }

    #[test]
    fn worker_error_envelope_rejects_non_string_message() {
        assert!(worker_ethos_error(br#"{"error":{"code":"invalid_pdf","message":42}}"#).is_none());
    }
}
