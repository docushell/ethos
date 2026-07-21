#!/usr/bin/env python3
from __future__ import annotations
import json, os, subprocess, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RUNNER=ROOT/"scripts/measure-v0-5-performance.py"
FAKE='''#!/usr/bin/env python3
import os,pathlib,sys,time
v=pathlib.Path(sys.argv[0]).name
if sys.argv[1:]==["--version"]: print("ethos "+v); raise SystemExit(0)
if os.environ.get("ETHOS_PERF_TEST_LOG"):
 with open(os.environ["ETHOS_PERF_TEST_LOG"],"a") as log: log.write(v+":"+sys.argv[1]+"\\n")
if sys.argv[1]=="verify": time.sleep(.006 if v=="0.4.0" else .001); print("{}")
elif sys.argv[1]=="verify-batch": print("{}\\n"*len(pathlib.Path(sys.argv[sys.argv.index("--citations-ndjson")+1]).read_text().splitlines()),end="")
'''
class RunnerTests(unittest.TestCase):
 def test_writes_bound_passing_record(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); source=root/"source.json"; citations=root/"citations.json"; source.write_text("{}"); citations.write_text("{}")
   bins=[]
   for v in ("0.4.0","0.5.0"):
    b=root/v; b.write_text(FAKE); b.chmod(0o755); bins.append(b)
   out=root/"record.json"; log=root/"calls.log"; env=dict(os.environ,ETHOS_PERF_TEST_LOG=str(log)); r=subprocess.run(["python3",str(RUNNER),"--baseline-bin",str(bins[0]),"--candidate-bin",str(bins[1]),"--source",str(source),"--citations",str(citations),"--out",str(out)],capture_output=True,text=True,env=env)
   self.assertEqual(0,r.returncode,r.stderr); record=json.loads(out.read_text()); self.assertTrue(record["derived"]["passed"]); self.assertEqual(30,len(record["single_request_cold_ns"]["baseline"])); self.assertEqual(10,len(record["batch_32_ns"]["individual_processes"])); self.assertEqual(10,len(record["batch_32_ns"]["batch_process"])); self.assertEqual({"os","os_release","architecture","cpu"},set(record["environment"]))
   self.assertIn("verify-batch", calls[-1])
   calls=log.read_text().splitlines(); cold=calls[1:61]; self.assertEqual(["0.4.0:verify","0.5.0:verify","0.5.0:verify","0.4.0:verify"],cold[:4])
 def test_rejects_wrong_version(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); b=root/"bad"; b.write_text(FAKE); b.chmod(0o755); f=root/"f"; f.write_text("{}"); r=subprocess.run(["python3",str(RUNNER),"--baseline-bin",str(b),"--candidate-bin",str(b),"--source",str(f),"--citations",str(f),"--out",str(root/"o")],capture_output=True,text=True); self.assertNotEqual(0,r.returncode); self.assertIn("0.4.0",r.stderr)
if __name__=="__main__": unittest.main()
