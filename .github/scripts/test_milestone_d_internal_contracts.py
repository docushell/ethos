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

import ast
import json
import re
import unittest
from pathlib import Path

from makefile_guard import makefile_text, target_block


ROOT = Path(__file__).resolve().parents[2]
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
ROADMAP = ROOT / "docs/roadmap.md"
SCHEMAS_README = ROOT / "schemas/README.md"
VALIDATE_EXAMPLES = ROOT / "schemas/validate_examples.py"
COMMON_CONTRACT_GATES = [
    "$(PYTHON) schemas/validate_examples.py",
    "$(PYTHON) .github/scripts/test_execution_status.py",
    "$(PYTHON) .github/scripts/test_roadmap_status.py",
]
OUT_OF_SCOPE_PUBLIC_CLAIM_TERMS = [
    "benchmark",
    "release",
    "package",
    "production",
    "speed",
    "footprint",
    "table-quality",
    "parser-quality",
]
SURFACE_EXPANSION_BLOCKER_PATTERN = re.compile(r"\b(surfaces?|bindings?|methods?)\b")
COMMAND_EXPANSION_BLOCKER_PATTERN = re.compile(r"\b(commands?|cli)\b")
INVENTORY_REPO_PATH_KEYS = {
    "base_contract_inventory",
    "checked_files",
    "citations",
    "descriptor",
    "descriptor_schema",
    "document",
    "golden",
    "implementation",
    "report_golden",
    "report_schema",
    "request",
    "request_schema",
    "schema",
    "source_fixture",
    "trait_module",
}
CONTRACT_REGISTRY = [
    {
        "contract": "verify_citations.v1",
        "carrier": "ethos verify",
        "target": "milestone-d-verify-citations-contract",
        "doc": "docs/milestone-d-verify-citations-contract.md",
        "inventory": "examples/verify/verify_citations_v1_contract.json",
        "schema": "schemas/ethos-verify-citations-contract.schema.json",
        "commands": [
            "cargo test --locked -p ethos-cli --test verify",
        ]
        + COMMON_CONTRACT_GATES
        + [
            "$(PYTHON) .github/scripts/test_milestone_d_verify_citations_contract.py",
            "git diff --check",
        ],
    },
    {
        "contract": "claim_kind_boundary.v1",
        "carrier": "ethos verify",
        "target": "milestone-d-claim-kind-boundary-contract",
        "doc": "docs/milestone-d-claim-kind-boundary-contract.md",
        "inventory": "examples/verify/claim_kind_boundary_v1_contract.json",
        "schema": "schemas/ethos-claim-kind-boundary-contract.schema.json",
        "commands": [
            "cargo test --locked -p ethos-verify claim_kind",
            "cargo test --locked -p ethos-cli --test verify invalid_config_constraints_are_usage_errors",
        ]
        + COMMON_CONTRACT_GATES
        + [
            "$(PYTHON) .github/scripts/test_milestone_d_claim_kind_boundary_contract.py",
            "git diff --check",
        ],
    },
    {
        "contract": "grounding_source.v1",
        "carrier": "GroundingSource trait",
        "target": "milestone-d-grounding-source-contract",
        "doc": "docs/milestone-d-grounding-source-contract.md",
        "inventory": "examples/verify/grounding_source_v1_contract.json",
        "schema": "schemas/ethos-grounding-source-contract.schema.json",
        "commands": [
            "cargo test --locked -p ethos-core grounding",
            "cargo test --locked -p ethos-cli --test verify native_ethos_verify_produces_non_empty_checks",
            "cargo test --locked -p ethos-cli --test verify opendataloader_verify_adapter_produces_capability_aware_report",
        ]
        + COMMON_CONTRACT_GATES
        + [
            "$(PYTHON) .github/scripts/test_milestone_d_grounding_source_contract.py",
            "git diff --check",
        ],
    },
    {
        "contract": "opendataloader_adapter_shape.v1",
        "carrier": "opendataloader-json adapter",
        "target": "milestone-d-opendataloader-adapter-shape-contract",
        "doc": "docs/milestone-d-opendataloader-adapter-shape-contract.md",
        "inventory": "examples/verify/opendataloader_adapter_shape_v1_contract.json",
        "schema": "schemas/ethos-opendataloader-adapter-shape-contract.schema.json",
        "commands": [
            "cargo test --locked -p ethos-grounding-opendataloader-json",
            "cargo test --locked -p ethos-cli --test verify opendataloader",
        ]
        + COMMON_CONTRACT_GATES
        + [
            "$(PYTHON) .github/scripts/test_milestone_d_opendataloader_adapter_shape_contract.py",
            "git diff --check",
        ],
    },
    {
        "contract": "capability_downgrade.v1",
        "carrier": "ethos verify",
        "target": "milestone-d-capability-downgrade-contract",
        "doc": "docs/milestone-d-capability-downgrade-contract.md",
        "inventory": "examples/verify/capability_downgrade_v1_contract.json",
        "schema": "schemas/ethos-capability-downgrade-contract.schema.json",
        "commands": [
            "cargo test --locked -p ethos-verify capability",
            "cargo test --locked -p ethos-cli --test verify capability",
        ]
        + COMMON_CONTRACT_GATES
        + [
            "$(PYTHON) .github/scripts/test_milestone_d_capability_downgrade_contract.py",
            "git diff --check",
        ],
    },
    {
        "contract": "crop_element.v1",
        "carrier": "ethos verify --crop-dir",
        "target": "milestone-d-crop-element-contract",
        "doc": "docs/milestone-d-crop-element-contract.md",
        "inventory": "examples/crop/crop_element_v1_contract.json",
        "schema": "schemas/ethos-crop-element-contract.schema.json",
        "commands": [
            "cargo test --locked -p ethos-cli --test verify native_verify_crop_dir_writes_deterministic_crop_descriptors",
        ]
        + COMMON_CONTRACT_GATES
        + [
            "$(PYTHON) .github/scripts/test_milestone_d_crop_element_contract.py",
            "git diff --check",
        ],
    },
    {
        "contract": "crop_element_surface_shape.v1",
        "carrier": "source-only crop_element surface shape",
        "target": "milestone-d-crop-element-surface-shape-contract",
        "doc": "docs/milestone-d-crop-element-surface-shape-contract.md",
        "inventory": "examples/crop/crop_element_surface_shape_v1_contract.json",
        "schema": "schemas/ethos-crop-element-surface-shape-contract.schema.json",
        "commands": COMMON_CONTRACT_GATES
        + [
            "$(PYTHON) .github/scripts/test_milestone_d_crop_element_surface_shape_contract.py",
            "git diff --check",
        ],
    },
    {
        "contract": "sandbox_subprocess.v1",
        "carrier": "pdfium worker process",
        "target": "milestone-d-sandbox-subprocess-contract",
        "doc": "docs/milestone-d-sandbox-subprocess-contract.md",
        "inventory": "examples/sandbox/sandbox_subprocess_v1_contract.json",
        "schema": "schemas/ethos-sandbox-subprocess-contract.schema.json",
        "commands": [
            "cargo test --locked -p ethos-cli json_artifact_header",
            "cargo test --locked -p ethos-cli --test pdf_parse worker",
        ]
        + COMMON_CONTRACT_GATES
        + [
            "$(PYTHON) .github/scripts/test_milestone_d_sandbox_subprocess_contract.py",
            "git diff --check",
        ],
    },
]
D_REQUEST_ENVELOPES = [
    {
        "schema": "schemas/ethos-crop-element-request.schema.json",
        "description": "source-only request envelope for Milestone D `crop_element` v1 contract work",
        "examples": [
            "schemas/examples/crop-element-request.example.json",
        ],
        "status_needles": [
            "request envelope at `schemas/examples/crop-element-request.example.json`",
        ],
    },
    {
        "schema": "schemas/ethos-sandbox-subprocess-request.schema.json",
        "description": "source-only request envelope for Milestone D `sandbox_subprocess` v1 contract work",
        "examples": [
            "schemas/examples/sandbox-subprocess-doc-parse-request.example.json",
            "schemas/examples/sandbox-subprocess-doc-parse-timeout-request.example.json",
            "schemas/examples/sandbox-subprocess-doc-parse-diagnostics-request.example.json",
            "schemas/examples/sandbox-subprocess-fingerprint-timeout-request.example.json",
        ],
        "status_needles": [
            "request envelopes under `schemas/examples/sandbox-subprocess-*.example.json`",
        ],
    },
]


def load_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def inventory_named_collections(path: str) -> list[tuple[str, list[str]]]:
    inventory = load_json(path)
    collections = []
    for key, value in inventory.items():
        if isinstance(value, dict) and "name" in value:
            collections.append((key, [value["name"]]))
        elif isinstance(value, list):
            names = [
                item["name"]
                for item in value
                if isinstance(item, dict) and "name" in item
            ]
            if names:
                collections.append((key, names))
    return collections


def repo_path_reference_values(value: object, pointer: str) -> list[tuple[str, str]]:
    if isinstance(value, str):
        return [(pointer, value)]
    if isinstance(value, list):
        return [
            (f"{pointer}/{index}", item)
            for index, item in enumerate(value)
            if isinstance(item, str)
        ]
    return []


def inventory_repo_path_references(node: object, pointer: str = "$") -> list[tuple[str, str]]:
    references = []
    if isinstance(node, dict):
        for key, value in node.items():
            child_pointer = f"{pointer}/{key}"
            if key in INVENTORY_REPO_PATH_KEYS:
                references.extend(repo_path_reference_values(value, child_pointer))
            references.extend(inventory_repo_path_references(value, child_pointer))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            references.extend(inventory_repo_path_references(value, f"{pointer}/{index}"))
    return references


def registered_targets() -> list[str]:
    return [entry["target"] for entry in CONTRACT_REGISTRY]


def registered_paths(key: str) -> list[str]:
    return sorted(entry[key] for entry in CONTRACT_REGISTRY)


def focused_validation_command(entry: dict) -> str:
    return f"make {entry['target']} PYTHON=<jsonschema-venv>/bin/python"


def contract_name(entry: dict) -> str:
    return entry["contract"].removesuffix(".v1")


def contract_kebab(entry: dict) -> str:
    return contract_name(entry).replace("_", "-")


def expected_contract_guard_script(entry: dict) -> str:
    target_slug = entry["target"].removeprefix("milestone-d-").replace("-", "_")
    return f".github/scripts/test_milestone_d_{target_slug}.py"


def schema_slug(entry: dict) -> str:
    name = Path(entry["schema"]).name
    return name.removeprefix("ethos-").removesuffix(".schema.json")


def schemas_readme_table_entries() -> dict[str, str]:
    entries = {}
    for line in SCHEMAS_README.read_text(encoding="utf-8").splitlines():
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(parts) == 2 and parts[0].startswith("`") and parts[0].endswith("`"):
            entries[parts[0].strip("`")] = parts[1]
    return entries


def schemas_readme_contract_table_entries() -> dict[str, str]:
    return {
        schema_name: description
        for schema_name, description in schemas_readme_table_entries().items()
        if re.fullmatch(r"ethos-.+-contract\.schema\.json", schema_name)
    }


def makefile_target_commands(target: str) -> list[str]:
    return [line.strip() for line in target_block(target).splitlines() if line.strip()]


def makefile_phony_targets() -> set[str]:
    targets: set[str] = set()
    for line in makefile_text().splitlines():
        if line.startswith(".PHONY:"):
            targets.update(line.removeprefix(".PHONY:").split())
    return targets


def doc_explicit_blockers(path: str) -> list[str]:
    lines = (ROOT / path).read_text(encoding="utf-8").splitlines()
    try:
        start = lines.index("## Explicit Blockers For This Slice") + 1
    except ValueError as exc:
        raise AssertionError(f"{path} is missing explicit blockers section") from exc

    blockers: list[str] = []
    for line in lines[start:]:
        if line.startswith("- "):
            blockers.append(line.removeprefix("- ").rstrip(";."))
        elif blockers and line.strip():
            break
    return blockers


def doc_title(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8").splitlines()[0]


def discovered_d_contract_docs() -> list[str]:
    return sorted(
        str(path.relative_to(ROOT))
        for path in (ROOT / "docs").glob("milestone-d-*-contract.md")
    )


def discovered_d_contract_schemas() -> list[str]:
    return sorted(
        str(path.relative_to(ROOT))
        for path in (ROOT / "schemas").glob("ethos-*-contract.schema.json")
    )


def discovered_d_request_envelope_schemas() -> list[str]:
    return sorted(
        str(path.relative_to(ROOT))
        for path in (ROOT / "schemas").glob("ethos-*-request.schema.json")
    )


def discovered_d_contract_inventories() -> list[str]:
    roots = [
        ROOT / "examples" / "verify",
        ROOT / "examples" / "crop",
        ROOT / "examples" / "sandbox",
    ]
    return sorted(
        str(path.relative_to(ROOT))
        for root in roots
        for path in root.glob("*_v1_contract.json")
    )


def discovered_d_contract_guard_scripts() -> list[str]:
    return sorted(
        str(path.relative_to(ROOT))
        for path in (ROOT / ".github" / "scripts").glob("test_milestone_d_*_contract.py")
    )


def path_expr_to_repo_path(node: ast.AST) -> str:
    roots = {
        "ROOT": "",
        "SCHEMAS": "schemas",
        "EXAMPLES": "schemas/examples",
    }
    if isinstance(node, ast.Name) and node.id in roots:
        return roots[node.id]
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        left = path_expr_to_repo_path(node.left)
        right = path_expr_to_repo_path(node.right)
        return f"{left}/{right}" if left else right
    raise AssertionError(f"unsupported validate_examples path expression: {ast.dump(node)}")


def schema_example_validation_pairs() -> set[tuple[str, str]]:
    tree = ast.parse(VALIDATE_EXAMPLES.read_text(encoding="utf-8"))
    pairs_node = next(
        node.value
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "PAIRS" for target in node.targets)
    )

    pairs = set()
    for pair_node in pairs_node.elts:
        schema_node, example_nodes = pair_node.elts
        schema_path = f"schemas/{schema_node.value}"
        for example_node in example_nodes.elts:
            pairs.add((schema_path, path_expr_to_repo_path(example_node)))
    return pairs


def object_schema_nodes(node: object, path: str = "#") -> list[tuple[str, dict]]:
    nodes: list[tuple[str, dict]] = []
    if isinstance(node, dict):
        if node.get("type") == "object":
            nodes.append((path, node))
        for key, value in node.items():
            nodes.extend(object_schema_nodes(value, f"{path}/{key}"))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            nodes.extend(object_schema_nodes(value, f"{path}/{index}"))
    return nodes


def roadmap_table_row(milestone: str) -> str:
    prefix = f"| {milestone} |"
    for line in ROADMAP.read_text(encoding="utf-8").splitlines():
        if line.startswith(prefix):
            return line
    raise AssertionError(f"docs/roadmap.md is missing the {milestone} row")


def execution_status_d_contract_bullets() -> list[str]:
    return [
        line
        for line in EXECUTION_STATUS.read_text(encoding="utf-8").splitlines()
        if line.startswith("- Milestone D ") and "Focused validation is" in line
    ]


class MilestoneDInternalContractsTests(unittest.TestCase):
    def test_target_is_declared_phony(self) -> None:
        text = makefile_text()

        self.assertIn(".PHONY:", text)
        self.assertIn("milestone-d-internal-contracts", text)

    def test_registered_contract_targets_are_declared_phony(self) -> None:
        phony_targets = makefile_phony_targets()

        for target in registered_targets():
            self.assertIn(target, phony_targets)
        self.assertIn("milestone-d-internal-contracts", phony_targets)

    def test_target_composes_current_d_contract_targets(self) -> None:
        block = target_block("milestone-d-internal-contracts")

        for target in registered_targets():
            self.assertIn(f"$(MAKE) {target} PYTHON=$(PYTHON)", block)
        self.assertIn("$(PYTHON) .github/scripts/test_milestone_d_internal_contracts.py", block)
        self.assertIn("git diff --check", block)

    def test_target_commands_match_registered_contracts(self) -> None:
        commands = makefile_target_commands("milestone-d-internal-contracts")

        self.assertEqual(
            [f"$(MAKE) {target} PYTHON=$(PYTHON)" for target in registered_targets()]
            + [
                "$(PYTHON) .github/scripts/test_milestone_d_internal_contracts.py",
                "git diff --check",
            ],
            commands,
        )

    def test_registered_contract_targets_match_declared_commands(self) -> None:
        for entry in CONTRACT_REGISTRY:
            self.assertEqual(
                entry["commands"],
                makefile_target_commands(entry["target"]),
                entry["contract"],
            )

    def test_registered_contracts_use_expected_focused_guard_scripts(self) -> None:
        for entry in CONTRACT_REGISTRY:
            expected_command = f"$(PYTHON) {expected_contract_guard_script(entry)}"
            matching_commands = [
                command
                for command in entry["commands"]
                if command.startswith("$(PYTHON) .github/scripts/test_milestone_d_")
                and command.endswith("_contract.py")
            ]

            self.assertEqual([expected_command], matching_commands, entry["contract"])

    def test_registered_contracts_run_common_gates_before_focused_guards(self) -> None:
        for entry in CONTRACT_REGISTRY:
            commands = entry["commands"]
            focused_command = f"$(PYTHON) {expected_contract_guard_script(entry)}"

            self.assertEqual(
                COMMON_CONTRACT_GATES,
                [command for command in commands if command in COMMON_CONTRACT_GATES],
                entry["contract"],
            )
            self.assertLess(
                commands.index(COMMON_CONTRACT_GATES[-1]),
                commands.index(focused_command),
                entry["contract"],
            )
            self.assertEqual("git diff --check", commands[-1], entry["contract"])

    def test_registered_cargo_validation_commands_use_locked_resolution(self) -> None:
        for entry in CONTRACT_REGISTRY:
            for command in entry["commands"]:
                if command.startswith("cargo test "):
                    self.assertIn(" --locked ", f" {command} ", entry["contract"])

    def test_registered_contract_commands_stay_on_source_tree_validation_tools(self) -> None:
        allowed_prefixes = (
            "cargo test ",
            "$(PYTHON) .github/scripts/",
            "$(PYTHON) schemas/",
            "git diff --check",
        )

        for entry in CONTRACT_REGISTRY:
            for command in entry["commands"]:
                self.assertTrue(command.startswith(allowed_prefixes), f"{entry['contract']}: {command}")

    def test_contract_registry_matches_current_d_inventories(self) -> None:
        contracts = [entry["contract"] for entry in CONTRACT_REGISTRY]
        targets = registered_targets()

        self.assertEqual(len(contracts), len(set(contracts)))
        self.assertEqual(len(targets), len(set(targets)))

        for entry in CONTRACT_REGISTRY:
            inventory = load_json(entry["inventory"])
            self.assertEqual(1, inventory["schema_version"], entry["contract"])
            self.assertEqual(entry["contract"], inventory["contract"])
            self.assertEqual("source-only-pre-alpha", inventory["status"])
            self.assertEqual(entry["carrier"], inventory["carrier"])
            self.assertTrue((ROOT / entry["schema"]).is_file(), entry["contract"])

    def test_registered_contract_artifact_names_match_contract_names(self) -> None:
        for entry in CONTRACT_REGISTRY:
            kebab = contract_kebab(entry)

            self.assertEqual(f"milestone-d-{kebab}-contract", entry["target"], entry["contract"])
            self.assertEqual(f"docs/milestone-d-{kebab}-contract.md", entry["doc"], entry["contract"])
            self.assertEqual(f"schemas/ethos-{kebab}-contract.schema.json", entry["schema"], entry["contract"])
            self.assertEqual(f"{contract_name(entry)}_v1_contract.json", Path(entry["inventory"]).name, entry["contract"])

    def test_registered_contract_doc_titles_match_contract_names(self) -> None:
        for entry in CONTRACT_REGISTRY:
            self.assertEqual(
                f"# Milestone D `{contract_name(entry)}` v1 Contract",
                doc_title(entry["doc"]),
                entry["contract"],
            )

    def test_registered_contract_schema_identity_matches_registry(self) -> None:
        for entry in CONTRACT_REGISTRY:
            schema = load_json(entry["schema"])
            properties = schema["properties"]

            self.assertFalse(schema["additionalProperties"], entry["contract"])
            self.assertEqual(1, properties["schema_version"]["const"], entry["contract"])
            self.assertEqual(entry["contract"], properties["contract"]["const"], entry["contract"])
            self.assertEqual("source-only-pre-alpha", properties["status"]["const"], entry["contract"])
            self.assertEqual(entry["carrier"], properties["carrier"]["const"], entry["contract"])

    def test_registered_contract_schema_metadata_matches_registry(self) -> None:
        for entry in CONTRACT_REGISTRY:
            schema = load_json(entry["schema"])
            contract_title = entry["contract"].removesuffix(".v1") + " v1"

            self.assertEqual("https://json-schema.org/draft/2020-12/schema", schema["$schema"], entry["contract"])
            self.assertEqual(f"urn:ethos:schema:{schema_slug(entry)}:1", schema["$id"], entry["contract"])
            self.assertEqual(f"Ethos {contract_title} contract inventory", schema["title"], entry["contract"])
            self.assertIn("Source-only pre-alpha Milestone D inventory", schema["description"], entry["contract"])
            self.assertIn("validates inventory shape and vocabulary", schema["description"], entry["contract"])

    def test_registered_contract_schemas_require_identity_and_blockers(self) -> None:
        required_fields = {
            "schema_version",
            "contract",
            "status",
            "carrier",
            "explicit_blockers",
        }

        for entry in CONTRACT_REGISTRY:
            schema_required = set(load_json(entry["schema"])["required"])

            self.assertTrue(required_fields.issubset(schema_required), entry["contract"])

    def test_registered_contract_schema_objects_are_closed(self) -> None:
        for entry in CONTRACT_REGISTRY:
            for path, node in object_schema_nodes(load_json(entry["schema"])):
                self.assertEqual(False, node.get("additionalProperties"), f"{entry['contract']}: {path}")

    def test_contract_registry_covers_current_d_artifacts(self) -> None:
        self.assertEqual(registered_paths("doc"), discovered_d_contract_docs())
        self.assertEqual(registered_paths("schema"), discovered_d_contract_schemas())
        self.assertEqual(registered_paths("inventory"), discovered_d_contract_inventories())
        self.assertEqual(
            sorted(expected_contract_guard_script(entry) for entry in CONTRACT_REGISTRY),
            discovered_d_contract_guard_scripts(),
        )

    def test_registered_contract_inventories_are_schema_validated(self) -> None:
        registered_pairs = {
            (entry["schema"], entry["inventory"])
            for entry in CONTRACT_REGISTRY
        }
        registered_schemas = {entry["schema"] for entry in CONTRACT_REGISTRY}
        validated_contract_pairs = {
            pair
            for pair in schema_example_validation_pairs()
            if pair[0] in registered_schemas
        }

        self.assertEqual(registered_pairs, validated_contract_pairs)

    def test_registry_references_are_consistent(self) -> None:
        for entry in CONTRACT_REGISTRY:
            doc = (ROOT / entry["doc"]).read_text(encoding="utf-8")
            self.assertIn(Path(entry["inventory"]).name, doc, entry["contract"])
            self.assertIn(entry["target"], doc, entry["contract"])

    def test_registered_contracts_publish_focused_validation_commands(self) -> None:
        execution_status = EXECUTION_STATUS.read_text(encoding="utf-8")

        for entry in CONTRACT_REGISTRY:
            command = f"`{focused_validation_command(entry)}`"
            doc = (ROOT / entry["doc"]).read_text(encoding="utf-8")

            self.assertIn(command, doc, entry["contract"])
            self.assertIn(command, execution_status, entry["contract"])

    def test_registered_contracts_are_documented_in_status_surfaces(self) -> None:
        roadmap = ROADMAP.read_text(encoding="utf-8")
        execution_status = EXECUTION_STATUS.read_text(encoding="utf-8")
        schemas_readme = SCHEMAS_README.read_text(encoding="utf-8")

        for entry in CONTRACT_REGISTRY:
            self.assertIn(Path(entry["doc"]).name, roadmap, entry["contract"])
            self.assertIn(entry["doc"], execution_status, entry["contract"])
            self.assertIn(entry["doc"], schemas_readme, entry["contract"])
            self.assertIn(Path(entry["schema"]).name, schemas_readme, entry["contract"])
            self.assertIn(entry["inventory"], schemas_readme, entry["contract"])

    def test_execution_status_d_contract_bullets_match_registry(self) -> None:
        bullets = execution_status_d_contract_bullets()

        self.assertEqual(len(CONTRACT_REGISTRY), len(bullets))
        for entry, bullet in zip(CONTRACT_REGISTRY, bullets):
            self.assertIn(f"`{contract_name(entry)}`", bullet, entry["contract"])
            self.assertIn(f"`{entry['doc']}`", bullet, entry["contract"])
            self.assertIn(f"`{focused_validation_command(entry)}`", bullet, entry["contract"])

    def test_roadmap_milestone_d_row_lists_registered_contract_docs(self) -> None:
        row = roadmap_table_row("D")
        registered_docs = {Path(entry["doc"]).name for entry in CONTRACT_REGISTRY}
        row_contract_docs = set(re.findall(r"\((milestone-d-[^)]+-contract\.md)\)", row))

        self.assertEqual(registered_docs, row_contract_docs)

    def test_schemas_readme_contract_table_matches_registry(self) -> None:
        table_entries = schemas_readme_table_entries()

        for entry in CONTRACT_REGISTRY:
            schema_name = Path(entry["schema"]).name
            description = f"Milestone D `{contract_name(entry)}` v1 source-only contract inventory"

            self.assertEqual(description, table_entries.get(schema_name), entry["contract"])

    def test_schemas_readme_contract_table_rows_match_registry(self) -> None:
        expected_entries = {
            Path(entry["schema"]).name: f"Milestone D `{contract_name(entry)}` v1 source-only contract inventory"
            for entry in CONTRACT_REGISTRY
        }

        self.assertEqual(
            expected_entries,
            schemas_readme_contract_table_entries(),
        )

    def test_request_envelope_schemas_are_documented_and_validated(self) -> None:
        table_entries = schemas_readme_table_entries()
        validated_pairs = schema_example_validation_pairs()
        execution_status = EXECUTION_STATUS.read_text(encoding="utf-8")

        for envelope in D_REQUEST_ENVELOPES:
            schema_name = Path(envelope["schema"]).name

            self.assertTrue((ROOT / envelope["schema"]).is_file(), envelope["schema"])
            self.assertEqual(envelope["description"], table_entries.get(schema_name), envelope["schema"])
            for example in envelope["examples"]:
                self.assertTrue((ROOT / example).is_file(), example)
                self.assertIn((envelope["schema"], example), validated_pairs)
            for needle in envelope["status_needles"]:
                self.assertIn(needle, execution_status, envelope["schema"])

    def test_request_envelope_schema_inventory_covers_current_d_artifacts(self) -> None:
        self.assertEqual(
            sorted(envelope["schema"] for envelope in D_REQUEST_ENVELOPES),
            discovered_d_request_envelope_schemas(),
        )

    def test_request_envelope_schema_identity_matches_registry(self) -> None:
        for envelope in D_REQUEST_ENVELOPES:
            schema = load_json(envelope["schema"])
            envelope_slug = Path(envelope["schema"]).name.removeprefix("ethos-").removesuffix(".schema.json")
            contract_name = envelope_slug.removesuffix("-request").replace("-", "_")

            self.assertEqual("https://json-schema.org/draft/2020-12/schema", schema["$schema"], envelope["schema"])
            self.assertEqual(f"urn:ethos:schema:{envelope_slug}:1", schema["$id"], envelope["schema"])
            self.assertEqual(f"Ethos {contract_name} v1 request", schema["title"], envelope["schema"])
            self.assertEqual(
                f"ethos.{contract_name}_request.v1",
                schema["properties"]["artifact_type"]["const"],
                envelope["schema"],
            )
            self.assertTrue(
                {"artifact_type", "schema_version", "request_ref"}.issubset(schema["required"]),
                envelope["schema"],
            )

    def test_request_envelope_schema_objects_are_closed(self) -> None:
        for envelope in D_REQUEST_ENVELOPES:
            for path, node in object_schema_nodes(load_json(envelope["schema"])):
                self.assertEqual(False, node.get("additionalProperties"), f"{envelope['schema']}: {path}")

    def test_contract_docs_keep_common_public_language_boundary(self) -> None:
        required_text = [
            "Status: source-only pre-alpha contract work for internal Milestone D continuation.",
            "## Explicit Blockers For This Slice",
            "language remains limited to source-only pre-alpha internal continuation",
            "evidence grounding",
            "diagnostics",
            "fixture-backed validation",
            "explicit blockers",
        ]

        for entry in CONTRACT_REGISTRY:
            doc = (ROOT / entry["doc"]).read_text(encoding="utf-8")
            normalized_doc = " ".join(doc.split())
            for text in required_text:
                self.assertIn(" ".join(text.split()), normalized_doc, entry["contract"])

    def test_registered_contract_artifacts_avoid_out_of_scope_public_claim_terms(self) -> None:
        for entry in CONTRACT_REGISTRY:
            for path in [entry["doc"], entry["inventory"], entry["schema"]]:
                text = (ROOT / path).read_text(encoding="utf-8").lower()
                for term in OUT_OF_SCOPE_PUBLIC_CLAIM_TERMS:
                    self.assertNotIn(term, text, f"{entry['contract']}: {path}: {term}")

    def test_contract_inventories_keep_explicit_blockers_nonempty(self) -> None:
        for entry in CONTRACT_REGISTRY:
            blockers = load_json(entry["inventory"])["explicit_blockers"]

            self.assertGreater(len(blockers), 0, entry["contract"])
            self.assertEqual(len(blockers), len(set(blockers)), entry["contract"])
            for blocker in blockers:
                self.assertEqual(blocker.strip(), blocker, entry["contract"])
                self.assertNotEqual("", blocker, entry["contract"])

    def test_contract_inventories_keep_surface_expansion_explicitly_blocked(self) -> None:
        for entry in CONTRACT_REGISTRY:
            blockers_text = "\n".join(
                blocker.lower()
                for blocker in load_json(entry["inventory"])["explicit_blockers"]
            )

            self.assertTrue(
                COMMAND_EXPANSION_BLOCKER_PATTERN.search(blockers_text),
                entry["contract"],
            )
            self.assertTrue(
                SURFACE_EXPANSION_BLOCKER_PATTERN.search(blockers_text),
                entry["contract"],
            )

    def test_contract_inventory_named_collections_have_stable_unique_names(self) -> None:
        for entry in CONTRACT_REGISTRY:
            named_collections = inventory_named_collections(entry["inventory"])

            self.assertGreater(len(named_collections), 0, entry["contract"])
            for collection_name, names in named_collections:
                for name in names:
                    self.assertIsInstance(name, str, f"{entry['contract']}: {collection_name}")
                    self.assertEqual(name.strip(), name, f"{entry['contract']}: {collection_name}: {name}")
                    self.assertNotEqual("", name, f"{entry['contract']}: {collection_name}")
                self.assertEqual(len(names), len(set(names)), f"{entry['contract']}: {collection_name}")

    def test_contract_inventory_repo_path_references_exist(self) -> None:
        reference_count = 0
        for entry in CONTRACT_REGISTRY:
            references = inventory_repo_path_references(load_json(entry["inventory"]))
            reference_count += len(references)

            for pointer, repo_path in references:
                path = Path(repo_path)

                self.assertFalse(path.is_absolute(), f"{entry['contract']}: {pointer}: {repo_path}")
                self.assertNotIn("..", path.parts, f"{entry['contract']}: {pointer}: {repo_path}")
                self.assertTrue((ROOT / path).is_file(), f"{entry['contract']}: {pointer}: {repo_path}")

        self.assertGreater(reference_count, 0)

    def test_contract_docs_mirror_inventory_explicit_blockers(self) -> None:
        for entry in CONTRACT_REGISTRY:
            inventory = load_json(entry["inventory"])

            self.assertEqual(
                inventory["explicit_blockers"],
                doc_explicit_blockers(entry["doc"]),
                entry["contract"],
            )

    def test_execution_status_names_registry_guard(self) -> None:
        text = EXECUTION_STATUS.read_text(encoding="utf-8")

        self.assertIn("make milestone-d-internal-contracts", text)
        self.assertIn("command wiring and contract registry", text)

    def test_target_stays_internal_contract_scoped(self) -> None:
        block = target_block("milestone-d-internal-contracts")

        for out_of_scope in [
            "verify-alpha",
            "rag-chunk-alpha",
            "security-report-alpha",
            "verify-rendered-crops",
            "compare-rendered-crops",
            "layout-evaluator-alpha",
            "python-surface-test",
            "milestone-b-internal-checks",
            "milestone-c-internal-checks",
            "release-",
            "third-party-license-manifest",
            "npm",
            "mcp",
        ]:
            self.assertNotIn(out_of_scope, block)


if __name__ == "__main__":
    unittest.main()
