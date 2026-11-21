import base64, csv, importlib.util, io, json, shutil, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from automation.sync_validate import CHAR, SHOP, CHAR_HEADER, SHOP_HEADER, ROOT, read_csv, character_schema, linked_transactions, validate
from automation.sync_batch import append_once, require_head
spec=importlib.util.spec_from_file_location('collector',ROOT/'automation/handoffs/sync-repair/collect.py');collector=importlib.util.module_from_spec(spec);spec.loader.exec_module(collector)

class FakeAPI:
    repo='owner/campaign'
    def __init__(self):self.files={};self.prs=[];self.branches={'campaign-sync-test/regression':'a'*40};self.writes=0
    def head(self,b):return self.branches[b]
    def get_file(self,p,ref='main'):
        s=self.files.get((ref,p));return {'content':base64.b64encode(s.encode()).decode()} if s else None
    def write(self,b,expected,files,message):
        require_head(expected,self.head(b));self.writes+=1
        for p,s in files.items():self.files[b,p]=s
        self.branches[b]=f'{self.writes:040x}';return self.head(b)
    def call(self,method,path,data=None):
        if path=='git/refs':
            b=data['ref'].removeprefix('refs/heads/')
            if b not in self.branches:self.branches[b]=data['sha']
            return {}
        if method=='GET' and path.startswith('pulls?'):return self.prs
        if method=='POST' and path=='pulls':
            self.prs.append(dict(data,html_url='https://github.com/owner/campaign/pull/1'));return self.prs[-1]
        raise AssertionError((method,path))

class SyncTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.sale='TEST-TARNFORD-ROPE-SALE-001'
        self.debit=dict(zip(CHAR_HEADER,['TEST-ROPE-DEBIT-001','265','Valenthia','currency','purse_cp','-2800','',self.sale+': explicitly accepted 28 gp','posted']))
        self.item=dict(zip(CHAR_HEADER,['TEST-ROPE-ITEM-001','265','Valenthia','inventory_create','Rope of Mending','','1',json.dumps(dict(source_event=self.sale,holder='V coach',detail='Original complete 50ft rope, accepted 28gp purchase')),'posted']))
        self.shop=dict(zip(SHOP_HEADER,[self.sale,'265','Tarnford','Mill Winch Ropeworks','R02','SALE — V buys rope','-1','265','Accepted 28gp','One original','','Complete']))
        self.links=[dict(sale_id=self.sale,currency_id=self.debit['event_id'],inventory_id=self.item['event_id'],price_cp=2800,quantity=1,owner='Valenthia',item='Rope of Mending')]
        self.write(CHAR,CHAR_HEADER,[self.debit,self.item]);self.write(SHOP,SHOP_HEADER,[self.shop])
    def tearDown(self):self.tmp.cleanup()
    def write(self,path,header,rows):
        p=self.root/path;p.parent.mkdir(parents=True,exist_ok=True)
        with p.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=header,lineterminator='\n');w.writeheader();w.writerows(rows)
    def test_valid_linked_rope(self):
        events,errors=read_csv(self.root,CHAR,CHAR_HEADER)
        self.assertEqual(errors+character_schema(events)+linked_transactions(self.root,self.links),[])
    def test_wrong_journal_rejected_before_publication(self):
        p=self.root/CHAR
        with p.open('a') as f:csv.writer(f).writerow(list(self.shop.values()))
        _,errors=read_csv(self.root,CHAR,CHAR_HEADER);self.assertEqual(len(errors),1);self.assertEqual(errors[0]['code'],'csv.width')
    def test_wrong_schema_same_width_rejected(self):
        self.debit['record_type']='SALE';self.assertTrue(character_schema([self.debit]))
    def test_duplicate_leg_rejected(self):
        self.write(CHAR,CHAR_HEADER,[self.debit,self.debit,self.item]);self.assertTrue(linked_transactions(self.root,self.links))
    def test_wrong_amount_and_missing_item(self):
        self.debit['delta']='-28';self.write(CHAR,CHAR_HEADER,[self.debit,self.item]);self.assertTrue(linked_transactions(self.root,self.links))
        self.write(CHAR,CHAR_HEADER,[self.debit]);self.assertTrue(linked_transactions(self.root,self.links))
    def test_idempotent_retry_and_conflict(self):
        before=(self.root/CHAR).read_text();self.assertEqual(append_once(before,self.debit,CHAR_HEADER,'event_id'),before)
        changed=dict(self.debit,delta='-29')
        with self.assertRaises(ValueError):append_once(before,changed,CHAR_HEADER,'event_id')
    def test_nonfinite_and_fractional_delta_rejected(self):
        for v in ['NaN','Infinity','1.2']:self.assertTrue(character_schema([dict(self.debit,delta=v)]))
    def test_intermediate_checkpoint_is_not_catastrophic(self):
        p=self.root/'campaign/continuity';p.mkdir(parents=True)
        (p/'campaign-state.md').write_text('CAMPAIGN_STATE — DAY 265\n\nCURRENT EXACT PLAYED CHECKPOINT — D265-OLD-001.')
        (p/'session-log.md').write_text('D266-NEW-001 — accepted newer play')
        self.assertEqual(validate(self.root,'checkpoint')['status'],'PENDING_CHECKPOINT')
        self.assertEqual(validate(self.root,'checkpoint','final')['status'],'FAIL')
        (p/'campaign-state.md').write_text('CAMPAIGN_STATE — DAY 266\n\nCURRENT EXACT PLAYED CHECKPOINT — D266-NEW-001.')
        self.assertEqual(validate(self.root,'checkpoint','final')['status'],'PASS')
    def test_concurrent_write_protected(self):
        with self.assertRaises(ValueError):require_head('old','new')
    def test_signature_stable_across_retries(self):
        r={'scope':'characters','findings':[{'code':'csv.width','path':CHAR,'message':'bad row'}]}
        self.assertEqual(collector.signature(r,'test'),collector.signature(dict(r,run_id=22,commit_sha='new'),'test'))
    def run_record(self):return dict(id=10,conclusion='failure',name='Campaign synchronization regression',head_repository={'full_name':'owner/campaign'},head_branch='campaign-sync-test/regression',event='push',head_sha='a'*40,path='.github/workflows/sync-regression.yml',html_url='https://github.com/owner/campaign/actions/runs/10')
    def report(self):return dict(scope='synthetic',findings=[dict(code='csv.width',path='fixture.csv',message='missing field')],affected_files=['fixture.csv'])
    def test_one_request_one_draft_pr_on_retries(self):
        api=FakeAPI();a=collector.enqueue(api,self.run_record(),self.report());b=collector.enqueue(api,self.run_record(),self.report())
        self.assertEqual(a['request_id'],b['request_id']);self.assertEqual(len(api.prs),1);self.assertTrue(api.prs[0]['draft']);self.assertEqual(api.prs[0]['base'],'campaign-sync-test/regression');self.assertEqual(api.writes,2)
    def test_success_and_repair_failures_cannot_loop(self):
        run=self.run_record()
        for updates in [dict(conclusion='success'),dict(head_branch='campaign-repair/test'),dict(head_repository={'full_name':'fork/campaign'}),dict(event='pull_request')]:
            self.assertFalse(collector.eligible(dict(run,**updates),'owner/campaign'))
    def test_collector_request_passes_real_handoff_schema(self):
        from automation.handoffs.validate import check
        api=FakeAPI();collector.enqueue(api,self.run_record(),self.report())
        for (branch,path),content in api.files.items():
            if branch=='campaign-sync-test/regression':
                p=self.root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content)
        self.assertEqual(check(self.root/'automation/handoffs'),[])
    def test_terminal_receipt_deduplicates(self):
        api=FakeAPI();r=collector.enqueue(api,self.run_record(),self.report());p='automation/handoffs/results/sync-repair/'+r['request_id']+'.json';api.files['campaign-sync-test/regression',p]=json.dumps({'status':'complete'})
        self.assertEqual(collector.enqueue(api,self.run_record(),self.report())['status'],'terminal')
    def test_artifact_redirect_strips_api_credentials(self):
        import urllib.request
        req=urllib.request.Request('https://api.github.com/repos/owner/campaign/actions/artifacts/1/zip',headers={'Authorization':'Bearer test-only'})
        r=collector.SafeRedirect().redirect_request(req,None,302,'Found',{},'https://example.blob.core.windows.net/artifact.zip')
        self.assertFalse(r.has_header('Authorization'))
        with self.assertRaises(ValueError):collector.SafeRedirect().redirect_request(req,None,302,'Found',{},'http://example.com/artifact.zip')
    def test_newer_main_can_supersede_failure(self):
        api=FakeAPI();api.branches['main']='b'*40;run=dict(self.run_record(),head_branch='main')
        report=dict(self.report(),scope='characters',phase='owners')
        with patch.dict('os.environ',{'COLLECTOR_SOURCE_SHA':'b'*40}),patch.object(collector,'validate',return_value={'findings':[]}):
            self.assertEqual(collector.enqueue(api,run,report)['status'],'already_resolved')
        self.assertEqual(api.writes,0);self.assertEqual(api.prs,[])
    def test_synthetic_rope_replay_debits_once_and_creates_inventory(self):
        from automation import build_dashboard as d
        for group in ('v','cirren','fenar'):
            shutil.copytree(ROOT/'trackers/csv'/group,self.root/'trackers/csv'/group)
        with patch.object(d,'ROOT',self.root),patch.object(d,'CSV',self.root/'trackers/csv'):
            def payload():return {'party':[d.character('v','Valenthia','v-character.csv','v-inventory.csv')], 'inventory':{'Valenthia':d.inventory('v','v-inventory.csv')}}
            a=payload();before=a['party'][0]['purse_cp'];d.apply_character_events(a)
            b=payload();d.apply_character_events(b)
            self.assertEqual(a,b);self.assertEqual(a['party'][0]['purse_cp'],before-2800)
            rope=[i for i in a['inventory']['Valenthia'] if i['item']=='Rope of Mending'];self.assertEqual(len(rope),1);self.assertEqual(rope[0]['qty'],'1')
    def test_real_current_character_replay_scoped(self):
        # Read-only replay validates real resource bounds without altering any owner.
        self.assertEqual(validate(ROOT,'characters')['status'],'PASS')
    def test_scopes_do_not_run_unrelated_work(self):
        with patch('automation.sync_validate.characters',side_effect=AssertionError('character replay should not run')):
            self.assertEqual(validate(ROOT,'shops')['status'],'PASS')
    def test_live_narration_contract(self):
        s=(ROOT/'AGENTS.md').read_text();self.assertIn('Narrate and return the next actionable scene immediately',s)

if __name__=='__main__':unittest.main()
