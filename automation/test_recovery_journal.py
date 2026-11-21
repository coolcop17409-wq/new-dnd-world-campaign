import copy
import unittest
from automation.recovery_journal import append, prune, digest

class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.entry = dict(schema_version=1, request_id='PLAY-REC-TEST-001', mode='accepted_play', base_commit='a'*40, source_checkpoint='A', destination_checkpoint='B', source_evidence='Synthetic fixture only', pending_action='Await choice', depends_on=[], events=[dict(event_id='TEST-1', accepted=True, evidence='Synthetic fixture only', before='before', after='after', owner_paths=['campaign/continuity/session-log.md'])])
        self.journal = append(dict(schema_version=1, entries=[]), self.entry)
        self.request = copy.deepcopy(self.entry)
        self.request['request_id'] = 'PLAY-BATCH-TEST-001'
        self.request['recovery_entries'] = {self.entry['request_id']: digest(self.entry)}
        self.receipt = dict(status='complete', request_id=self.request['request_id'], request_digest=digest(self.request), owners_verified=True, owner_commit='b'*40, tested_commit='c'*40, checkpoint_commit='d'*40, checkpoint_verified=True, tests=[dict(command='synthetic test', exit_code=0)], owner_refs=['synthetic owner at commit b'], verified_event_ids=['TEST-1'])
    def test_identical_append_retry(self):
        self.assertEqual(append(self.journal, self.entry), self.journal)
    def test_conflicting_id(self):
        changed = copy.deepcopy(self.entry); changed['pending_action'] = 'different'
        with self.assertRaises(ValueError): append(self.journal, changed)
    def test_duplicate_event_other_entry(self):
        changed = copy.deepcopy(self.entry); changed['request_id'] = 'PLAY-REC-TEST-002'
        with self.assertRaises(ValueError): append(self.journal, changed)
    def test_cleanup_keeps_newer_and_retries(self):
        newer = copy.deepcopy(self.entry); newer['request_id'] = 'PLAY-REC-TEST-002'; newer['events'][0]['event_id'] = 'TEST-2'
        journal = append(self.journal, newer)
        result = prune(journal, self.request, self.receipt)
        self.assertEqual(result['entries'], [newer])
        self.assertEqual(prune(result, self.request, self.receipt), result)
        self.assertEqual(len(journal['entries']), 2)
    def test_partial_or_failed_receipts_retain(self):
        for field, value in [('status','partial'), ('status','blocked'), ('owners_verified',False), ('checkpoint_verified',False), ('verified_event_ids',[]), ('request_digest','wrong'), ('owner_refs',[]), ('tests',[dict(command='test',exit_code=1)])]:
            receipt = dict(self.receipt); receipt[field] = value
            with self.subTest(field=field,value=value), self.assertRaises(ValueError): prune(self.journal,self.request,receipt)
    def test_modified_entry_blocks_cleanup(self):
        journal=copy.deepcopy(self.journal); journal['entries'][0]['pending_action']='newer correction'
        with self.assertRaises(ValueError): prune(journal,self.request,self.receipt)
    def test_event_content_must_match(self):
        request=copy.deepcopy(self.request); request['events'][0]['after']='different'
        receipt=dict(self.receipt,request_digest=digest(request))
        with self.assertRaises(ValueError): prune(self.journal,request,receipt)
    def test_empty_after_complete(self):
        self.assertEqual(prune(self.journal,self.request,self.receipt)['entries'], [])
    def test_smoke_cannot_append_or_prune(self):
        smoke=dict(self.entry,mode='smoke_test',events=[],destination_checkpoint='A')
        with self.assertRaises(ValueError): append(self.journal,smoke)
        with self.assertRaises(ValueError): prune(self.journal,smoke,self.receipt)
    def test_unaccepted_rejected(self):
        entry=copy.deepcopy(self.entry); entry['events'][0]['accepted']=False
        with self.assertRaises(ValueError): append(self.journal,entry)
