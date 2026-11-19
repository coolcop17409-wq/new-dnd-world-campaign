#!/usr/bin/env python3
"""Replay Blackthorn's source workbook production, stock, shipment and acceptance rules."""
from __future__ import annotations
import csv
import json
from collections import defaultdict
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROPERTY = ROOT / "trackers" / "csv" / "property"
DATA = ROOT / "data" / "estate"
REPORT = ROOT / "reports" / "blackthorn-operations.json"


def dec(value):
    value = str(value or "").strip().replace(",", "").replace("gp", "").strip()
    if not value or value in {"-", "–", "—"}:
        return Decimal("0")
    if value.startswith("(") and value.endswith(")"):
        value = "-" + value[1:-1]
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"invalid numeric value {value!r}") from exc


def qmoney(value):
    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def qcost(value):
    return Decimal(value).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


def read_register(path, header_key):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))
    header_index = next((i for i, row in enumerate(rows) if row and row[0].strip() == header_key), None)
    if header_index is None:
        raise ValueError(f"{path.name}: header {header_key!r} not found")
    header = [cell.strip() for cell in rows[header_index]]
    return [
        {header[i]: row[i].strip() if i < len(row) else "" for i in range(len(header))}
        for row in rows[header_index + 1:] if row and row[0].strip()
    ]


def active(row, day):
    start = int(dec(row.get("From day", row.get("from_day", 0))))
    through = row.get("Through day", row.get("through_day", ""))
    return start <= day and (not through or day <= int(dec(through)))


def replay(opening_stock, rates, orders, schedule, operations):
    """Return calculated row values and findings; never writes campaign events."""
    findings = []
    stock = {}
    for row in opening_stock:
        grade = row["Grade"].strip()
        if grade in stock:
            findings.append(f"duplicate opening stock grade {grade}")
        stock[grade] = {"quantity": dec(row["Quantity t"]), "cost": dec(row["Amount gp"])}
    products = defaultdict(list)
    payroll = defaultdict(list)
    for row in rates:
        kind = row.get("Type", row.get("type", "")).strip()
        family = row.get("Cost family", row.get("cost_family", "")).strip()
        if kind == "ProductCost":
            grade = row.get("Product grade", row.get("product_grade", "")).strip()
            products[grade].append(row)
        elif kind == "Payroll":
            payroll[family].append(row)
    order_map = {r["Order line ID"].strip(): r for r in orders if r.get("Order line ID", "").strip()}
    task_map = {r["Task / settlement ID"].strip(): r for r in schedule if r.get("Task / settlement ID", "").strip()}
    transit = {}
    transfer_costs = {}
    seen_ids = set()
    dispatch_ids = set()
    order_flow = defaultdict(lambda: {"accepted": Decimal("0"), "in_transit": Decimal("0")})
    shipment_orders = {}
    produce_totals = defaultdict(Decimal)
    family_by_row = {}
    family_pay_by_day = {}
    for row in operations:
        if row["Event type"].strip() == "Produce":
            day = int(dec(row["Day"]))
            grade = row["Product grade"].strip()
            active_costs = [r for r in products.get(grade, []) if active(r, day)]
            if len(active_costs) == 1:
                family = active_costs[0].get("Cost family", active_costs[0].get("cost_family", "")).strip()
                family_by_row[row["Event ID"]] = family
                produce_totals[(day, family)] += dec(row["Quantity t"])
            else:
                findings.append(f"{row['Event ID']}: needs exactly one active ProductCost rate for {grade} on Day {day}")
    cumulative_produce = defaultdict(Decimal)
    results = []
    totals = {key: Decimal("0") for key in ("revenue", "cogs", "loss", "produced_cost")}
    last_day = 0

    def get_stock(grade):
        return stock.setdefault(grade, {"quantity": Decimal("0"), "cost": Decimal("0")})

    def order_for(row, requires_order=True):
        oid = row.get("Order line ID", "").strip()
        if not oid and not requires_order:
            return None
        order = order_map.get(oid)
        if not order:
            findings.append(f"{row['Event ID']}: order line {oid!r} is missing")
            return None
        if order.get("Status", "").strip() != "Confirmed":
            findings.append(f"{row['Event ID']}: order {oid} is not confirmed")
        if order.get("Product grade", "").strip() != row["Product grade"].strip():
            findings.append(f"{row['Event ID']}: order {oid} grade does not match")
        return order

    for row in operations:
        eid = row["Event ID"].strip()
        day = int(dec(row["Day"]))
        kind = row["Event type"].strip()
        grade = row["Product grade"].strip()
        qty = dec(row.get("Quantity t", "0"))
        extra = dec(row.get("Extra direct gp / labor allocation", "0"))
        ship = row.get("Shipment / transfer ID", "").strip()
        order_id = row.get("Order line ID", "").strip()
        if not eid:
            findings.append("operation without Event ID")
            continue
        if not row.get("Evidence / inspection", "").strip():
            findings.append(f"{eid}: actual operation requires evidence")
        if eid in seen_ids:
            findings.append(f"duplicate operation Event ID {eid}")
        seen_ids.add(eid)
        if day < last_day:
            findings.append(f"{eid}: event day is out of chronological order")
        last_day = max(last_day, day)
        calculated = {
            "on_site_delta_t": Decimal("0"), "on_site_delta_gp": Decimal("0"),
            "transit_delta_t": Decimal("0"), "transit_delta_gp": Decimal("0"),
            "revenue_gp": Decimal("0"), "cogs_gp": Decimal("0"),
            "loss_idle_gp": Decimal("0"), "production_labor_gp": Decimal("0"),
            "nonlabor_cost_gp": Decimal("0"),
        }
        on_site = get_stock(grade)
        prior_qty = on_site["quantity"]
        prior_cost = on_site["cost"]
        unit_cost = prior_cost / prior_qty if prior_qty > 0 else Decimal("0")
        calculated.update({"prior_on_site_t": prior_qty, "prior_on_site_gp": prior_cost,
                           "unit_cost_gp_per_t": unit_cost})
        if kind in {"Produce", "Dispatch", "Accept", "Gate sale", "Return", "Loss"} and qty <= 0:
            findings.append(f"{eid}: {kind} quantity must be positive")
        if kind in {"Dispatch", "Accept", "Gate sale", "Return"}:
            order = order_for(row)
        else:
            order = order_map.get(order_id) if order_id else None
        if kind in {"Dispatch", "Gate sale"}:
            task_id = order.get("Readiness task ID", "").strip() if order else ""
            task = task_map.get(task_id)
            if not task or task.get("Result", "").strip() != "Pass":
                findings.append(f"{eid}: readiness task {task_id!r} has no passed result")
            elif not task.get("Actual day", "").strip() or dec(task["Actual day"]) <= 0 or dec(task["Actual day"]) > day:
                findings.append(f"{eid}: readiness must have passed on or before the event day")
        if kind in {"Dispatch", "Accept", "Return"} and not ship:
            findings.append(f"{eid}: {kind} requires a shipment ID")
        if kind == "Dispatch":
            if ship in dispatch_ids:
                findings.append(f"{eid}: dispatch shipment ID {ship} must be unique per line")
            dispatch_ids.add(ship)
            if qty <= 0 or qty > prior_qty:
                findings.append(f"{eid}: dispatch quantity exceeds on-site {grade} stock")
            moved = qcost(qty * unit_cost)
            on_site["quantity"] -= qty
            on_site["cost"] -= moved
            transit[(ship, grade)] = {"quantity": qty, "cost": moved}
            if order:
                order_id = order.get("Order line ID", "").strip()
                order_limit = dec(order.get("Ordered t", "0"))
                flow = order_flow[order_id]
                if order_limit <= 0 or flow["accepted"] + flow["in_transit"] + qty > order_limit:
                    findings.append(f"{eid}: dispatch exceeds confirmed order quantity")
                flow["in_transit"] += qty
                shipment_orders[ship] = order_id
            calculated.update({"on_site_delta_t": -qty, "on_site_delta_gp": -moved,
                               "transit_delta_t": qty, "transit_delta_gp": moved})
        elif kind == "Produce":
            family = family_by_row.get(eid, "")
            day_total = produce_totals[(day, family)]
            family_rates = [r for r in payroll.get(family, []) if active(r, day) and r.get("Unit", r.get("unit", "")).strip().lower() == "day"]
            family_pay = sum((dec(r.get("Rate gp", r.get("rate_gp", "0"))) for r in family_rates), Decimal("0"))
            prior_cumulative = cumulative_produce[(day, family)]
            cumulative_produce[(day, family)] += qty
            current_share = qmoney(family_pay * cumulative_produce[(day, family)] / day_total) if day_total else Decimal("0")
            prior_share = qmoney(family_pay * prior_cumulative / day_total) if day_total else Decimal("0")
            labor_cost = current_share - prior_share
            cost_rows = [r for r in products.get(grade, []) if active(r, day)]
            product_rate = sum((dec(r.get("Rate gp", r.get("rate_gp", "0"))) for r in cost_rows), Decimal("0"))
            nonlabor = qmoney(qty * product_rate + extra)
            new_cost = qcost(labor_cost + nonlabor)
            on_site["quantity"] += qty
            on_site["cost"] += new_cost
            calculated.update({"on_site_delta_t": qty, "on_site_delta_gp": new_cost,
                               "production_labor_gp": labor_cost, "nonlabor_cost_gp": nonlabor})
            totals["produced_cost"] += new_cost
        elif kind == "Idle labor":
            calculated["production_labor_gp"] = extra
            calculated["loss_idle_gp"] = extra
        elif kind == "Labor allocation":
            on_site["cost"] += extra
            calculated["production_labor_gp"] = extra
            calculated["on_site_delta_gp"] = extra
        elif kind == "Accept":
            cargo = transit.get((ship, grade))
            if not cargo or qty <= 0 or qty > cargo["quantity"]:
                findings.append(f"{eid}: acceptance exceeds shipment {ship} in-transit quantity")
            else:
                order = order or {}
                order_id = order.get("Order line ID", "").strip()
                if ship in shipment_orders and shipment_orders[ship] != order_id:
                    findings.append(f"{eid}: accepted shipment is linked to a different order")
                flow = order_flow[order_id]
                if flow["in_transit"] < qty:
                    findings.append(f"{eid}: accepted quantity exceeds this order's dispatched balance")
                flow["in_transit"] -= qty
                flow["accepted"] += qty
                revenue = qmoney(qty * dec(order.get("Price gp/t", "0")))
                cogs = qcost(qty * cargo["cost"] / cargo["quantity"]) if cargo["quantity"] else Decimal("0")
                cargo["quantity"] -= qty
                cargo["cost"] -= cogs
                calculated.update({"transit_delta_t": -qty, "transit_delta_gp": -cogs,
                                   "revenue_gp": revenue, "cogs_gp": cogs})
                totals["revenue"] += revenue
                totals["cogs"] += cogs
        elif kind == "Gate sale":
            if qty <= 0 or qty > prior_qty:
                findings.append(f"{eid}: gate sale exceeds on-site {grade} stock")
            else:
                moved = qcost(qty * unit_cost)
                order = order or {}
                order_id = order.get("Order line ID", "").strip()
                flow = order_flow[order_id]
                order_limit = dec(order.get("Ordered t", "0"))
                if order_limit <= 0 or flow["accepted"] + flow["in_transit"] + qty > order_limit:
                    findings.append(f"{eid}: gate sale exceeds confirmed order quantity")
                flow["accepted"] += qty
                revenue = qmoney(qty * dec(order.get("Price gp/t", "0")))
                on_site["quantity"] -= qty
                on_site["cost"] -= moved
                calculated.update({"on_site_delta_t": -qty, "on_site_delta_gp": -moved,
                                   "revenue_gp": revenue, "cogs_gp": moved})
                totals["revenue"] += revenue
                totals["cogs"] += moved
        elif kind == "Return":
            cargo = transit.get((ship, grade))
            if not cargo or qty <= 0 or qty > cargo["quantity"]:
                findings.append(f"{eid}: return exceeds shipment {ship} in-transit quantity")
            else:
                order_id = order.get("Order line ID", "").strip()
                if ship in shipment_orders and shipment_orders[ship] != order_id:
                    findings.append(f"{eid}: returned shipment is linked to a different order")
                order_flow[order_id]["in_transit"] -= qty
                moved = qcost(qty * cargo["cost"] / cargo["quantity"])
                cargo["quantity"] -= qty
                cargo["cost"] -= moved
                on_site["quantity"] += qty
                on_site["cost"] += moved
                calculated.update({"on_site_delta_t": qty, "on_site_delta_gp": moved,
                                   "transit_delta_t": -qty, "transit_delta_gp": -moved})
        elif kind in {"Regrade out", "Regrade in"}:
            if not ship:
                findings.append(f"{eid}: {kind} requires a transfer ID")
            if kind == "Regrade out":
                if qty <= 0 or qty > prior_qty:
                    findings.append(f"{eid}: regrade exceeds on-site {grade} stock")
                else:
                    moved = qcost(qty * unit_cost)
                    on_site["quantity"] -= qty
                    on_site["cost"] -= moved
                    transfer_costs[ship] = {"quantity": qty, "cost": moved}
                    calculated.update({"on_site_delta_t": -qty, "on_site_delta_gp": -moved})
            else:
                transfer = transfer_costs.get(ship)
                if not transfer or qty <= 0 or qty > transfer["quantity"]:
                    findings.append(f"{eid}: regrade-in exceeds transfer {ship}")
                else:
                    moved = qcost(qty * transfer["cost"] / transfer["quantity"])
                    on_site["quantity"] += qty
                    on_site["cost"] += moved
                    transfer["quantity"] -= qty
                    transfer["cost"] -= moved
                    calculated.update({"on_site_delta_t": qty, "on_site_delta_gp": moved})
        elif kind == "Loss":
            if qty <= 0:
                findings.append(f"{eid}: loss quantity must be positive")
            elif ship:
                cargo = transit.get((ship, grade))
                if not cargo or qty > cargo["quantity"]:
                    findings.append(f"{eid}: loss exceeds shipment {ship} in-transit quantity")
                else:
                    cost = qcost(qty * cargo["cost"] / cargo["quantity"])
                    cargo["quantity"] -= qty
                    cargo["cost"] -= cost
                    if ship in shipment_orders:
                        order_flow[shipment_orders[ship]]["in_transit"] -= qty
                    calculated.update({"transit_delta_t": -qty, "transit_delta_gp": -cost, "loss_idle_gp": cost})
            elif qty > prior_qty:
                findings.append(f"{eid}: loss exceeds on-site {grade} stock")
            else:
                cost = qcost(qty * unit_cost)
                on_site["quantity"] -= qty
                on_site["cost"] -= cost
                calculated.update({"on_site_delta_t": -qty, "on_site_delta_gp": -cost, "loss_idle_gp": cost})
            totals["loss"] += calculated["loss_idle_gp"]
        else:
            findings.append(f"{eid}: unsupported operation type {kind!r}")
        if kind == "Idle labor":
            totals["loss"] += extra
        results.append({"event_id": eid, **{k: str(v) for k, v in calculated.items()}})
    return {"status": "CHECK" if findings else "PASS", "events": results, "findings": findings,
            "totals": {k: str(qmoney(v)) for k, v in totals.items()},
            "on_site": {g: {"quantity_t": str(qcost(v["quantity"])), "cost_gp": str(qcost(v["cost"]))}
                        for g, v in sorted(stock.items())},
            "in_transit": {f"{ship}:{grade}": {"quantity_t": str(qcost(v["quantity"])), "cost_gp": str(qcost(v["cost"]))}
                           for (ship, grade), v in sorted(transit.items()) if v["quantity"] or v["cost"]}}


def main():
    opening = [r for r in read_register(PROPERTY / "blackthorn-opening-balances.csv", "Property")
               if r.get("Account") == "Stock"]
    rates = read_register(PROPERTY / "blackthorn-rates-staff.csv", "Rate ID")
    orders = read_register(PROPERTY / "blackthorn-orders.csv", "Order line ID")
    schedule = read_register(PROPERTY / "blackthorn-schedule.csv", "Task / settlement ID")
    operations = read_register(PROPERTY / "blackthorn-operations.csv", "Event ID")
    report = replay(opening, rates, orders, schedule, operations)
    totals = report["totals"]
    checkpoint = {}
    with (DATA / "blackthorn-tax-checkpoint.csv").open(encoding="utf-8-sig", newline="") as handle:
        checkpoint = {r["component"]: dec(r["value_gp"]) for r in csv.DictReader(handle)}
    for key, expected in (("revenue", checkpoint["accepted_revenue"]),
                          ("cogs", checkpoint["cogs"]), ("loss", checkpoint["loss_and_idle"])):
        if qmoney(dec(totals[key])) != qmoney(expected):
            report["findings"].append(f"Day 230 {key} {qmoney(dec(totals[key]))} does not match source checkpoint {qmoney(expected)}")
    quantity_fields = {"prior_on_site_t": "Prior on-site t", "on_site_delta_t": "On-site delta t", "transit_delta_t": "Transit delta t"}
    money_fields = {
        "prior_on_site_gp": "Prior on-site gp", "unit_cost_gp_per_t": "Unit cost gp/t",
        "on_site_delta_gp": "On-site delta gp", "transit_delta_gp": "Transit delta gp",
        "revenue_gp": "Revenue gp", "cogs_gp": "COGS gp", "loss_idle_gp": "Loss / idle expense gp",
        "production_labor_gp": "Production labor gp", "nonlabor_cost_gp": "Nonlabor cost gp",
    }
    for source, calculated in zip(operations, report["events"]):
        for key, source_header in quantity_fields.items():
            if qcost(dec(source.get(source_header, "0"))) != qcost(dec(calculated[key])):
                report["findings"].append(f"{calculated['event_id']}: {source_header} does not match replay")
        for key, source_header in money_fields.items():
            if qmoney(dec(source.get(source_header, "0"))) != qmoney(dec(calculated[key])):
                report["findings"].append(f"{calculated['event_id']}: {source_header} does not match replay")
    if report["findings"]:
        report["status"] = "CHECK"
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "event_count": len(report["events"]),
                      "totals": report["totals"], "findings": report["findings"]}, indent=2))
    return 1 if report["status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
