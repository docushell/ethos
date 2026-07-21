#!/usr/bin/env python3
"""Model-free Evidence Handle Bridge walkthrough using a recorded Ethos report."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python"))
from ethos_pdf import build_evidence_citation_emission, build_evidence_handle_context, citation_json_bytes, hydrate_evidence_citations, project_evidence_states

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument("--out-dir", type=Path, default=ROOT / "target/evidence-handle-bridge")
args = parser.parse_args()
records = json.loads((HERE / "retrieval-records.json").read_text())
model = json.loads((HERE / "model-output.json").read_text())
report = json.loads((ROOT / "schemas/examples/verification-report.example.json").read_text())
context = build_evidence_handle_context(records)
emission = build_evidence_citation_emission(model["answer"], model["claims"])
hydrated = hydrate_evidence_citations(emission, context)
states = project_evidence_states(context, emission, report)
args.out_dir.mkdir(parents=True, exist_ok=True)
for name, value in (("context.json", context), ("emission.json", emission), ("hydrated-citations.json", hydrated), ("evidence-states.json", states)):
    (args.out_dir / name).write_bytes(citation_json_bytes(value))
