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

    def test_battle_master_resource_overlay(self):
        v=build_dashboard.character("v","Valenthia","v-character.csv","v-inventory.csv")
        matches=[r for r in v["resources"] if r["name"]=="Superiority Dice"]
        self.assertEqual(len(matches),1)
        self.assertEqual((matches[0]["current"],matches[0]["max"]),("4","4"))
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            journal=root/"data/characters/events.csv"
            journal.parent.mkdir(parents=True)
            fields=["event_id","campaign_day","owner","record_type","target","delta","absolute_value","evidence","status"]
            events=[
                dict(event_id="TEST-SUP-SPEND",campaign_day="245",owner="Valenthia",record_type="resource",
                     target="Superiority Dice",delta="-1",absolute_value="",
                     evidence="Test fixture: one Tactical Assessment spend",status="posted"),
                dict(event_id="TEST-SUP-REST",campaign_day="246",owner="Valenthia",record_type="resource",
                     target="Superiority Dice",delta="1",absolute_value="",
                     evidence="Test fixture: one confirmed short rest",status="posted")]
            def replay(items):
                with journal.open("w",newline="") as handle:
                    writer=csv.DictWriter(handle,fieldnames=fields);writer.writeheader();writer.writerows(items)
                payload={"party":[build_dashboard.character("v","Valenthia","v-character.csv","v-inventory.csv")],
                         "inventory":{"Valenthia":[]}}
                with patch.object(build_dashboard,"ROOT",root):
                    build_dashboard.apply_character_events(payload)
                return next(r for r in payload["party"][0]["resources"] if r["name"]=="Superiority Dice")
            self.assertEqual(float(replay(events[:1])["current"]),3)
            self.assertEqual(float(replay(events)["current"]),4)
            events[1]["delta"]="2"
            with self.assertRaises(ValueError): replay(events)

    def test_checkpoint_must_begin_with_current_heading(self):
        with self.assertRaises(ValueError):
            active_checkpoint("ARCHIVED PARAGRAPH\n\n"+STATE)
        with self.assertRaises(ValueError):
            active_checkpoint(STATE + "X"*12000)

    def test_dashboard_day_requires_front_heading(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            state=root/"campaign/continuity/campaign-state.md"
            state.parent.mkdir(parents=True)
            state.write_text("old text\nCAMPAIGN_STATE — DAY 245\n")
            with patch.object(build_dashboard,"ROOT",root):
                with self.assertRaises(ValueError): build_dashboard.campaign_day()
                state.write_text(STATE)
                self.assertEqual(build_dashboard.campaign_day(),244)

    def test_current_only(self):
        day, section = active_checkpoint(STATE)
        self.assertEqual(day,244)
        self.assertNotIn("Archived only",section)
        packet=make_packet(STATE,json.dumps(DASH))
        self.assertIn("TEST-EVENT",packet)
        self.assertIn("Psi 6/6",packet)
        self.assertIn("1185 gp",packet)
        self.assertNotIn("Archived only",packet)

    def test_explicit_correction_excludes_superseded_checkpoint(self):
        state = ("CAMPAIGN_STATE — DAY 244 EVENING — TEST\n\n"
                 "LATEST PLAYER CORRECTION — TEST-CORRECTION. CURRENT PLAYABLE CHECKPOINT: HP48, V must choose.\n\n"
                 "HISTORICAL PRE-CORRECTION CHECKPOINT — superseded HP39.\n\n## Earlier checkpoints\nArchived")
        day, section = active_checkpoint(state)
        self.assertEqual(day,244)
        self.assertIn("TEST-CORRECTION",section)
        self.assertIn("V must choose",section)
        self.assertNotIn("superseded HP39",section)
        self.assertNotIn("Archived",section)
        with self.assertRaises(ValueError):
            active_checkpoint("CAMPAIGN_STATE — DAY 244\n\nLATEST PLAYER CORRECTION without a playable checkpoint")

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

