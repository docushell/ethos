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

"""Print the caller-provided PDFium setup path for wheel consumers."""

PDFIUM_SETUP_GUIDANCE = (
    "PDFium setup command: scripts/fetch-pdfium.sh. Run it from an Ethos source "
    "checkout, apply the printed ETHOS_PDFIUM_LIBRARY_PATH export, then run ethos "
    "doctor --require-pdfium. The script verifies pinned archive and runtime sha256 "
    "values and never runs automatically. See docs/pdfium-manual-setup.md."
)


def main() -> None:
    print(PDFIUM_SETUP_GUIDANCE)


if __name__ == "__main__":
    main()
