#!/usr/bin/env python3
"""Fast-play parser/guard regression checks (no campaign simulation)."""
import json
import csv
import tempfile
from pathlib import Path
from unittest.mock import patch
import unittest
from automation.build_play_packet import active_checkpoint, make_packet
from automation import build_dashboard

STATE = "CAMPAIGN_STATE — DAY 244 EVENING — TEST\n\nCURRENT EXACT PLAYED CHECKPOINT — TEST-EVENT, V must choose.\n\n## Earlier checkpoints and source history\nArchived only."
DASH = {"campaign_day":244,"tracker_status":"PASS","party":[{"name":"Valenthia","hp":"39","max_hp":"48","ac":"19","level":"7","resources":[{"name":"Psi","current":"6","max":"6"}],"purse":{"gp":1185,"sp":3,"cp":8}}]}

class FastPlayTests(unittest.TestCase):
    def test_new_inventory_custody_replays_once_and_rejects_duplicates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            baseline=root/'trackers/csv/cirren/cirren-inventory.csv'
            baseline.parent.mkdir(parents=True)
            baseline.write_text('ITEM,Qty\nExisting record,0\n')
            journal=root/'data/characters/events.csv'
            journal.parent.mkdir(parents=True)
            event=dict(event_id='TEST-CUSTODY',campaign_day='233',owner='Cirren',record_type='inventory_create',target='Test original',delta='',absolute_value='1',evidence=json.dumps(dict(source_event='TEST-SIGNED',holder='Cirren case',detail='One existing signed original.')),status='posted')
            def write():
                with journal.open('w',newline='') as f:
                    w=csv.DictWriter(f,fieldnames=list(event));w.writeheader();w.writerow(event)
            def payload():return dict(party=[dict(name='Cirren')],inventory={'Cirren':[]})
            with patch.object(build_dashboard,'ROOT',root):
                write()
                a=payload();b=payload()
                build_dashboard.apply_character_events(a);build_dashboard.apply_character_events(b)
                self.assertEqual(a,b)
                self.assertEqual(len(a['inventory']['Cirren']),1)
                self.assertEqual(a['inventory']['Cirren'][0]['qty'],'1')
                with self.assertRaises(ValueError):build_dashboard.apply_character_events(a)
                event['target']='Existing record';write()
                with self.assertRaises(ValueError):build_dashboard.apply_character_events(payload())
                event['target']='Test original';event['absolute_value']='0';write()
                with self.assertRaises(ValueError):build_dashboard.apply_character_events(payload())
                event['absolute_value']='1';event['evidence']='{}';write()
                with self.assertRaises(ValueError):build_dashboard.apply_character_events(payload())

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

