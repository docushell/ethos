use std::io::{self, Read};
use std::path::PathBuf;
use std::process::{Command as ProcessCommand, ExitStatus, Output, Stdio};
use std::thread::{self, JoinHandle};
use std::time::{Duration, Instant};

use ethos_core::config::ParseConfig;
use ethos_core::error::{ErrorCode, EthosError};
use ethos_core::model::Document;

use crate::{Failure, EXIT_USAGE};

pub(crate) fn parse_pdf_with_worker(
    input: &PathBuf,
    pages: Option<&str>,
    config: &ParseConfig,
    diagnostics: bool,
) -> Result<Document, Failure> {
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

    let output =
        run_worker_with_timeout(command, Duration::from_millis(config.limits.max_parse_ms))?;
    if output.status.success() {
        let doc: Document = serde_json::from_slice(&output.stdout).map_err(|_| {
            EthosError::internal("pdfium worker returned an invalid canonical document")
        })?;
        doc.verify_integrity()?;
        return Ok(doc);
    }

    if output.status.code() == Some(EXIT_USAGE as i32) {
        return Err(Failure::Usage(worker_usage_message(&output.stderr)));
    }
    if let Some(error) = worker_ethos_error(&output.stderr) {
        return Err(error.into());
    }
    let error = EthosError::internal("pdfium worker failed");
    if diagnostics {
        return Err(Failure::EthosWithDiagnostics {
            error,
            diagnostics: worker_failure_diagnostics(&output),
        });
    }
    Err(error.into())
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

fn read_pipe<R: Read>(mut pipe: R) -> io::Result<Vec<u8>> {
    let mut bytes = Vec::new();
    pipe.read_to_end(&mut bytes)?;
    Ok(bytes)
}

fn collect_worker_output(
    status: ExitStatus,
    stdout_handle: JoinHandle<io::Result<Vec<u8>>>,
    stderr_handle: JoinHandle<io::Result<Vec<u8>>>,
) -> Result<Output, Failure> {
    Ok(Output {
        status,
        stdout: join_reader(stdout_handle)?,
        stderr: join_reader(stderr_handle)?,
    })
}

fn join_reader(handle: JoinHandle<io::Result<Vec<u8>>>) -> Result<Vec<u8>, Failure> {
    handle
        .join()
        .map_err(|_| EthosError::internal("pdfium worker pipe reader failed"))?
        .map_err(|_| EthosError::internal("pdfium worker pipe read failed").into())
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
