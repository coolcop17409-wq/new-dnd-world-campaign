"""Lightweight, PRIVATE/LOCAL live-DM performance trace analyzer.

This does not intercept ChatGPT hidden reasoning or other chats. It accepts
explicitly provided timing/connector metadata; never publishes play records.
No GitHub operations, RNG, changes to RPG canon or gameplay write targets.
"""
from __future__ import annotations
import argparse, collections, json, sys
from pathlib import Path

KINDS={"turn_start","turn_end","github_read","github_write",
       "recovery_create","recovery_readback","dice","scene_logic",
       "source_lookup","ci_poll","other"}
READ_KINDS={"github_read","source_lookup"}
WRITE_KINDS={"github_write","recovery_create"}

def _valid(row):
    if not isinstance(row,dict) or row.get("kind") not in KINDS:
        raise ValueError("Invalid performance event kind")
    if not isinstance(row.get("turn_id"),str) or not row["turn_id"].strip():
        raise ValueError("Performance event needs stable turn_id")
    t=row.get("time_ms")
    if not isinstance(t,(int,float)) or isinstance(t,bool) or t<0:
        raise ValueError("Performance event needs actual nonnegative time_ms")
    b=row.get("bytes",0)
    if not isinstance(b,int) or isinstance(b,bool) or b<0:
        raise ValueError("bytes must be a nonnegative integer")
    if row["kind"] in READ_KINDS and not isinstance(row.get("path"),str):
        raise ValueError("Read event needs a path; do not embed source content")
    if any(key in row for key in ("source_evidence","message_text","raw_response","file_content")):
        raise ValueError("Do not put player statements, secrets, or full content in performance logs")
    return row

def summarize(rows):
    grouped=collections.defaultdict(list)
    for row in rows:
        row=_valid(row)
        grouped[row["turn_id"]].append(row)
    result=[]
    for ident,events in grouped.items():
        begins=[x["time_ms"] for x in events if x["kind"]=="turn_start"]
        ends=[x["time_ms"] for x in events if x["kind"]=="turn_end"]
        complete=len(begins)==len(ends)==1 and ends[0]>=begins[0]
        seen=set()
        reads=0; duplicates=0; read_bytes=0; missing_sha=0
        writes=0; recovery=0; readbacks=0; ci=0; dice=0
        by_path=collections.Counter()
        for x in events:
            kind=x["kind"]
            if kind in READ_KINDS:
                reads+=1
                path=x["path"]
                by_path[path]+=1
                revision=x.get("revision")
                if not revision:missing_sha+=1
                key=(path,revision)
                if key in seen:duplicates+=1
                seen.add(key)
                read_bytes+=x.get("bytes",0)
            if kind in WRITE_KINDS:writes+=1
            if kind=="recovery_create":recovery+=1
            if kind=="recovery_readback":readbacks+=1
            if kind=="ci_poll":ci+=1
            if kind=="dice":dice+=1
        report={"turn_id":ident,"observed_duration_ms":(ends[0]-begins[0] if complete else None),
                "complete":complete,"github_source_reads":reads,"duplicate_same_revision_reads":duplicates,
                "read_bytes":read_bytes,"unversioned_reads":missing_sha,
                "all_writes":writes,"recovery_creates":recovery,
                "recovery_readbacks":readbacks,"ci_polls":ci,"dice_events":dice,
                "most_read_paths":[{"path":p,"count":n} for p,n in by_path.most_common(5)],
                "flags":[]}
        if not complete:report["flags"].append("time_unverified")
        if duplicates:report["flags"].append("repeated_unchanged_source")
        if ci:report["flags"].append("foreground_ci_poll")
        if writes>1:report["flags"].append("multiple_foreground_writes")
        if recovery>1:report["flags"].append("multiple_recovery_creates")
        if recovery and readbacks!=recovery:
            report["flags"].append("missing_recovery_readback")
        result.append(report)
    return {"schema_version":1,"source":"explicit_user_or_local_tool_trace_only",
            "turn_count":len(result),"turns":sorted(result,key=lambda x:x["turn_id"])}

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jsonl",required=True,help="Explicit metadata-only trace path or - for stdin")
    parser.add_argument("--output",help="Optional local JSON output; do NOT commit per-turn")
    args=parser.parse_args(argv)
    if args.jsonl=="-":lines=sys.stdin.readlines()
    else:lines=Path(args.jsonl).read_text(encoding="utf-8").splitlines()
    rows=[json.loads(line) for line in lines if line.strip()]
    report=summarize(rows)
    data=json.dumps(report,indent=2,ensure_ascii=False)+"\n"
    if args.output:Path(args.output).write_text(data,encoding="utf-8")
    else:sys.stdout.write(data)

if __name__=="__main__":main()
