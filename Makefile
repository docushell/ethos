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

.PHONY: verify-alpha verify-alpha-tree rag-chunk-alpha security-report-alpha milestone-d-verify-citations-contract milestone-d-crop-element-contract milestone-d-sandbox-subprocess-contract milestone-d-internal-contracts milestone-e-prep verify-rendered-crops compare-rendered-crops layout-evaluator-alpha python-surface-test milestone-b-internal-checks milestone-c-internal-checks release-hygiene release-advisory third-party-license-manifest release-notice-draft
.PHONY: milestone-d-capability-downgrade-contract
.PHONY: milestone-d-opendataloader-adapter-shape-contract
.PHONY: milestone-d-grounding-source-contract
.PHONY: milestone-d-crop-element-surface-shape-contract
.PHONY: milestone-d-claim-kind-boundary-contract

$(ETHOS_BIN):
	cargo build --locked -p ethos-cli

verify-alpha-tree:
	@tree="$$(cargo tree -p ethos-verify -e normal)"; \
	printf '%s\n' "$$tree"; \
	if printf '%s\n' "$$tree" | grep -qiE 'ethos-pdf|ethos-layout|ethos-tables|ethos-render|pdfium'; then \
		echo "ethos-verify depends on parser internals"; exit 1; \
	fi

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

milestone-d-verify-citations-contract:
	cargo test --locked -p ethos-cli --test verify
	$(PYTHON) schemas/validate_examples.py
	$(PYTHON) .github/scripts/test_execution_status.py
	$(PYTHON) .github/scripts/test_roadmap_status.py
	$(PYTHON) .github/scripts/test_milestone_d_verify_citations_contract.py
	git diff --check

milestone-d-claim-kind-boundary-contract:
	cargo test --locked -p ethos-verify claim_kind
	cargo test --locked -p ethos-cli --test verify invalid_config_constraints_are_usage_errors
	$(PYTHON) schemas/validate_examples.py
	$(PYTHON) .github/scripts/test_execution_status.py
	$(PYTHON) .github/scripts/test_roadmap_status.py
	$(PYTHON) .github/scripts/test_milestone_d_claim_kind_boundary_contract.py
	git diff --check

milestone-d-grounding-source-contract:
	cargo test --locked -p ethos-core grounding
	cargo test --locked -p ethos-cli --test verify native_ethos_verify_produces_non_empty_checks
	cargo test --locked -p ethos-cli --test verify opendataloader_verify_adapter_produces_capability_aware_report
	$(PYTHON) schemas/validate_examples.py
	$(PYTHON) .github/scripts/test_execution_status.py
	$(PYTHON) .github/scripts/test_roadmap_status.py
	$(PYTHON) .github/scripts/test_milestone_d_grounding_source_contract.py
	git diff --check

milestone-d-crop-element-contract:
	cargo test --locked -p ethos-core crop_element
	cargo test --locked -p ethos-cli --test verify native_verify_crop_dir_writes_deterministic_crop_descriptors
	cargo test --locked -p ethos-cli --test verify crop_element_cli
	$(PYTHON) schemas/validate_examples.py
	$(PYTHON) .github/scripts/test_execution_status.py
	$(PYTHON) .github/scripts/test_roadmap_status.py
	$(PYTHON) .github/scripts/test_milestone_d_crop_element_contract.py
	git diff --check

milestone-d-crop-element-surface-shape-contract:
	$(MAKE) python-surface-test PYTHON=$(PYTHON)
	$(PYTHON) schemas/validate_examples.py
	$(PYTHON) .github/scripts/test_execution_status.py
	$(PYTHON) .github/scripts/test_roadmap_status.py
	$(PYTHON) .github/scripts/test_milestone_d_crop_element_surface_shape_contract.py
	git diff --check

milestone-d-sandbox-subprocess-contract:
	cargo test --locked -p ethos-cli json_artifact_header
	cargo test --locked -p ethos-cli worker_pipe_limit
	cargo test --locked -p ethos-cli worker_error_envelope
	cargo test --locked -p ethos-cli --test pdf_parse worker
	$(PYTHON) schemas/validate_examples.py
	$(PYTHON) .github/scripts/test_execution_status.py
	$(PYTHON) .github/scripts/test_roadmap_status.py
	$(PYTHON) .github/scripts/test_milestone_d_sandbox_subprocess_contract.py
	git diff --check

milestone-d-capability-downgrade-contract:
	cargo test --locked -p ethos-verify capability
	cargo test --locked -p ethos-cli --test verify capability
	$(PYTHON) schemas/validate_examples.py
	$(PYTHON) .github/scripts/test_execution_status.py
	$(PYTHON) .github/scripts/test_roadmap_status.py
	$(PYTHON) .github/scripts/test_milestone_d_capability_downgrade_contract.py
	git diff --check

milestone-d-opendataloader-adapter-shape-contract:
	cargo test --locked -p ethos-grounding-opendataloader-json
	cargo test --locked -p ethos-cli --test verify opendataloader
	$(PYTHON) schemas/validate_examples.py
	$(PYTHON) .github/scripts/test_execution_status.py
	$(PYTHON) .github/scripts/test_roadmap_status.py
	$(PYTHON) .github/scripts/test_milestone_d_opendataloader_adapter_shape_contract.py
	git diff --check

milestone-d-internal-contracts:
	$(MAKE) milestone-d-verify-citations-contract PYTHON=$(PYTHON)
	$(MAKE) milestone-d-claim-kind-boundary-contract PYTHON=$(PYTHON)
	$(MAKE) milestone-d-grounding-source-contract PYTHON=$(PYTHON)
	$(MAKE) milestone-d-opendataloader-adapter-shape-contract PYTHON=$(PYTHON)
	$(MAKE) milestone-d-capability-downgrade-contract PYTHON=$(PYTHON)
	$(MAKE) milestone-d-crop-element-contract PYTHON=$(PYTHON)
	$(MAKE) milestone-d-crop-element-surface-shape-contract PYTHON=$(PYTHON)
	$(MAKE) milestone-d-sandbox-subprocess-contract PYTHON=$(PYTHON)
	$(PYTHON) .github/scripts/test_milestone_d_closeout_prep_record.py
	$(PYTHON) .github/scripts/test_milestone_d_closeout_record.py
	$(PYTHON) .github/scripts/test_milestone_d_final_closeout_record.py
	$(PYTHON) .github/scripts/test_public_surface_posture.py
	$(PYTHON) .github/scripts/claims_gate.py
	$(PYTHON) .github/scripts/test_milestone_d_internal_contracts.py
	git diff --check

milestone-e-prep:
	$(PYTHON) .github/scripts/test_execution_status.py
	$(PYTHON) .github/scripts/test_roadmap_status.py
	$(PYTHON) .github/scripts/test_public_surface_posture.py
	$(PYTHON) .github/scripts/claims_gate.py
	$(PYTHON) schemas/validate_examples.py
	$(PYTHON) .github/scripts/test_milestone_e_schema_registry_alignment.py
	$(PYTHON) .github/scripts/test_milestone_e_public_boundary_alignment.py
	$(PYTHON) .github/scripts/test_milestone_e_blocked_output_alignment.py
	$(PYTHON) .github/scripts/test_milestone_e_evidence_lane_alignment.py
	$(PYTHON) .github/scripts/test_milestone_e_prep_scope.py
	$(PYTHON) .github/scripts/test_milestone_e_fixture_promotion_criteria.py
	$(PYTHON) .github/scripts/test_milestone_e_fixture_candidate_blocker_alignment_validation_record.py
	$(PYTHON) .github/scripts/test_milestone_e_prep_scope_structured_blocker_validation_record.py
	$(PYTHON) .github/scripts/test_milestone_e_internal_trust_loop_walkthrough.py
	$(PYTHON) .github/scripts/test_milestone_e_internal_trust_loop_use_protocol.py
	$(PYTHON) .github/scripts/test_milestone_e_internal_trust_loop_rehearsal_evidence_matrix.py
	$(PYTHON) .github/scripts/test_milestone_e_internal_trust_loop_blocker_ledger.py
	$(PYTHON) .github/scripts/test_milestone_e_fixture_promotion_criteria_validation_record.py
	$(PYTHON) .github/scripts/test_milestone_e_internal_trust_loop_walkthrough_validation_record.py
	$(PYTHON) .github/scripts/test_milestone_e_internal_trust_loop_use_protocol_validation_record.py
	$(PYTHON) .github/scripts/test_milestone_e_internal_trust_loop_rehearsal_evidence_matrix_validation_record.py
	$(PYTHON) .github/scripts/test_milestone_e_internal_trust_loop_blocker_ledger_validation_record.py
	$(PYTHON) .github/scripts/test_milestone_e_native_grounding_baseline_rehearsal_validation_record.py
	$(PYTHON) .github/scripts/test_milestone_e_diagnostic_boundary_check_rehearsal_validation_record.py
	$(PYTHON) .github/scripts/test_milestone_e_capability_downgrade_boundary_rehearsal_validation_record.py
	$(PYTHON) .github/scripts/test_milestone_e_opendataloader_adapter_grounding_rehearsal_validation_record.py
	$(PYTHON) .github/scripts/test_milestone_e_pinned_opendataloader_fixture_path_rehearsal_validation_record.py
	$(PYTHON) .github/scripts/test_milestone_e_crop_descriptor_source_bound_shape_rehearsal_validation_record.py
	$(PYTHON) .github/scripts/test_milestone_e_rag_chunk_artifact_loop_rehearsal_validation_record.py
	$(PYTHON) .github/scripts/test_milestone_e_security_report_artifact_loop_rehearsal_validation_record.py
	$(PYTHON) .github/scripts/test_milestone_e_demo_narrative_index_rehearsal_validation_record.py
	$(PYTHON) .github/scripts/test_milestone_e_rehearsal_row_record_coverage_validation.py
	$(PYTHON) .github/scripts/test_milestone_e_schema_registry_alignment_validation_record.py
	$(PYTHON) .github/scripts/test_milestone_e_public_boundary_alignment_validation_record.py
	$(PYTHON) .github/scripts/test_milestone_e_blocked_output_alignment_validation_record.py
	$(PYTHON) .github/scripts/test_milestone_e_evidence_lane_alignment_validation_record.py
	$(PYTHON) .github/scripts/test_milestone_e_validation_command_index.py
	$(PYTHON) .github/scripts/test_milestone_e_validation_command_index_validation_record.py
	$(PYTHON) .github/scripts/test_milestone_e_validation_record_index.py
	$(PYTHON) .github/scripts/test_milestone_e_validation_record_index_validation_record.py
	$(PYTHON) .github/scripts/test_milestone_e_prep_guard_sequence_index.py
	$(PYTHON) .github/scripts/test_milestone_e_prep_guard_sequence_index_validation_record.py
	$(PYTHON) .github/scripts/test_milestone_e_prep_validation_record.py
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

milestone-b-internal-checks:
	$(PYTHON) fixtures/validate_fixtures.py
	$(PYTHON) fixtures/test_validate_fixtures.py
	$(PYTHON) schemas/test_font_policy_validation.py
	$(PYTHON) schemas/test_security_report_validation.py
	$(PYTHON) .github/scripts/test_execution_status.py
	$(PYTHON) .github/scripts/test_roadmap_status.py
	$(PYTHON) .github/scripts/test_milestone_b_closeout_record.py
	$(PYTHON) .github/scripts/test_milestone_b_exit_checklist.py
	$(MAKE) verify-alpha PYTHON=$(PYTHON)
	$(MAKE) layout-evaluator-alpha PYTHON=$(PYTHON)
	$(MAKE) python-surface-test PYTHON=$(PYTHON)
	$(PYTHON) .github/scripts/claims_gate.py
	$(PYTHON) .github/scripts/readiness_gate.py public
	git diff --check

milestone-c-internal-checks:
	$(MAKE) rag-chunk-alpha PYTHON=$(PYTHON)
	$(MAKE) security-report-alpha PYTHON=$(PYTHON)
	$(PYTHON) .github/scripts/test_milestone_c_closeout_record.py
	$(PYTHON) .github/scripts/test_milestone_c_internal_checks.py
	git diff --check

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
