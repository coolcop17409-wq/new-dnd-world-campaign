#!/usr/bin/env python3
"""Trusted default-branch failure collector. Never executes failed-branch code."""
from __future__ import annotations
import base64, hashlib, io, json, os, re, sys, urllib.error, urllib.parse, urllib.request, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from automation.sync_validate import validate
ALLOWED={'Lightweight live-play validation','Campaign character journal validation','Magic shops — lightweight stock validation','Handoff queue integrity (not a background ChatGPT worker)','Estate audit and campaign dashboard','Campaign synchronization regression',
         'Queue accepted play at explicit recovery boundary',
         'Assemble immutable recovery at explicit boundary'}
PREFIX='automation/handoffs'

def signature(report, workflow):
    # Run ID, retry number, SHA and timestamps deliberately excluded.
    facts=sorted((e.get('code',''),e.get('path',''),e.get('event_id',''),e.get('message','')) for e in report['findings'])
    return hashlib.sha256(json.dumps([workflow,report['scope'],facts],sort_keys=True).encode()).hexdigest()[:24].upper()

def eligible(run, repository):
    return (run['conclusion']=='failure' and run['name'] in ALLOWED and
            run.get('head_repository',{}).get('full_name')==repository and
            (run['head_branch']=='main' or run['head_branch'].startswith('campaign-sync-test/')) and
            run['event'] in {'push','workflow_dispatch'})

class SafeRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if urllib.parse.urlsplit(newurl).scheme != 'https':
            raise ValueError('Refusing non-HTTPS artifact redirect')
        redirected=super().redirect_request(req,fp,code,msg,headers,newurl)
        if redirected is not None and urllib.parse.urlsplit(req.full_url).netloc != urllib.parse.urlsplit(newurl).netloc:
            redirected.remove_header('Authorization')
        return redirected

class API:
    def __init__(self, repo, token):self.repo=repo;self.token=token
    def call(self, method, path, data=None, binary=False):
        url=path if path.startswith('https://') else f'https://api.github.com/repos/{self.repo}/{path}'
        req=urllib.request.Request(url,data=json.dumps(data).encode() if data is not None else None,method=method,
            headers={'Authorization':'Bearer '+self.token,'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','Content-Type':'application/json'})
        with urllib.request.build_opener(SafeRedirect()).open(req,timeout=45) as r:
            raw=r.read(8_000_001)
            if len(raw)>8_000_000:raise ValueError('API response exceeds collector bound')
            return raw if binary else json.loads(raw) if raw else None
    def get_file(self,path,ref='main'):
        try:return self.call('GET','contents/'+path+'?ref='+urllib.parse.quote(ref,safe=''))
        except urllib.error.HTTPError as e:
            if e.code==404:return None
            raise
    def head(self,branch):return self.call('GET','git/ref/heads/'+branch)['object']['sha']
    def write(self,branch,expected,files,message):
        if self.head(branch)!=expected:raise RuntimeError('Concurrent head changed; retain request and retry from fresh sources')
        parent=self.call('GET','git/commits/'+expected)
        tree=self.call('POST','git/trees',{'base_tree':parent['tree']['sha'],'tree':[{'path':p,'mode':'100644','type':'blob','content':s} for p,s in files.items()]})
        commit=self.call('POST','git/commits',{'message':message,'tree':tree['sha'],'parents':[expected]})
        # A concurrent update cannot be ancestor of this new commit: force=false rejects it.
        self.call('PATCH','git/refs/heads/'+branch,{'sha':commit['sha'],'force':False})
        for p,s in files.items():
            actual=self.get_file(p,commit['sha'])
            if base64.b64decode(actual['content']).decode()!=s:raise RuntimeError('Readback failed: '+p)
        return commit['sha']

def auto_sync_failure_diagnostic(result):
    """Preserve the actual auto-submit error in a deduplicatable repair signature."""
    if not isinstance(result,dict) or result.get('status')!='blocked':
        return None
    reason=result.get('reason')
    if not isinstance(reason,str) or not reason.strip():
        return None
    return {'schema_version':1,'status':'FAIL','scope':'workflow',
        'findings':[{'code':'auto_sync.submit',
                     'path':'automation/recovery/sync-ready.json',
                     'event_id':'','message':reason[:2000]}],
        'affected_files':['automation/recovery/sync-ready.json',
                          'automation/recovery/active.json',
                          'automation/recovery_batch.py'],
        'notes':['Exact blocked auto-submit artifact, not an inferred gameplay event.',
                 'Pinned source commit: '+str(result.get('source_commit') or 'unknown')]}

def diagnose(api,run):
    artifacts=api.call('GET',f"actions/runs/{run['id']}/artifacts?per_page=100")['artifacts']
    for a in artifacts:
        if a['name']!='auto-sync-submission' or a['expired']:continue
        raw=api.call('GET',f"actions/artifacts/{a['id']}/zip",binary=True)
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            for info in archive.infolist():
                if info.filename.endswith('auto-sync-submission.json') and info.file_size<1_000_000:
                    result=auto_sync_failure_diagnostic(json.loads(archive.read(info)))
                    if result is not None:return result
    for a in artifacts:
        if a['name']!='campaign-sync-diagnostic' or a['expired']:continue
        raw=api.call('GET',f"actions/artifacts/{a['id']}/zip",binary=True)
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            for info in z.infolist():
                if info.filename.endswith('sync-diagnostic.json') and info.file_size<1_000_000:
                    report=json.loads(z.read(info))
                    if report.get('findings') and report.get('scope') in {'characters','shops','checkpoint','final','handoffs','synthetic'}:return report
    jobs=api.call('GET',f"actions/runs/{run['id']}/jobs?per_page=100")['jobs']
    failed=[j['name']+': '+s['name'] for j in jobs for s in j.get('steps',[]) if s['conclusion']=='failure']
    files=api.call('GET','commits/'+run['head_sha']).get('files',[])
    return {'schema_version':1,'status':'FAIL','scope':'workflow','findings':[{'code':'workflow.step','path':run['path'].split('@')[0],'event_id':'','message':x} for x in failed or ['Workflow failed; inspect linked job logs']],
            'affected_files':[f['filename'] for f in files], 'notes':['Artifact unavailable or tests failed outside scoped validator; no automatic record correction.']}

def enqueue(api,run,report,root=ROOT):
    if not eligible(run,api.repo):return {'status':'ignored','reason':'not eligible; repair branches never enqueue'}
    sig=signature(report,run['name']);rid='HANDOFF-SYNC-REPAIR-'+sig
    path=f'{PREFIX}/requests/sync-repair/{rid}.json';result_path=f'{PREFIX}/results/sync-repair/{rid}.json'
    synthetic=run['head_branch'].startswith('campaign-sync-test/')
    base=run['head_branch'] if synthetic else 'main';branch='campaign-repair/'+sig.lower()
    existing=api.get_file(path,base)
    receipt=api.get_file(result_path,base)
    if receipt:
        result=json.loads(base64.b64decode(receipt['content']))
        if result.get('status') in {'complete','superseded'}:return {'status':'terminal','request_id':rid}
    # A newer trusted checkout can prove scoped data already passes. Never suppress
    # infrastructure/test failures merely because a data-only check passes.
    if not existing and not synthetic and report['scope'] in {'characters','shops','checkpoint','final','handoffs'}:
        current=validate(root,report['scope'],report.get('phase','owners'))
        if not current['findings'] and api.head('main')==os.environ.get('COLLECTOR_SOURCE_SHA'):
            return {'status':'already_resolved','failure_signature':sig,'verified_head':api.head('main'),'original_run_id':run['id']}
    request={'request_id':rid,'lane':'sync-repair','source':{'kind':'validation_failure','checkpoint_id':'UNCHANGED-ADMIN-ONLY','commit_sha':run['head_sha'],'workflow_run_id':run['id'],'workflow_url':run['html_url']},
             'request':'Investigate this exact validation failure; propose only evidence-supported corrections on the existing repair branch.',
             'scope':report['affected_files'] or [run['path']],'output_owner_paths':report['affected_files'] or [run['path']],
             'priority':'high','advances_gameplay':False,'failure_signature':sig,'diagnostic':report,'repair_branch':branch,'base_branch':base,'synthetic':synthetic}
    if not existing:
        # Retry only metadata creation after a concurrent head update, never replay gameplay.
        for attempt in range(3):
            if api.get_file(path,base):break
            try:
                api.write(base,api.head(base),{path:json.dumps(request,indent=2)+'\n'},f'Queue campaign validation repair {sig}')
                break
            except (RuntimeError,urllib.error.HTTPError) as exc:
                if isinstance(exc,urllib.error.HTTPError) and exc.code not in {409,422}:raise
                if attempt==2:raise
    try:api.call('POST','git/refs',{'ref':'refs/heads/'+branch,'sha':api.head(base)})
    except urllib.error.HTTPError as exc:
        if exc.code!=422:raise
        api.head(branch) # A 422 must really mean this branch already exists.
    marker=f'{PREFIX}/sync-repair/attempts/{rid}.json'
    if not api.get_file(marker,branch):
        api.write(branch,api.head(branch),{marker:json.dumps({'request_id':rid,'request_path':path,'status':'awaiting_worker','failure_commit':run['head_sha'],'workflow_run_id':run['id'],'synthetic':synthetic},indent=2)+'\n'},f'Prepare isolated repair {sig}')
    # Deterministic branch is the primary dedup key; include closed PRs to avoid loops.
    prs=api.call('GET','pulls?state=all&head='+urllib.parse.quote(api.repo.split('/')[0]+':'+branch,safe='')+'&per_page=100')
    if prs:return {'status':'existing_pr','request_id':rid,'pr_url':prs[0]['html_url']}
    body=f'''Campaign repair request: `{path}`\n\nFailure signature: `{sig}`\nWorkflow: {run['html_url']}\nFailure commit: `{run['head_sha']}`\nAffected files: {', '.join(report['affected_files'])}\n\nRead `automation/handoffs/sync-repair/README.md`. This is a diagnostic draft, not a verified fix. Compare current owners with the failure commit; preserve newer gameplay. Commit supported fixes and separate test receipts here. Never merge automatically.\n\nSynthetic test: {synthetic}. Base branch: `{base}`. Synthetic fixtures must never merge into main.\n\nErrors:\n```json\n{json.dumps(report['findings'],indent=2)[:12000]}\n```\n'''
    pr=api.call('POST','pulls',{'title':'[CAMPAIGN-REPAIR] '+('Synthetic regression ' if synthetic else '')+sig,'head':branch,'base':base,'draft':True,'body':body})
    return {'status':'created','request_id':rid,'pr_url':pr['html_url']}

def main():
    api=API(os.environ['GITHUB_REPOSITORY'],os.environ['GH_TOKEN'])
    event=json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text());run=event.get('workflow_run')
    if run is None:run=api.call('GET','actions/runs/'+os.environ['FAILURE_RUN_ID'])
    try:
        result=enqueue(api,run,diagnose(api,run)) if eligible(run,api.repo) else {'status':'ignored'}
    except Exception as exc:
        result={'status':'blocked','original_run_id':run['id'],'original_commit':run['head_sha'],
                'error_type':type(exc).__name__,'error':str(exc),
                'next_trigger':'Retry the collector for this original run after resolving the error; reuse the same signature/request/PR.'}
        raise
    finally:
        Path('reports').mkdir(exist_ok=True);Path('reports/repair-collection.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
