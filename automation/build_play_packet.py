#!/usr/bin/env python3
"""Generate a bounded, nonauthoritative LIVE PLAY packet from current GitHub owners.

This script NEVER advances play or changes campaign state. Run after dashboard
generation when a checkpoint/character event changes.
"""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "campaign" / "continuity" / "campaign-state.md"
DASHBOARD = ROOT / "dashboard" / "dashboard.json"
OUTPUT = ROOT / "runtime" / "PLAY_NOW.md"
DAY = re.compile(r"^CAMPAIGN_STATE\s*[—–-]\s*DAY\s+(\d+)\b", re.M | re.I)

def active_checkpoint(text: str) -> tuple[int, str]:
    hit = DAY.search(text)
    if not hit:
        raise ValueError("Active CAMPAIGN_STATE day heading missing")
    section = text[hit.start():].split("\n\n## Earlier checkpoints", 1)[0].strip()
    # An explicit accepted correction can keep the same scene while replacing
    # a resource fact. Preserve its current paragraph, not the labelled old pause.
    corrected = "LATEST PLAYER CORRECTION" in section and "CURRENT PLAYABLE CHECKPOINT" in section
    if corrected:
        section = section.split("\n\nHISTORICAL PRE-CORRECTION CHECKPOINT", 1)[0].strip()
    if not section or ("CURRENT EXACT PLAYED CHECKPOINT" not in section and not corrected):
        raise ValueError("Current played checkpoint marker missing")
    if len(section) > 12000:
        raise ValueError("Live checkpoint too large; archive superseded checkpoints first")
    return int(hit.group(1)), section

def make_packet(state_text: str, dashboard_text: str) -> str:
    day, section = active_checkpoint(state_text)
    dash = json.loads(dashboard_text)
    if dash.get("campaign_day") != day:
        raise ValueError(f"Dashboard day {dash.get('campaign_day')} disagrees with checkpoint day {day}")
    if dash.get("tracker_status") != "PASS":
        raise ValueError("Cannot publish a play packet from an unverified tracker dashboard")
    lines = [
        "# LIVE PLAY — generated fast packet",
        "",
        "**Read-only convenience, NOT an authority or a record of new events.**",
        f"Source: `campaign/continuity/campaign-state.md` (SHA256 `{hashlib.sha256(state_text.encode('utf-8')).hexdigest()}`).",
        f"Dashboard SHA256: `{hashlib.sha256(dashboard_text.encode('utf-8')).hexdigest()}`.",
        f"Confirmed campaign day: **{day}**.",
        "",
        "## Exact playable checkpoint (verbatim from owner)",
        "",
        section,
        "",
        "## Current character counters (CSV baselines + posted event overlay)",
        "",
        "Snapshot values support lookups; rule interpretations, contextual conditions, custody and exceptions remain in the owning records.",
        "",
    ]
    party = dash.get("party", [])
    if not party:
        raise ValueError("Dashboard has no party character entries")
    for person in party:
        name = str(person.get("name") or "").strip()
        if not name:
            raise ValueError("Character name missing")
        line = f"- **{name}** — HP {person.get('hp', '?')}/{person.get('max_hp', '?')}; AC {person.get('ac', '?')}; level {person.get('level') or '?'}."
        purse = person.get("purse")
        if isinstance(purse, dict) and name.lower() == "valenthia":
            line += f" Personal purse {purse.get('gp', '?')} gp {purse.get('sp', '?')} sp {purse.get('cp', '?')} cp."
        lines.append(line)
        resources = person.get("resources") or []
        listed = []
        for resource in resources:
            label = str(resource.get("name") or "").strip()
            current = str(resource.get("current") or "").strip()
            maximum = str(resource.get("max") or "").strip()
            if label and current and maximum:
                listed.append(f"{label} {current}/{maximum}")
        if listed:
            lines.append("  - Resources: " + "; ".join(listed))
    lines.extend([
        "",
        "## Fast-play guardrails",
        "",
        "Use the exact player-pending choice above. V controls nondelegated speech and actions. Independent NPCs roll genuinely; do not invent dice or outcomes.",
        "Keep tactics and unsynced event deltas in conversation until a natural synchronization boundary. No per-round GitHub refresh or comprehensive estate audit.",
        "For missing/changed facts read scoped RULES, DM prep, journal or owning trackers. For a stale/contradictory packet, inspect authoritative CAMPAIGN_STATE and dashboard before action.",
        "Scheduled workflows, real-world time and generated views never advance game time or create an event.",
        "",
    ])
    return "\n".join(lines)

def main() -> None:
    result = make_packet(STATE.read_text(encoding="utf-8"), DASHBOARD.read_text(encoding="utf-8"))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != result:
        OUTPUT.write_text(result, encoding="utf-8")
    print(f"Generated fast play packet: {OUTPUT}")

if __name__ == "__main__":
    main()
