#!/usr/bin/env bash
#
# Copyright 2026 The Ethos maintainers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# fetch-pdfium.sh — optional operator convenience for the caller-provided
# PDFium posture (ADR-0002 Phase 1 pins; ADR-0013 caller-provided beta posture).
#
# Downloads the EXACT pinned `bblanchon/pdfium-binaries` release archive
# recorded in docs/pdfium-profile.md, verifies the recorded archive sha256
# BEFORE extraction, extracts it, verifies the recorded runtime library
# sha256, and prints the ETHOS_PDFIUM_LIBRARY_PATH export line.
#
# This script is repository tooling. The `ethos` binary itself never
# downloads, installs, or repairs dynamic libraries; it only loads the
# operator-supplied path and verifies the runtime hash (docs/pdfium-profile.md,
# "Distribution method"). PDFium is NOT redistributed by Ethos.
#
# Usage:
#   scripts/fetch-pdfium.sh [DEST_DIR]
#
# DEST_DIR defaults to ${XDG_CACHE_HOME:-$HOME/.cache}/ethos/pdfium/chromium-7881
#
# Any hash mismatch is fatal. Do not edit the pins here; the source of truth
# is docs/pdfium-profile.md and profiles/ethos-deterministic-v1.json. Update
# those first, then mirror the values here in the same PR.

set -euo pipefail

# --- Pins (mirror of docs/pdfium-profile.md "Phase 1 pins") ------------------
RELEASE_TAG="chromium/7881"
RELEASE_NAME="PDFium 151.0.7881.0"
BASE_URL="https://github.com/bblanchon/pdfium-binaries/releases/download/chromium%2F7881"

MAC_ARM64_ARCHIVE="pdfium-mac-arm64.tgz"
MAC_ARM64_ARCHIVE_SHA256="52e94ca5aa8847934330daf3f8150c190682c5ca93831468794f8b90d4392e40"
MAC_ARM64_LIB_RELPATH="lib/libpdfium.dylib"
MAC_ARM64_LIB_SHA256="1bc45b15466b34cef96641ce25c77a876e70010c6b114f909dda2f5325fc5bd7"

LINUX_X64_ARCHIVE="pdfium-linux-x64.tgz"
LINUX_X64_ARCHIVE_SHA256="1470e21b8b4a3b4ad7f85684e2da11d94f3b69a86d81dee11b9b6709d927ac1d"
LINUX_X64_LIB_RELPATH="lib/libpdfium.so"
LINUX_X64_LIB_SHA256="f728930966f503652b92acc89b9374a2eeca00ce42e26dccd3e4b5c5161b2d64"
# -----------------------------------------------------------------------------

fail() {
    echo "fetch-pdfium: error: $*" >&2
    exit 1
}

sha256_of() {
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$1" | awk '{print $1}'
    elif command -v shasum >/dev/null 2>&1; then
        shasum -a 256 "$1" | awk '{print $1}'
    else
        fail "need sha256sum or shasum on PATH"
    fi
}

# --- Platform selection -------------------------------------------------------
OS="$(uname -s)"
ARCH="$(uname -m)"

case "${OS}/${ARCH}" in
    Darwin/arm64)
        ARCHIVE="${MAC_ARM64_ARCHIVE}"
        ARCHIVE_SHA256="${MAC_ARM64_ARCHIVE_SHA256}"
        LIB_RELPATH="${MAC_ARM64_LIB_RELPATH}"
        LIB_SHA256="${MAC_ARM64_LIB_SHA256}"
        ;;
    Linux/x86_64)
        ARCHIVE="${LINUX_X64_ARCHIVE}"
        ARCHIVE_SHA256="${LINUX_X64_ARCHIVE_SHA256}"
        LIB_RELPATH="${LINUX_X64_LIB_RELPATH}"
        LIB_SHA256="${LINUX_X64_LIB_SHA256}"
        ;;
    *)
        fail "unsupported platform ${OS}/${ARCH}. Current evaluation platforms are macOS arm64 and Linux x64; pins for other platforms live in docs/pdfium-profile.md."
        ;;
esac

DEST_DIR="${1:-${XDG_CACHE_HOME:-${HOME}/.cache}/ethos/pdfium/chromium-7881}"
LIB_PATH="${DEST_DIR}/${LIB_RELPATH}"

echo "fetch-pdfium: release ${RELEASE_NAME} (${RELEASE_TAG}), platform ${OS}/${ARCH}"

# --- Already present and verified? --------------------------------------------
if [ -f "${LIB_PATH}" ]; then
    got="$(sha256_of "${LIB_PATH}")"
    if [ "${got}" = "${LIB_SHA256}" ]; then
        echo "fetch-pdfium: verified runtime library already present."
        echo
        echo "export ETHOS_PDFIUM_LIBRARY_PATH=\"${LIB_PATH}\""
        exit 0
    fi
    fail "existing ${LIB_PATH} has sha256 ${got}, expected ${LIB_SHA256}. Remove ${DEST_DIR} and rerun."
fi

command -v curl >/dev/null 2>&1 || fail "need curl on PATH"
command -v tar >/dev/null 2>&1 || fail "need tar on PATH"

mkdir -p "${DEST_DIR}"
TMP_ARCHIVE="$(mktemp "${TMPDIR:-/tmp}/${ARCHIVE}.XXXXXX")"
trap 'rm -f "${TMP_ARCHIVE}"' EXIT

# --- Download and verify archive BEFORE extraction ----------------------------
echo "fetch-pdfium: downloading ${BASE_URL}/${ARCHIVE}"
curl -fL --retry 3 -o "${TMP_ARCHIVE}" "${BASE_URL}/${ARCHIVE}"

got="$(sha256_of "${TMP_ARCHIVE}")"
if [ "${got}" != "${ARCHIVE_SHA256}" ]; then
    fail "archive sha256 mismatch: got ${got}, expected ${ARCHIVE_SHA256}. Refusing to extract."
fi
echo "fetch-pdfium: archive sha256 verified."

tar -xzf "${TMP_ARCHIVE}" -C "${DEST_DIR}"

# --- Verify extracted runtime library -----------------------------------------
[ -f "${LIB_PATH}" ] || fail "expected runtime library ${LIB_RELPATH} missing after extraction"
got="$(sha256_of "${LIB_PATH}")"
if [ "${got}" != "${LIB_SHA256}" ]; then
    fail "runtime library sha256 mismatch: got ${got}, expected ${LIB_SHA256}"
fi
echo "fetch-pdfium: runtime library sha256 verified."
echo
echo "PDFium ${RELEASE_NAME} is ready. To use it:"
echo
echo "export ETHOS_PDFIUM_LIBRARY_PATH=\"${LIB_PATH}\""
echo
echo "Then run: ethos doctor --require-pdfium"
