ROOT := ../..
ETHOS_BIN ?= $(ROOT)/target/release/ethos
RESULTS_DIR ?= $(ROOT)/benchmarks/results/fixtures
FIXTURE_REPORT ?= $(RESULTS_DIR)/baseline.json
ITERATIONS ?= 3

.PHONY: bench fixtures smoke

$(ETHOS_BIN):
	cd $(ROOT) && cargo build --locked --release -p ethos-cli

fixtures: $(ETHOS_BIN)
	mkdir -p $(RESULTS_DIR)
	python3 run_fixtures.py \
		--repo-root $(ROOT) \
		--ethos-bin $(ETHOS_BIN) \
		--iterations $(ITERATIONS) \
		--out $(FIXTURE_REPORT)

bench: fixtures

smoke:
	python3 run_fixtures.py --help >/dev/null
