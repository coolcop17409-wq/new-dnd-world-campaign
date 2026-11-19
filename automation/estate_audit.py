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
import sys
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROPERTY = ROOT / "trackers" / "csv" / "property"
REPORT = ROOT / "reports" / "estate-review.md"

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
    },
    "Reedbed": {
        "path": "reedbed-overview.csv",
        "cash": ("cash held",),
        "available": ("available after liabilities",),
        "liabilities": (
            "unpaid operating / capital", "rolling tax unpaid", "customer advances",
        ),
        "schedule": "reedbed-schedule.csv",
    },
    "Old Distributary Fort": {
        "path": "old-distributary-fort-overview.csv",
        "cash": ("cash held",),
        "available": ("available after liabilities",),
        "liabilities": (
            "unpaid operating / capital", "rolling tax unpaid", "customer advances",
        ),
        "schedule": "old-distributary-fort-schedule.csv",
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
    },
}

CASHBOOKS = (
    "miregate-cashbook.csv",
    "reedbed-cashbook.csv",
    "old-distributary-fort-cashbook.csv",
    "blackthorn-cashbook.csv",
)

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
            return row_index, {"status": headers[status_key], "task": headers[task_key], "target": headers[target_key]}
    return None

def due_tasks(name: str, filename: str, campaign_day: int) -> list[str]:
    rows = read_rows(PROPERTY / filename)
    found = find_schedule_columns(rows)
    if found is None:
        return [f"- **{name}: schedule needs review** — no recognizable task/status/target columns in `{filename}`."]
    header_index, columns = found
    due: list[str] = []
    for row in rows[header_index + 1:]:
        if len(row) <= max(columns.values()):
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
        if norm(status) in {"complete", "completed", "cancelled", "canceled", "closed"}:
            continue
        if target <= campaign_day:
            due.append(f"- **{name} — Day {target}: {task}** ({status})")
    return due

def audit_cashbook_ids() -> list[str]:
    errors: list[str] = []
    for filename in CASHBOOKS:
        rows = read_rows(PROPERTY / filename)
        header_index = None
        id_index = None
        for index, row in enumerate(rows):
            for column, value in enumerate(row):
                if norm(value) in {"cash id", "transaction id"}:
                    header_index, id_index = index, column
                    break
            if header_index is not None:
                break
        if header_index is None or id_index is None:
            errors.append(f"{filename}: cashbook ID column not found.")
            continue
        seen: set[str] = set()
        for row in rows[header_index + 1:]:
            if id_index >= len(row):
                continue
            identifier = row[id_index].strip()
            if not identifier:
                continue
            if identifier in seen:
                errors.append(f"{filename}: duplicate cash ID {identifier}.")
            seen.add(identifier)
    return errors

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign-day", default=os.environ.get("CAMPAIGN_DAY", "").strip())
    parser.add_argument("--output", type=Path, default=REPORT)
    args = parser.parse_args()
    campaign_day = int(args.campaign_day) if args.campaign_day else None

    notes: list[str] = []
    errors: list[str] = []
    for name, config in ESTATES.items():
        estate_errors, estate_notes = audit_estate(name, config)
        errors.extend(estate_errors)
        notes.extend(estate_notes)
    errors.extend(audit_cashbook_ids())

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
        lines.extend(["", "All configured cash reconciliations and cashbook ID checks passed."])

    if campaign_day is None:
        lines.extend([
            "",
            "## Schedule review",
            "",
            "No campaign day was supplied. Run the workflow manually with the current in-game day to list due and overdue unfinished estate tasks.",
        ])
    else:
        lines.extend(["", f"## Unfinished tasks due by campaign Day {campaign_day}", ""])
        due: list[str] = []
        for name, config in ESTATES.items():
            due.extend(due_tasks(name, config["schedule"], campaign_day))
        lines.extend(due if due else ["No unfinished scheduled tasks at or before that day were found in the four schedule snapshots."])

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
