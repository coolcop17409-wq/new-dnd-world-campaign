import json
import tempfile
import unittest
from pathlib import Path
from automation.handoffs.validate import check

class HandoffValidationTests(unittest.TestCase):
    def test_empty_and_matching_completed_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            self.assertEqual(check(base), [])
            rq = base / "requests" / "shops"
            rs = base / "results" / "shops"
            rq.mkdir(parents=True); rs.mkdir(parents=True)
            rid = "HANDOFF-D265-SHOPS-MARKET-PREP-001"
            obj = {"request_id":rid,"lane":"shops","source":{"kind":"ooc_request","checkpoint_id":"D265-TEST-001","campaign_day":265},
                   "request":"Prepare item candidates without playing.","scope":["Tarnford reuse"],
                   "output_owner_paths":["trackers/csv/magic-shops/"],"priority":"normal","advances_gameplay":False}
            (rq/(rid+".json")).write_text(json.dumps(obj),encoding="utf-8")
            self.assertEqual(check(base), [])
            receipt = {"request_id":rid,"lane":"shops","status":"complete","summary":"Prepared candidates, no gameplay.",
                       "owner_refs":["trackers/csv/magic-shops/templates.csv"],"verified_commit":"a"*40}
            (rs/(rid+".json")).write_text(json.dumps(receipt),encoding="utf-8")
            self.assertEqual(check(base), [])
            obj["advances_gameplay"] = True
            (rq/(rid+".json")).write_text(json.dumps(obj),encoding="utf-8")
            self.assertTrue(any("cannot advance" in e for e in check(base)))

    def test_wrong_lane_and_unsupported_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            rs = base/"results"/"quests"
            rs.mkdir(parents=True)
            (rs/"HANDOFF-D265-QUESTS-INVALID-001.json").write_text(json.dumps({"request_id":"HANDOFF-D265-QUESTS-INVALID-001",
                "lane":"quests","status":"complete","summary":"Unsupported","owner_refs":["x"],"verified_commit":"b"*40}))
            self.assertTrue(any("no matching request" in e for e in check(base)))
