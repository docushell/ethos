ROOT := ../..
ETHOS_BIN ?= $(ROOT)/target/release/ethos
FIXTURE_RESULTS_DIR ?= $(ROOT)/benchmarks/results/fixtures
GATE_ZERO_RESULTS_DIR ?= $(ROOT)/benchmarks/results/gate-zero
GATE_ZERO_PLATFORM ?= macos-arm64
GATE_ZERO_GATE ?= g1
FIXTURE_REPORT ?= $(FIXTURE_RESULTS_DIR)/baseline.json
GATE_ZERO_READINESS_REPORT ?= $(GATE_ZERO_RESULTS_DIR)/readiness.json
GATE_ZERO_RESULT_REPORT ?= $(GATE_ZERO_RESULTS_DIR)/$(GATE_ZERO_PLATFORM)/$(GATE_ZERO_GATE).json
GATE_ZERO_EVIDENCE_OUT_ROOT ?= $(GATE_ZERO_RESULTS_DIR)
GATE_ZERO_EVIDENCE_TIMESTAMP ?=
GATE_ZERO_REPRODUCTION_COMMAND ?=
GATE_ZERO_REPRODUCTION_COMMAND_FILE ?=
GATE_ZERO_REPRODUCTION_ENV_FILE ?=
GATE_ZERO_BENCHMARK_COMMIT ?=
GATE_ZERO_G2_RESULT_REPORT ?= $(GATE_ZERO_RESULTS_DIR)/$(GATE_ZERO_PLATFORM)/g2.json
GATE_ZERO_G3_RESULT_REPORT ?= $(GATE_ZERO_RESULTS_DIR)/g3.json
GATE_ZERO_G3_PLATFORM_RESULTS ?=
GATE_ZERO_GEOMETRY_LEFT_DIR ?=
GATE_ZERO_GEOMETRY_RIGHT_DIR ?=
GATE_ZERO_GEOMETRY_RESULT_REPORT ?= $(GATE_ZERO_RESULTS_DIR)/geometry-stability-experiment.json
GATE_ZERO_ETHOS_FOOTPRINT ?=
GATE_ZERO_PDFIUM_LIBRARY_PATH ?=
GATE_ZERO_PDFIUM_ARTIFACT ?=
OPENDATALOADER_ROOT ?=
OPENDATALOADER_COMMAND ?=
OPENDATALOADER_ARTIFACT ?=
OPENDATALOADER_INSTALL_PATH ?=
EDGEPARSE_COMMAND ?=
EDGEPARSE_ARTIFACT ?=
EDGEPARSE_INSTALL_PATH ?=
LITEPARSE_COMMAND ?=
LITEPARSE_ARTIFACT ?=
LITEPARSE_INSTALL_PATH ?=
PYMUPDF4LLM_PYTHON ?=
PYMUPDF4LLM_ARTIFACT ?=
PYMUPDF4LLM_INSTALL_PATH ?=
ITERATIONS ?= 3

.PHONY: bench fixtures gate-zero-evidence gate-zero-g2 gate-zero-g3 gate-zero-geometry-experiment gate-zero-readiness gate-zero-results smoke test

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
	mkdir -p $(dir $(GATE_ZERO_RESULT_REPORT))
	python3 run_gate_zero.py \
		--mode ethos \
		--repo-root $(ROOT) \
		--ethos-bin $(ETHOS_BIN) \
		--install-path $(ETHOS_BIN) \
		--iterations $(ITERATIONS) \
		$(if $(OPENDATALOADER_ROOT),--opendataloader-root $(OPENDATALOADER_ROOT),) \
		$(if $(OPENDATALOADER_COMMAND),--opendataloader-command $(OPENDATALOADER_COMMAND),) \
		$(if $(OPENDATALOADER_ARTIFACT),--opendataloader-artifact $(OPENDATALOADER_ARTIFACT),) \
		$(if $(OPENDATALOADER_INSTALL_PATH),--opendataloader-install-path $(OPENDATALOADER_INSTALL_PATH),) \
		$(if $(EDGEPARSE_COMMAND),--edgeparse-command $(EDGEPARSE_COMMAND),) \
		$(if $(EDGEPARSE_ARTIFACT),--edgeparse-artifact $(EDGEPARSE_ARTIFACT),) \
		$(if $(EDGEPARSE_INSTALL_PATH),--edgeparse-install-path $(EDGEPARSE_INSTALL_PATH),) \
		$(if $(LITEPARSE_COMMAND),--liteparse-command $(LITEPARSE_COMMAND),) \
		$(if $(LITEPARSE_ARTIFACT),--liteparse-artifact $(LITEPARSE_ARTIFACT),) \
		$(if $(LITEPARSE_INSTALL_PATH),--liteparse-install-path $(LITEPARSE_INSTALL_PATH),) \
		$(if $(PYMUPDF4LLM_PYTHON),--pymupdf4llm-python $(PYMUPDF4LLM_PYTHON),) \
		$(if $(PYMUPDF4LLM_ARTIFACT),--pymupdf4llm-artifact $(PYMUPDF4LLM_ARTIFACT),) \
		$(if $(PYMUPDF4LLM_INSTALL_PATH),--pymupdf4llm-install-path $(PYMUPDF4LLM_INSTALL_PATH),) \
		--out $(GATE_ZERO_RESULT_REPORT)

gate-zero-g2:
	mkdir -p $(dir $(GATE_ZERO_G2_RESULT_REPORT))
	python3 run_gate_zero_g2.py \
		--repo-root $(ROOT) \
		--platform $(GATE_ZERO_PLATFORM) \
		$(if $(GATE_ZERO_ETHOS_FOOTPRINT),$(foreach item,$(GATE_ZERO_ETHOS_FOOTPRINT),--ethos-footprint $(item)),) \
		--opendataloader-install-path $(OPENDATALOADER_INSTALL_PATH) \
		$(if $(OPENDATALOADER_ARTIFACT),--opendataloader-artifact $(OPENDATALOADER_ARTIFACT),) \
		$(if $(GATE_ZERO_PDFIUM_LIBRARY_PATH),--pdfium-library-path $(GATE_ZERO_PDFIUM_LIBRARY_PATH),) \
		$(if $(GATE_ZERO_PDFIUM_ARTIFACT),--pdfium-artifact $(GATE_ZERO_PDFIUM_ARTIFACT),) \
		--out $(GATE_ZERO_G2_RESULT_REPORT)

gate-zero-g3:
	mkdir -p $(dir $(GATE_ZERO_G3_RESULT_REPORT))
	python3 run_gate_zero_g3.py \
		--repo-root $(ROOT) \
		$(if $(GATE_ZERO_G3_PLATFORM_RESULTS),$(foreach item,$(GATE_ZERO_G3_PLATFORM_RESULTS),--platform-result $(item)),) \
		--out $(GATE_ZERO_G3_RESULT_REPORT)

gate-zero-geometry-experiment:
	mkdir -p $(dir $(GATE_ZERO_GEOMETRY_RESULT_REPORT))
	python3 experiment_gate_zero_geometry_stability.py \
		--left-dir $(GATE_ZERO_GEOMETRY_LEFT_DIR) \
		--right-dir $(GATE_ZERO_GEOMETRY_RIGHT_DIR) \
		--out $(GATE_ZERO_GEOMETRY_RESULT_REPORT)

gate-zero-evidence:
	python3 build_gate_zero_evidence.py \
		--repo-root $(ROOT) \
		--result $(GATE_ZERO_RESULT_REPORT) \
		--out-root $(GATE_ZERO_EVIDENCE_OUT_ROOT) \
		--platform $(GATE_ZERO_PLATFORM) \
		--gate $(GATE_ZERO_GATE) \
		$(if $(GATE_ZERO_EVIDENCE_TIMESTAMP),--timestamp $(GATE_ZERO_EVIDENCE_TIMESTAMP),) \
		$(if $(GATE_ZERO_REPRODUCTION_COMMAND_FILE),--reproduction-command-file $(GATE_ZERO_REPRODUCTION_COMMAND_FILE),) \
		$(if $(GATE_ZERO_REPRODUCTION_COMMAND),--reproduction-command "$(GATE_ZERO_REPRODUCTION_COMMAND)",) \
		$(if $(GATE_ZERO_REPRODUCTION_ENV_FILE),--reproduction-env-file $(GATE_ZERO_REPRODUCTION_ENV_FILE),) \
		$(if $(GATE_ZERO_BENCHMARK_COMMIT),--benchmark-commit $(GATE_ZERO_BENCHMARK_COMMIT),)

bench: gate-zero-results

smoke:
	python3 run_fixtures.py --help >/dev/null
	python3 run_gate_zero.py --help >/dev/null
	python3 run_gate_zero_g2.py --help >/dev/null
	python3 run_gate_zero_g3.py --help >/dev/null
	python3 diff_gate_zero_docs.py --help >/dev/null
	python3 compare_gate_zero_geometry_probes.py --help >/dev/null
	python3 experiment_gate_zero_geometry_stability.py --help >/dev/null
	python3 build_gate_zero_evidence.py --help >/dev/null

test:
	python3 test_compare_gate_zero_geometry_probes.py
	python3 test_diff_gate_zero_docs.py
	python3 test_experiment_gate_zero_geometry_stability.py
	python3 test_run_gate_zero.py
	python3 test_run_gate_zero_g2.py
	python3 test_run_gate_zero_g3.py
	python3 test_gate_zero_evidence.py
	python3 test_gate_zero_gates.py
