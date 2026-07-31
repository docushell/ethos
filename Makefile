ROOT := $(CURDIR)
PYTHON ?= python3
CARGO_DENY ?= cargo deny
CARGO_DENY_ADVISORY ?= $(CARGO_DENY)
ADVISORY_RUSTUP_TOOLCHAIN ?= stable
THIRD_PARTY_MANIFEST_OUT ?= $(ROOT)/target/release-third-party/cargo-third-party-licenses.json
RELEASE_NOTICE_OUT ?= $(ROOT)/target/release-notice-draft
RELEASE_ARTIFACT_NAME ?= ethos-cli-draft
ETHOS_BIN ?= $(ROOT)/target/debug/ethos
VERIFY_ALPHA_OUT ?= $(ROOT)/target/verify-alpha
VERIFY_RENDERED_CROPS_OUT ?= $(ROOT)/target/verify-rendered-crops
COMPARE_RENDERED_CROPS_LEFT ?= $(VERIFY_RENDERED_CROPS_OUT)/run1
COMPARE_RENDERED_CROPS_RIGHT ?= $(VERIFY_RENDERED_CROPS_OUT)/run2
LAYOUT_EVALUATOR_OUT ?= $(ROOT)/target/layout-evaluator-alpha

.PHONY: verify-alpha verify-alpha-tree rag-chunk-alpha security-report-alpha evidence-anchor-v1-contract citation-emission-v1-contract rag-framework-examples trust-benchmark-corpus ethos-full-candidate-contract windows-verify-candidate-contract ethos-verify-action-contract milestone-d-verify-citations-contract milestone-d-crop-element-contract milestone-d-sandbox-subprocess-contract v0-5-release-prep light-check package-publication-dry-run-smoke verify-rendered-crops compare-rendered-crops layout-evaluator-alpha python-surface-test release-hygiene release-advisory third-party-license-manifest release-notice-draft
.PHONY: milestone-d-capability-downgrade-contract
.PHONY: milestone-d-opendataloader-adapter-shape-contract
.PHONY: milestone-d-grounding-source-contract
.PHONY: milestone-d-crop-element-surface-shape-contract
.PHONY: milestone-d-claim-kind-boundary-contract
.PHONY: app-answer-release-contract app-answer-release-demo
.PHONY: frozen-record-guards release-state-check release-live-state-check registry-surface-check v0-5-performance-record v0-5-npm-b-activation-contract
.PHONY: validator-ceiling-check

$(ETHOS_BIN):
	cargo build --locked -p ethos-cli

verify-alpha-tree:
	cargo check --locked -p ethos-verify
	cargo check --locked -p ethos-grounding-opendataloader-json
	$(PYTHON) .github/scripts/check_verify_dependency_boundary.py

# Runs BOTH ceiling tests: the cheap `capabilities` all-false shape and the expensive
# spans + char_offsets shape. Release profile, because the ceiling describes that profile.
validator-ceiling-check:
	ETHOS_CHECK_VALIDATOR_CEILING=1 cargo test --locked --release -p ethos-doc-core ceiling

verify-alpha: $(ETHOS_BIN)
	cargo test --locked -p ethos-verify
	cargo test --locked -p ethos-grounding-opendataloader-json
	cargo test --locked -p ethos-cli --test verify
	$(MAKE) verify-alpha-tree
	$(PYTHON) schemas/validate_examples.py
	$(PYTHON) examples/verify/check_verify_alpha.py --repo-root $(ROOT) --ethos-bin $(ETHOS_BIN) --out-dir $(VERIFY_ALPHA_OUT)
	git diff --check

rag-chunk-alpha:
	cargo test --locked -p ethos-cli --test rag
	$(PYTHON) schemas/validate_examples.py
	$(PYTHON) .github/scripts/test_rag_chunk_alpha.py
	git diff --check

security-report-alpha:
	cargo test --locked -p ethos-cli --test security_report
	$(PYTHON) schemas/validate_examples.py
	$(PYTHON) schemas/test_security_report_validation.py
	$(PYTHON) .github/scripts/test_security_report_alpha.py
	git diff --check

evidence-anchor-v1-contract:
	cargo test --locked -p ethos-cli --test evidence_anchor
	cargo test --locked -p ethos-grounding-opendataloader-json
	$(PYTHON) schemas/validate_examples.py
	$(PYTHON) .github/scripts/test_execution_status.py
	$(PYTHON) .github/scripts/test_evidence_anchor_v1_contract.py
	git diff --check

citation-emission-v1-contract:
	cargo build --locked -p ethos-cli
	$(PYTHON) schemas/validate_examples.py
	$(PYTHON) .github/scripts/test_citation_emission_v1_contract.py
	git diff --check

rag-framework-examples:
	cargo build --locked -p ethos-cli
	$(PYTHON) .github/scripts/test_rag_framework_examples.py
	git diff --check

trust-benchmark-corpus: $(ETHOS_BIN)
	$(PYTHON) .github/scripts/test_trust_benchmark_corpus.py --ethos $(ETHOS_BIN)
	git diff --check

ethos-full-candidate-contract:
	$(PYTHON) .github/scripts/test_ethos_full_candidate.py

v0-5-performance-record:
	@test -n "$(V0_4_ETHOS_BIN)" && test -n "$(V0_5_ETHOS_BIN)" && test -n "$(V0_5_PERFORMANCE_OUT)" || (echo "set V0_4_ETHOS_BIN, V0_5_ETHOS_BIN, and V0_5_PERFORMANCE_OUT"; exit 2)
	$(PYTHON) scripts/measure-v0-5-performance.py --baseline-bin "$(V0_4_ETHOS_BIN)" --candidate-bin "$(V0_5_ETHOS_BIN)" --out "$(V0_5_PERFORMANCE_OUT)"
	$(PYTHON) scripts/validate-v0-5-performance.py --record "$(V0_5_PERFORMANCE_OUT)" --baseline-bin "$(V0_4_ETHOS_BIN)" --candidate-bin "$(V0_5_ETHOS_BIN)" --source schemas/examples/document.example.json --citations examples/verify/native_grounded_citations.json

v0-5-npm-b-activation-contract:
	$(PYTHON) .github/scripts/test_validate_npm_b_activation.py

windows-verify-candidate-contract:
	$(PYTHON) .github/scripts/test_windows_verify_candidate.py
	$(PYTHON) .github/scripts/test_release_artifact_workflow_prep.py
	$(PYTHON) .github/scripts/test_release_reproducibility_scaffold.py

ethos-verify-action-contract:
	$(PYTHON) -m unittest discover -s actions/verify/tests -p 'test_*.py'

app-answer-release-contract:
	cargo test --locked -p ethos-doc-core --no-default-features --features verify-types app_answer_release
	$(MAKE) python-surface-test PYTHON=$(PYTHON)
	$(PYTHON) schemas/validate_examples.py
	$(PYTHON) .github/scripts/test_app_answer_release_contract.py
	$(PYTHON) .github/scripts/test_app_answer_release_demo.py
	$(PYTHON) .github/scripts/claims_gate.py
	$(PYTHON) .github/scripts/public_boundary_claims_gate.py
	git diff --check

app-answer-release-demo:
	$(PYTHON) .github/scripts/test_app_answer_release_demo.py
	git diff --check

v0-5-release-prep:
	cargo build --locked --workspace
	cargo test --locked --workspace
	$(MAKE) verify-alpha PYTHON=$(PYTHON)
	$(MAKE) citation-emission-v1-contract PYTHON=$(PYTHON)
	$(MAKE) python-surface-test PYTHON=$(PYTHON)
	npm test --prefix packages/npm/ethos-pdf
	$(PYTHON) .github/scripts/test_build_release_cli_archive.py
	$(PYTHON) .github/scripts/test_release_artifact_workflow_prep.py
	$(PYTHON) .github/scripts/test_v0_5_0_version_activation.py
	$(MAKE) v0-5-npm-b-activation-contract PYTHON=$(PYTHON)
	$(PYTHON) scripts/test_measure_v0_5_performance.py
	$(MAKE) release-hygiene PYTHON=$(PYTHON)
	$(PYTHON) .github/scripts/claims_gate.py
	$(PYTHON) .github/scripts/public_boundary_claims_gate.py
	git diff --check

milestone-d-verify-citations-contract:
	cargo test --locked -p ethos-cli --test verify
	$(PYTHON) schemas/validate_examples.py
	$(PYTHON) .github/scripts/test_execution_status.py
	$(PYTHON) .github/scripts/test_milestone_d_verify_citations_contract.py
	git diff --check

milestone-d-claim-kind-boundary-contract:
	cargo test --locked -p ethos-verify claim_kind
	cargo test --locked -p ethos-cli --test verify invalid_config_constraints_are_usage_errors
	$(PYTHON) schemas/validate_examples.py
	$(PYTHON) .github/scripts/test_execution_status.py
	$(PYTHON) .github/scripts/test_milestone_d_claim_kind_boundary_contract.py
	git diff --check

.PHONY: milestone-d-internal-contracts
milestone-d-internal-contracts:
	$(MAKE) milestone-d-verify-citations-contract PYTHON=$(PYTHON)
	$(MAKE) milestone-d-claim-kind-boundary-contract PYTHON=$(PYTHON)
	$(MAKE) milestone-d-grounding-source-contract PYTHON=$(PYTHON)
	$(MAKE) milestone-d-opendataloader-adapter-shape-contract PYTHON=$(PYTHON)
	$(MAKE) milestone-d-capability-downgrade-contract PYTHON=$(PYTHON)
	$(MAKE) milestone-d-crop-element-contract PYTHON=$(PYTHON)
	$(MAKE) milestone-d-crop-element-surface-shape-contract PYTHON=$(PYTHON)
	$(MAKE) milestone-d-sandbox-subprocess-contract PYTHON=$(PYTHON)
	$(PYTHON) .github/scripts/test_public_surface_posture.py
	$(PYTHON) .github/scripts/claims_gate.py
	$(PYTHON) .github/scripts/test_milestone_d_internal_contracts.py
	git diff --check

milestone-d-grounding-source-contract:
	cargo test --locked -p ethos-doc-core grounding
	cargo test --locked -p ethos-cli --test verify native_ethos_verify_produces_non_empty_checks
	cargo test --locked -p ethos-cli --test verify opendataloader_verify_adapter_produces_capability_aware_report
	$(PYTHON) schemas/validate_examples.py
	$(PYTHON) .github/scripts/test_execution_status.py
	$(PYTHON) .github/scripts/test_milestone_d_grounding_source_contract.py
	git diff --check

milestone-d-crop-element-contract:
	cargo test --locked -p ethos-doc-core --features crop-element crop_element
	cargo test --locked -p ethos-cli --test verify native_verify_crop_dir_writes_deterministic_crop_descriptors
	cargo test --locked -p ethos-cli --test verify crop_element_cli
	$(PYTHON) schemas/validate_examples.py
	$(PYTHON) .github/scripts/test_execution_status.py
	$(PYTHON) .github/scripts/test_milestone_d_crop_element_contract.py
	git diff --check

milestone-d-crop-element-surface-shape-contract:
	$(MAKE) python-surface-test PYTHON=$(PYTHON)
	$(PYTHON) schemas/validate_examples.py
	$(PYTHON) .github/scripts/test_execution_status.py
	$(PYTHON) .github/scripts/test_milestone_d_crop_element_surface_shape_contract.py
	git diff --check

milestone-d-sandbox-subprocess-contract:
	cargo test --locked -p ethos-cli json_artifact_header
	cargo test --locked -p ethos-cli worker_pipe_limit
	cargo test --locked -p ethos-cli worker_error_envelope
	cargo test --locked -p ethos-cli --test pdf_parse worker
	$(PYTHON) schemas/validate_examples.py
	$(PYTHON) .github/scripts/test_execution_status.py
	$(PYTHON) .github/scripts/test_milestone_d_sandbox_subprocess_contract.py
	git diff --check

milestone-d-capability-downgrade-contract:
	cargo test --locked -p ethos-verify capability
	cargo test --locked -p ethos-cli --test verify capability
	$(PYTHON) schemas/validate_examples.py
	$(PYTHON) .github/scripts/test_execution_status.py
	$(PYTHON) .github/scripts/test_milestone_d_capability_downgrade_contract.py
	git diff --check

milestone-d-opendataloader-adapter-shape-contract:
	cargo test --locked -p ethos-grounding-opendataloader-json
	cargo test --locked -p ethos-cli --test verify opendataloader
	$(PYTHON) schemas/validate_examples.py
	$(PYTHON) .github/scripts/test_execution_status.py
	$(PYTHON) .github/scripts/test_milestone_d_opendataloader_adapter_shape_contract.py
	git diff --check

light-check:
	$(PYTHON) .github/scripts/claims_gate.py
	$(PYTHON) .github/scripts/public_boundary_claims_gate.py
	$(PYTHON) .github/scripts/test_package_registry_source_consistency.py
	$(PYTHON) .github/scripts/check_release_state.py --check
	$(PYTHON) .github/scripts/test_public_surface_posture.py
	$(PYTHON) .github/scripts/check_release_boundary_paths.py
	$(PYTHON) .github/scripts/check_golden_change_rationale.py
	$(PYTHON) .github/scripts/validation_record_integrity.py
	git diff --check

registry-surface-check:
	npm test --prefix packages/npm/ethos-pdf
	$(PYTHON) .github/scripts/test_package_registry_source_consistency.py
	$(PYTHON) .github/scripts/test_claims_gate_registry_surfaces.py
	$(PYTHON) .github/scripts/claims_gate.py
	$(PYTHON) .github/scripts/public_boundary_claims_gate.py

release-state-check:
	$(PYTHON) .github/scripts/test_release_state.py
	$(PYTHON) .github/scripts/test_github_release_metadata.py
	$(PYTHON) .github/scripts/check_release_state.py --check

release-live-state-check: release-state-check
	$(PYTHON) .github/scripts/check_github_release_metadata.py --repo docushell/ethos

frozen-record-guards:
	$(PYTHON) .github/scripts/test_run_frozen_record_guards.py
	$(PYTHON) .github/scripts/run_frozen_record_guards.py --python $(PYTHON)

package-publication-dry-run-smoke:
	cargo package --locked --offline -p ethos-doc-core --allow-dirty --no-verify
	cargo package --list --locked --offline -p ethos-doc-core --allow-dirty
	cargo check --locked --offline -p ethos-verify
	cargo check --locked --offline -p ethos-pdf
	git diff --check

verify-rendered-crops: $(ETHOS_BIN)
	$(PYTHON) examples/verify/check_rendered_crops.py --repo-root $(ROOT) --ethos-bin $(ETHOS_BIN) --out-dir $(VERIFY_RENDERED_CROPS_OUT)
	git diff --check

compare-rendered-crops:
	$(PYTHON) examples/verify/compare_rendered_crop_runs.py --left-run $(COMPARE_RENDERED_CROPS_LEFT) --right-run $(COMPARE_RENDERED_CROPS_RIGHT)

layout-evaluator-alpha:
	$(PYTHON) fixtures/evaluate_layout_alpha.py --out $(LAYOUT_EVALUATOR_OUT)/report.json
	$(PYTHON) fixtures/test_evaluate_layout_alpha.py

python-surface-test:
	PYTHONPATH=$(ROOT)/python $(PYTHON) -m unittest discover -s python/tests

release-hygiene:
	cargo metadata --locked --offline --format-version 1 --no-deps >/dev/null
	$(CARGO_DENY) --version
	$(CARGO_DENY) check licenses bans sources
	git diff --check

release-advisory:
	cargo +$(ADVISORY_RUSTUP_TOOLCHAIN) metadata --locked --offline --format-version 1 --no-deps >/dev/null
	RUSTUP_TOOLCHAIN=$(ADVISORY_RUSTUP_TOOLCHAIN) $(CARGO_DENY_ADVISORY) --version
	RUSTUP_TOOLCHAIN=$(ADVISORY_RUSTUP_TOOLCHAIN) $(CARGO_DENY_ADVISORY) check
	git diff --check

third-party-license-manifest:
	$(PYTHON) .github/scripts/generate_third_party_manifest.py --out $(THIRD_PARTY_MANIFEST_OUT)

release-notice-draft:
	$(MAKE) third-party-license-manifest THIRD_PARTY_MANIFEST_OUT=$(THIRD_PARTY_MANIFEST_OUT)
	$(PYTHON) .github/scripts/generate_release_notice_bundle.py --cargo-manifest $(THIRD_PARTY_MANIFEST_OUT) --out-dir $(RELEASE_NOTICE_OUT) --artifact-name $(RELEASE_ARTIFACT_NAME)
