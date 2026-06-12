ROOT := ../..
ETHOS_BIN ?= $(ROOT)/target/release/ethos
FIXTURE_RESULTS_DIR ?= $(ROOT)/benchmarks/results/fixtures
GATE_ZERO_RESULTS_DIR ?= $(ROOT)/benchmarks/results/gate-zero
FIXTURE_REPORT ?= $(FIXTURE_RESULTS_DIR)/baseline.json
GATE_ZERO_READINESS_REPORT ?= $(GATE_ZERO_RESULTS_DIR)/readiness.json
GATE_ZERO_RESULT_REPORT ?= $(GATE_ZERO_RESULTS_DIR)/g1.json
OPENDATALOADER_ROOT ?=
ITERATIONS ?= 3

.PHONY: bench fixtures gate-zero-readiness gate-zero-results smoke test

$(ETHOS_BIN):
	cd $(ROOT) && cargo build --locked --release -p ethos-cli

fixtures: $(ETHOS_BIN)
	mkdir -p $(FIXTURE_RESULTS_DIR)
	python3 run_fixtures.py \
		--repo-root $(ROOT) \
		--ethos-bin $(ETHOS_BIN) \
		--iterations $(ITERATIONS) \
		--out $(FIXTURE_REPORT)

gate-zero-readiness:
	mkdir -p $(GATE_ZERO_RESULTS_DIR)
	python3 run_gate_zero.py \
		--repo-root $(ROOT) \
		--out $(GATE_ZERO_READINESS_REPORT)

gate-zero-results: $(ETHOS_BIN)
	mkdir -p $(GATE_ZERO_RESULTS_DIR)
	python3 run_gate_zero.py \
		--mode ethos \
		--repo-root $(ROOT) \
		--ethos-bin $(ETHOS_BIN) \
		--install-path $(ETHOS_BIN) \
		--iterations $(ITERATIONS) \
		$(if $(OPENDATALOADER_ROOT),--opendataloader-root $(OPENDATALOADER_ROOT),) \
		--out $(GATE_ZERO_RESULT_REPORT)

bench: gate-zero-results

smoke:
	python3 run_fixtures.py --help >/dev/null
	python3 run_gate_zero.py --help >/dev/null

test:
	python3 test_run_gate_zero.py
