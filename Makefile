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

.PHONY: verify-alpha verify-alpha-tree verify-rendered-crops compare-rendered-crops layout-evaluator-alpha python-surface-test milestone-b-internal-checks release-hygiene release-advisory third-party-license-manifest release-notice-draft

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
	$(PYTHON) schemas/test_font_policy_validation.py
	$(MAKE) verify-alpha PYTHON=$(PYTHON)
	$(MAKE) layout-evaluator-alpha PYTHON=$(PYTHON)
	$(MAKE) python-surface-test PYTHON=$(PYTHON)
	$(PYTHON) .github/scripts/claims_gate.py
	$(PYTHON) .github/scripts/readiness_gate.py public
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
