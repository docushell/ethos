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
use std::process::{Command, Output};
use std::time::{SystemTime, UNIX_EPOCH};

use serde_json::Value;

const PDFIUM_ENV: &str = "ETHOS_PDFIUM_LIBRARY_PATH";

fn ethos_bin() -> &'static str {
    env!("CARGO_BIN_EXE_ethos")
}

fn run_ethos(args: &[&str]) -> Output {
    Command::new(ethos_bin())
        .args(args)
        .env_remove(PDFIUM_ENV)
        .output()
        .expect("ethos command runs")
}

fn run_ethos_with_env(args: &[&str], envs: &[(&str, &str)]) -> Output {
    let mut command = Command::new(ethos_bin());
    command.args(args).env_remove(PDFIUM_ENV);
    for (key, value) in envs {
        command.env(key, value);
    }
    command.output().expect("ethos command runs")
}

fn temp_file(name: &str, bytes: &[u8]) -> PathBuf {
    let unique = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_nanos();
    let path = std::env::temp_dir().join(format!("ethos-doctor-{name}-{unique}"));
    std::fs::write(&path, bytes).expect("temp file is writable");
    path
}

fn pdfium_configured() -> Option<PathBuf> {
    std::env::var_os(PDFIUM_ENV)
        .map(PathBuf::from)
        .filter(|path| path.is_file())
}

#[test]
fn public_help_lists_doctor_but_not_internal_probe() {
    let output = run_ethos(&["--help"]);
    assert!(output.status.success());
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("doctor"));
    assert!(!stdout.contains("__pdfium-load-probe"));
}

#[test]
fn internal_pdfium_load_probe_is_env_gated() {
    let output = run_ethos(&["__pdfium-load-probe"]);
    assert_eq!(output.status.code(), Some(2));
    assert!(output.stdout.is_empty());
    let stderr = String::from_utf8_lossy(&output.stderr);
    assert!(stderr.contains("__pdfium-load-probe requires ETHOS_INTERNAL_PDFIUM_LOAD_PROBE=1"));
}

#[test]
fn doctor_warns_and_succeeds_when_pdfium_is_unset() {
    let output = run_ethos(&["doctor"]);
    assert!(output.status.success());
    assert!(output.stderr.is_empty());
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("Ethos doctor"));
    assert!(stdout.contains("ETHOS_PDFIUM_LIBRARY_PATH: unset"));
    assert!(stdout.contains("PDFium"));
    assert!(stdout.contains("warning"));
    if cfg!(all(target_os = "macos", target_arch = "aarch64"))
        || cfg!(all(target_os = "linux", target_arch = "x86_64"))
    {
        assert!(stdout.contains("packaged target: supported by the approved npm vendor manifest"));
    }
}

#[test]
fn doctor_require_pdfium_fails_with_exit_12_when_pdfium_is_unset() {
    let output = run_ethos(&["doctor", "--require-pdfium"]);
    assert_eq!(output.status.code(), Some(12));
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("ETHOS_PDFIUM_LIBRARY_PATH: unset"));
    let error: Value = serde_json::from_slice(&output.stderr).expect("stderr is error JSON");
    assert_eq!(error["error"]["code"], "internal_error");
    assert!(error["error"]["message"]
        .as_str()
        .unwrap()
        .contains("ETHOS_PDFIUM_LIBRARY_PATH is unset"));
}

#[test]
fn doctor_reports_missing_pdfium_path_without_worker_probe() {
    let output = run_ethos_with_env(
        &["doctor", "--require-pdfium"],
        &[(PDFIUM_ENV, "/tmp/ethos-doctor-missing-libpdfium")],
    );
    assert_eq!(output.status.code(), Some(12));
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("ETHOS_PDFIUM_LIBRARY_PATH: set"));
    assert!(stdout.contains("does not point to a file"));
}

#[test]
fn doctor_reports_non_library_file_as_unusable_without_crashing_main_process() {
    let path = temp_file("not-a-library", b"not a dynamic library");
    let output = run_ethos_with_env(
        &["doctor", "--require-pdfium"],
        &[(PDFIUM_ENV, path.to_str().unwrap())],
    );
    let _ = std::fs::remove_file(&path);

    assert_eq!(output.status.code(), Some(12));
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("configured PDFium is not usable by Ethos"));
    let error: Value = serde_json::from_slice(&output.stderr).expect("stderr is error JSON");
    assert_eq!(error["error"]["code"], "internal_error");
}

#[test]
fn doctor_require_pdfium_succeeds_when_real_pdfium_is_configured() {
    let Some(path) = pdfium_configured() else {
        eprintln!("skipping doctor real PDFium test: ETHOS_PDFIUM_LIBRARY_PATH is not configured");
        return;
    };
    let output = run_ethos_with_env(
        &["doctor", "--require-pdfium"],
        &[(PDFIUM_ENV, path.to_str().unwrap())],
    );
    assert!(
        output.status.success(),
        "doctor failed\nstatus: {:?}\nstderr:\n{}\nstdout:\n{}",
        output.status.code(),
        String::from_utf8_lossy(&output.stderr),
        String::from_utf8_lossy(&output.stdout)
    );
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("configured PDFium is usable by Ethos"));
}
