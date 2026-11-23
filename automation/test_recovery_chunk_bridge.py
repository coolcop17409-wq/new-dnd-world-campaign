"""No-network tests: background bridge may assemble bytes, never invent gameplay."""
import base64,copy,json,unittest
from unittest.mock import patch
from automation import recovery_chunk_bridge as bridge
from automation.recovery_chunks import chunk_path,chunk_content,make_boundary
from automation.test_recovery_journal import RecoveryTests
SOURCE="a"*40
NEXT="b"*40

class FakeAPI:
    def __init__(self,entry,mode="chunked",existing=None):
        self.entry=copy.deepcopy(entry)
        self.boundary=make_boundary([self.entry],"PLAY-D281-TEST-BRIDGE-001","combat_end")
        self.snapshot={
            chunk_path(self.entry):chunk_content(self.entry),
            "automation/recovery/boundaries/PLAY-D281-TEST-BRIDGE-001.json":
              json.dumps(self.boundary),
            "automation/recovery/mode.json":
              json.dumps({"schema_version":2,"mode":mode}),
            "automation/recovery/active.json":
              json.dumps(existing if existing is not None else {"schema_version":1,"entries":[]}),
            "campaign/continuity/campaign-state.md":
              "CAMPAIGN_STATE — DAY 281\n\nCURRENT EXACT PLAYED CHECKPOINT — "+entry["source_checkpoint"]+"\n"
        }
        self.files={SOURCE:self.snapshot}
        self.head_sha=SOURCE
        self.writes=[]
    def get_file(self,path,sha):
        s=self.files.get(sha,self.snapshot).get(path)
        if s is None:return None
        return {"encoding":"base64","content":base64.b64encode(s.encode()).decode()}
    def head(self,branch):
        assert branch=="main"
        return self.head_sha
    def call(self,method,path,payload=None):
        if method=="GET" and path=="compare/"+SOURCE+"...main":
            return {"status":"identical"}
        raise AssertionError((method,path))
    def write(self,branch,expected,files,message):
        assert branch=="main" and expected==self.head_sha
        self.files[NEXT]=dict(self.files[SOURCE],**files)
        self.head_sha=NEXT
        self.writes.append(files)
        return NEXT

class BridgeTests(unittest.TestCase):
    def setUp(self):
        f=RecoveryTests();f.setUp()
        self.entry=copy.deepcopy(f.entry)
        self.entry["request_id"]="PLAY-REC-D281-TEST-BRIDGE-001"
    def test_guarded_legacy_compatibility_and_direct_pr(self):
        api=FakeAPI(self.entry)
        with patch.object(bridge,"submit",return_value={"status":"queued","url":"https://example.test/pr/1"}) as send:
            result=bridge.run(api,SOURCE,"PLAY-D281-TEST-BRIDGE-001")
        self.assertEqual(result["status"],"submitted")
        self.assertEqual(result["entry_count"],1)
        self.assertEqual(len(api.writes),1)
        legacy=json.loads(api.writes[0]["automation/recovery/active.json"])
        self.assertEqual(legacy["entries"],[self.entry])
        self.assertEqual(legacy["sync_trigger"]["reason"],"combat_end")
        args=send.call_args.args
        self.assertEqual(args[1],NEXT)
        self.assertEqual(args[2]["journal_commit"],NEXT)
        self.assertEqual(api.snapshot[chunk_path(self.entry)],chunk_content(self.entry))
    def test_inactive_mode_never_writes(self):
        api=FakeAPI(self.entry,mode="legacy")
        self.assertEqual(bridge.run(api,SOURCE,"PLAY-D281-TEST-BRIDGE-001")["status"],"not_activated")
        self.assertFalse(api.writes)
    def test_existing_unsynced_legacy_not_overwritten(self):
        api=FakeAPI(self.entry,existing={"schema_version":1,"entries":[self.entry]})
        with self.assertRaisesRegex(ValueError,"Unfinished earlier sync"):
            bridge.run(api,SOURCE,"PLAY-D281-TEST-BRIDGE-001")
        self.assertFalse(api.writes)
    def test_missing_or_changed_chunk_refused(self):
        api=FakeAPI(self.entry)
        api.snapshot[chunk_path(self.entry)]=api.snapshot[chunk_path(self.entry)].replace("Await choice","invented choice")
        with self.assertRaises(ValueError):bridge.run(api,SOURCE,"PLAY-D281-TEST-BRIDGE-001")
        self.assertFalse(api.writes)
    def test_checkpoint_mismatch_refused(self):
        api=FakeAPI(self.entry)
        api.snapshot["campaign/continuity/campaign-state.md"]="CURRENT EXACT PLAYED CHECKPOINT — OTHER"
        with self.assertRaisesRegex(ValueError,"does not match"):
            bridge.run(api,SOURCE,"PLAY-D281-TEST-BRIDGE-001")
        self.assertFalse(api.writes)

if __name__=="__main__":unittest.main()
