"""Network-free regression tests for explicitly marked accepted-play auto submission."""
import base64,copy,json,unittest,urllib.error
from automation.auto_sync_submit import ready_trigger,submit,priors,StaleBoundary
from automation.test_recovery_journal import RecoveryTests
SOURCE="e"*40
MAIN="a"*40
NEW="d"*40

def fixture():
    f=RecoveryTests();f.setUp()
    entry=copy.deepcopy(f.entry)
    return {"schema_version":1,"entries":[entry],
        "sync_trigger":{"ready":True,"reason":"combat_end",
            "request_id":"PLAY-AUTO-TEST-001",
            "last_recovery_id":entry["request_id"],
            "destination_checkpoint":entry["destination_checkpoint"]}}

class FakeAPI:
    def __init__(self,journal):
        self.journal=journal;self.prs=[];self.requests={};self.created=[];self.branches={"main":MAIN}
    def get_file(self,path,ref):
        if path=="automation/recovery/active.json" and ref==SOURCE:
            content=json.dumps(self.journal)
        elif (path,ref) in self.requests:
            content=self.requests[(path,ref)]
        else:return None
        return {"encoding":"base64","content":base64.b64encode(content.encode()).decode()}
    def head(self,branch):
        if branch not in self.branches:
            raise urllib.error.HTTPError(branch,404,"Not found",None,None)
        return self.branches[branch]
    def call(self,method,path,payload=None):
        if method=="GET" and path=="compare/"+SOURCE+"...main":
            return {"status":"identical"}
        if method=="GET" and path.startswith("pulls?state=all"):
            return list(self.prs)
        if method=="POST" and path=="git/refs":
            name=payload["ref"].removeprefix("refs/heads/")
            self.branches[name]=payload["sha"];return {}
        if method=="POST" and path=="pulls":
            pr={"title":payload["title"],"html_url":"https://github.com/example/repo/pull/1"}
            self.prs.append(pr);self.created.append(pr);return pr
        raise AssertionError((method,path))
    def write(self,branch,expected,files,message):
        assert self.head(branch)==expected
        for path,content in files.items():
            self.requests[(path,NEW)]=content
        self.branches[branch]=NEW
        return NEW

class AutoSyncTests(unittest.TestCase):
    def test_no_marker_means_no_pr(self):
        journal=fixture();journal.pop("sync_trigger");api=FakeAPI(journal)
        self.assertEqual(submit(api,SOURCE)["status"],"not_ready")
        self.assertFalse(api.created)
    def test_boundary_validation(self):
        journal=fixture()
        self.assertEqual(ready_trigger(journal)["reason"],"combat_end")
        for change in [{"reason":"ordinary_attack"},{"ready":False},
                       {"request_id":"../invalid"}]:
            candidate=copy.deepcopy(journal);candidate["sync_trigger"].update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):
                ready_trigger(candidate)
    def test_stale_marker_is_nonfatal_and_never_queues(self):
        api=FakeAPI(fixture())
        api.journal["sync_trigger"]["last_recovery_id"]="WRONG"
        with self.assertRaises(StaleBoundary):ready_trigger(api.journal)
        self.assertEqual(submit(api,SOURCE)["status"],"stale_marker")
        self.assertFalse(api.prs)
    def test_exact_events_queued_once(self):
        api=FakeAPI(fixture())
        first=submit(api,SOURCE)
        self.assertEqual(first["status"],"queued")
        self.assertEqual(first["event_count"],1)
        record=json.loads(next(iter(api.requests.values())))
        self.assertEqual(record["events"],api.journal["entries"][0]["events"])
        self.assertEqual(record["journal_source"]["commit"],SOURCE)
        self.assertEqual(record["destination_checkpoint"],"B")
        self.assertEqual(submit(api,SOURCE)["status"],"existing_pr")
        self.assertEqual(len(api.created),1)
    def test_empty_journal_blocks_dispatch(self):
        api=FakeAPI(fixture());api.journal["entries"].clear()
        with self.assertRaises(ValueError):submit(api,SOURCE)
    def test_missing_prior_request_blocks(self):
        api=FakeAPI(fixture())
        previous=[{"title":"[CAMPAIGN-SYNC] PLAY-OLD-001",
            "head":{"ref":"campaign-sync/play-old-001","sha":"b"*40}}]
        with self.assertRaises(ValueError):priors(api,previous)
if __name__=="__main__":unittest.main()
