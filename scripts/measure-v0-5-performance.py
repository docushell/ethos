#!/usr/bin/env python3
"""Record bounded internal v0.4-to-v0.5 verification timing evidence."""
from __future__ import annotations
import argparse, hashlib, json, os, statistics, subprocess, tempfile, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def fail(m: str) -> None: raise SystemExit(f"measure-v0-5-performance: error: {m}")
def sha(p: Path) -> str: return hashlib.sha256(p.read_bytes()).hexdigest()
def med(v: list[int]) -> int: return int(statistics.median(v))
def run(c: list[str], expected: bytes | None = None) -> tuple[int, bytes]:
    t=time.monotonic_ns(); r=subprocess.run(c,stdout=subprocess.PIPE,stderr=subprocess.PIPE); e=time.monotonic_ns()-t
    if r.returncode: fail(f"command failed: {' '.join(c)}")
    if expected is not None and r.stdout != expected: fail("verification output was not canonical")
    return e,r.stdout
def main() -> int:
    p=argparse.ArgumentParser(); p.add_argument("--baseline-bin",required=True,type=Path); p.add_argument("--candidate-bin",required=True,type=Path); p.add_argument("--source",default=ROOT/"schemas/examples/document.example.json",type=Path); p.add_argument("--citations",default=ROOT/"examples/verify/native_grounded_citations.json",type=Path); p.add_argument("--out",required=True,type=Path); a=p.parse_args()
    for b,v in ((a.baseline_bin,"ethos 0.4.0"),(a.candidate_bin,"ethos 0.5.0")):
        if not b.is_file() or b.is_symlink() or not os.access(b,os.X_OK): fail("binary must be regular executable")
        if subprocess.run([str(b),"--version"],stdout=subprocess.PIPE).stdout.decode().strip()!=v: fail(f"binary does not report {v}")
    c=[str(a.candidate_bin),"verify",str(a.source),"--citations",str(a.citations)]; _,expected=run(c)
    base=[run([str(a.baseline_bin),"verify",str(a.source),"--citations",str(a.citations)],expected)[0] for _ in range(30)]
    candidate=[run(c,expected)[0] for _ in range(30)]; individual=[run(c,expected)[0] for _ in range(32)]
    with tempfile.TemporaryDirectory() as d:
        nd=Path(d)/"requests.ndjson"; nd.write_bytes((a.citations.read_bytes().rstrip(b"\n")+b"\n")*32); batch,out=run([str(a.candidate_bin),"verify-batch",str(a.source),"--citations-ndjson",str(nd)])
    if out != (expected.rstrip(b"\n")+b"\n")*32: fail("batch output was not canonical")
    bm,cm,im=med(base),med(candidate),med(individual); passed=cm*100<=bm*110 and batch*2<=im*32
    if not passed: fail("performance threshold failed")
    record={"schema":"ethos.v0_5_performance_record.v1","baseline_version":"0.4.0","candidate_version":"0.5.0","baseline_binary_sha256":sha(a.baseline_bin),"candidate_binary_sha256":sha(a.candidate_bin),"source_sha256":sha(a.source),"citations_sha256":sha(a.citations),"single_request_cold_ns":{"baseline":base,"candidate":candidate},"batch_32_ns":{"individual_process":individual,"batch_elapsed":batch},"derived":{"baseline_median_ns":bm,"candidate_median_ns":cm,"individual_median_ns":im,"passed":passed}}
    a.out.write_text(json.dumps(record,sort_keys=True,indent=2)+"\n"); return 0
if __name__=="__main__": raise SystemExit(main())
