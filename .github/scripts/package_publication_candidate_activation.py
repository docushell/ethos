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

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VERSION = "0.1.0"
CORE_PACKAGE = "ethos-doc-core"
CANDIDATE_PACKAGES = (CORE_PACKAGE, "ethos-verify", "ethos-pdf")
CONSUMER_PACKAGE = "ethos-package-candidate-consumer"
CANDIDATE_NORMAL_DEPENDENCIES = {
    CORE_PACKAGE: ["serde", "serde_json", "sha2", "thiserror"],
    "ethos-pdf": [CORE_PACKAGE, "serde", "serde_json"],
    "ethos-verify": [CORE_PACKAGE, "serde"],
    CONSUMER_PACKAGE: [CORE_PACKAGE, "ethos-pdf", "ethos-verify"],
}
IGNORE_NAMES = {
    ".git",
    "target",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "web",
    ".roadmap.md.swp",
}


def should_ignore(_: str, names: list[str]) -> set[str]:
    return {name for name in names if name in IGNORE_NAMES}


def run(command: list[str], cwd: Path, commands: list[dict[str, object]]) -> None:
    result = subprocess.run(
        command,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    commands.append(
        {
            "command": " ".join(command),
            "returncode": result.returncode,
            "stdout_tail": result.stdout[-1200:],
            "stderr_tail": result.stderr[-1200:],
        }
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"command failed in candidate activation workspace: {' '.join(command)}\n"
            f"{result.stdout}\n{result.stderr}"
        )


def run_output(command: list[str], cwd: Path, commands: list[dict[str, object]]) -> str:
    result = subprocess.run(
        command,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    commands.append(
        {
            "command": " ".join(command),
            "returncode": result.returncode,
            "stdout_tail": result.stdout[-1200:],
            "stderr_tail": result.stderr[-1200:],
        }
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"command failed in candidate activation workspace: {' '.join(command)}\n"
            f"{result.stdout}\n{result.stderr}"
        )
    return result.stdout


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"expected text not found in {path}: {old}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def rewrite_candidate_lockfile(workspace: Path) -> None:
    lockfile = workspace / "Cargo.lock"
    text = lockfile.read_text(encoding="utf-8")
    if 'name = "ethos-core"' not in text:
        raise RuntimeError("expected ethos-core package entry in candidate Cargo.lock")
    lockfile.write_text(text.replace("ethos-core", CORE_PACKAGE), encoding="utf-8")


def materialize_candidate_workspace(workspace: Path) -> None:
    shutil.copytree(ROOT, workspace, ignore=should_ignore)

    replace_once(
        workspace / "Cargo.toml",
        'ethos-core = { path = "crates/ethos-core", version = "0.1.0", default-features = false }',
        'ethos-core = { package = "ethos-doc-core", path = "crates/ethos-core", version = "0.1.0", default-features = false }',
    )
    with (workspace / "Cargo.toml").open("a", encoding="utf-8") as handle:
        handle.write(
            '\n[patch.crates-io]\n'
            'ethos-doc-core = { path = "crates/ethos-core" }\n'
        )

    core_manifest = workspace / "crates/ethos-core/Cargo.toml"
    replace_once(core_manifest, 'name = "ethos-core"', 'name = "ethos-doc-core"')
    replace_once(
        core_manifest,
        "authors.workspace = true\n\n[package.metadata.ethos_publication]",
        'authors.workspace = true\n\n[lib]\nname = "ethos_core"\n\n[package.metadata.ethos_publication]',
    )
    rewrite_candidate_lockfile(workspace)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_packaged_manifest(crate_path: Path, package: str) -> str:
    with tarfile.open(crate_path, "r:gz") as archive:
        member = archive.getmember(f"{package}-{VERSION}/Cargo.toml")
        extracted = archive.extractfile(member)
        if extracted is None:
            raise RuntimeError(f"missing packaged Cargo.toml in {crate_path}")
        return extracted.read().decode("utf-8")


def package_candidate(workspace: Path, package: str, commands: list[dict[str, object]]) -> dict[str, str]:
    run(
        ["cargo", "package", "--locked", "--offline", "-p", package, "--allow-dirty", "--no-verify"],
        workspace,
        commands,
    )
    crate_path = workspace / "target/package" / f"{package}-{VERSION}.crate"
    if not crate_path.is_file():
        raise RuntimeError(f"missing package artifact: {crate_path}")
    manifest = read_packaged_manifest(crate_path, package)
    return {
        "package": package,
        "crate_file": crate_path.name,
        "sha256": sha256(crate_path),
        "manifest": manifest,
    }


def extract_crates(workspace: Path, artifacts: list[dict[str, str]]) -> Path:
    unpacked = workspace / "target/package-candidate-unpacked"
    unpacked.mkdir(parents=True, exist_ok=True)
    for artifact in artifacts:
        crate_path = workspace / "target/package" / artifact["crate_file"]
        with tarfile.open(crate_path, "r:gz") as archive:
            archive.extractall(unpacked)
    return unpacked


def write_cargo_checksum(package_dir: Path, crate_path: Path) -> None:
    files: dict[str, str] = {}
    for path in sorted(package_dir.rglob("*")):
        if not path.is_file() or path.name == ".cargo-checksum.json":
            continue
        rel = path.relative_to(package_dir).as_posix()
        files[rel] = sha256(path)
    (package_dir / ".cargo-checksum.json").write_text(
        json.dumps({"files": files, "package": sha256(crate_path)}, sort_keys=True),
        encoding="utf-8",
    )


def activate_registry_equivalent_source(
    workspace: Path,
    core_artifact: dict[str, str],
    commands: list[dict[str, object]],
) -> None:
    vendor_dir = workspace / "target/package-candidate-vendor"
    cargo_config = run_output(
        ["cargo", "vendor", "--locked", "--offline", "target/package-candidate-vendor"],
        workspace,
        commands,
    )
    crate_path = workspace / "target/package" / core_artifact["crate_file"]
    with tarfile.open(crate_path, "r:gz") as archive:
        archive.extractall(vendor_dir)
    write_cargo_checksum(vendor_dir / f"ethos-doc-core-{VERSION}", crate_path)

    config_dir = workspace / ".cargo"
    config_dir.mkdir(exist_ok=True)
    (config_dir / "config.toml").write_text(cargo_config, encoding="utf-8")


def write_consumer(workspace: Path, unpacked: Path) -> Path:
    consumer = workspace / "target/package-candidate-consumer"
    (consumer / "src").mkdir(parents=True, exist_ok=True)
    (consumer / "Cargo.toml").write_text(
        f"""[package]
name = "{CONSUMER_PACKAGE}"
version = "0.0.0"
edition = "2021"
publish = false

[workspace]

[dependencies]
ethos-core = {{ package = "ethos-doc-core", version = "{VERSION}", default-features = false, features = ["grounding", "verify-types"] }}
ethos-verify = {{ version = "{VERSION}" }}
ethos-pdf = {{ version = "{VERSION}" }}

[patch.crates-io]
ethos-doc-core = {{ path = "{unpacked / f'ethos-doc-core-{VERSION}'}" }}
ethos-verify = {{ path = "{unpacked / f'ethos-verify-{VERSION}'}" }}
ethos-pdf = {{ path = "{unpacked / f'ethos-pdf-{VERSION}'}" }}
""",
        encoding="utf-8",
    )
    (consumer / "src/lib.rs").write_text(
        """use ethos_core::grounding::GroundingSource;

pub fn candidate_surface_links() -> &'static str {
    let _ = core::any::type_name::<dyn GroundingSource>();
    let _ = ethos_verify::normalize_quote("candidate");
    let _ = ethos_pdf::PDFIUM_LIBRARY_PATH_ENV;
    ethos_core::SCHEMA_VERSION
}
""",
        encoding="utf-8",
    )
    return consumer


def dependency_name(dependency: str) -> str:
    return dependency.split(" ", 1)[0]


def lock_dependency_list(dependencies: list[str]) -> str:
    lines = ["dependencies = ["]
    lines.extend(f" {json.dumps(dependency)}," for dependency in dependencies)
    lines.append("]")
    return "\n".join(lines)


def lock_package_entry(package: dict[str, object]) -> str:
    lines = [
        "[[package]]",
        f"name = {json.dumps(package['name'])}",
        f"version = {json.dumps(package['version'])}",
    ]
    if "source" in package:
        lines.append(f"source = {json.dumps(package['source'])}")
    if "checksum" in package:
        lines.append(f"checksum = {json.dumps(package['checksum'])}")
    dependencies = package.get("dependencies")
    if dependencies:
        lines.append(lock_dependency_list(dependencies))
    return "\n".join(lines)


def parse_lock_packages(lockfile: Path) -> list[dict[str, object]]:
    packages: list[dict[str, object]] = []
    for block in lockfile.read_text(encoding="utf-8").split("[[package]]\n")[1:]:
        package: dict[str, object] = {}
        dependencies: list[str] = []
        in_dependencies = False
        for raw_line in block.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if in_dependencies:
                if line == "]":
                    in_dependencies = False
                else:
                    dependencies.append(json.loads(line.rstrip(",")))
                continue
            if line == "dependencies = [":
                in_dependencies = True
                continue
            if " = " not in line:
                continue
            key, value = line.split(" = ", 1)
            if key in {"name", "version", "source", "checksum"}:
                package[key] = json.loads(value)
        if dependencies:
            package["dependencies"] = dependencies
        if package:
            packages.append(package)
    return packages


def write_consumer_lockfile(workspace: Path, consumer: Path) -> None:
    packages = parse_lock_packages(workspace / "Cargo.lock")
    by_name = {package["name"]: package for package in packages}

    selected: set[str] = set()
    stack = [CONSUMER_PACKAGE]
    while stack:
        package_name = stack.pop()
        if package_name in selected:
            continue
        selected.add(package_name)
        if package_name in CANDIDATE_NORMAL_DEPENDENCIES:
            dependencies = CANDIDATE_NORMAL_DEPENDENCIES[package_name]
        else:
            if package_name not in by_name:
                raise RuntimeError(f"missing locked package for consumer dependency: {package_name}")
            dependencies = by_name[package_name].get("dependencies", [])
        stack.extend(dependency_name(dependency) for dependency in dependencies)

    entries: list[dict[str, object]] = []
    for package_name in sorted(selected):
        if package_name == CONSUMER_PACKAGE:
            entries.append(
                {
                    "name": CONSUMER_PACKAGE,
                    "version": "0.0.0",
                    "dependencies": CANDIDATE_NORMAL_DEPENDENCIES[CONSUMER_PACKAGE],
                }
            )
        elif package_name in CANDIDATE_NORMAL_DEPENDENCIES:
            entries.append(
                {
                    "name": package_name,
                    "version": VERSION,
                    "dependencies": CANDIDATE_NORMAL_DEPENDENCIES[package_name],
                }
            )
        else:
            entries.append(by_name[package_name])

    text = "# This file is automatically @generated by Cargo.\n"
    text += "# It is not intended for manual editing.\n"
    text += "version = 4\n\n"
    text += "\n\n".join(lock_package_entry(package) for package in entries)
    text += "\n"
    (consumer / "Cargo.lock").write_text(text, encoding="utf-8")


def validate_packaged_manifests(artifacts: list[dict[str, str]]) -> dict[str, object]:
    manifests = {artifact["package"]: artifact["manifest"] for artifact in artifacts}
    core = manifests[CORE_PACKAGE]
    verify = manifests["ethos-verify"]
    pdf = manifests["ethos-pdf"]

    checks = {
        "core_package_name": 'name = "ethos-doc-core"' in core,
        "core_library_name": 'name = "ethos_core"' in core,
        "verify_depends_on_core_package": "ethos-doc-core" in verify,
        "verify_retains_grounding_features": "grounding" in verify and "verify-types" in verify,
        "pdf_depends_on_core_package": "ethos-doc-core" in pdf,
        "pdf_retains_full_feature": "full" in pdf,
    }
    missing = [name for name, passed in checks.items() if not passed]
    if missing:
        raise RuntimeError(f"packaged manifest checks failed: {', '.join(missing)}")
    return checks


def source_manifests_are_still_blocked() -> bool:
    core = (ROOT / "crates/ethos-core/Cargo.toml").read_text(encoding="utf-8")
    verify = (ROOT / "crates/ethos-verify/Cargo.toml").read_text(encoding="utf-8")
    pdf = (ROOT / "crates/ethos-pdf/Cargo.toml").read_text(encoding="utf-8")
    return all(
        [
            'name = "ethos-core"' in core,
            "publish = false" in core,
            "publish = false" in verify,
            "publish = false" in pdf,
            'package = "ethos-doc-core"' not in verify,
            'package = "ethos-doc-core"' not in pdf,
            not (ROOT / ".cargo/config.toml").exists(),
            not (ROOT / "target/package-registry").exists(),
        ]
    )


def run_candidate_activation(workspace: Path) -> dict[str, object]:
    commands: list[dict[str, object]] = []
    materialize_candidate_workspace(workspace)
    run(["cargo", "check", "--locked", "--offline", "-p", "ethos-verify"], workspace, commands)
    run(["cargo", "check", "--locked", "--offline", "-p", "ethos-pdf"], workspace, commands)
    core_artifact = package_candidate(workspace, CORE_PACKAGE, commands)
    activate_registry_equivalent_source(workspace, core_artifact, commands)
    artifacts = [core_artifact] + [
        package_candidate(workspace, package, commands)
        for package in ("ethos-verify", "ethos-pdf")
    ]
    checks = validate_packaged_manifests(artifacts)
    unpacked = extract_crates(workspace, artifacts)
    consumer = write_consumer(workspace, unpacked)
    write_consumer_lockfile(workspace, consumer)
    run(["cargo", "check", "--locked", "--offline"], consumer, commands)

    return {
        "status": "pass",
        "candidate_version": VERSION,
        "candidate_packages": list(CANDIDATE_PACKAGES),
        "manifest_activation": {
            "core_package_name": "ethos-doc-core",
            "core_library_name": "ethos_core",
            "dependency_key": "ethos-core",
            "verify_core_features": ["grounding", "verify-types"],
            "pdf_core_features": ["full"],
        },
        "packaged_manifest_checks": checks,
        "artifacts": [
            {
                "package": artifact["package"],
                "crate_file": artifact["crate_file"],
                "sha256": artifact["sha256"],
            }
            for artifact in artifacts
        ],
        "registry_equivalent_consumer_check": "pass",
        "source_manifests_remain_blocked": source_manifests_are_still_blocked(),
        "package_publication_approved": False,
        "public_installation_approved": False,
        "commands": commands,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--keep-workspace", type=Path, help="write the candidate workspace here")
    args = parser.parse_args()

    if args.keep_workspace:
        workspace = args.keep_workspace.resolve()
        if workspace.exists():
            shutil.rmtree(workspace)
        result = run_candidate_activation(workspace)
    else:
        with tempfile.TemporaryDirectory(prefix="ethos-package-candidate-") as tmp:
            result = run_candidate_activation(Path(tmp) / "ethos")

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("candidate package activation evidence passed")


if __name__ == "__main__":
    main()
