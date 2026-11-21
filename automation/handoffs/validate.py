#!/usr/bin/env python3
"""Validate GitHub handoff request/receipt identity and nonplay boundaries."""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "automation" / "handoffs"
LANES = ("shops", "quests", "estates", "atlas", "maintenance")
ID = re.compile(r"^HANDOFF-[A-Z0-9]+(?:-[A-Z0-9]+){3,}$")
TERMINAL = {"complete", "superseded"}
STATUSES = TERMINAL | {"blocked", "partial"}

def check_string(value, label, findings):
    if not isinstance(value, str) or not value.strip():
        findings.append(f"{label}: required nonempty string")

def check_list(value, label, findings):
    if not isinstance(value, list) or not value or any(not isinstance(v, str) or not v.strip() for v in value):
        findings.append(f"{label}: required list of nonempty strings")

def check(base: Path = BASE):
    findings = []
    seen = set()
    req = {}
    for lane in LANES:
        for file in sorted((base / "requests" / lane).glob("*.json")):
            try:
                item = json.loads(file.read_text(encoding="utf-8"))
            except (ValueError, OSError) as exc:
                findings.append(f"{file}: invalid JSON: {exc}")
                continue
            rid = item.get("request_id", "")
            if not ID.fullmatch(rid) or file.name != f"{rid}.json":
                findings.append(f"{file}: invalid or mismatched request_id")
            if rid in seen:
                findings.append(f"{rid}: duplicate request ID")
            seen.add(rid)
            if item.get("lane") != lane:
                findings.append(f"{rid}: wrong lane {item.get('lane')}")
            source = item.get("source")
            if not isinstance(source, dict):
                findings.append(f"{rid}: missing source object")
            else:
                check_string(source.get("kind"), f"{rid}.source.kind", findings)
                check_string(source.get("checkpoint_id"), f"{rid}.source.checkpoint_id", findings)
                day = source.get("campaign_day")
                if day is not None and (type(day) is not int or day < 0):
                    findings.append(f"{rid}: invalid optional source campaign_day")
            check_string(item.get("request"), f"{rid}.request", findings)
            check_list(item.get("scope"), f"{rid}.scope", findings)
            check_list(item.get("output_owner_paths"), f"{rid}.output_owner_paths", findings)
            if item.get("priority") not in {"normal", "high"}:
                findings.append(f"{rid}: priority must be normal or high")
            if item.get("advances_gameplay") is not False:
                findings.append(f"{rid}: a handoff cannot advance gameplay")
            req[rid] = lane
    for lane in LANES:
        for file in sorted((base / "results" / lane).glob("*.json")):
            try:
                item = json.loads(file.read_text(encoding="utf-8"))
            except (ValueError, OSError) as exc:
                findings.append(f"{file}: invalid JSON: {exc}")
                continue
            rid = item.get("request_id", "")
            if file.name != f"{rid}.json" or req.get(rid) != lane:
                findings.append(f"{file}: result has no matching request in lane")
            if item.get("lane") != lane:
                findings.append(f"{rid}: result lane mismatch")
            status = item.get("status")
            if status not in STATUSES:
                findings.append(f"{rid}: invalid result status {status}")
            check_string(item.get("summary"), f"{rid}.summary", findings)
            if status == "complete":
                check_list(item.get("owner_refs"), f"{rid}.owner_refs", findings)
                check_string(item.get("verified_commit"), f"{rid}.verified_commit", findings)
                sha = item.get("verified_commit", "")
                if isinstance(sha, str) and not re.fullmatch(r"[0-9a-f]{40}", sha):
                    findings.append(f"{rid}: verified_commit must be an exact 40-hex SHA")
            if status in {"blocked", "partial"}:
                check_string(item.get("blocker"), f"{rid}.blocker", findings)
                check_string(item.get("next_trigger"), f"{rid}.next_trigger", findings)
    return findings

if __name__ == "__main__":
    errors = check()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        sys.exit(1)
    print("Handoff requests and results: PASS")
