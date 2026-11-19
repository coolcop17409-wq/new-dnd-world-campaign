#!/usr/bin/env python3
"""Audit estate summary snapshots and surface due schedule items.

This first staging automation reads the existing property workbook's CSV snapshots.
It does not post transactions, accrue forecasts, or modify campaign ledgers.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROPERTY = ROOT / "trackers" / "csv" / "property"
REPORT = ROOT / "reports" / "estate-review.md"
TASK_SUPERSESSIONS = ROOT / "data" / "estate" / "task-supersessions.csv"

ESTATES = {
    "Miregate": {
        "path": "miregate-overview.csv",
        "cash": ("estate cash",),
        "available": ("available after actual liabilities",),
        "liabilities": (
            "payroll payable", "recurring operations payable",
            "incremental bills payable", "rolling tax unpaid", "customer advances",
        ),
        "schedule": "miregate-schedule.csv",
        "cashbook": "miregate-cashbook.csv",
        "opening_balance": None,
    },
    "Reedbed": {
        "path": "reedbed-overview.csv",
        "cash": ("cash held",),
        "available": ("available after liabilities",),
        "liabilities": (
            "unpaid operating / capital", "rolling tax unpaid", "customer advances",
        ),
        "schedule": "reedbed-schedule.csv",
        "cashbook": "reedbed-cashbook.csv",
        "opening_balance": None,
    },
    "Old Distributary Fort": {
        "path": "old-distributary-fort-overview.csv",
        "cash": ("cash held",),
        "available": ("available after liabilities",),
        "liabilities": (
            "unpaid operating / capital", "rolling tax unpaid", "customer advances",
        ),
        "schedule": "old-distributary-fort-schedule.csv",
        "cashbook": "old-distributary-fort-cashbook.csv",
        "opening_balance": None,
    },
    "Blackthorn": {
        "path": "blackthorn-overview.csv",
        "cash": ("cash gp",),
        "available": ("available after actual liabilities",),
        "liabilities": (
            "carrow unpaid gp", "payroll payable gp",
            "production / upkeep payable gp", "incremental bills payable gp",
            "rolling tax unpaid gp", "customer advances gp",
        ),
        "schedule": "blackthorn-schedule.csv",
        "cashbook": "blackthorn-cashbook.csv",
        "opening_balance": "blackthorn-opening-balances.csv",
    },
}

def norm(value: str) -> str:
    return " ".join(value.strip().lower().replace("—", "-").split())

def read_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.reader(handle))

def money(value: str) -> Decimal:
    value = value.strip().replace(",", "").replace("$", "").replace("gp", "").strip()
    if not value or value in {"-", "–", "—"}:
        return Decimal("0")
    if value.startswith("(") and value.endswith(")"):
        value = "-" + value[1:-1]
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"not a numeric amount: {value!r}") from exc

def field_values(rows: list[list[str]], aliases: tuple[str, ...]) -> list[Decimal]:
    wanted = {norm(alias) for alias in aliases}
    found: list[Decimal] = []
    for row in rows:
        for index, cell in enumerate(row):
            if norm(cell) not in wanted:
                continue
            value_cell = next((part for part in row[index + 1:] if part.strip()), "")
            if value_cell:
                found.append(money(value_cell))
    return found

def first_field(rows: list[list[str]], aliases: tuple[str, ...]) -> Decimal:
    values = field_values(rows, aliases)
    if not values:
        raise ValueError(f"missing field {aliases}")
    return values[0]

def fmt(value: Decimal) -> str:
    return f"{value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP):.2f}"

def audit_estate(name: str, config: dict) -> tuple[list[str], list[str]]:
    path = PROPERTY / config["path"]
    errors: list[str] = []
    notes: list[str] = []
    rows = read_rows(path)

    cash = first_field(rows, config["cash"])
    available = first_field(rows, config["available"])
    liabilities = sum(field_values(rows, config["liabilities"]), Decimal("0"))
    computed = (cash - liabilities).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    recorded = available.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if computed != recorded:
        errors.append(
            f"{name}: available cash mismatch — {fmt(cash)} cash − "
            f"{fmt(liabilities)} recorded liabilities = {fmt(computed)}, "
            f"but overview says {fmt(recorded)}."
        )
    else:
        notes.append(
            f"- **{name}: PASS** — cash {fmt(cash)} gp − liabilities "
            f"{fmt(liabilities)} gp = available {fmt(recorded)} gp."
        )

    for row in rows:
        if not row:
            continue
        label = norm(row[0])
        if "cash hold" in label or "reserve hold" in label:
            value = next((part for part in row[1:] if part.strip()), "")
            if value and money(value) != 0:
                errors.append(f"{name}: nonzero discretionary/protected cash hold recorded ({value}).")
    return errors, notes

def find_schedule_columns(rows: list[list[str]]) -> tuple[int, dict[str, int]] | None:
    for row_index, row in enumerate(rows):
        headers = {norm(value): index for index, value in enumerate(row) if value.strip()}
        status_key = next((key for key in ("status", "live status", "plan status") if key in headers), None)
        task_key = next((key for key in ("task id", "task / settlement id", "task", "settlement id") if key in headers), None)
        target_key = next((key for key in ("target day", "earliest target", "earliest day", "planned day") if key in headers), None)
        if status_key and task_key and target_key:
            evidence_key = next((key for key in ("actual evidence", "evidence / restriction", "evidence / dependency", "evidence") if key in headers), None)
            return row_index, {"status": headers[status_key], "task": headers[task_key], "target": headers[target_key], "evidence": headers[evidence_key] if evidence_key else -1}
    return None

def due_tasks(name: str, filename: str, campaign_day: int) -> tuple[list[str], list[str]]:
    rows = read_rows(PROPERTY / filename)
    found = find_schedule_columns(rows)
    if found is None:
        return [f"- **{name}: schedule needs review** — no recognizable task/status/target columns in `{filename}`."], []
    header_index, columns = found
    task_status: dict[str, str] = {}
    for row in rows[header_index + 1:]:
        if len(row) > max(columns["task"], columns["status"]):
            task_id = row[columns["task"]].strip()
            if task_id:
                task_status[task_id] = row[columns["status"]].strip()
    completed = {"complete", "completed", "cancelled", "canceled", "closed", "paid", "settled", "resolved", "fulfilled"}
    suppressed: dict[str, str] = {}
    if TASK_SUPERSESSIONS.exists():
        with TASK_SUPERSESSIONS.open("r", encoding="utf-8-sig", newline="") as handle:
            for item in csv.DictReader(handle):
                if norm(item.get("estate", "")) != norm(name):
                    continue
                source, successor = item.get("task_id", "").strip(), item.get("superseded_by", "").strip()
                if source in task_status and norm(task_status.get(successor, "")) in completed:
                    suppressed[source] = successor
    due: list[str] = []
    resolved: list[str] = []
    for row in rows[header_index + 1:]:
        if len(row) <= max(columns["task"], columns["status"], columns["target"]):
            continue
        task = row[columns["task"]].strip()
        status = row[columns["status"]].strip()
        target_raw = row[columns["target"]].strip()
        if not task or not status or not target_raw:
            continue
        try:
            target = int(money(target_raw))
        except (ValueError, OverflowError):
            continue
        if task in suppressed:
            resolved.append(f"- **{name} — {task}** is superseded by completed `{suppressed[task]}` (verified against the staging successor map).")
            continue
        if norm(status) in completed:
            continue
        if target <= campaign_day:
            due.append(f"- **{name} — Day {target}: {task}** ({status})")
    return due, resolved

def opening_cash(config: dict) -> Decimal:
    source = config.get("opening_balance")
    if not source:
        return Decimal("0")
    rows = read_rows(PROPERTY / source)
    for row in rows:
        if len(row) > 5 and norm(row[0]) == "blackthorn" and norm(row[1]) == "cash":
            return money(row[5])
    raise ValueError(f"opening cash row not found in {source}")

def audit_cashbook(name: str, filename: str) -> tuple[Decimal, list[str]]:
    rows = read_rows(PROPERTY / filename)
    errors: list[str] = []
    header_index = None
    columns: dict[str, int] = {}
    for index, row in enumerate(rows):
        headers = {norm(value): col for col, value in enumerate(row) if value.strip()}
        id_key = next((key for key in ("cash id", "transaction id") if key in headers), None)
        delta_key = next((key for key in ("cash delta", "cash delta gp") if key in headers), None)
        if id_key and delta_key:
            header_index = index
            columns = {"id": headers[id_key], "delta": headers[delta_key]}
            columns["check"] = next((headers[k] for k in ("check", "status") if k in headers), -1)
            break
    if header_index is None:
        return Decimal("0"), [f"{filename}: cashbook ID/cash-delta columns not found."]
    seen: set[str] = set()
    total = Decimal("0")
    for row_number, row in enumerate(rows[header_index + 1:], start=header_index + 2):
        if columns["id"] >= len(row):
            continue
        identifier = row[columns["id"]].strip()
        if not identifier:
            continue
        if identifier in seen:
            errors.append(f"{filename}: duplicate cash ID {identifier}.")
        seen.add(identifier)
        delta = row[columns["delta"]].strip() if columns["delta"] < len(row) else ""
        if not delta:
            errors.append(f"{filename}: {identifier} has no displayed cash delta (row {row_number}).")
            continue
        try:
            total += money(delta)
        except ValueError as exc:
            errors.append(f"{filename}: {identifier} has invalid cash delta {delta!r}: {exc}.")
        check_index = columns["check"]
        if check_index >= 0 and check_index < len(row):
            result = row[check_index].strip()
            if result and norm(result) not in {"ok", "pass", "reconciled"}:
                errors.append(f"{filename}: {identifier} check is {result!r}.")
    return total, errors

def audit_cashbooks() -> tuple[dict[str, Decimal], list[str]]:
    totals: dict[str, Decimal] = {}
    errors: list[str] = []
    for name, config in ESTATES.items():
        total, findings = audit_cashbook(name, config["cashbook"])
        totals[name] = total
        errors.extend(findings)
    return totals, errors

def current_campaign_day() -> int | None:
    state_path = ROOT / "campaign" / "continuity" / "campaign-state.md"
    if not state_path.exists():
        return None
    text = state_path.read_text(encoding="utf-8")[:1500]
    match = re.search(r"CAMPAIGN_STATE\s*[—–-]\s*DAY\s+(\d+)", text, re.IGNORECASE)
    return int(match.group(1)) if match else None

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign-day", default=os.environ.get("CAMPAIGN_DAY", "").strip())
    parser.add_argument("--output", type=Path, default=REPORT)
    args = parser.parse_args()
    campaign_day = int(args.campaign_day) if args.campaign_day else current_campaign_day()
    campaign_day_source = "manual workflow input" if args.campaign_day else ("CAMPAIGN_STATE" if campaign_day is not None else "not found")

    notes: list[str] = []
    errors: list[str] = []
    for name, config in ESTATES.items():
        estate_errors, estate_notes = audit_estate(name, config)
        errors.extend(estate_errors)
        notes.extend(estate_notes)
    cashbook_totals, cashbook_errors = audit_cashbooks()
    errors.extend(cashbook_errors)
    for name, config in ESTATES.items():
        rows = read_rows(PROPERTY / config["path"])
        summary_cash = first_field(rows, config["cash"])
        opening = opening_cash(config)
        ledger_cash = (opening + cashbook_totals[name]).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        expected_cash = summary_cash.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if ledger_cash != expected_cash:
            errors.append(
                f"{name}: cashbook roll-forward mismatch — opening {fmt(opening)} gp + "
                f"net cashbook changes {fmt(cashbook_totals[name])} gp = {fmt(ledger_cash)} gp, "
                f"but overview says {fmt(expected_cash)} gp."
            )
        else:
            notes.append(
                f"- **{name} cashbook: PASS** — opening {fmt(opening)} gp + net posted changes "
                f"{fmt(cashbook_totals[name])} gp = {fmt(ledger_cash)} gp."
            )

    snapshot_day = "unknown"
    index_path = ROOT / "trackers" / "index.json"
    if index_path.exists():
        index = json.loads(index_path.read_text(encoding="utf-8"))
        snapshot_day = str(index.get("captured_utc", "unknown"))

    lines = [
        "# Estate Review",
        "",
        f"Generated from the property workbook CSV snapshot captured {snapshot_day}.",
        "Audit/report only: this process does not post wages, income, expenses, transfers, taxes, or campaign decisions.",
        "",
        "## Cash reconciliation",
        "",
        *notes,
    ]
    if errors:
        lines.extend(["", "## Findings requiring correction", ""])
        lines.extend(f"- **CHECK:** {error}" for error in errors)
    else:
        lines.extend(["", "All available-cash, cashbook roll-forward, and cashbook ID checks passed."])

    if campaign_day is None:
        lines.extend([
            "",
            "## Schedule review",
            "",
            "The current campaign day could not be read from CAMPAIGN_STATE. Supply it in the manual workflow input to list due and overdue unfinished estate tasks.",
        ])
    else:
        lines.extend(["", f"## Unfinished tasks due by campaign Day {campaign_day}", "", f"Campaign-day source: {campaign_day_source}."])
        due: list[str] = []
        resolved: list[str] = []
        for name, config in ESTATES.items():
            estate_due, estate_resolved = due_tasks(name, config["schedule"], campaign_day)
            due.extend(estate_due)
            resolved.extend(estate_resolved)
        lines.extend(due if due else ["No unfinished scheduled tasks at or before that day were found in the four schedule snapshots."])
        if resolved:
            lines.extend(["", "### Verified later settlements", "", *resolved])

    lines.extend([
        "",
        "## Source boundary",
        "",
        "Drive remains authoritative. These files are staging snapshots; reconcile any proposed correction against the live workbook before changing campaign records.",
        "",
    ])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {args.output}")
    if errors:
        print(f"{len(errors)} finding(s) need attention.", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
