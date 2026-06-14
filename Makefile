ROOT := $(CURDIR)
PYTHON ?= python3
ETHOS_BIN ?= $(ROOT)/target/debug/ethos
VERIFY_ALPHA_OUT ?= $(ROOT)/target/verify-alpha

.PHONY: verify-alpha verify-alpha-tree

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
	$(PYTHON) -c 'from jsonschema import Draft202012Validator'
	$(PYTHON) schemas/validate_examples.py
	$(PYTHON) examples/verify/check_verify_alpha.py --repo-root $(ROOT) --ethos-bin $(ETHOS_BIN) --out-dir $(VERIFY_ALPHA_OUT)
	git diff --check
