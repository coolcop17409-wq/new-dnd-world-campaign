#!/usr/bin/env python3
"""Structural check for the QDF quest readiness coverage ledger.

This checks explicit gate status, owner references, and evidence text only. It
cannot judge narrative quality, balance, agency, canon, or whether evidence is true.
It never edits records or gameplay.
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

STATUSES = {"PASS", "CONDITIONAL", "HOLD", "NOT REVIEWED", "N/A"}

def validate(text: str) -> list[str]:
    errors = []
    lines = text.splitlines()
    start = next((i for i, line in enumerate(lines)
                  if "Design review coverage" in line), None)
    if start is None:
        return ["missing Design review coverage section"]
    table = []
    for line in lines[start + 1:]:
        if line.lstrip().startswith("|"):
            table.append(line)
        elif table:
            break
    if len(table) < 2:
        return ["missing readiness coverage table"]
    header = [cell.strip().lower() for cell in table[0].strip().strip("|").split("|")]
    required = ("owner / reference", "g1", "g2", "g3")
    if any(key not in header for key in required):
        return ["coverage table must include Owner / reference, G1, G2, G3 columns"]
    indexes = {key: header.index(key) for key in required}
    for line_no, row in enumerate(table[2:], start + 3):
        cells = [cell.strip() for cell in row.strip().strip("|").split("|")]
        if len(cells) <= max(indexes.values()):
            errors.append(f"line {line_no}: incomplete table row")
            continue
        owner = cells[indexes["owner / reference"]]
        if not re.search(r"\[[^]]+\]\([^)]+\)", owner):
            errors.append(f"line {line_no}: owner needs a linked source reference")
        for key in ("g1", "g2", "g3"):
            value = cells[indexes[key]]
            status = next((s for s in STATUSES if re.search(r"\\b" + re.escape(s) + r"\\b", value)), None)
            if status is None:
                errors.append(f"line {line_no}: {key.upper()} needs an explicit status")
            elif status in {"PASS", "CONDITIONAL", "HOLD"} and not value[value.find(status) + len(status):].strip(" ;:—-"):
                errors.append(f"line {line_no}: {key.upper()} {status} needs evidence or a concrete blocker")
    return errors

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path, help="DM-only quest index Markdown file")
    args = parser.parse_args()
    try:
        errors = validate(args.ledger.read_text(encoding="utf-8"))
    except OSError as exc:
        print(f"cannot read {args.ledger}: {exc}", file=sys.stderr)
        return 2
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        return 1
    print("Readiness ledger structure is complete; qualitative gate judgment remains required.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
