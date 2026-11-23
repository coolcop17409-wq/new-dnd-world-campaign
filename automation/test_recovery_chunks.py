import copy,json,tempfile,unittest
from pathlib import Path
from automation.recovery_chunks import (chunk_path,chunk_content,validate_chunk,
  make_boundary,validate_boundary,compatibility_journal,boundary_path)
from automation.recovery_journal import digest
from automation.test_recovery_journal import RecoveryTests

class ChunkTests(unittest.TestCase):
    def setUp(self):
        f=RecoveryTests();f.setUp()
        self.first=copy.deepcopy(f.entry)
        self.first["request_id"]="PLAY-REC-D281-TEST-001"
        self.second=copy.deepcopy(self.first)
        self.second["request_id"]="PLAY-REC-D281-TEST-002"
        self.second["source_checkpoint"]="B"
        self.second["destination_checkpoint"]="C"
        self.second["depends_on"]=[self.first["request_id"]]
        self.second["events"][0]["event_id"]="TEST-2"
        self.parts={chunk_path(x):chunk_content(x) for x in (self.first,self.second)}
        self.boundary=make_boundary([self.first,self.second],"PLAY-D281-TEST-SYNC-001","significant_exploration")
        self.reader=lambda path:self.parts.get(path)
    def test_exact_roundtrip_preserves_objects(self):
        self.assertEqual(validate_boundary(self.boundary,self.reader),[self.first,self.second])
        compat=compatibility_journal(self.boundary,self.reader,{"schema_version":1,"entries":[]},
                 {"schema_version":2,"mode":"chunked"})
        self.assertEqual(compat["entries"],[self.first,self.second])
        self.assertEqual(compat["sync_trigger"]["last_recovery_id"],self.second["request_id"])
        self.assertEqual(boundary_path(self.boundary["request_id"]),
            "automation/recovery/boundaries/PLAY-D281-TEST-SYNC-001.json")
    def test_tampering_rejected(self):
        p=chunk_path(self.first)
        changed=dict(self.parts)
        entry=copy.deepcopy(self.first);entry["events"][0]["after"]="FAKED"
        changed[p]=chunk_content(entry)
        with self.assertRaisesRegex(ValueError,"digest mismatch"):
            validate_boundary(self.boundary,changed.get)
    def test_swapped_order_duplicate_and_missing_rejected(self):
        swapped=copy.deepcopy(self.boundary)
        swapped["records"].reverse()
        with self.assertRaises(ValueError):validate_boundary(swapped,self.reader)
        duplicate=copy.deepcopy(self.boundary)
        duplicate["records"][1]=duplicate["records"][0]
        with self.assertRaises(ValueError):validate_boundary(duplicate,self.reader)
        with self.assertRaises(ValueError):validate_boundary(self.boundary,lambda path:None)
    def test_old_ledger_not_discarded(self):
        with self.assertRaisesRegex(ValueError,"still has unsynchronized"):
            compatibility_journal(self.boundary,self.reader,
                {"schema_version":1,"entries":[self.first]},
                {"schema_version":2,"mode":"chunked"})
        with self.assertRaises(ValueError):
            compatibility_journal(self.boundary,self.reader,
                {"schema_version":1,"entries":[]},
                {"schema_version":2,"mode":"legacy"})
    def test_invalid_id_or_chain_rejected(self):
        altered=copy.deepcopy(self.first);altered["request_id"]="../escape"
        with self.assertRaises(ValueError):chunk_content(altered)
        broken=copy.deepcopy(self.second);broken["source_checkpoint"]="UNPLAYED"
        with self.assertRaises(ValueError):
            make_boundary([self.first,broken],"PLAY-D281-TEST-SYNC-001","combat_end")
        with self.assertRaises(ValueError):
            make_boundary([self.first],"PLAY-D281-TEST-SYNC-001","ordinary_attack")
    def test_source_file_is_not_modified_by_compaction(self):
        orig=copy.deepcopy(self.parts)
        compatibility_journal(self.boundary,self.reader,{"schema_version":1,"entries":[]},
            {"schema_version":2,"mode":"chunked"})
        self.assertEqual(self.parts,orig)
    def test_single_chunk_under_legacy_limit_fixture(self):
        self.assertGreater(len(chunk_content(self.first)),100)
        self.assertEqual(json.loads(chunk_content(self.first)),self.first)

if __name__=="__main__":unittest.main()
