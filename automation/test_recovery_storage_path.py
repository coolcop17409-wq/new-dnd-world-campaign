"""Regression for one immutable historical path, without changing source records."""
import copy,json,unittest
from pathlib import Path
from unittest.mock import patch
from automation import recovery_chunks as chunks
from automation.recovery_journal import digest

ROOT=Path(__file__).resolve().parents[1]
BOUNDARY='automation/recovery/boundaries/PLAY-D314-RETHWYN-REST-CAERETH-ARRIVAL-SYNC-001.json'
class StoragePathTests(unittest.TestCase):
    def setUp(self):
        self.boundary=json.loads((ROOT/BOUNDARY).read_text())
        self.parts={r['path']:(ROOT/r['path']).read_text() for r in self.boundary['records']}
        self.path=next(iter(chunks.PINNED_STORAGE_PATHS))
        self.raw=self.parts[self.path];self.entry=json.loads(self.raw);self.hash=digest(self.entry)
    def test_exact_historical_source_preserved(self):
        original=dict(self.parts)
        mode=json.loads((ROOT/'automation/recovery/mode.json').read_text())
        with patch.object(chunks,'validate_rng',wraps=chunks.validate_rng) as rng:
            journal=chunks.compatibility_journal(self.boundary,self.parts.get,{'schema_version':1,'entries':[]},mode)
        self.assertEqual(journal['entries'],[json.loads(self.parts[r['path']]) for r in self.boundary['records']])
        self.assertEqual(self.parts,original)
        self.assertIn(self.path,[c.args[1] for c in rng.call_args_list])
        self.assertEqual(chunks.chunk_path(self.entry),self.path.replace('/D310/','/D308/'))
    def test_payload_digest_or_id_change_rejected(self):
        changed=copy.deepcopy(self.entry);changed['pending_action']+=' altered'
        for raw,expected in [(json.dumps(changed),self.hash),(json.dumps(changed),digest(changed)),(self.raw,'0'*64)]:
            with self.assertRaises(ValueError):chunks.validate_chunk(self.path,raw,expected)
        changed=copy.deepcopy(self.entry);changed['request_id']+='-OTHER'
        with self.assertRaises(ValueError):chunks.validate_chunk(self.path,json.dumps(changed),digest(changed))
    def test_other_directory_and_traversal_rejected(self):
        for path in [self.path.replace('/D310/','/D311/'),self.path.replace('/D310/','/D310/../D310/'),self.path.replace('.json','-COPY.json')]:
            with self.assertRaises(ValueError):chunks.validate_chunk(path,self.raw,self.hash)
    def test_pending_journal_still_blocks(self):
        with self.assertRaisesRegex(ValueError,'unsynchronized'):
            chunks.compatibility_journal(self.boundary,self.parts.get,{'schema_version':1,'entries':[self.entry]},{'schema_version':2,'mode':'chunked'})
if __name__=='__main__':unittest.main()
