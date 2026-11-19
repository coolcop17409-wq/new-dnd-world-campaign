#!/usr/bin/env python3
"""List Magic Shops contacts whose recorded reviews are due by a confirmed day.

This does not roll or resolve campaign turnover. The DM follows the Magic Shops
Rules, executes genuine RNG when needed, and writes the actual outcome once.
"""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOPS = ROOT / "trackers" / "csv" / "magic-shops"
REPORT = ROOT / "reports" / "magic-shop-review-queue.json"


def review_queue(dealers, campaign_day=None):
    if campaign_day is None:
        return {
            "status": "PASS",
            "campaign_day": None,
            "due_count": None,
            "due_reviews": [],
            "unbound_count": 0,
            "note": "No campaign day supplied; no turnover is inferred or resolved.",
        }
    day = int(campaign_day)
    due = []
    unbound = 0
    for row in dealers:
        raw = str(row.get("Next due", "")).strip()
        if not raw:
            continue
        try:
            next_due = int(raw)
        except ValueError:
            unbound += 1
            continue
        if next_due <= day:
            due.append({
                "settlement": row.get("Settlement", "").strip(),
                "dealer": row.get("Dealer", "").strip(),
                "due_day": next_due,
                "last_review": row.get("Last review / turnover", "").strip(),
                "status": row.get("Status", "").strip(),
                "review_question": row.get("Review question · preparation", "").strip(),
            })
    due.sort(key=lambda item: (item["due_day"], item["settlement"], item["dealer"]))
    return {
        "status": "PASS",
        "campaign_day": day,
        "due_count": len(due),
        "due_reviews": due,
        "unbound_count": unbound,
        "note": "Queue only. Apply the Magic Shops Rules once for each elapsed due review; this script does not roll, reveal, or post turnover.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--campaign-day", type=int)
    args = parser.parse_args()
    with (SHOPS / "dealers.csv").open(encoding="utf-8-sig", newline="") as handle:
        dealers = list(csv.DictReader(handle))
    report = review_queue(dealers, args.campaign_day)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
