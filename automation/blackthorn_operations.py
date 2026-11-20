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
        results.append({"event_id": eid, "day": day, "operation_type": kind,
                        "product_grade": grade, "quantity_t": str(qty),
                        "order_line_id": order_id, "shipment_id": ship,
                        **{k: str(v) for k, v in calculated.items()}})
    return {"status": "CHECK" if findings else "PASS", "events": results, "findings": findings,
            "totals": {k: str(qmoney(v)) for k, v in totals.items()},
            "on_site": {g: {"quantity_t": str(qcost(v["quantity"])), "cost_gp": str(qcost(v["cost"]))}
                        for g, v in sorted(stock.items())},
            "in_transit": {f"{ship}:{grade}": {"quantity_t": str(qcost(v["quantity"])), "cost_gp": str(qcost(v["cost"]))}
                           for (ship, grade), v in sorted(transit.items()) if v["quantity"] or v["cost"]}}


def inventory_key(grade):
    grade = grade.strip()
    opening_path = DATA / "opening-inventory.csv"
    if opening_path.exists():
        for row in read_register(opening_path, "inventory_id"):
            if row.get("item", "").strip() == grade:
                return row.get("inventory_id", "").strip()
    slug = "".join(ch if ch.isalnum() else "-" for ch in grade.upper()).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return "BT-STOCK-" + slug


def ledger_events_for_operations(operation_rows, calculated_rows, orders):
    """Normalize future Blackthorn operation results for the estate event ledger."""
    order_map = {row.get("Order line ID", "").strip(): row for row in orders}
    calculations = {row["event_id"]: row for row in calculated_rows}
    events = []
    findings = []
    for source_row, operation in enumerate(operation_rows, start=1):
        eid = operation.get("Event ID", "").strip()
        calc = calculations.get(eid)
        if not calc:
            findings.append(f"{eid}: calculated operation result missing")
            continue
        kind = operation.get("Event type", "").strip()
        revenue = qmoney(dec(calc.get("revenue_gp", "0")))
        cogs = qmoney(dec(calc.get("cogs_gp", "0")))
        loss = qmoney(dec(calc.get("loss_idle_gp", "0")))
        cash = Decimal("0")
        receivable = Decimal("0")
        receivable_id = ""
        if kind in {"Accept", "Gate sale"}:
            if not operation.get("Cash received gp", "").strip():
                findings.append(f"{eid}: sale acceptance must state actual Cash received gp (use 0 if unpaid)")
                continue
            cash = qmoney(dec(operation.get("Cash received gp", "0")))
            if cash < 0 or cash > revenue:
                findings.append(f"{eid}: cash received must be between zero and earned revenue {revenue}")
                continue
            receivable = qmoney(revenue - cash)
            receivable_id = operation.get("Receivable ID", "").strip()
            if receivable > 0 and not receivable_id:
                findings.append(f"{eid}: unpaid sale balance requires a stable Receivable ID")
                continue
        elif operation.get("Cash received gp", "").strip() or operation.get("Receivable ID", "").strip():
            findings.append(f"{eid}: only accepted sale rows may carry cash/receivable settlement fields")
            continue
        order_id = operation.get("Order line ID", "").strip()
        order = order_map.get(order_id, {})
        prerequisite = order.get("Readiness task ID", "").strip() if kind in {"Dispatch", "Accept", "Gate sale"} else ""
        events.append({
            "event_id": f"BT-OPS-{eid}",
            "estate": "Blackthorn",
            "effective_day": str(calc["day"]),
            "event_type": {
                "Produce": "blackthorn_production",
                "Dispatch": "shipment_dispatch",
                "Accept": "shipment_acceptance",
                "Gate sale": "gate_sale",
                "Return": "shipment_return",
                "Loss": "inventory_loss",
                "Idle labor": "blackthorn_idle_labor",
                "Labor allocation": "blackthorn_labor_capitalization",
                "Regrade out": "inventory_regrade_out",
                "Regrade in": "inventory_regrade_in",
            }.get(kind, "blackthorn_operation"),
            "reference_id": order_id,
            "receivable_id": receivable_id,
            "cash_delta_gp": str(cash) if cash else "",
            "receivable_delta_gp": str(receivable) if receivable else "",
            "income_delta_gp": str(revenue) if revenue else "",
            "expense_delta_gp": str(cogs + loss) if cogs + loss else "",
            "inventory_id": inventory_key(operation.get("Product grade", "").strip()),
            "quantity_delta": calc["on_site_delta_t"],
            "inventory_cost_delta_gp": calc["on_site_delta_gp"],
            "shipment_id": operation.get("Shipment / transfer ID", "").strip(),
            "accepted_quantity": operation.get("Quantity t", "").strip() if kind == "Accept" else "",
            "prerequisite_ref": prerequisite,
            "description": f"Blackthorn operation {eid}: {kind}.",
            "evidence": operation.get("Evidence / inspection", "").strip(),
            "source_file": "data/estate/blackthorn-operations-events.csv",
            "source_row": str(source_row),
            "status": "posted",
            "in_transit_quantity_delta": calc["transit_delta_t"],
            "in_transit_cost_delta_gp": calc["transit_delta_gp"],
        })
    return events, findings


def apply_supplements(canonical, supplements, manifests, live_records):
    """Validate exact bounded authorization for omitted historical operations."""
    findings = []
    records = {r["record_id"]: r for r in live_records}
    expected = []
    for manifest in manifests:
        authority = records.get(manifest.get("authority"), {})
        if authority.get("record_type") != "Retcon authorization" or authority.get("status") not in {"PREPARED", "RESOLVED", "COMMITTED"}:
            findings.append("supplement manifest lacks explicit player authorization")
        scoped = manifest.get("operation_rows", [])
        expected.extend(scoped)
        for row in scoped:
            if (row.get("Status", "").lower() != "supplement"
                or not int(manifest["start_day"]) <= int(dec(row.get("Day"))) <= int(manifest["end_day"])
                or not row.get("Evidence / inspection", "").startswith(manifest["authority"] + ":")):
                findings.append("supplement operation outside exact authorized scope")
    if expected != supplements:
        findings.append("supplement rows do not exactly match resolved manifests")
    ids = [r["Event ID"] for r in canonical + supplements]
    if len(ids) != len(set(ids)):
        findings.append("duplicate canonical/supplement event ID")
    result = sorted(canonical + supplements, key=lambda r: int(dec(r["Day"])))
    return result, findings


def main():
    opening = [r for r in read_register(PROPERTY / "blackthorn-opening-balances.csv", "Property")
               if r.get("Account") == "Stock"]
    rates = read_register(PROPERTY / "blackthorn-rates-staff.csv", "Rate ID")
    orders = read_register(PROPERTY / "blackthorn-orders.csv", "Order line ID")
    schedule = read_register(PROPERTY / "blackthorn-schedule.csv", "Task / settlement ID")
    history = read_register(PROPERTY / "blackthorn-operations.csv", "Event ID")
    all_additions = read_register(DATA / "blackthorn-operations-events.csv", "Event ID")
    additions = [r for r in all_additions if r.get("Status", "").lower() not in {"retcon", "supplement"}]
    supplements = [r for r in all_additions if r.get("Status", "").lower() == "supplement"]
    replacements = [r for r in all_additions if r.get("Status", "").lower() == "retcon"]
    live_records = read_register(DATA / "operational-checkpoint.csv", "record_id")
    retcons = [json.loads(r["source_and_limits"]) for r in live_records
               if r.get("record_type") == "Blackthorn retrospective replacement" and r.get("status") == "Resolved"]
    meta = json.loads((DATA / "snapshot-meta.json").read_text(encoding="utf-8"))
    checkpoint_day = int(meta["snapshot_day"])
    operations_closed_day = int(meta.get("operations_opening_closed_day", checkpoint_day))
    # Post-cutover orders and readiness live in the owning operational journal.
    for live in live_records:
        if live.get("record_type") == "Blackthorn order" and live.get("status") == "Confirmed":
            orders.append(json.loads(live["source_and_limits"]))
        elif live.get("record_type") == "Prerequisite" and live.get("status") == "Complete":
            schedule.append({"Task / settlement ID": live["record_id"], "Actual day": live["day"],
                             "Result": "Pass", "Evidence / restriction": live["source_and_limits"]})
    extra_findings = []
    opening_verification = {}
    for row in read_register(DATA / "opening-inventory.csv", "inventory_id"):
        opening_verification[row.get("item", "").strip()] = row.get("verification_status", "unverified").strip().lower()
    verification_events = []
    for event in read_register(DATA / "events.csv", "event_id") if (DATA / "events.csv").exists() else []:
        iid = event.get("inventory_id", "").strip()
        status = event.get("inventory_verification_status", "").strip().lower()
        if iid and status and event.get("status", "").strip().lower() == "posted":
            verification_events.append((int(dec(event.get("effective_day", "0"))), iid, status))
    for row in additions:
        if row.get("Status", "").strip().lower() != "posted":
            extra_findings.append(f"{row.get('Event ID', '')}: only actual posted operations can update the staging projection")
        day = int(dec(row.get("Day", "0")))
        if day <= operations_closed_day:
            extra_findings.append(f"{row.get('Event ID', '')}: new operation must be after Day {operations_closed_day} operations close")
        grade = row.get("Product grade", "").strip()
        inv_id = inventory_key(grade)
        current_verification = opening_verification.get(grade, "unverified")
        for verified_day, verified_id, verified_status in verification_events:
            if verified_id == inv_id and verified_day <= day:
                current_verification = verified_status
        if row.get("Event type", "").strip() in {"Dispatch", "Gate sale"} and current_verification != "verified":
            extra_findings.append(f"{row.get('Event ID', '')}: {grade} is not physically verified for release")
    legacy_operations = history + additions
    canonical_operations = legacy_operations
    legacy_report = replay(opening, rates, orders, schedule, legacy_operations)
    retcon_end = None
    if replacements:
        if len(retcons) != 1:
            extra_findings.append("retrospective operation rows require exactly one resolved replacement manifest")
        else:
            manifest = retcons[0]
            authority = next((r for r in live_records if r["record_id"] == manifest.get("authority")), {})
            if authority.get("record_type") != "Retcon authorization" or authority.get("status") not in {"PREPARED", "RESOLVED", "COMMITTED"}:
                extra_findings.append("replacement manifest lacks explicit player retcon authorization")
            start, retcon_end = int(manifest["start_day"]), int(manifest["end_day"])
            removed = [r["Event ID"] for r in legacy_operations if start <= int(dec(r["Day"])) <= retcon_end]
            if removed != manifest.get("superseded_event_ids"):
                extra_findings.append("retcon superseded IDs do not exactly match its bounded original interval")
            if [r["Event ID"] for r in replacements] != manifest.get("replacement_event_ids"):
                extra_findings.append("retcon replacement IDs do not exactly match its manifest")
            if any(not start <= int(dec(r["Day"])) <= retcon_end or not r.get("Evidence / inspection", "").startswith(manifest["authority"] + ":") for r in replacements):
                extra_findings.append("replacement operation is outside its authorized interval or evidence")
            canonical_operations = [r for r in legacy_operations if r["Event ID"] not in set(removed)] + replacements
            canonical_operations.sort(key=lambda r: int(dec(r["Day"])))
            # Old financial bridge is immutable; later operations use the corrected stock basis.
            legacy_report = replay(opening, rates, orders, schedule, [r for r in legacy_operations if int(dec(r["Day"])) <= retcon_end])
    # Newly authorized omitted activities supplement, never replace or bridge twice.
    supplemental_manifests = [json.loads(r["source_and_limits"]) for r in live_records
                             if r.get("record_type") == "Blackthorn retrospective supplement"
                             and r.get("status") == "Resolved"]
    canonical_operations, supplement_findings = apply_supplements(
        canonical_operations, supplements, supplemental_manifests, live_records)
    extra_findings.extend(supplement_findings)
    report = replay(opening, rates, orders, schedule, canonical_operations)
    report["superseded_interval"] = retcons[0] if replacements and len(retcons) == 1 else None
    report["supplemental_manifests"] = supplemental_manifests
    report["legacy_totals"] = legacy_report["totals"]
    report["findings"].extend(legacy_report["findings"])
    history_report = replay(opening, rates, orders, schedule, history)
    report["history_event_count"] = len(history)
    report["staging_event_count"] = len(all_additions)
    report["checkpoint_day"] = checkpoint_day
    report["source_history_totals"] = history_report["totals"]
    report["findings"].extend(extra_findings)
    report["staging_event_ids"] = [row.get("Event ID", "").strip() for row in all_additions]
    bridge_calculations = legacy_report["events"] if retcon_end is not None else report["events"]
    if retcon_end is not None:
        bridge_calculations = bridge_calculations + [r for r in report["events"] if r["day"] > retcon_end]
    report["ledger_events"], bridge_findings = ledger_events_for_operations(additions, bridge_calculations, orders)
    report["findings"].extend(bridge_findings)
    checkpoint = {}
    with (DATA / "blackthorn-tax-checkpoint.csv").open(encoding="utf-8-sig", newline="") as handle:
        checkpoint = {r["component"]: dec(r["value_gp"]) for r in csv.DictReader(handle)}
    for key, expected in (("revenue", checkpoint["accepted_revenue"]),
                          ("cogs", checkpoint["cogs"]), ("loss", checkpoint["loss_and_idle"])):
        if qmoney(dec(history_report["totals"][key])) != qmoney(expected):
            report["findings"].append(f"Day 230 {key} {qmoney(dec(history_report['totals'][key]))} does not match source checkpoint {qmoney(expected)}")
    quantity_fields = {"prior_on_site_t": "Prior on-site t", "on_site_delta_t": "On-site delta t", "transit_delta_t": "Transit delta t"}
    money_fields = {
        "prior_on_site_gp": "Prior on-site gp", "unit_cost_gp_per_t": "Unit cost gp/t",
        "on_site_delta_gp": "On-site delta gp", "transit_delta_gp": "Transit delta gp",
        "revenue_gp": "Revenue gp", "cogs_gp": "COGS gp", "loss_idle_gp": "Loss / idle expense gp",
        "production_labor_gp": "Production labor gp", "nonlabor_cost_gp": "Nonlabor cost gp",
    }
    for source, calculated in zip(history, history_report["events"]):
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

