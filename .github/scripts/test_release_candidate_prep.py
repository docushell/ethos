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

import unittest

from makefile_guard import target_block


EXPECTED_COMMANDS = (
    "$(MAKE) light-check PYTHON=$(PYTHON)",
    "$(PYTHON) .github/scripts/test_public_surface_posture.py",
    "$(PYTHON) .github/scripts/claims_gate.py",
    "$(PYTHON) schemas/validate_examples.py",
    "$(PYTHON) .github/scripts/test_first_public_release_scope_decision.py",
    "$(PYTHON) .github/scripts/test_python_public_api_policy.py",
    "$(MAKE) python-surface-test PYTHON=$(PYTHON)",
    "$(PYTHON) .github/scripts/test_npm_binary_package_scaffold.py",
    "npm test --prefix packages/npm/ethos-pdf",
    "$(PYTHON) .github/scripts/test_npm_vendor_binary_payload_strategy.py",
    "$(PYTHON) .github/scripts/test_npm_tarball_candidate_evidence.py",
    "$(PYTHON) .github/scripts/test_npm_publication_final_approval_request.py",
    "$(PYTHON) .github/scripts/test_npm_publication_final_approval_decision.py",
    "$(PYTHON) .github/scripts/test_npm_publication_closeout.py",
    "$(PYTHON) .github/scripts/test_pdfium_manual_setup_contract.py",
    "$(PYTHON) .github/scripts/test_release_artifact_workflow_prep.py",
    "$(PYTHON) .github/scripts/test_release_candidate_prep.py",
    "$(PYTHON) .github/scripts/test_release_reproducibility_scaffold.py",
    "$(PYTHON) .github/scripts/test_launch_copy_approval_scaffold.py",
    "$(PYTHON) .github/scripts/test_first_public_release_artifact_evidence.py",
    "$(PYTHON) .github/scripts/test_first_public_release_final_decider.py",
    "$(PYTHON) .github/scripts/test_first_public_release_linux_x64_artifact_evidence.py",
    "$(PYTHON) .github/scripts/test_first_public_release_linux_x64_final_decider.py",
    "$(PYTHON) .github/scripts/test_first_public_release_linux_x64_publication_closeout.py",
    "cargo test --locked -p ethos-cli --test verify invalid_config_constraints_are_usage_errors",
    "git diff --check",
)


class ReleaseCandidatePrepTargetTests(unittest.TestCase):
    def test_release_candidate_target_runs_exact_guard_sequence(self) -> None:
        block = target_block("release-candidate-prep")
        commands = [line.strip() for line in block.splitlines() if line.strip()]

        self.assertEqual(list(EXPECTED_COMMANDS), commands)

    def test_target_keeps_publication_out_of_release_candidate_prep(self) -> None:
        block = target_block("release-candidate-prep")

        self.assertNotIn("gh release create", block)
        self.assertNotIn("npm publish", block)
        self.assertNotIn("twine upload", block)
        self.assertNotIn("pypa/gh-action-pypi-publish", block)


if __name__ == "__main__":
    unittest.main()
