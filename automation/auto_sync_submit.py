#!/usr/bin/env python3
"""Queue already accepted play from a pinned GitHub recovery journal boundary.

Does NOT adjudicate, write campaign owners, advance time, or merge PRs.
"""
from __future__ import annotations
import base64, importlib.util, json, os, re, sys, urllib.error, urllib.parse
from pathlib import Path
from automation.play_handoff import validate as validate_play
from automation.recovery_batch import build, verify
from automation.recovery_journal import check

HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location("trusted_repair_api", HERE/"handoffs"/"sync-repair"/"collect.py")
API_MODULE=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(API_MODULE)
API=API_MODULE.API
JOURNAL="automation/recovery/active.json"
REQUESTS="automation/handoffs/play-sync/requests"
RESULTS="automation/handoffs/play-sync/results"
REASONS={"combat_end","significant_exploration","qualifying_rest","major_transaction",
         "quest_milestone","npc_milestone","substantive_exchanges",
         "explicit_sync","pause","chat_handoff"}

class StaleBoundary(Exception):
    """Later accepted play supersedes an older sync marker."""

def ready_trigger(journal):
    check(journal)
    marker=journal.get("sync_trigger")
    if marker is None:return None
    if not isinstance(marker,dict) or marker.get("ready") is not True:
        raise ValueError("Invalid recovery sync marker")
    if marker.get("reason") not in REASONS:
        raise ValueError("No accepted natural sync boundary")
    rid=marker.get("request_id")
    if not isinstance(rid,str) or not re.fullmatch("PLAY-[A-Z0-9-]+",rid):
        raise ValueError("Invalid stable sync request ID")
    if not journal["entries"]:
        raise ValueError("Cannot sync an empty recovery journal")
    last=journal["entries"][-1]
    if marker.get("last_recovery_id")!=last["request_id"] or marker.get("destination_checkpoint")!=last["destination_checkpoint"]:
        raise StaleBoundary("Later accepted play follows a marked boundary")
    return marker

def file(api,path,ref):
    item=api.get_file(path,ref)
    if item is None:return None
    if item.get("encoding")!="base64" or not item.get("content"):
        raise ValueError("Cannot verify GitHub file: "+path)
    return base64.b64decode(item["content"]).decode("utf-8")

def pulls(api):
    all_prs=[]
    for page in range(1,11):
        part=api.call("GET",f"pulls?state=all&per_page=100&page={page}")
        all_prs.extend(part)
        if len(part)<100:return all_prs
    raise ValueError("Historical PR list truncated; do not invent empty prior requests")

def priors(api,prs):
    out=[];retired=[];seen=set()
    for pr in prs:
        title=pr.get("title","")
        if not title.startswith("[CAMPAIGN-SYNC] "):continue
        rid=title.split("] ",1)[1].strip()
        head=pr.get("head",{})
        if rid in seen or not head.get("ref","").startswith("campaign-sync/") or not head.get("sha"):
            raise ValueError("Invalid or duplicate historical sync PR")
        seen.add(rid)
        text=file(api,f"{REQUESTS}/{rid}.json",head["sha"])
        if text is None:raise ValueError("Missing historical request "+rid)
        item=json.loads(text)
        if item.get("request_id")!=rid or validate_play(item):
            raise ValueError("Invalid historical request "+rid)
        if item.get("mode")=="smoke_test":continue
        if item.get("mode")!="accepted_play":raise ValueError("Unknown transport mode")
        out.append(item)
        receipt=file(api,f"{RESULTS}/{rid}.json","main")
        if receipt:
            r=json.loads(receipt)
            if r.get("status")=="superseded":retired.append(r)
    return out,retired

def submit(api,source_commit):
    if not re.fullmatch("[0-9a-f]{40}",source_commit):
        raise ValueError("Need exact main source SHA")
    data=file(api,JOURNAL,source_commit)
    if data is None:raise ValueError("Pinned recovery journal missing")
    journal=json.loads(data)
    try:marker=ready_trigger(journal)
    except StaleBoundary:
        return {"status":"stale_marker","source_commit":source_commit}
    if marker is None:return {"status":"not_ready","source_commit":source_commit}
    status=api.call("GET",f"compare/{source_commit}...main")["status"]
    if status not in ("identical","ahead"):
        raise ValueError("Recovery commit is no longer on current main history")
    rid=marker["request_id"]
    prs=pulls(api)
    old=[p for p in prs if p.get("title")=="[CAMPAIGN-SYNC] "+rid]
    if old:return {"status":"existing_pr","request_id":rid,"url":old[0]["html_url"]}
    previous,supersessions=priors(api,prs)
    request=build(journal,rid,source_commit,previous,supersessions)
    if not verify(journal,request,previous,supersessions):
        raise ValueError("Pinned journal round trip failed")
    branch="campaign-sync/"+rid.lower()
    path=f"{REQUESTS}/{rid}.json"
    content=json.dumps(request,indent=2,ensure_ascii=False)+"\n"
    try:sha=api.head(branch)
    except urllib.error.HTTPError as exc:
        if exc.code!=404:raise
        sha=None
    if sha is not None:
        existing=file(api,path,sha)
        if existing is None or json.loads(existing)!=request:
            raise ValueError("Existing branch contains conflicting request")
    else:
        base=api.head("main")
        try:api.call("POST","git/refs",{"ref":"refs/heads/"+branch,"sha":base})
        except urllib.error.HTTPError as exc:
            if exc.code!=422:raise
            existing=file(api,path,api.head(branch))
            if existing is None or json.loads(existing)!=request:
                raise ValueError("Concurrent branch collision; preserve original")
        else:
            sha=api.write(branch,base,{path:content},"Queue pinned accepted-play recovery boundary")
    if file(api,path,api.head(branch))!=content:
        raise ValueError("Request branch readback failed")
    found=[p for p in pulls(api) if p.get("title")=="[CAMPAIGN-SYNC] "+rid]
    if found:return {"status":"existing_pr","request_id":rid,"url":found[0]["html_url"]}
    body=(f"Immutable accepted-play transport, DO NOT MERGE.\nRequest: {path}\n"
          f"Pinned recovery source: {source_commit}; reason: {marker['reason']}.\n"
          f"Events: {len(request['events'])}. Preserve all accepted rolls and choices.\n"
          "Use trusted main play-sync procedure; verify pinned journal and prior "
          "requests, write actual owners in causal order and checkpoint last, then "
          "independently verify and prune. No rerolls, unauthorized V actions or merges.")
    try:
        pr=api.call("POST","pulls",{"title":"[CAMPAIGN-SYNC] "+rid,
            "head":branch,"base":"main","draft":True,"body":body})
    except urllib.error.HTTPError as exc:
        if exc.code!=422:raise
        existing=[p for p in pulls(api) if p.get("title")=="[CAMPAIGN-SYNC] "+rid]
        if not existing:raise
        pr=existing[0]
    return {"status":"queued","request_id":rid,"url":pr["html_url"],
            "source_commit":source_commit,"event_count":len(request["events"])}

def main():
    result={"status":"not_started"}
    try:
        api=API(os.environ["GITHUB_REPOSITORY"],os.environ["GITHUB_TOKEN"])
        result=submit(api,os.environ["GITHUB_SHA"])
        print(json.dumps(result,indent=2))
    except Exception as exc:
        result={"status":"blocked","reason":str(exc),"source_commit":os.environ.get("GITHUB_SHA")}
        print(json.dumps(result,indent=2),file=sys.stderr)
        raise
    finally:
        Path("reports").mkdir(exist_ok=True)
        Path("reports/auto-sync-submission.json").write_text(json.dumps(result,indent=2)+"\n")

if __name__=="__main__":main()
