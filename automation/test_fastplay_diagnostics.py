import unittest
from automation.fastplay_diagnostics import summarize

class DiagnosticTests(unittest.TestCase):
    def test_duplicate_same_revision_read_and_one_recovery_are_visible(self):
        data=[
            {"turn_id":"D282-TEST","kind":"turn_start","time_ms":100},
            {"turn_id":"D282-TEST","kind":"github_read","time_ms":110,"path":"campaign/continuity/npcs.md","revision":"a"*40,"bytes":100},
            {"turn_id":"D282-TEST","kind":"github_read","time_ms":130,"path":"campaign/continuity/npcs.md","revision":"a"*40,"bytes":100},
            {"turn_id":"D282-TEST","kind":"dice","time_ms":150},
            {"turn_id":"D282-TEST","kind":"recovery_create","time_ms":170},
            {"turn_id":"D282-TEST","kind":"recovery_readback","time_ms":180},
            {"turn_id":"D282-TEST","kind":"turn_end","time_ms":300}]
        result=summarize(data)["turns"][0]
        self.assertEqual(result["observed_duration_ms"],200)
        self.assertEqual(result["github_source_reads"],2)
        self.assertEqual(result["duplicate_same_revision_reads"],1)
        self.assertEqual(result["recovery_creates"],1)
        self.assertEqual(result["recovery_readbacks"],1)
        self.assertIn("repeated_unchanged_source",result["flags"])
        self.assertNotIn("missing_recovery_readback",result["flags"])
    def test_hidden_timing_absence_not_fabricated(self):
        report=summarize([{"turn_id":"T","kind":"github_read","time_ms":0,"path":"runtime/PLAY_NOW.md"}])["turns"][0]
        self.assertIsNone(report["observed_duration_ms"])
        self.assertIn("time_unverified",report["flags"])
        self.assertEqual(report["unversioned_reads"],1)
    def test_conflicting_or_private_payload_rejected(self):
        rows=[{"turn_id":"T","kind":"turn_start","time_ms":1,"source_evidence":"secret"}]
        with self.assertRaisesRegex(ValueError,"Do not put"):summarize(rows)
        with self.assertRaises(ValueError):summarize([{"turn_id":"T","kind":"unknown","time_ms":1}])
        with self.assertRaises(ValueError):summarize([{"turn_id":"T","kind":"github_read","time_ms":1}])
    def test_ci_poll_write_fail_flags(self):
        events=[{"turn_id":"X","kind":"turn_start","time_ms":0},
                {"turn_id":"X","kind":"github_write","time_ms":1},
                {"turn_id":"X","kind":"recovery_create","time_ms":2},
                {"turn_id":"X","kind":"ci_poll","time_ms":3},
                {"turn_id":"X","kind":"turn_end","time_ms":4}]
        report=summarize(events)["turns"][0]
        self.assertTrue({"multiple_foreground_writes","foreground_ci_poll",
                         "missing_recovery_readback"}.issubset(report["flags"]))
