#!/usr/bin/env python3
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

"""Fixture manifest validation gate.

Checks, in order:
1. fixtures/manifest.json has the expected v1 shape;
2. every fixture directory has a 1:1 fixture.json/document.pdf pair;
3. every fixture document is indexed exactly once;
4. manifest corpus metadata matches fixture.json;
5. manifest sha256 == fixture.json sha256 == sha256(document.pdf);
6. successful parse fixtures carry stage goldens with the expected v1 shape;
7. foreign parser fixture packages bind their manifest hashes to committed files.

Exit 0 = green. Any failure prints the offending file/context and exits 1.
"""

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "manifest.json"
ALLOWED_CATEGORIES = {"failure", "public", "security", "synthetic"}
MANIFEST_KEYS = {"manifest_version", "root", "subsets_declared", "fixtures"}
ENTRY_KEYS = {"id", "file", "sha256", "pages", "subsets", "provenance", "license"}
EXTRACTION_GOLDEN_KEYS = {"pages", "spans", "regions", "warnings"}
LAYOUT_GOLDEN_KEYS = {"elements", "warnings"}
TEXT_EXPORT = "text.txt"
MARKDOWN_EXPORT = "markdown.md"
FOREIGN_MANIFEST_KEYS = {
    "parser",
    "version",
    "source_pdf",
    "source_pdf_sha256",
    "output_json",
    "output_json_sha256",
    "generator_artifact",
    "generator_artifact_sha256",
    "generated_by_command",
    "generated_at_policy",
    "source_provenance",
    "license",
}
HEX256 = re.compile(r"^[0-9a-f]{64}$")
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]*$")
SUBSET = re.compile(r"^[a-z0-9][a-z0-9_]*$")
PLACEHOLDER = re.compile(r"todo|_{4,}|found it somewhere", re.IGNORECASE)
MAX_SAFE_INTEGER = 9_007_199_254_740_991

failures = 0


def fail(msg: str) -> None:
    global failures
    failures += 1
    print(f"FAIL  {msg}")


def ok(msg: str) -> None:
    print(f"ok    {msg}")


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"{path.relative_to(ROOT)} is not valid JSON: {exc}")
        return None


def is_safe_relative_path(value: str) -> bool:
    path = Path(value)
    return not path.is_absolute() and ".." not in path.parts and str(path) == value


def non_placeholder_text(value, ctx: str) -> bool:
    if not isinstance(value, str) or not value.strip():
        fail(f"{ctx} must be a non-empty string")
        return False
    if PLACEHOLDER.search(value):
        fail(f"{ctx} contains placeholder text")
        return False
    return True


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_bytes(value) -> bytes:
    text = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return f"{text}\n".encode("utf-8")


def validate_c14n_scalar_contract(value, ctx: str) -> None:
    if value is None or isinstance(value, (bool, str)):
        return
    if isinstance(value, int):
        if abs(value) > MAX_SAFE_INTEGER:
            fail(f"{ctx} integer is outside c14n safe range")
        return
    if isinstance(value, float):
        fail(f"{ctx} floats are not valid c14n values")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            validate_c14n_scalar_contract(item, f"{ctx}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            validate_c14n_scalar_contract(item, f"{ctx}.{key}")
        return
    fail(f"{ctx} is not a valid JSON scalar/container")


def validate_golden_file(path: Path, stage: str, keys: set[str]):
    if not path.is_file():
        fail(f"{path.relative_to(ROOT)} missing for successful fixture")
        return None

    golden = load_json(path)
    if golden is None:
        return None
    ctx = str(path.relative_to(ROOT))
    if not isinstance(golden, dict):
        fail(f"{ctx} must be an object")
        return None
    validate_c14n_scalar_contract(golden, ctx)
    if path.read_bytes() != canonical_json_bytes(golden):
        fail(f"{ctx} must be canonical JSON with one trailing newline")
    if set(golden) != keys:
        fail(f"{ctx} must contain exactly {sorted(keys)}")

    if stage == "extraction":
        for key in ("pages", "spans", "regions", "warnings"):
            if not isinstance(golden.get(key), list):
                fail(f"{ctx} {key} must be an array")
        validate_projection_items(ctx, "pages", golden.get("pages"), required=True)
        validate_projection_items(ctx, "spans", golden.get("spans"), required=True)
    elif stage == "layout":
        if not isinstance(golden.get("elements"), list):
            fail(f"{ctx} elements must be an array")
        validate_projection_items(ctx, "elements", golden.get("elements"), required=True)
    return golden


def render_text_export(layout):
    elements = layout.get("elements") if isinstance(layout, dict) else None
    if not isinstance(elements, list):
        return None
    text = "\n\n".join(
        element["text"]
        for element in elements
        if isinstance(element, dict) and isinstance(element.get("text"), str)
    )
    return f"{text}\n".encode("utf-8")


def render_markdown_export(layout, ctx: str):
    elements = layout.get("elements") if isinstance(layout, dict) else None
    if not isinstance(elements, list):
        return None

    blocks = []
    for index, element in enumerate(elements):
        if not isinstance(element, dict) or not isinstance(element.get("text"), str):
            continue
        text = element["text"]
        if element.get("type") == "heading":
            level = element.get("heading_level", 1)
            if not isinstance(level, int):
                fail(f"{ctx} elements[{index}].heading_level must be an integer")
                level = 1
            level = min(max(level, 1), 6)
            blocks.append(f"{'#' * level} {text}")
        else:
            blocks.append(text)
    markdown = "\n\n".join(blocks)
    return f"{markdown}\n".encode("utf-8")


def validate_export_file(path: Path, expected, label: str) -> None:
    if expected is None:
        return
    rel = path.relative_to(ROOT)
    if not path.is_file():
        fail(f"{rel} missing for successful fixture")
        return
    actual = path.read_bytes()
    try:
        actual.decode("utf-8")
    except UnicodeDecodeError as exc:
        fail(f"{rel} must be UTF-8 text: {exc}")
        return
    if actual != expected:
        fail(f"{rel} must match {label} rendered from committed layout.json")


def validate_export_goldens(fixture_dir: Path, layout) -> None:
    ctx = str((fixture_dir / "layout.json").relative_to(ROOT))
    validate_export_file(
        fixture_dir / TEXT_EXPORT,
        render_text_export(layout),
        "text export",
    )
    validate_export_file(
        fixture_dir / MARKDOWN_EXPORT,
        render_markdown_export(layout, ctx),
        "Markdown export",
    )


def validate_projection_items(ctx: str, key: str, value, required: bool) -> None:
    if not isinstance(value, list):
        return
    if required and not value:
        fail(f"{ctx} {key} must not be empty")
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            fail(f"{ctx} {key}[{index}] must be an object")
            continue
        if not isinstance(item.get("id"), str) or not item["id"]:
            fail(f"{ctx} {key}[{index}].id must be a non-empty string")


def validate_hex_sha(value, ctx: str) -> bool:
    if not isinstance(value, str) or not HEX256.fullmatch(value):
        fail(f"{ctx} must be lowercase hex sha256")
        return False
    return True


def validate_foreign_file_hash(package_dir: Path, rel_value, sha_value, ctx: str) -> None:
    if not isinstance(rel_value, str) or not is_safe_relative_path(rel_value):
        fail(f"{ctx} path must be a safe relative path")
        return
    if not validate_hex_sha(sha_value, f"{ctx} sha256"):
        return

    path = package_dir / rel_value
    if not path.is_file():
        fail(f"{path.relative_to(ROOT)} missing for foreign fixture manifest")
        return

    actual_sha = sha256_file(path)
    if actual_sha != sha_value:
        fail(
            f"{path.relative_to(ROOT)} sha256 {actual_sha} "
            f"does not match foreign manifest {sha_value}"
        )


def validate_foreign_fixture_packages() -> int:
    count = 0
    for manifest_path in sorted(ROOT.glob("foreign/*/*/manifest.json")):
        count += 1
        package_dir = manifest_path.parent
        ctx = str(manifest_path.relative_to(ROOT))
        manifest = load_json(manifest_path)
        if manifest is None:
            continue
        if not isinstance(manifest, dict):
            fail(f"{ctx} must be an object")
            continue
        if set(manifest) != FOREIGN_MANIFEST_KEYS:
            fail(f"{ctx} must contain exactly {sorted(FOREIGN_MANIFEST_KEYS)}")
            continue

        for key in (
            "parser",
            "version",
            "generator_artifact",
            "generated_by_command",
            "generated_at_policy",
            "source_provenance",
            "license",
        ):
            non_placeholder_text(manifest.get(key), f"{ctx} {key}")

        validate_hex_sha(
            manifest.get("generator_artifact_sha256"),
            f"{ctx} generator_artifact_sha256",
        )
        validate_foreign_file_hash(
            package_dir,
            manifest.get("source_pdf"),
            manifest.get("source_pdf_sha256"),
            f"{ctx} source_pdf",
        )
        validate_foreign_file_hash(
            package_dir,
            manifest.get("output_json"),
            manifest.get("output_json_sha256"),
            f"{ctx} output_json",
        )
    return count


def validate_expected_count(value, expected, ctx: str) -> None:
    if expected is None:
        return
    if not isinstance(expected, int) or expected < 0:
        fail(f"{ctx} must be an integer >= 0")
        return
    if len(value) != expected:
        fail(f"{ctx} expected {expected}, found {len(value)}")


def validate_expected_text(metadata, layout, ctx: str) -> None:
    if "expected_text" not in metadata:
        return
    expected = metadata["expected_text"]
    elements = layout.get("elements") if isinstance(layout, dict) else None
    if not isinstance(elements, list):
        return
    actual = [element.get("text") for element in elements]

    if isinstance(expected, str):
        if actual != [expected]:
            fail(f"{ctx} expected_text must match layout element text order")
    elif isinstance(expected, list) and all(isinstance(item, str) for item in expected):
        if actual != expected:
            fail(f"{ctx} expected_text list must match layout reading order")
    else:
        fail(f"{ctx} expected_text must be a string or string array")


def validate_expected_element_types(metadata, layout, ctx: str) -> None:
    if "expected_element_types" not in metadata:
        return
    expected = metadata["expected_element_types"]
    if not isinstance(expected, list) or not all(isinstance(item, str) for item in expected):
        fail(f"{ctx} expected_element_types must be a string array")
        return
    elements = layout.get("elements") if isinstance(layout, dict) else None
    if not isinstance(elements, list):
        return
    actual = [element.get("type") for element in elements]
    if actual != expected:
        fail(f"{ctx} expected_element_types must match layout element type order")


def validate_expected_span_text(metadata, extraction, ctx: str) -> None:
    if "expected_span_text" not in metadata:
        return
    expected = metadata["expected_span_text"]
    if not isinstance(expected, list) or not all(isinstance(item, str) for item in expected):
        fail(f"{ctx} expected_span_text must be a string array")
        return
    spans = extraction.get("spans") if isinstance(extraction, dict) else None
    if not isinstance(spans, list):
        return
    actual = [span.get("text") for span in spans]
    if actual != expected:
        fail(f"{ctx} expected_span_text must match extraction span order")


def validate_expected_font_id(metadata, extraction, ctx: str) -> None:
    if "expected_font_id" not in metadata:
        return
    expected = metadata["expected_font_id"]
    if not isinstance(expected, str) or not expected:
        fail(f"{ctx} expected_font_id must be a non-empty string")
        return
    spans = extraction.get("spans") if isinstance(extraction, dict) else None
    if not isinstance(spans, list):
        return
    actual = []
    for index, span in enumerate(spans):
        font_id = span.get("font_id") if isinstance(span, dict) else None
        if not isinstance(font_id, str) or not font_id:
            fail(f"{ctx} extraction span {index} font_id must be a non-empty string")
            return
        actual.append(font_id)
    if actual != [expected] * len(actual):
        fail(f"{ctx} expected_font_id must match every extraction span font_id")


def validate_stage_expectations(metadata_path: Path, metadata, extraction, layout) -> None:
    ctx = str(metadata_path.relative_to(ROOT))
    if isinstance(extraction, dict):
        validate_expected_count(
            extraction.get("pages", []),
            metadata.get("expected_pages"),
            f"{ctx} expected_pages",
        )
        validate_expected_span_text(metadata, extraction, ctx)
        validate_expected_font_id(metadata, extraction, ctx)
    if isinstance(layout, dict):
        validate_expected_count(
            layout.get("elements", []),
            metadata.get("expected_elements"),
            f"{ctx} expected_elements",
        )
        validate_expected_text(metadata, layout, ctx)
        validate_expected_element_types(metadata, layout, ctx)


manifest = load_json(MANIFEST)
if manifest is None:
    sys.exit(1)

if set(manifest) != MANIFEST_KEYS:
    fail(f"manifest.json must contain exactly {sorted(MANIFEST_KEYS)}")
if manifest.get("manifest_version") != "1.0.0":
    fail("manifest.json manifest_version must be 1.0.0")
if manifest.get("root") != "fixtures":
    fail("manifest.json root must be fixtures")
if not isinstance(manifest.get("subsets_declared"), list):
    fail("manifest.json subsets_declared must be an array")
    subsets_declared = []
else:
    subsets_declared = manifest["subsets_declared"]
if subsets_declared != sorted(set(subsets_declared)):
    fail("manifest.json subsets_declared must be sorted and unique")
for subset in subsets_declared:
    if not isinstance(subset, str) or not SUBSET.fullmatch(subset):
        fail(f"manifest.json subsets_declared contains invalid subset '{subset}'")
if not isinstance(manifest.get("fixtures"), list):
    fail("manifest.json fixtures must be an array")
    entries = []
else:
    entries = manifest["fixtures"]

declared_subset_set = set(subsets_declared)
metadata_paths = {
    path.parent.relative_to(ROOT).as_posix(): path
    for path in sorted(ROOT.glob("*/*/fixture.json"))
}
document_paths = {
    path.relative_to(ROOT).as_posix(): path
    for path in sorted(ROOT.glob("*/*/document.pdf"))
}

seen_ids = set()
seen_files = set()
indexed_files = []

for index, entry in enumerate(entries):
    ctx = f"manifest fixtures[{index}]"
    if not isinstance(entry, dict):
        fail(f"{ctx} must be an object")
        continue
    if set(entry) != ENTRY_KEYS:
        fail(f"{ctx} must contain exactly {sorted(ENTRY_KEYS)}")
        continue

    fixture_id = entry["id"]
    fixture_file = entry["file"]
    manifest_sha = entry["sha256"]
    manifest_pages = entry["pages"]
    manifest_subsets = entry["subsets"]
    manifest_provenance = entry["provenance"]
    manifest_license = entry["license"]

    if not isinstance(fixture_id, str) or not SLUG.fullmatch(fixture_id):
        fail(f"{ctx}.id must be a slug")
    if fixture_id in seen_ids:
        fail(f"{ctx}.id duplicates '{fixture_id}'")
    seen_ids.add(fixture_id)

    if not isinstance(fixture_file, str) or not is_safe_relative_path(fixture_file):
        fail(f"{ctx}.file must be a safe relative path")
        continue
    parts = Path(fixture_file).parts
    if len(parts) != 3 or parts[0] not in ALLOWED_CATEGORIES or parts[2] != "document.pdf":
        fail(f"{ctx}.file must be category/name/document.pdf under {sorted(ALLOWED_CATEGORIES)}")
        continue
    if fixture_file in seen_files:
        fail(f"{ctx}.file duplicates '{fixture_file}'")
    seen_files.add(fixture_file)
    indexed_files.append(fixture_file)

    if not isinstance(manifest_sha, str) or not HEX256.fullmatch(manifest_sha):
        fail(f"{ctx}.sha256 must be lowercase hex sha256")
    if not isinstance(manifest_pages, int) or manifest_pages < 0:
        fail(f"{ctx}.pages must be an integer >= 0")
    if not isinstance(manifest_subsets, list) or not manifest_subsets:
        fail(f"{ctx}.subsets must be a non-empty array")
        manifest_subsets = []
    for subset in manifest_subsets:
        if not isinstance(subset, str) or not SUBSET.fullmatch(subset):
            fail(f"{ctx}.subsets contains invalid subset '{subset}'")
        elif subset not in declared_subset_set:
            fail(f"{ctx}.subsets contains undeclared subset '{subset}'")
    if parts[0] == "failure" and "failure" not in manifest_subsets:
        fail(f"{ctx}.subsets must include failure for failure fixtures")
    non_placeholder_text(manifest_provenance, f"{ctx}.provenance")
    non_placeholder_text(manifest_license, f"{ctx}.license")

    metadata_rel = f"{parts[0]}/{parts[1]}"
    metadata_path = metadata_paths.get(metadata_rel)
    document_path = document_paths.get(fixture_file)
    if metadata_path is None:
        fail(f"{metadata_rel}/fixture.json missing for manifest entry")
        continue
    if document_path is None:
        fail(f"{fixture_file} missing for manifest entry")
        continue

    metadata = load_json(metadata_path)
    if metadata is None:
        continue
    expected_document = metadata.get("document", "document.pdf")
    comparisons = [
        ("id", fixture_id),
        ("sha256", manifest_sha),
        ("pages", manifest_pages),
        ("subsets", manifest_subsets),
        ("provenance", manifest_provenance),
        ("license", manifest_license),
    ]
    for key, expected in comparisons:
        if metadata.get(key) != expected:
            fail(f"{metadata_path.relative_to(ROOT)} {key} does not match manifest")
    if expected_document != "document.pdf":
        fail(f"{metadata_path.relative_to(ROOT)} document must be document.pdf")
    if not isinstance(metadata.get("sha256"), str) or not HEX256.fullmatch(metadata["sha256"]):
        fail(f"{metadata_path.relative_to(ROOT)} sha256 must be lowercase hex sha256")
    non_placeholder_text(metadata.get("provenance"), f"{metadata_path.relative_to(ROOT)} provenance")
    non_placeholder_text(metadata.get("license"), f"{metadata_path.relative_to(ROOT)} license")

    actual_sha = sha256_file(document_path)
    if actual_sha != manifest_sha:
        fail(f"{fixture_file} sha256 {actual_sha} does not match manifest {manifest_sha}")

    if "failure" not in manifest_subsets:
        fixture_dir = metadata_path.parent
        extraction_golden = validate_golden_file(
            fixture_dir / "extraction.json",
            "extraction",
            EXTRACTION_GOLDEN_KEYS,
        )
        layout_golden = validate_golden_file(
            fixture_dir / "layout.json",
            "layout",
            LAYOUT_GOLDEN_KEYS,
        )
        if layout_golden is not None:
            validate_export_goldens(fixture_dir, layout_golden)
        if extraction_golden is not None and layout_golden is not None:
            validate_stage_expectations(
                metadata_path,
                metadata,
                extraction_golden,
                layout_golden,
            )

if indexed_files != sorted(indexed_files):
    fail("manifest fixture entries must be sorted by file")

missing_metadata = sorted(set(document_path.rsplit("/", 1)[0] for document_path in document_paths) - set(metadata_paths))
missing_documents = sorted(set(f"{metadata_path}/document.pdf" for metadata_path in metadata_paths) - set(document_paths))
for path in missing_metadata:
    fail(f"{path}/document.pdf exists but fixture.json is missing")
for path in missing_documents:
    fail(f"{path} is missing for fixture.json")

missing_manifest = sorted(set(document_paths) - set(indexed_files))
extra_manifest = sorted(set(indexed_files) - set(document_paths))
for path in missing_manifest:
    fail(f"{path} is missing from manifest")
for path in extra_manifest:
    fail(f"{path} appears in manifest but has no document.pdf")

foreign_package_count = validate_foreign_fixture_packages()

if not failures:
    ok(f"fixture manifest indexes {len(entries)} fixtures")
    ok("fixture metadata matches manifest corpus identity")
    ok("fixture.json sha256 values match document.pdf bytes")
    ok("fixture manifest has no missing or extra fixture documents")
    ok("successful fixture goldens have valid stage metadata")
    ok("successful fixture metadata expectations match committed stage goldens")
    ok("successful fixture text and Markdown exports match committed layout goldens")
    ok(f"foreign fixture manifests bind {foreign_package_count} package(s) to committed hashes")

if failures:
    print(f"\n{failures} failure(s)")
    sys.exit(1)
print("\nAll fixture checks green.")
