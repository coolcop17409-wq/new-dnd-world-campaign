#!/usr/bin/env python3
"""Source-based Blackthorn rolling-period tax preview and explicit assessment posting."""
from __future__ import annotations
import argparse
import csv
import json
import os
import tempfile
from decimal import Decimal
from pathlib import Path

from blackthorn_rules import accrue_daily_rates, blackthorn_tax_assessment, money
from blackthorn_operations import read_register, dec

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "estate"
PROPERTY = ROOT / "trackers" / "csv" / "property"
REPORT = ROOT / "reports" / "blackthorn-tax.json"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def tax_periods(schedule):
    periods = []
    for row in schedule:
        period_id = (row.get("Task / settlement ID") or "").strip()
        if not period_id.startswith("TAX-"):
            continue
        try:
            start = int(period_id.split("-", 1)[1])
            due = int(dec(row.get("Planned day", "0")))
        except (ValueError, ArithmeticError):
            continue
        if due <= start:
            continue
        periods.append({
            "period_id": period_id,
            "start_day": start,
            "end_day": due - 1,
            "due_day": due,
            "liability_id": "",
        })
    periods.sort(key=lambda p: p["due_day"])
    return periods


def actual_profit_delta(events, *, start_day, through_day, exclusive_start=False):
    income = Decimal("0")
    expenses = Decimal("0")
    for row in events:
        if (row.get("estate") or "").strip() != "Blackthorn":
            continue
        if (row.get("status") or "").strip().lower() != "posted":
            continue
        try:
            day = int(dec(row.get("effective_day", "0")))
        except (ValueError, ArithmeticError):
            continue
        if day > through_day or (day <= start_day if exclusive_start else day < start_day):
            continue
        event_type = (row.get("event_type") or "").strip().lower()
        category = (row.get("category") or "").strip().lower()
        if event_type == "routine_accrual":
            # Management and upkeep are rebuilt from effective-dated source rates below.
            # Production payroll is capitalized into COGS or idle loss, never deducted twice.
            continue
        if event_type in {"tax_assessment", "tax_adjustment", "tax_payment"}:
            continue
        income += dec(row.get("income_delta_gp", "0"))
        expenses += dec(row.get("expense_delta_gp", "0"))
    return income, expenses


def calculate_tax_report(events, rates, periods, config, through_day):
    """Calculate source-rule taxable bases through a confirmed closed day.

    For the first period, the verified Day 230 taxable base is the starting
    checkpoint. Later periods start at zero and use only realized activity in
    their own day window. Management payroll and upkeep are recomputed from
    effective-dated source rates, matching the workbook formula.
    """
    checkpoint_day = int(config["source_checkpoint_day"])
    through_day = int(through_day)
    if through_day < checkpoint_day:
        raise ValueError("through_day cannot precede the verified tax checkpoint")
    report_periods = []
    for period in periods:
        start = int(period["start_day"])
        end = int(period["end_day"])
        current_through = min(through_day, end)
        first = period["period_id"] == config["source_period_id"]
        source_base = dec(config["source_taxable_base_gp"]) if first else Decimal("0")
        if current_through < start:
            report_periods.append({
                **period, "through_day": None, "taxable_base_gp": None,
                "assessment_estimate_gp": None, "period_closed": False,
                "note": "Period has not started.",
            })
            continue
        if first:
            lower = max(checkpoint_day + 1, start)
            opening_day = int(config.get("source_opening_day", 182))
            source_base = dec(config["source_taxable_base_gp"])
            actual_start = checkpoint_day
            exclusive_start = True
        else:
            lower = max(start, int(config.get("source_opening_day", 182)) + 1)
            opening_day = int(config.get("source_opening_day", 182))
            source_base = Decimal("0")
            actual_start = start
            exclusive_start = False
        if current_through < lower:
            management = upkeep = Decimal("0")
        else:
            management_rows = [r for r in rates
                               if r.get("type") == "Payroll"
                               and r.get("cost_family") == "Management"]
            upkeep_rows = [r for r in rates if r.get("type") == "Upkeep"]
            management = accrue_daily_rates(
                management_rows, opening_day, lower, current_through, "Payroll"
            )
            upkeep = accrue_daily_rates(
                upkeep_rows, opening_day, lower, current_through, "Upkeep"
            )
        income, expenses = actual_profit_delta(
            events, start_day=actual_start, through_day=current_through,
            exclusive_start=exclusive_start,
        )
        taxable_base = money(source_base + income - expenses - management - upkeep)
        assessment = blackthorn_tax_assessment(taxable_base, Decimal(str(config["tax_rate"])))
        closed = through_day >= end
        report_periods.append({
            **period,
            "through_day": current_through,
            "actual_income_gp": str(money(income)),
            "actual_expenses_gp": str(money(expenses)),
            "management_payroll_gp": str(money(management)),
            "upkeep_gp": str(money(upkeep)),
            "taxable_base_gp": str(taxable_base),
            "assessment_estimate_gp": str(assessment),
            "period_closed": closed,
        })
    return {
        "status": "PASS",
        "through_day": through_day,
        "source_checkpoint_day": checkpoint_day,
        "periods": report_periods,
        "note": "Preview uses posted actual events and source effective-dated rates. A scheduled due day alone does not assess or pay tax.",
    }


def assessment_event(period, delta, closed_through_day, prior_assessed):
    delta = money(delta)
    if delta == 0:
        return None
    period_id = period["period_id"]
    first_assessment = prior_assessed == 0
    effective_day = int(period["end_day"]) if first_assessment else int(closed_through_day)
    event_type = "tax_assessment" if first_assessment else "tax_adjustment"
    event_id = (f"BT-TAX-ASSESS-{period_id}-D{effective_day}" if first_assessment
                else f"BT-TAX-ADJUST-{period_id}-D{effective_day}")
    return {
        "event_id": event_id,
        "estate": "Blackthorn",
        "effective_day": str(effective_day),
        "event_type": event_type,
        "category": "income_tax",
        "reference_id": period_id,
        "liability_id": period["liability_id"],
        "amount_gp": str(abs(delta)),
        "liability_delta_gp": str(delta),
        "description": f"{period_id} tax assessment adjustment; target period assessment updated from realized results.",
        "evidence": f"Explicit close through Day {closed_through_day}; source tax period {period['start_day']}–{period['end_day']} recalculated from posted actual activity and effective-dated rates.",
        "source_file": "reports/blackthorn-tax.json",
        "status": "posted",
    }


def prior_period_assessment(events, period, config):
    """Include source-linked daily accruals as well as period-linked assessments.

    Older authorized daily tax legs retain their source-event reference, while
    the exact liability ID identifies the bill. Payments do not reduce the
    assessment, and a row matching both keys is counted only once.
    """
    baseline = (dec(config["source_assessment_gp"])
                if period["period_id"] == config["source_period_id"]
                else Decimal("0"))
    return baseline + sum(
        (dec(row.get("liability_delta_gp", "0")) for row in events
         if row.get("estate") == "Blackthorn"
         and (row.get("status") or "").strip().lower() == "posted"
         and (row.get("event_type") or "").strip().lower()
             in {"tax_assessment", "tax_adjustment"}
         and (row.get("reference_id") == period["period_id"]
              or (period.get("liability_id")
                  and row.get("liability_id") == period["liability_id"]))),
        Decimal("0"),
    )


def append_rows(path, additions):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames
        existing = list(reader)
    known = {row.get("event_id", "").strip() for row in existing}
    for row in additions:
        if row["event_id"] in known:
            raise ValueError(f"tax event ID already exists with a different calculation: {row['event_id']}")
        existing.append(row)
        known.add(row["event_id"])
    fd, temp_path = tempfile.mkstemp(prefix="blackthorn-tax-", suffix=".csv", dir=path.parent)
    with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(existing)
    os.replace(temp_path, path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--closed-through-day", type=int)
    parser.add_argument("--apply", action="store_true",
                        help="post assessments for periods explicitly confirmed closed")
    args = parser.parse_args()
    snapshot = json.loads((DATA / "snapshot-meta.json").read_text(encoding="utf-8"))
    accrual_meta = json.loads((DATA / "routine-accrual-meta.json").read_text(encoding="utf-8"))
    config = json.loads((DATA / "blackthorn-tax-config.json").read_text(encoding="utf-8"))
    through = (args.closed_through_day if args.closed_through_day is not None
               else int(accrual_meta.get("last_accounted_day", accrual_meta["last_confirmed_closed_day"])))
    if through > int(accrual_meta["last_confirmed_closed_day"]) and args.apply:
        raise ValueError("tax assessment posting requires recurring accruals confirmed through the same closed day")
    operation_report = json.loads((ROOT / "reports" / "blackthorn-operations.json").read_text(encoding="utf-8"))
    if operation_report.get("status") != "PASS":
        raise ValueError("Blackthorn operation replay must pass before tax calculation")
    if int(operation_report.get("checkpoint_day", -1)) != int(snapshot["snapshot_day"]):
        raise ValueError("Blackthorn operation replay is stale against the tax snapshot")
    operations = read_register(DATA / "blackthorn-operations-events.csv", "Event ID")
    if operation_report.get("staging_event_ids", []) != [r.get("Event ID", "").strip() for r in operations]:
        raise ValueError("Blackthorn operation replay is stale against staged operation IDs")
    events = read_csv(DATA / "events.csv")
    events.extend(operation_report.get("ledger_events", []))
    if len({(r.get("event_id") or "").strip() for r in events}) != len(events):
        raise ValueError("duplicate event IDs across estate and Blackthorn operation journals")
    rates = read_csv(DATA / "blackthorn-rates.csv")
    schedule = read_register(PROPERTY / "blackthorn-schedule.csv", "Task / settlement ID")
    periods = tax_periods(schedule)
    # The opening period's current assessment is already included in Day 230 liabilities.
    for period in periods:
        if period["period_id"] == config["source_period_id"]:
            period["liability_id"] = config["source_liability_id"]
        else:
            period["liability_id"] = f"BT-{period['period_id']}"
    report = calculate_tax_report(events, rates, periods, config, through)
    existing_tax = [row for row in events
                    if (row.get("event_type") or "").strip().lower() in {"tax_assessment", "tax_adjustment"}]
    for period, calculated in zip(periods, report["periods"]):
        if not calculated.get("period_closed"):
            continue
        prior_assessed = prior_period_assessment(existing_tax, period, config)
        target = dec(calculated["assessment_estimate_gp"])
        delta = money(target - prior_assessed)
        calculated["prior_assessed_gp"] = str(money(prior_assessed))
        calculated["assessment_delta_gp"] = str(delta)
        calculated["assessment_event"] = assessment_event(period, delta, through, prior_assessed)
    posted_count = 0
    if args.apply:
        eligible = [p["assessment_event"] for p in report["periods"]
                    if p.get("period_closed") and p.get("assessment_event")]
        if eligible:
            ids = {row.get("event_id", "").strip() for row in events}
            collision = [r["event_id"] for r in eligible if r["event_id"] in ids]
            if collision:
                raise ValueError(f"tax assessment event IDs already exist: {collision}")
            append_rows(DATA / "events.csv", eligible)
            posted_count = len(eligible)
        report["posted_count"] = posted_count
        report["note"] = "Assessment deltas posted to the staging ledger after explicit close confirmation. No tax payment was posted."
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "through_day": report["through_day"],
                      "periods": [{"period_id": p["period_id"], "taxable_base_gp": p.get("taxable_base_gp"),
                                   "assessment_estimate_gp": p.get("assessment_estimate_gp"),
                                   "assessment_delta_gp": p.get("assessment_delta_gp"),
                                   "period_closed": p.get("period_closed")} for p in report["periods"]],
                      "posted_count": posted_count, "note": report["note"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

