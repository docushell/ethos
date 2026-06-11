#!/usr/bin/env python3
"""Fixture manifest validation gate.

Checks, in order:
1. fixtures/manifest.json has the expected v1 shape;
2. every fixture directory has a 1:1 fixture.json/document.pdf pair;
3. every fixture document is indexed exactly once;
4. manifest corpus metadata matches fixture.json;
5. manifest sha256 == fixture.json sha256 == sha256(document.pdf).

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
HEX256 = re.compile(r"^[0-9a-f]{64}$")
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]*$")
SUBSET = re.compile(r"^[a-z0-9][a-z0-9_]*$")
PLACEHOLDER = re.compile(r"todo|_{4,}|found it somewhere", re.IGNORECASE)

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

if not failures:
    ok(f"fixture manifest indexes {len(entries)} fixtures")
    ok("fixture metadata matches manifest corpus identity")
    ok("fixture.json sha256 values match document.pdf bytes")
    ok("fixture manifest has no missing or extra fixture documents")

if failures:
    print(f"\n{failures} failure(s)")
    sys.exit(1)
print("\nAll fixture checks green.")
