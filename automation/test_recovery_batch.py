import copy
import unittest
from automation.recovery_batch import build, verify
from automation import test_recovery_journal as fixtures

class BatchTests(unittest.TestCase):
    def setUp(self):
        fixture=fixtures.RecoveryTests();fixture.setUp()
        self.first=fixture.entry
        self.second=copy.deepcopy(self.first)
        self.second.update(request_id='PLAY-REC-TEST-002',source_checkpoint='B',destination_checkpoint='C',pending_action='Latest exact decision',depends_on=[self.first['request_id']])
        self.second['events'][0]['event_id']='TEST-2'
        self.journal=dict(schema_version=1,entries=[self.first,self.second])
    def batch(self,journal=None,prior=None):
        return build(journal or self.journal,'PLAY-BATCH-NEW-001','f'*40,prior or [])
    def test_exact_order_evidence_and_pending_action(self):
        request=self.batch()
        self.assertEqual(request['events'],self.first['events']+self.second['events'])
        self.assertEqual(request['pending_action'],self.second['pending_action'])
        self.assertEqual((request['source_checkpoint'],request['destination_checkpoint']),('A','C'))
        self.assertEqual(request['depends_on'],[])
        self.assertTrue(verify(self.journal,request,[]))
        self.assertEqual(self.batch(),request)
    def test_skip_queued_prefix_and_map_dependency(self):
        old=build(dict(schema_version=1,entries=[self.first]),'PLAY-OLD-001','e'*40,[])
        request=self.batch(prior=[old])
        self.assertEqual(request['events'],self.second['events'])
        self.assertEqual(request['depends_on'],['PLAY-OLD-001'])
    def test_pruned_historical_recovery_dependency_maps_to_prior_batch(self):
        # The exact Day279 failure: first active entry refers to a recovery
        # ID present only in an already-verified historical batch manifest.
        old=build(dict(schema_version=1,entries=[self.first]),
                  'PLAY-D279-FREIGHT-YARD-RESOLUTION-001','e'*40,[])
        current=dict(schema_version=1,entries=[self.second])
        request=build(current,'PLAY-D281-KESTREL-LAB-ENTRY-001','f'*40,[old])
        self.assertEqual(request['events'],self.second['events'])
        self.assertEqual(request['depends_on'],['PLAY-D279-FREIGHT-YARD-RESOLUTION-001'])
        self.assertEqual(request['recovery_entries'].keys(),{self.second['request_id']})
        self.assertTrue(verify(current,request,[old]))

    def test_duplicate_historical_manifest_owner_rejected(self):
        old=build(dict(schema_version=1,entries=[self.first]),
                  'PLAY-OLD-001','e'*40,[])
        duplicate=copy.deepcopy(old)
        duplicate['request_id']='PLAY-OTHER-001'
        duplicate['events'][0]['event_id']='DIFFERENT-EVENT'
        with self.assertRaises(ValueError):
            self.batch(prior=[old,duplicate])

    def test_unknown_historical_recovery_dependency_still_fails(self):
        old=build(dict(schema_version=1,entries=[self.first]),
                  'PLAY-OLD-001','e'*40,[])
        self.second['depends_on']=['PLAY-REC-NOT-IN-HISTORY']
        with self.assertRaises(ValueError):
            build(dict(schema_version=1,entries=[self.second]),
                  'PLAY-NEW-001','f'*40,[old])

    def test_invented_or_edited_payload_rejected(self):
        for key,value in [('pending_action','invented'),('source_evidence','invented'),('destination_checkpoint','D')]:
            request=self.batch();request[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError): verify(self.journal,request,[])
    def test_pinned_snapshot_survives_new_append(self):
        request=self.batch();new=copy.deepcopy(self.journal);new['entries'][0]['source_evidence']='edited'
        with self.assertRaises(ValueError): verify(new,request,[])
        self.assertTrue(verify(self.journal,request,[]))
    def test_checkpoint_gap(self):
        self.second['source_checkpoint']='missing'
        with self.assertRaises(ValueError): self.batch()
    def test_forward_dependency(self):
        self.first['depends_on']=[self.second['request_id']]
        with self.assertRaises(ValueError): self.batch()
    def test_missing_dependency(self):
        self.second['depends_on']=['PLAY-MISSING-001']
        with self.assertRaises(ValueError): self.batch()
    def test_empty_no_request(self):
        with self.assertRaises(ValueError): build(dict(schema_version=1,entries=[]),'PLAY-NEW-001','f'*40,[])
    def test_existing_id_not_rebuilt(self):
        old=self.batch()
        with self.assertRaises(ValueError): self.batch(prior=[old])
    def test_conflicting_prior_event(self):
        old=build(dict(schema_version=1,entries=[self.first]),'PLAY-OLD-001','e'*40,[])
        old['events'][0]['after']='contradiction'
        with self.assertRaises(ValueError): self.batch(prior=[old])
    def test_partial_overlap(self):
        old=build(dict(schema_version=1,entries=[self.first]),'PLAY-OLD-001','e'*40,[])
        event=copy.deepcopy(self.first['events'][0]);event['event_id']='TEST-EXTRA';self.first['events'].append(event)
        with self.assertRaises(ValueError): self.batch(prior=[old])


class SupersessionTests(BatchTests):
    def setup_replacement(self):
        from automation.recovery_journal import digest
        old = build(dict(schema_version=1, entries=[self.first]), 'PLAY-OLD-001', 'e'*40, [])
        replacement = self.batch()
        receipt = dict(request_id=old['request_id'], status='superseded',
            superseded_by=replacement['request_id'], request_digest=digest(old),
            replacement_digest=digest(replacement), owners_unapplied_verified=True,
            applied_event_ids=[], verified_base_commit='a'*40)
        return old, replacement, receipt

    def test_explicit_exact_replacement(self):
        old, new, receipt = self.setup_replacement()
        with self.assertRaises(ValueError): verify(self.journal, new, [old])
        self.assertTrue(verify(self.journal, new, [old], [receipt]))

    def test_invalid_bindings_and_partial_application_fail(self):
        old, new, receipt = self.setup_replacement()
        for key, value in [('request_digest', 'wrong'), ('replacement_digest', 'wrong'),
                           ('owners_unapplied_verified', False), ('applied_event_ids', ['TEST-1']),
                           ('status', 'blocked'), ('verified_base_commit', '')]:
            altered = dict(receipt, **{key:value})
            with self.subTest(key=key), self.assertRaises(ValueError):
                verify(self.journal, new, [old], [altered])

    def test_conflicting_replacement_rejected_even_with_matching_digest(self):
        from automation.recovery_journal import digest
        old, new, receipt = self.setup_replacement()
        old['events'][0]['after'] = 'Different outcome'
        receipt['request_digest'] = digest(old)
        with self.assertRaises(ValueError): verify(self.journal, new, [old], [receipt])

    def test_future_batches_skip_retired_transport(self):
        from automation.recovery_batch import reconcile_supersessions
        old, new, receipt = self.setup_replacement()
        self.assertEqual(reconcile_supersessions([old,new], [receipt]), [new])
        with self.assertRaises(ValueError): reconcile_supersessions([old], [receipt])
        with self.assertRaises(ValueError): reconcile_supersessions([old,new], [receipt,receipt])
