#!/usr/bin/env python3
"""Fast-play parser/guard regression checks (no campaign simulation)."""
import json
import unittest
from automation.build_play_packet import active_checkpoint, make_packet

STATE = "CAMPAIGN_STATE — DAY 244 EVENING — TEST\n\nCURRENT EXACT PLAYED CHECKPOINT — TEST-EVENT, V must choose.\n\n## Earlier checkpoints and source history\nArchived only."
DASH = {"campaign_day":244,"tracker_status":"PASS","party":[{"name":"Valenthia","hp":"39","max_hp":"48","ac":"19","level":"7","resources":[{"name":"Psi","current":"6","max":"6"}],"purse":{"gp":1185,"sp":3,"cp":8}}]}

class FastPlayTests(unittest.TestCase):
    def test_current_only(self):
        day, section = active_checkpoint(STATE)
        self.assertEqual(day,244)
        self.assertNotIn("Archived only",section)
        packet=make_packet(STATE,json.dumps(DASH))
        self.assertIn("TEST-EVENT",packet)
        self.assertIn("Psi 6/6",packet)
        self.assertIn("1185 gp",packet)
        self.assertNotIn("Archived only",packet)

    def test_stale_dashboard_rejected(self):
        changed=dict(DASH,campaign_day=243)
        with self.assertRaises(ValueError):
            make_packet(STATE,json.dumps(changed))

    def test_invalid_tracker_rejected(self):
        changed=dict(DASH,tracker_status="CHECK")
        with self.assertRaises(ValueError):
            make_packet(STATE,json.dumps(changed))

    def test_missing_checkpoint_rejected(self):
        with self.assertRaises(ValueError):
            active_checkpoint("CAMPAIGN_STATE — DAY 244\n\nNo recorded checkpoint")

if __name__ == "__main__":
    unittest.main()
