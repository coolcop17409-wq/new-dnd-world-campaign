#!/usr/bin/env python3
"""Background adapter: exact immutable recovery chunks -> existing guarded sync.

Runs only from trusted main code; never adjudicates play, edits a chunk,
touches owners, merges a PR, or chooses V's actions.
"""
from __future__ import annotations
import base64, importlib.util, json, os, re, sys
from pathlib import Path
from automation.recovery_chunks import boundary_path, compatibility_journal
from automation.recovery_journal import digest
from automation.auto_sync_submit import submit

HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location("trusted_repair_api",HERE/"handoffs"/"sync-repair"/"collect.py")
MODULE=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
API=MODULE.API
LIVE="automation/recovery/active.json"
MODE="automation/recovery/mode.json"
RESULTS="automation/handoffs/play-sync/results/"

def get(api,path,sha):
    doc=api.get_file(path,sha)
    if doc is None:return None
    if doc.get("encoding")!="base64" or not doc.get("content"):
        raise ValueError("Invalid pinned file "+path)
    return base64.b64decode(doc["content"]).decode("utf-8")

def completed(api,request_id):
    text=get(api,RESULTS+request_id+".json","main")
    return json.loads(text) if text is not None else None

def prepare(api,source_sha,request_id):
    if not re.fullmatch("[0-9a-f]{40}",source_sha):
        raise ValueError("Missing source SHA for immutable boundary")
    text=get(api,boundary_path(request_id),source_sha)
    if text is None:raise ValueError("Immutable boundary missing")
    boundary=json.loads(text)
    if boundary.get("request_id")!=request_id:raise ValueError("Boundary path/ID mismatch")
    mode_text=get(api,MODE,source_sha)
    if mode_text is None or json.loads(mode_text).get("mode")!="chunked":
        return {"status":"not_activated"}
    parts={}
    for rec in boundary.get("records",[]):
        if not isinstance(rec,dict) or not isinstance(rec.get("path"),str):
            raise ValueError("Malformed immutable boundary record")
        parts[rec["path"]]=get(api,rec["path"],source_sha)
    journal=compatibility_journal(boundary,parts.get,{"schema_version":1,"entries":[]},
                                  json.loads(mode_text))
    return {"status":"prepared","request_id":request_id,
            "boundary":boundary,"journal":journal,"digest":digest(journal)}

def run(api,source_sha,request_id):
    prep=prepare(api,source_sha,request_id)
    if prep["status"]!="prepared":return prep
    receipt=completed(api,request_id)
    if receipt and receipt.get("status")=="complete" and receipt.get("owners_verified") is True:
        return {"status":"already_completed","request_id":request_id}
    ancestry=api.call("GET","compare/"+source_sha+"...main")
    if ancestry.get("status") not in ("identical","ahead"):
        raise ValueError("Boundary commit is not in current main ancestry")
    wanted=prep["digest"]
    head=api.head("main")
    current=json.loads(get(api,LIVE,head))
    mode=json.loads(get(api,MODE,head))
    if mode.get("mode")!="chunked":return {"status":"not_activated"}
    state=get(api,"campaign/continuity/campaign-state.md",head)
    if state is None:raise ValueError("Cannot establish authoritative current checkpoint")
    match=re.search(r"CURRENT EXACT PLAYED CHECKPOINT\s*[—–-]\s*([A-Za-z0-9-]+)",state)
    if not match or match.group(1)!=prep["boundary"]["source_checkpoint"]:
        raise ValueError("Current owner checkpoint does not match new chunk boundary source")

    if current.get("entries"):
        if digest(current)!=wanted:
            raise ValueError("Unfinished earlier sync: do not overwrite owner evidence")
        journal_head=head
    else:
        journal_head=api.write("main",head,{
            LIVE:json.dumps(prep["journal"],indent=2,ensure_ascii=False)+"\n"},
            "Assemble exact immutable recovery chunks for accepted-play handoff")
        if digest(json.loads(get(api,LIVE,journal_head)))!=wanted:
            raise ValueError("Compatibility journal readback mismatch")
    # Create PR directly: Actions-created pushes may not trigger a second Action.
    marker={"schema_version":1,"ready":True,
            "reason":prep["boundary"]["reason"],"request_id":request_id,
            "last_recovery_id":prep["boundary"]["last_recovery_id"],
            "destination_checkpoint":prep["boundary"]["destination_checkpoint"],
            "journal_commit":journal_head,"journal_digest":wanted}
    result=submit(api,journal_head,marker)
    if result.get("status") not in ("queued","existing_pr"):
        raise ValueError("Worker handoff was not durably queued: "+str(result))
    return {"status":"submitted","request_id":request_id,
            "source_commit":source_sha,"journal_commit":journal_head,
            "pr":result.get("url"),"entry_count":len(prep["journal"]["entries"])}

def changed_boundaries(api, event, source_sha):
    """Use GitHub's authoritative commit diff; push payload may omit commits."""
    if not re.fullmatch("[0-9a-f]{40}", source_sha):
        raise ValueError("Missing exact push commit")
    after=event.get("after")
    if after and after!=source_sha:
        raise ValueError("Push event after SHA disagrees with pinned checkout")
    before=event.get("before")
    if isinstance(before,str) and re.fullmatch("[0-9a-f]{40}",before) and before!="0"*40:
        changes=api.call("GET","compare/"+before+"..."+source_sha).get("files")
    else:
        changes=api.call("GET","commits/"+source_sha).get("files")
    if not isinstance(changes,list):
        raise ValueError("Cannot verify pushed file changes")
    if len(changes)>=300:
        raise ValueError("GitHub file comparison may be truncated")
    added=[]
    for item in changes:
        path=item.get("filename","")
        if not path.startswith("automation/recovery/boundaries/") or not path.endswith(".json"):
            continue
        if item.get("status")!="added":
            raise ValueError("Immutable boundary was modified/deleted instead of created: "+path)
        added.append(path)
    if len(added)!=1:
        raise ValueError("Expected exactly one newly added boundary, found "+str(len(added)))
    return added[0]

def main():
    output={"status":"not_started"}
    try:
        api=API(os.environ["GITHUB_REPOSITORY"],os.environ["GITHUB_TOKEN"])
        event=json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
        path=changed_boundaries(api,event,os.environ["GITHUB_SHA"])
        output=run(api,os.environ["GITHUB_SHA"],Path(path).stem)
        print(json.dumps(output,indent=2))
    except Exception as exc:
        output={"status":"blocked","reason":str(exc),
                "source_commit":os.environ.get("GITHUB_SHA")}
        print(json.dumps(output,indent=2),file=sys.stderr)
        raise
    finally:
        Path("reports").mkdir(exist_ok=True)
        Path("reports/chunk-bridge-status.json").write_text(json.dumps(output,indent=2)+"\n")

if __name__=="__main__":main()
