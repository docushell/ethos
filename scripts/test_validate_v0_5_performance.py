#!/usr/bin/env python3
from __future__ import annotations
import copy, importlib.util, tempfile, unittest
from pathlib import Path
_spec = importlib.util.spec_from_file_location("validate_v0_5_performance", __file__.replace("test_validate_v0_5_performance.py", "validate-v0-5-performance.py"))
_module = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_module)
validate = _module.validate

def sample() -> dict[str, object]:
    return {"schema":"ethos.v0_5_performance_record.v1","baseline_version":"0.4.0","candidate_version":"0.5.0","baseline_binary_sha256":"a"*64,"candidate_binary_sha256":"b"*64,"source_sha256":"c"*64,"citations_sha256":"d"*64,"environment":{"os":"TestOS","os_release":"1","architecture":"x64","cpu":"test-cpu"},"single_request_cold_ns":{"baseline":[100]*30,"candidate":[110]*30},"batch_32_ns":{"individual_processes":[3200]*10,"batch_process":[1600]*10},"derived":{"baseline_median_ns":100,"candidate_median_ns":110,"individual_median_ns":3200,"batch_median_ns":1600,"passed":True}}

class PerformanceValidatorTests(unittest.TestCase):
    def test_accepts_threshold_bound_record(self): self.assertTrue(validate(sample())["passed"])
    def test_rejects_tampered_derived_values_and_thresholds(self):
        record=sample(); record["derived"]["candidate_median_ns"]=111
        with self.assertRaisesRegex(ValueError,"derived"): validate(record)
        record=sample(); record["batch_32_ns"]["batch_process"]=[1601]*10
        record["derived"]["batch_median_ns"]=1601; record["derived"]["passed"]=False
        with self.assertRaisesRegex(ValueError,"thresholds"): validate(record)

    def test_rejects_bound_fixture_hash_drift(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "source.json"
            source.write_text("different")
            with self.assertRaisesRegex(ValueError, "source hash"):
                validate(sample(), source=source)

    def test_rejects_invalid_environment(self):
        record = sample()
        record["environment"]["cpu"] = ""
        with self.assertRaisesRegex(ValueError, "environment"):
            validate(record)

if __name__=="__main__": unittest.main()
