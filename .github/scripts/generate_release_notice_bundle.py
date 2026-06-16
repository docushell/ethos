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

"""Generate a draft release license/NOTICE bundle.

The output is intentionally marked not release-ready. It assembles the project NOTICE and Cargo
third-party manifest, then records the external artifact notice obligations that still need to be
satisfied for real binaries, wheels, npm packages, or bundled native/font assets.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_manifest(artifact_name: str, cargo_manifest: dict[str, Any]) -> dict[str, Any]:
    summary = cargo_manifest["summary"]
    return {
        "schema_version": 1,
        "artifact_name": artifact_name,
        "status": "draft_not_release_ready",
        "release_boundary": (
            "This bundle is a draft planning artifact. Release workflows remain blocked until "
            "the concrete artifact payload, external native/font assets, provenance, and notices "
            "are reviewed for that artifact."
        ),
        "included_materials": [
            {"id": "project-license", "path": "LICENSE", "status": "included-in-source"},
            {"id": "project-notice", "path": "NOTICE", "status": "included-in-source"},
            {
                "id": "cargo-third-party-manifest",
                "path": "THIRD-PARTY-CARGO-LICENSES.json",
                "status": "generated",
                "third_party_package_count": summary["third_party_package_count"],
                "workspace_package_count": summary["workspace_package_count"],
            },
        ],
        "conditional_external_materials": [
            {
                "id": "pdfium",
                "license": "BSD-3-Clause",
                "required_when": "artifact bundles a PDFium binary or extracted PDFium library",
                "status": "not-included-in-source-tree",
                "release_blocking_if_bundled_without_notice": True,
            },
            {
                "id": "liberation-fonts",
                "license": "SIL Open Font License 1.1",
                "required_when": "artifact bundles Liberation font files",
                "status": "not-included-in-source-tree",
                "release_blocking_if_bundled_without_notice": True,
            },
        ],
        "blocked_release_artifact_types": [
            "github-release-binary",
            "wheel",
            "npm-package",
            "crate-publication",
            "public-benchmark-report",
        ],
        "required_before_release": [
            "replace this draft artifact name with the concrete artifact identifier",
            "attach or embed the reviewed artifact-specific license and NOTICE bundle",
            "include upstream PDFium license/notice material if PDFium is bundled",
            "include upstream font license/notice material if fonts are bundled",
            "record artifact checksums and provenance",
            "rerun claim-language and public-release gates",
        ],
    }


def build_notice(artifact_name: str, cargo_manifest: dict[str, Any]) -> str:
    summary = cargo_manifest["summary"]
    licenses = "\n".join(f"- {item}" for item in summary["license_expressions"])
    return f"""# Draft Release NOTICE Bundle

Artifact: `{artifact_name}`
Status: `draft_not_release_ready`

This is a planning bundle, not a public release artifact notice. Ethos release workflows remain
blocked until a concrete artifact payload, provenance record, and artifact-specific license/NOTICE
bundle are reviewed.

## Included Source Materials

- `LICENSE` - Apache License 2.0 for Ethos source.
- `NOTICE` - project NOTICE with PDFium and Liberation font notice boundaries.
- `THIRD-PARTY-CARGO-LICENSES.json` - generated Cargo registry dependency manifest.

## Cargo Dependency Summary

- Workspace packages: {summary["workspace_package_count"]}
- Third-party registry packages: {summary["third_party_package_count"]}

License expressions:

{licenses}

## Conditional External Materials

- PDFium: include upstream BSD-3-Clause license and notice material if a release artifact bundles
  a PDFium binary or extracted PDFium library.
- Liberation Fonts: include upstream SIL Open Font License 1.1 material if a release artifact
  bundles font files.

## Release Blockers

- No GitHub release binaries yet.
- No wheels yet.
- No npm package updates yet.
- No crate publication beyond reservation placeholders yet.
- No public benchmark report yet.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cargo-manifest", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--artifact-name", default="ethos-cli-draft")
    args = parser.parse_args()

    cargo_manifest_path = Path(args.cargo_manifest)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cargo_manifest = read_json(cargo_manifest_path)
    manifest = build_manifest(args.artifact_name, cargo_manifest)

    (out_dir / "THIRD-PARTY-CARGO-LICENSES.json").write_text(
        json.dumps(cargo_manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_json(out_dir / "release-notice-manifest.json", manifest)
    (out_dir / "NOTICE.release.md").write_text(
        build_notice(args.artifact_name, cargo_manifest),
        encoding="utf-8",
    )
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
