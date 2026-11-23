"""Immutable per-response recovery chunks and verified legacy-compatibility boundary.

A chunk is one original accepted_play entry, never a transformed or summarized
record. All gameplay and random rolls must have been accepted BEFORE creation.
No read/transform in this module advances game time or changes V decisions.
"""
from __future__ import annotations
import json
import re
from pathlib import Path
from automation.recovery_journal import check, digest

PREFIX="automation/recovery/chunks/"
BOUNDARY_DIR="automation/recovery/boundaries/"
ID=re.compile(r"^PLAY-REC-D(?P<day>\d{3,4})-[A-Z0-9-]+$")
REQUEST_ID=re.compile(r"^PLAY-[A-Z0-9-]+$")
REASONS=frozenset(("combat_end","significant_exploration","qualifying_rest",
"major_transaction","quest_milestone","npc_milestone","substantive_exchanges",
"explicit_sync","pause","chat_handoff"))

def chunk_path(entry):
    rid=entry.get("request_id") if isinstance(entry,dict) else None
    matched=ID.fullmatch(str(rid))
    if not matched:raise ValueError("Recovery chunk requires a stable campaign-day request ID")
    return PREFIX+"D"+matched.group("day")+"/"+rid+".json"

def chunk_content(entry):
    check({"schema_version":1,"entries":[entry]})
    chunk_path(entry)
    return json.dumps(entry,indent=2,ensure_ascii=False)+"\n"

def validate_chunk(path,content,expected_digest):
    if not isinstance(content,str) or not isinstance(expected_digest,str):
        raise ValueError("Invalid chunk payload/digest")
    entry=json.loads(content)
    if path!=chunk_path(entry):
        raise ValueError("Chunk filename and accepted entry ID mismatch")
    check({"schema_version":1,"entries":[entry]})
    if digest(entry)!=expected_digest:
        raise ValueError("Immutable chunk digest mismatch; refuse silent edit")
    return entry

def make_boundary(entries,request_id,reason):
    if not entries or reason not in REASONS or not REQUEST_ID.fullmatch(request_id):
        raise ValueError("A real boundary needs accepted entries, stable ID and valid reason")
    check({"schema_version":1,"entries":entries})
    records=[]
    for i,entry in enumerate(entries):
        if i and entries[i-1]["destination_checkpoint"]!=entry["source_checkpoint"]:
            raise ValueError("Recovery checkpoint chain gap")
        records.append({"path":chunk_path(entry),"digest":digest(entry)})
    return {"schema_version":2,"ready":True,"request_id":request_id,
            "reason":reason,"source_checkpoint":entries[0]["source_checkpoint"],
            "destination_checkpoint":entries[-1]["destination_checkpoint"],
            "last_recovery_id":entries[-1]["request_id"],"records":records}

def validate_boundary(boundary,loader):
    if (not isinstance(boundary,dict) or boundary.get("schema_version")!=2
        or boundary.get("ready") is not True
        or boundary.get("reason") not in REASONS
        or not isinstance(boundary.get("request_id"),str)
        or not REQUEST_ID.fullmatch(boundary["request_id"])
        or not isinstance(boundary.get("records"),list)
        or not boundary["records"]):
        raise ValueError("Invalid explicit chunk boundary")
    entries=[];paths=set()
    for row in boundary["records"]:
        if not isinstance(row,dict) or set(row)!={"path","digest"}:
            raise ValueError("Invalid chunk manifest row")
        path=row["path"]
        if not isinstance(path,str) or not path.startswith(PREFIX) or path in paths:
            raise ValueError("Duplicate or invalid recovery chunk path")
        paths.add(path)
        raw=loader(path)
        if raw is None:raise ValueError("Missing immutable recovery chunk: "+path)
        entry=validate_chunk(path,raw,row["digest"])
        if entries and entries[-1]["destination_checkpoint"]!=entry["source_checkpoint"]:
            raise ValueError("Out-of-order or incomplete recovery checkpoint chain")
        entries.append(entry)
    if (entries[0]["source_checkpoint"]!=boundary.get("source_checkpoint") or
        entries[-1]["destination_checkpoint"]!=boundary.get("destination_checkpoint") or
        entries[-1]["request_id"]!=boundary.get("last_recovery_id")):
        raise ValueError("Boundary does not identify exact first/last accepted play")
    check({"schema_version":1,"entries":entries})
    return entries

def compatibility_journal(boundary,loader,existing,mode):
    """Fail closed if old live journal is still pending or cutover not approved."""
    if (not isinstance(mode,dict) or mode.get("schema_version")!=2
        or mode.get("mode")!="chunked"):
        raise ValueError("Chunk mode has not been safely activated")
    check(existing)
    if existing["entries"]:
        raise ValueError("Old recovery journal still has unsynchronized evidence")
    entries=validate_boundary(boundary,loader)
    trigger={k:boundary[k] for k in
             ("ready","reason","request_id","last_recovery_id","destination_checkpoint")}
    return {"schema_version":1,"entries":entries,"sync_trigger":trigger}

def boundary_path(request_id):
    if not isinstance(request_id,str) or not REQUEST_ID.fullmatch(request_id):
        raise ValueError("Invalid immutable boundary ID")
    return BOUNDARY_DIR+request_id+".json"

def read_chunks(root,boundary):
    """Only explicitly listed pinned files, never the full history or archive."""
    return validate_boundary(boundary,lambda path:(Path(root)/path).read_text(encoding="utf-8")
        if (Path(root)/path).is_file() else None)
