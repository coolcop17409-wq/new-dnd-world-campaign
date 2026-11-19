#!/usr/bin/env python3
"""Generate idempotent Blackthorn daily accrual rows for explicitly closed days."""
from __future__ import annotations
import argparse
import csv
import json
import os
import tempfile
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "estate"
REPORT = ROOT / "reports" / "routine-accrual-preview.json"
EVENT_FIELDS = [
    "event_id", "estate", "effective_day", "event_type", "category",
    "reference_id", "liability_id", "receivable_id", "amount_gp",
    "cash_delta_gp", "liability_delta_gp", "receivable_delta_gp",
    "income_delta_gp", "expense_delta_gp", "inventory_id", "quantity_delta",
    "inventory_cost_delta_gp", "shipment_id", "accepted_quantity",
    "prerequisite_ref", "counterparty", "description", "evidence",
    "source_file", "source_row", "status", "reserved_quantity_delta",
    "in_transit_quantity_delta", "in_transit_cost_delta_gp", "inventory_verification_status",
]


def money(value):
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def load_rates():
    with (DATA / "blackthorn-rates.csv").open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load_existing():
    path = DATA / "events.csv"
    if not path.exists():
        return {}
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return {r.get("event_id", "").strip(): r for r in csv.DictReader(handle) if r.get("event_id", "").strip()}


def active(row, day):
    start = int(row.get("from_day") or 0)
    through = row.get("through_day", "")
    return start <= day and (not through or day <= int(through))


def generate(rates, last_closed_day, closed_through_day, existing=None):
    """Create one stable obligation row per category/day; never assumes an open day closed."""
    existing = existing or {}
    last_closed_day = int(last_closed_day)
    closed_through_day = int(closed_through_day)
    if closed_through_day < last_closed_day:
        raise ValueError("closed_through_day cannot move backward")
    events = []
    conflicts = []
    cumulative_upkeep_before = Decimal("0")
    for day in range(1, last_closed_day + 1):
        cumulative_upkeep_before += sum(
            (Decimal(str(r["rate_gp"])) for r in rates
             if r.get("type") == "Upkeep" and r.get("unit", "").lower() == "day" and active(r, day)),
            Decimal("0"),
        )
    previous_upkeep_posted = money(cumulative_upkeep_before)
    for day in range(last_closed_day + 1, closed_through_day + 1):
        daily = defaultdict(Decimal)
        for rate in rates:
            if rate.get("unit", "").strip().lower() != "day" or not active(rate, day):
                continue
            amount = Decimal(str(rate.get("rate_gp") or "0"))
            kind = rate.get("type", "").strip()
            if kind == "Payroll":
                family = rate.get("cost_family", "").strip()
                daily["management_payroll" if family == "Management" else "production_payroll"] += amount
            elif kind == "Upkeep":
                daily["upkeep"] += amount
        cumulative_upkeep_before += daily["upkeep"]
        upkeep_to_date = money(cumulative_upkeep_before)
        amounts = {
            "management_payroll": money(daily["management_payroll"]),
            "production_payroll": money(daily["production_payroll"]),
            "upkeep": upkeep_to_date - previous_upkeep_posted,
        }
        previous_upkeep_posted = upkeep_to_date
        for category, amount in amounts.items():
            if amount == 0:
                continue
            code = {"management_payroll": "MGMT-PAY", "production_payroll": "PROD-PAY", "upkeep": "UPKEEP"}[category]
            liability = {"management_payroll": "BT-PAYROLL-MANAGEMENT",
                         "production_payroll": "BT-PAYROLL-PRODUCTION",
                         "upkeep": "BT-UPKEEP"}[category]
            event_id = f"BT-ROUTINE-{code}-D{day}"
            row = {name: "" for name in EVENT_FIELDS}
            row.update({
                "event_id": event_id,
                "estate": "Blackthorn",
                "effective_day": str(day),
                "event_type": "routine_accrual",
                "category": category,
                "reference_id": f"DAY-{day}",
                "liability_id": liability,
                "amount_gp": str(amount),
                "liability_delta_gp": str(amount),
                "expense_delta_gp": str(amount) if category != "production_payroll" else "0",
                "description": f"Earned {category.replace('_', ' ')} for confirmed closed Day {day}.",
                "evidence": "Day closure explicitly confirmed; accrued from effective-dated Blackthorn rate register.",
                "source_file": "data/estate/blackthorn-rates.csv",
                "status": "posted",
            })
            if event_id in existing:
                saved = existing[event_id]
                if (saved.get("estate") != "Blackthorn"
                        or int(Decimal(saved.get("effective_day") or "0")) != day
                        or money(saved.get("liability_delta_gp") or "0") != amount
                        or saved.get("liability_id") != liability):
                    conflicts.append(f"{event_id}: existing row conflicts with generated accrual")
                continue
            events.append(row)
    totals = defaultdict(Decimal)
    for event in events:
        totals[event["category"]] += Decimal(event["amount_gp"])
    return {
        "status": "CHECK" if conflicts else "PASS",
        "last_closed_day": last_closed_day,
        "closed_through_day": closed_through_day,
        "event_count": len(events),
        "totals_gp": {k: str(money(v)) for k, v in totals.items()},
        "events": events,
        "conflicts": conflicts,
        "note": "Preview only. Rows are generated only through an explicitly confirmed closed day; they are not appended to events.csv by this script.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--closed-through-day", type=int)
    parser.add_argument("--apply", action="store_true",
                        help="append generated rows to the staging event ledger and advance the confirmed close")
    args = parser.parse_args()
    meta = json.loads((DATA / "routine-accrual-meta.json").read_text(encoding="utf-8"))
    through = args.closed_through_day if args.closed_through_day is not None else int(meta["last_confirmed_closed_day"])
    existing = load_existing()
    report = generate(load_rates(), int(meta["last_confirmed_closed_day"]), through, existing)
    applied_count = 0
    if args.apply:
        if args.closed_through_day is None:
            raise ValueError("--apply requires an explicit --closed-through-day confirmation")
        if report["status"] != "PASS":
            raise ValueError("cannot apply accruals while the preview has conflicts")
        event_path = DATA / "events.csv"
        with event_path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            fields = reader.fieldnames
            all_events = list(reader)
        known = {row.get("event_id", "").strip() for row in all_events}
        new_rows = [row for row in report["events"] if row["event_id"] not in known]
        if new_rows:
            all_events.extend(new_rows)
            event_path.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp = tempfile.mkstemp(prefix="events-", suffix=".csv", dir=event_path.parent)
            with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                writer.writerows(all_events)
            os.replace(tmp, event_path)
        meta["last_confirmed_closed_day"] = through
        meta_path = DATA / "routine-accrual-meta.json"
        meta_fd, meta_tmp = tempfile.mkstemp(prefix="routine-meta-", suffix=".json", dir=meta_path.parent)
        with os.fdopen(meta_fd, "w", encoding="utf-8") as handle:
            json.dump(meta, handle, indent=2)
            handle.write("\n")
        os.replace(meta_tmp, meta_path)
        applied_count = len(new_rows)
        report["applied_count"] = applied_count
        report["note"] = "Generated rows appended idempotently to the staging event ledger; Drive was not changed."
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report.get(k) for k in ("status", "last_closed_day", "closed_through_day", "event_count", "applied_count", "totals_gp", "conflicts", "note")}, indent=2))
    return 1 if report["status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
