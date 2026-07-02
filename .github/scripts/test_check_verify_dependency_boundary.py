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

import copy
import importlib.util
import unittest
from pathlib import Path
from unittest import mock

from makefile_guard import target_block


SCRIPT = Path(__file__).with_name("check_verify_dependency_boundary.py")
SPEC = importlib.util.spec_from_file_location("check_verify_dependency_boundary", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


def dependency(
    name: str,
    *,
    kind: str | None = None,
    rename: str | None = None,
    features: list[str] | None = None,
    uses_default_features: bool = True,
) -> dict[str, object]:
    return {
        "name": name,
        "kind": kind,
        "rename": rename,
        "features": features or [],
        "uses_default_features": uses_default_features,
        "optional": False,
        "target": None,
    }


def valid_package() -> dict[str, object]:
    return {
        "name": "ethos-verify",
        "dependencies": [
            dependency(
                "ethos-doc-core",
                rename="ethos-core",
                features=["grounding", "verify-types"],
                uses_default_features=False,
            ),
            dependency("serde", features=["derive"]),
            dependency("sha2"),
            dependency("serde_json", kind="dev"),
        ],
    }


class VerifyDependencyBoundaryTests(unittest.TestCase):
    def test_accepts_the_exact_parser_neutral_policy(self) -> None:
        self.assertEqual(CHECK.boundary_errors(valid_package()), [])

    def test_rejects_an_extra_normal_dependency(self) -> None:
        package = valid_package()
        package["dependencies"].append(dependency("ethos-pdf"))

        self.assertIn(
            "unexpected normal dependencies: ethos-pdf",
            CHECK.boundary_errors(package),
        )

    def test_rejects_an_empty_normal_dependency_set(self) -> None:
        package = valid_package()
        package["dependencies"] = [dependency("serde_json", kind="dev")]

        self.assertEqual(
            CHECK.boundary_errors(package),
            ["missing normal dependencies: ethos-doc-core, serde, sha2"],
        )

    def test_rejects_a_duplicate_normal_dependency(self) -> None:
        package = valid_package()
        package["dependencies"].append(dependency("serde"))

        self.assertIn("duplicate normal dependencies: serde", CHECK.boundary_errors(package))

    def test_ignores_dev_dependencies_for_the_normal_dependency_policy(self) -> None:
        package = valid_package()
        package["dependencies"].append(dependency("ethos-pdf", kind="dev"))

        self.assertEqual(CHECK.boundary_errors(package), [])

    def test_rejects_missing_or_extra_ethos_core_features(self) -> None:
        for features in (["grounding"], ["grounding", "verify-types", "full"]):
            with self.subTest(features=features):
                package = copy.deepcopy(valid_package())
                package["dependencies"][0]["features"] = features

                errors = CHECK.boundary_errors(package)

                self.assertTrue(
                    any("ethos-core features must be exactly" in error for error in errors),
                    errors,
                )

    def test_rejects_ethos_core_default_features(self) -> None:
        package = valid_package()
        package["dependencies"][0]["uses_default_features"] = True

        self.assertIn(
            "ethos-core default features must be disabled",
            CHECK.boundary_errors(package),
        )

    def test_rejects_wrong_ethos_core_binding_shape(self) -> None:
        mutations = {
            "rename": None,
            "optional": True,
            "target": "cfg(unix)",
        }
        expected_errors = {
            "rename": "ethos-doc-core must be imported as ethos-core",
            "optional": "ethos-core must be a required dependency",
            "target": "ethos-core must not be target-specific",
        }
        for field, value in mutations.items():
            with self.subTest(field=field):
                package = copy.deepcopy(valid_package())
                package["dependencies"][0][field] = value

                self.assertIn(expected_errors[field], CHECK.boundary_errors(package))

    def test_missing_cargo_has_a_concise_actionable_error(self) -> None:
        with mock.patch.object(
            CHECK.subprocess,
            "run",
            side_effect=FileNotFoundError("cargo"),
        ):
            with self.assertRaisesRegex(
                SystemExit,
                "cargo is required to check the ethos-verify dependency boundary",
            ):
                CHECK.load_metadata()

    def test_light_check_stays_toolchain_free_while_verify_target_enforces_policy(self) -> None:
        policy_command = "$(PYTHON) .github/scripts/check_verify_dependency_boundary.py"

        self.assertNotIn(policy_command, target_block("light-check"))
        self.assertIn(policy_command, target_block("verify-alpha-tree"))


if __name__ == "__main__":
    unittest.main()
