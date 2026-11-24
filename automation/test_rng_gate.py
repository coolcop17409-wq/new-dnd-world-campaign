import json
import unittest
from automation.rng_gate import validate_rng, reject_void, VOID_IDS

class RNGGateTests(unittest.TestCase):
    def test_void_rejected(self):
        with self.assertRaisesRegex(ValueError,"Voided"):
            reject_void({"request_id":next(iter(VOID_IDS))})
    def test_missing_and_bad_receipts_refused(self):
        entry={"request_id":"PLAY-REC-D308-NEW-001"}
        policy={"version":1,"legacy_blobs":{}}
        with self.assertRaisesRegex(ValueError,"Missing RNG"):
            validate_rng(entry,"x",json.dumps(entry),policy,set())
        entry["rng_evidence"]={"status":"rolled","receipts":[{"schema_version":1,"generator":"python.secrets.randbelow","batch_id":"a"*32,"rolls":[{"id":"test","sides":20,"faces":[21]}]}]}
        with self.assertRaisesRegex(ValueError,"Invalid raw"):
            validate_rng(entry,"x",json.dumps(entry),policy,set())
    def test_valid_receipt_and_duplicate_refused(self):
        entry={"request_id":"PLAY-REC-D308-NEW-001","rng_evidence":{"status":"rolled","receipts":[{"schema_version":1,"generator":"python.secrets.randbelow","batch_id":"b"*32,"rolls":[{"id":"test","sides":20,"faces":[1,20]}]}]}}
        policy={"version":1,"legacy_blobs":{}}
        seen=set()
        validate_rng(entry,"x",json.dumps(entry),policy,seen)
        with self.assertRaisesRegex(ValueError,"repeated"):
            validate_rng(entry,"x",json.dumps(entry),policy,seen)
    def test_no_rolls(self):
        entry={"request_id":"PLAY-REC-D308-NEW-001","rng_evidence":{"status":"no_rolls","reason":"Player decision only"}}
        validate_rng(entry,"x",json.dumps(entry),{"version":1},set())
