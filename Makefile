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

.PHONY: verify-alpha verify-alpha-tree rag-chunk-alpha security-report-alpha evidence-anchor-v1-contract milestone-d-verify-citations-contract milestone-d-crop-element-contract milestone-d-sandbox-subprocess-contract milestone-d-internal-contracts milestone-e-prep release-candidate-prep light-check package-publication-dry-run-smoke verify-rendered-crops compare-rendered-crops layout-evaluator-alpha python-surface-test milestone-b-internal-checks milestone-c-internal-checks release-hygiene release-advisory third-party-license-manifest release-notice-draft
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

evidence-anchor-v1-contract:
	cargo test --locked -p ethos-cli --test evidence_anchor
	cargo test --locked -p ethos-grounding-opendataloader-json
	$(PYTHON) schemas/validate_examples.py
	$(PYTHON) .github/scripts/test_execution_status.py
	$(PYTHON) .github/scripts/test_roadmap_status.py
	$(PYTHON) .github/scripts/test_evidence_anchor_v1_contract.py
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
	cargo test --locked -p ethos-doc-core grounding
	cargo test --locked -p ethos-cli --test verify native_ethos_verify_produces_non_empty_checks
	cargo test --locked -p ethos-cli --test verify opendataloader_verify_adapter_produces_capability_aware_report
	$(PYTHON) schemas/validate_examples.py
	$(PYTHON) .github/scripts/test_execution_status.py
	$(PYTHON) .github/scripts/test_roadmap_status.py
	$(PYTHON) .github/scripts/test_milestone_d_grounding_source_contract.py
	git diff --check

milestone-d-crop-element-contract:
	cargo test --locked -p ethos-doc-core --features crop-element crop_element
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

light-check:
	$(PYTHON) .github/scripts/claims_gate.py
	$(PYTHON) .github/scripts/public_boundary_claims_gate.py
	$(PYTHON) .github/scripts/test_public_surface_posture.py
	$(PYTHON) .github/scripts/check_release_boundary_paths.py
	$(PYTHON) .github/scripts/check_golden_change_rationale.py
	$(PYTHON) .github/scripts/validation_record_integrity.py
	git diff --check

milestone-e-prep:
	$(MAKE) light-check PYTHON=$(PYTHON)
	$(PYTHON) .github/scripts/test_execution_status.py
	$(PYTHON) .github/scripts/test_roadmap_status.py
	$(PYTHON) .github/scripts/test_public_surface_posture.py
	$(PYTHON) .github/scripts/claims_gate.py
	$(PYTHON) .github/scripts/test_public_prealpha_wording_approval.py
	$(PYTHON) .github/scripts/test_release_readiness_next_steps_approval.py
	$(PYTHON) .github/scripts/test_h1_public_safe_comparison_closeout.py
	$(PYTHON) .github/scripts/test_h2_source_snapshot_scope_approval.py
	$(PYTHON) .github/scripts/test_milestone_e_source_snapshot_candidate_audit.py
	$(PYTHON) .github/scripts/test_h2_source_snapshot_candidate_evidence.py
	$(PYTHON) .github/scripts/test_h2_source_snapshot_closeout.py
	$(PYTHON) schemas/validate_examples.py
	$(PYTHON) .github/scripts/test_milestone_e_schema_registry_alignment.py
	$(PYTHON) .github/scripts/test_milestone_e_public_boundary_alignment.py
	$(PYTHON) .github/scripts/test_milestone_e_blocked_output_alignment.py
	$(PYTHON) .github/scripts/test_milestone_e_evidence_lane_alignment.py
	$(PYTHON) .github/scripts/test_milestone_e_diagnostic_boundary_alignment.py
	$(PYTHON) .github/scripts/test_milestone_e_promotion_status_alignment.py
	$(PYTHON) .github/scripts/test_milestone_e_source_status_alignment.py
	$(PYTHON) .github/scripts/test_milestone_e_applies_to_binding_alignment.py
	$(PYTHON) .github/scripts/test_milestone_e_required_before_alignment.py
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
	$(PYTHON) .github/scripts/test_milestone_e_diagnostic_boundary_alignment_validation_record.py
	$(PYTHON) .github/scripts/test_milestone_e_promotion_status_alignment_validation_record.py
	$(PYTHON) .github/scripts/test_milestone_e_source_status_alignment_validation_record.py
	$(PYTHON) .github/scripts/test_milestone_e_applies_to_binding_alignment_validation_record.py
	$(PYTHON) .github/scripts/test_milestone_e_required_before_alignment_validation_record.py
	$(PYTHON) .github/scripts/test_milestone_e_public_approval_lane_blockers.py
	$(PYTHON) .github/scripts/test_milestone_e_public_approval_lane_blockers_validation_record.py
	$(PYTHON) .github/scripts/test_milestone_e_public_beta_approval_prep.py
	$(PYTHON) .github/scripts/test_milestone_e_public_beta_approval_prep_validation_record.py
	$(PYTHON) .github/scripts/test_milestone_e_public_beta_required_evidence_records.py
	$(PYTHON) .github/scripts/test_milestone_e_public_beta_source_only_approval.py
	$(PYTHON) .github/scripts/test_milestone_e_package_publication_approval_prep.py
	$(PYTHON) .github/scripts/test_milestone_e_package_publication_approval_prep_validation_record.py
	$(PYTHON) .github/scripts/test_milestone_e_package_publication_prep_approval_validation_record.py
	$(PYTHON) .github/scripts/test_milestone_e_package_publication_evidence_records.py
	$(PYTHON) .github/scripts/test_milestone_e_package_publication_metadata_readiness.py
	$(PYTHON) .github/scripts/test_milestone_e_package_publication_dry_run_smoke.py
	$(PYTHON) .github/scripts/test_milestone_e_package_publication_version_tag_policy.py
	$(PYTHON) .github/scripts/test_milestone_e_package_publication_pdfium_boundary.py
	$(PYTHON) .github/scripts/test_milestone_e_package_publication_dependency_ordering.py
	$(PYTHON) .github/scripts/test_milestone_e_package_publication_manifest_migration_prep.py
	$(PYTHON) .github/scripts/test_milestone_e_package_publication_registry_assembly_prep.py
	$(PYTHON) .github/scripts/test_milestone_e_package_publication_real_version_selection_prep.py
	$(PYTHON) .github/scripts/test_milestone_e_package_publication_tag_creation_prep.py
	$(PYTHON) .github/scripts/test_milestone_e_package_publication_manifest_activation_prep.py
	$(PYTHON) .github/scripts/test_milestone_e_package_publication_registry_assembly_activation_prep.py
	$(PYTHON) .github/scripts/test_milestone_e_package_publication_decision_bundle_validation_record.py
	$(PYTHON) .github/scripts/test_milestone_e_package_publication_pre_approval_gap_ledger.py
	$(PYTHON) .github/scripts/test_milestone_e_package_publication_approval_resolution_plan.py
	$(PYTHON) .github/scripts/test_milestone_e_package_publication_decision_input_packet.py
	$(PYTHON) .github/scripts/test_milestone_e_package_publication_approval_readiness_review.py
	$(PYTHON) .github/scripts/test_milestone_e_package_publication_manifest_activation_diff_review.py
	$(PYTHON) .github/scripts/test_milestone_e_package_publication_registry_assembly_evidence_review.py
	$(PYTHON) .github/scripts/test_milestone_e_package_publication_public_installation_wording_review.py
	$(PYTHON) .github/scripts/test_milestone_e_package_publication_approval_decision_template.py
	$(PYTHON) .github/scripts/test_milestone_e_package_publication_approval_decision_record.py
	$(PYTHON) .github/scripts/test_milestone_e_package_publication_candidate_activation_evidence.py
	$(PYTHON) .github/scripts/test_milestone_e_package_publication_approval_decision_refresh.py
	$(PYTHON) .github/scripts/test_milestone_e_package_publication_manifest_activation_applied.py
	$(PYTHON) .github/scripts/test_milestone_e_package_publication_current_registry_assembly.py
	$(PYTHON) .github/scripts/test_milestone_e_package_publication_final_approval_request.py
	$(PYTHON) .github/scripts/test_milestone_e_package_publication_final_approval_decision.py
	$(PYTHON) .github/scripts/test_milestone_e_package_publication_activation_request.py
	$(PYTHON) .github/scripts/test_milestone_e_package_publication_activation_applied.py
	$(PYTHON) .github/scripts/test_milestone_e_package_publication_tag_binding_refresh.py
	$(PYTHON) .github/scripts/test_milestone_e_package_publication_operator_preflight.py
	$(PYTHON) .github/scripts/test_milestone_e_package_publication_manual_registry_evidence_request.py
	$(PYTHON) .github/scripts/test_milestone_e_package_publication_manual_registry_evidence_supplied.py
	$(PYTHON) .github/scripts/test_milestone_e_package_publication_registry_action_authorization_request.py
	$(PYTHON) .github/scripts/test_milestone_e_package_publication_registry_action_approval.py
	$(PYTHON) .github/scripts/test_milestone_e_package_publication_registry_action_evidence.py
	$(PYTHON) .github/scripts/test_milestone_e_package_publication_dependent_registry_action_approval.py
	$(PYTHON) .github/scripts/test_milestone_e_package_publication_dependent_registry_action_evidence.py
	$(PYTHON) .github/scripts/test_milestone_e_package_publication_public_installation_availability.py
	$(PYTHON) .github/scripts/test_milestone_e_public_facing_readiness_ledger.py
	$(PYTHON) .github/scripts/test_milestone_e_public_beta_current_main_refresh_prep.py
	$(PYTHON) .github/scripts/test_milestone_e_public_beta_current_main_source_only_approval.py
	$(PYTHON) .github/scripts/test_milestone_e_public_evaluation_current_state_closeout.py
	$(PYTHON) .github/scripts/test_milestone_e_prep_validation_record.py
	$(PYTHON) .github/scripts/test_milestone_e_final_closeout_record.py
	git diff --check

release-candidate-prep:
	$(MAKE) light-check PYTHON=$(PYTHON)
	$(PYTHON) .github/scripts/test_public_surface_posture.py
	$(PYTHON) .github/scripts/claims_gate.py
	$(PYTHON) schemas/validate_examples.py
	$(PYTHON) .github/scripts/test_first_public_release_scope_decision.py
	$(PYTHON) .github/scripts/test_python_public_api_policy.py
	$(MAKE) python-surface-test PYTHON=$(PYTHON)
	$(PYTHON) .github/scripts/test_patch_0_1_1_python_publication_approval_request.py
	$(PYTHON) .github/scripts/test_patch_0_1_1_python_publication_approval_decision.py
	$(PYTHON) .github/scripts/test_patch_0_1_1_python_wheel_reproducibility_blocker.py
	$(PYTHON) .github/scripts/test_patch_0_1_1_python_deterministic_wheel_approval_request.py
	$(PYTHON) .github/scripts/test_patch_0_1_1_python_deterministic_wheel_approval_decision.py
	$(PYTHON) .github/scripts/test_patch_0_1_1_python_publication_closeout.py
	$(PYTHON) .github/scripts/test_patch_0_1_1_public_install_wording_closeout.py
	$(PYTHON) .github/scripts/test_npm_binary_package_scaffold.py
	npm test --prefix packages/npm/ethos-pdf
	$(PYTHON) .github/scripts/test_npm_vendor_binary_payload_strategy.py
	$(PYTHON) .github/scripts/test_npm_tarball_candidate_evidence.py
	$(PYTHON) .github/scripts/test_npm_publication_final_approval_request.py
	$(PYTHON) .github/scripts/test_npm_publication_final_approval_decision.py
	$(PYTHON) .github/scripts/test_npm_publication_closeout.py
	$(PYTHON) .github/scripts/test_patch_0_1_2_npm_publication_approval_request.py
	$(PYTHON) .github/scripts/test_patch_0_1_2_npm_publication_approval_decision.py
	$(PYTHON) .github/scripts/test_patch_0_1_2_npm_publication_blocker.py
	$(PYTHON) .github/scripts/test_patch_0_1_2_npm_publication_closeout.py
	$(PYTHON) .github/scripts/test_patch_0_1_1_crates_publication_approval_request.py
	$(PYTHON) .github/scripts/test_patch_0_1_1_crates_publication_approval_decision.py
	$(PYTHON) .github/scripts/test_patch_0_1_1_crates_publication_closeout.py
	$(PYTHON) .github/scripts/test_pdfium_manual_setup_contract.py
	$(PYTHON) .github/scripts/test_release_artifact_workflow_prep.py
	$(PYTHON) .github/scripts/test_patch_0_1_1_release_artifact_evidence.py
	$(PYTHON) .github/scripts/test_patch_0_1_1_artifact_publication_approval_request.py
	$(PYTHON) .github/scripts/test_patch_0_1_1_artifact_publication_approval_decision.py
	$(PYTHON) .github/scripts/test_patch_0_1_1_artifact_publication_closeout.py
	$(PYTHON) .github/scripts/test_release_candidate_prep.py
	$(PYTHON) .github/scripts/test_release_reproducibility_scaffold.py
	$(PYTHON) .github/scripts/test_launch_copy_approval_scaffold.py
	$(PYTHON) .github/scripts/test_patch_0_1_2_readiness_prep.py
	$(PYTHON) .github/scripts/test_patch_0_1_2_version_activation.py
	$(PYTHON) .github/scripts/test_patch_0_1_2_artifact_package_evidence.py
	$(PYTHON) .github/scripts/test_patch_0_1_2_draft_artifact_evidence.py
	$(PYTHON) .github/scripts/test_patch_0_1_2_artifact_publication_approval_request.py
	$(PYTHON) .github/scripts/test_patch_0_1_2_artifact_publication_approval_decision.py
	$(PYTHON) .github/scripts/test_patch_0_1_2_artifact_publication_closeout.py
	$(PYTHON) .github/scripts/test_patch_0_1_2_npm_vendor_refresh.py
	$(PYTHON) .github/scripts/test_first_public_release_artifact_evidence.py
	$(PYTHON) .github/scripts/test_first_public_release_final_decider.py
	$(PYTHON) .github/scripts/test_first_public_release_linux_x64_artifact_evidence.py
	$(PYTHON) .github/scripts/test_first_public_release_linux_x64_final_decider.py
	$(PYTHON) .github/scripts/test_first_public_release_linux_x64_publication_closeout.py
	cargo test --locked -p ethos-cli --test verify invalid_config_constraints_are_usage_errors
	git diff --check

package-publication-dry-run-smoke:
	cargo package --locked --offline -p ethos-doc-core --allow-dirty --no-verify
	cargo package --list --locked --offline -p ethos-doc-core --allow-dirty
	cargo check --locked --offline -p ethos-verify
	cargo check --locked --offline -p ethos-pdf
	$(PYTHON) .github/scripts/test_milestone_e_package_publication_dry_run_smoke.py
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
