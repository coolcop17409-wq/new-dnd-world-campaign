import copy
import unittest
from automation.play_handoff import validate

class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.batch = dict(schema_version=1, request_id='PLAY-TEST-001', mode='accepted_play', base_commit='a'*40,
            source_checkpoint='before', destination_checkpoint='after', source_evidence='Accepted conversation excerpt',
            pending_action='Await V choice', depends_on=[], events=[dict(event_id='E-1', accepted=True,
            evidence='Actual accepted outcome, no simulated data', before='before', after='after',
            owner_paths=['data/characters/events.csv'])])
    def test_valid(self):
        self.assertEqual(validate(self.batch), [])
    def test_duplicate(self):
        self.batch['events'] *= 2
        self.assertIn('duplicate event ID', validate(self.batch))
    def test_unaccepted(self):
        self.batch['events'][0]['accepted'] = False
        self.assertIn('unaccepted event', validate(self.batch))
    def test_missing_evidence(self):
        self.batch['events'][0]['evidence'] = ''
        self.assertTrue(validate(self.batch))
    def test_path_escape_or_code(self):
        for path in ['data/characters/../../automation/a.py', '.github/workflows/a.yml', '/etc/passwd', 'runtime/PLAY_NOW.md']:
            b = copy.deepcopy(self.batch); b['events'][0]['owner_paths'] = [path]
            self.assertIn('invalid owner path', validate(b))
    def test_dependency_cycle(self):
        self.batch['depends_on'] = ['PLAY-TEST-001']
        self.assertTrue(validate(self.batch))
    def test_smoke_never_changes_play(self):
        self.batch['mode'] = 'smoke_test'
        self.assertTrue(validate(self.batch))
        self.batch['events'] = []; self.batch['destination_checkpoint'] = 'before'
        self.assertEqual(validate(self.batch), [])
