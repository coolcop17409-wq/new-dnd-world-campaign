#!/usr/bin/env python3
"""Synthetic rule checks for the estate event ledger; no campaign data is changed."""
import csv
import importlib.util
import io
import json
import tempfile
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

SCRIPT = Path(__file__).with_name("estate_ledger.py")
SPEC = importlib.util.spec_from_file_location("estate_ledger", SCRIPT)
ledger = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ledger)
RULES_SPEC = importlib.util.spec_from_file_location("blackthorn_rules", Path(__file__).with_name("blackthorn_rules.py"))
blackthorn_rules = importlib.util.module_from_spec(RULES_SPEC)
RULES_SPEC.loader.exec_module(blackthorn_rules)
DASHBOARD_SPEC = importlib.util.spec_from_file_location("build_dashboard", Path(__file__).with_name("build_dashboard.py"))
dashboard = importlib.util.module_from_spec(DASHBOARD_SPEC)
DASHBOARD_SPEC.loader.exec_module(dashboard)
SHOP_REVIEW_SPEC = importlib.util.spec_from_file_location("magic_shop_review_queue", Path(__file__).with_name("magic_shop_review_queue.py"))
magic_shop_review = importlib.util.module_from_spec(SHOP_REVIEW_SPEC)
SHOP_REVIEW_SPEC.loader.exec_module(magic_shop_review)
OPERATIONS_SPEC = importlib.util.spec_from_file_location("blackthorn_operations", Path(__file__).with_name("blackthorn_operations.py"))
blackthorn_operations = importlib.util.module_from_spec(OPERATIONS_SPEC)
OPERATIONS_SPEC.loader.exec_module(blackthorn_operations)
ACCRUAL_SPEC = importlib.util.spec_from_file_location("routine_accruals", Path(__file__).with_name("routine_accruals.py"))
routine_accruals = importlib.util.module_from_spec(ACCRUAL_SPEC)
ACCRUAL_SPEC.loader.exec_module(routine_accruals)

FIELDS = [
    "event_id", "estate", "effective_day", "event_type", "category",
    "reference_id", "liability_id", "receivable_id", "amount_gp",
    "cash_delta_gp", "liability_delta_gp", "receivable_delta_gp",
    "income_delta_gp", "expense_delta_gp", "inventory_id", "quantity_delta",
    "inventory_cost_delta_gp", "shipment_id", "accepted_quantity",
    "prerequisite_ref", "counterparty", "description", "evidence",
    "source_file", "source_row", "status", "reserved_quantity_delta",
    "in_transit_quantity_delta", "in_transit_cost_delta_gp", "inventory_verification_status",
]

class EstateLedgerScenarioTests(unittest.TestCase):
    def write_csv(self, path, fields, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(data)

    def test_partial_payment_delayed_sale_failed_work_tax_due_and_transfer(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data = root / "data" / "estate"
            prop = root / "trackers" / "csv" / "property"
            reports = root / "reports"
            (data / "snapshot-meta.json").parent.mkdir(parents=True, exist_ok=True)
            (data / "snapshot-meta.json").write_text(
                json.dumps({"snapshot_day": 10, "captured_date": "fixture"}),
                encoding="utf-8",
            )
            self.write_csv(prop / "test-schedule.csv",
                ["Task ID", "Actual day", "Result", "Actual evidence"],
                [{"Task ID": "READY-1", "Actual day": "10", "Result": "Pass",
                  "Actual evidence": "fixture readiness evidence"}])
            self.write_csv(data / "opening-balances.csv",
                ["estate", "opening_cash_gp"],
                [{"estate": "Test", "opening_cash_gp": "100"},
                 {"estate": "Partner", "opening_cash_gp": "20"}])
            self.write_csv(data / "opening-liabilities.csv",
                ["liability_id", "estate", "description", "opening_amount_gp", "as_of_day", "evidence"],
                [{"liability_id": "L0", "estate": "Test", "opening_amount_gp": "10", "as_of_day": "10"}])
            self.write_csv(data / "opening-receivables.csv",
                ["receivable_id", "estate", "customer", "opening_amount_gp", "as_of_day", "evidence"],
                [{"receivable_id": "R0", "estate": "Test", "opening_amount_gp": "20", "as_of_day": "10"}])
            self.write_csv(data / "opening-inventory.csv",
                ["inventory_id", "estate", "item", "opening_quantity", "opening_reserved_quantity", "opening_transit_quantity", "opening_cost_gp", "opening_transit_cost_gp", "as_of_day", "verification_status", "evidence"],
                [{"inventory_id": "grain", "estate": "Test", "item": "Grain", "opening_quantity": "5", "opening_reserved_quantity": "2", "opening_cost_gp": "50", "as_of_day": "10", "verification_status": "verified"},
                 {"inventory_id": "timber", "estate": "Test", "item": "Timber", "opening_quantity": "4", "opening_cost_gp": "20", "as_of_day": "10", "verification_status": "provisional"}])
            events = []
            def event(event_id, estate, day, **values):
                row = {name: "" for name in FIELDS}
                row.update({"event_id": event_id, "estate": estate, "effective_day": str(day), "status": "posted"})
                row.update(values)
                if row["status"] == "posted":
                    row["evidence"] = row.get("evidence") or "fixture evidence"
                events.append(row)
            event("accrue", "Test", 11, event_type="service_complete", liability_id="L1",
                  liability_delta_gp="5", expense_delta_gp="5")
            event("partial-pay", "Test", 12, event_type="bill_payment", liability_id="L0",
                  liability_delta_gp="-3", cash_delta_gp="-3")
            event("accepted-sale", "Test", 11, event_type="sale_accepted", reference_id="SHIP-1",
                  prerequisite_ref="READY-1",
                  receivable_id="R1", receivable_delta_gp="30", income_delta_gp="30",
                  expense_delta_gp="20", inventory_id="grain", quantity_delta="-2",
                  inventory_cost_delta_gp="-20", shipment_id="SHIP-1", accepted_quantity="2", reserved_quantity_delta="-2")
            event("collect", "Test", 12, event_type="receivable_collection", receivable_id="R1",
                  receivable_delta_gp="-10", cash_delta_gp="10")
            event("dispatch", "Test", 13, event_type="shipment_dispatch", inventory_id="grain", quantity_delta="-1",
                  prerequisite_ref="READY-1",
                  inventory_cost_delta_gp="-10", in_transit_quantity_delta="1", in_transit_cost_delta_gp="10", shipment_id="SHIP-2")
            event("delivery", "Test", 14, event_type="shipment_arrival", inventory_id="grain", quantity_delta="1",
                  inventory_cost_delta_gp="10", in_transit_quantity_delta="-1", in_transit_cost_delta_gp="-10", shipment_id="SHIP-2")
            event("failed-work", "Test", 11, event_type="service_failed", status="failed")
            event("tax-calendar-only", "Test", 11, event_type="tax_due", status="scheduled")
            event("transfer-out", "Test", 12, event_type="estate_transfer", reference_id="XFER-1", cash_delta_gp="-7")
            event("transfer-in", "Partner", 12, event_type="estate_transfer", reference_id="XFER-1", cash_delta_gp="7")
            self.write_csv(data / "events.csv", FIELDS, events)
            for filename, cash, liabilities in [("test.csv", "100", "10"), ("partner.csv", "20", "0")]:
                self.write_csv(prop / filename, ["label", "value"], [
                    {"label": "cash", "value": cash},
                    {"label": "available", "value": str(float(cash) - float(liabilities))},
                    {"label": "liabilities", "value": liabilities},
                ])
            old = (ledger.DATA, ledger.PROPERTY, ledger.REPORT, ledger.ESTATES)
            ledger.DATA, ledger.PROPERTY, ledger.REPORT = data, prop, reports / "ledger.json"
            ledger.ESTATES = {
                "Test": {"overview": "test.csv", "cash": ["cash"], "available": ["available"], "liabilities": ["liabilities"]},
                "Partner": {"overview": "partner.csv", "cash": ["cash"], "available": ["available"], "liabilities": ["liabilities"]},
            }
            try:
                with redirect_stdout(io.StringIO()):
                    self.assertEqual(ledger.main(), 0)
                report = json.loads((reports / "ledger.json").read_text(encoding="utf-8"))
                event("income-no-prerequisite", "Test", 15, event_type="service_income",
                      income_delta_gp="1", evidence="fixture actual income")
                self.write_csv(data / "events.csv", FIELDS, events)
                with redirect_stdout(io.StringIO()):
                    self.assertEqual(ledger.main(), 1)
                gate_report = json.loads((reports / "ledger.json").read_text(encoding="utf-8"))
                self.assertTrue(any("requires prerequisite_ref" in finding for finding in gate_report["findings"]))
                event("provisional-release", "Test", 15, event_type="shipment_dispatch",
                      prerequisite_ref="READY-1", inventory_id="timber", quantity_delta="-1",
                      inventory_cost_delta_gp="-5", shipment_id="SHIP-PROVISIONAL",
                      in_transit_quantity_delta="1", in_transit_cost_delta_gp="5")
                self.write_csv(data / "events.csv", FIELDS, events)
                with redirect_stdout(io.StringIO()):
                    self.assertEqual(ledger.main(), 1)
                blocked_report = json.loads((reports / "ledger.json").read_text(encoding="utf-8"))
            finally:
                ledger.DATA, ledger.PROPERTY, ledger.REPORT, ledger.ESTATES = old
            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report["estates"]["Test"]["projected_cash_gp"], "100.00")
            self.assertEqual(report["estates"]["Test"]["projected_liabilities_gp"], "12.00")
            self.assertEqual(report["estates"]["Test"]["projected_receivables_gp"], "40.00")
            self.assertEqual(report["estates"]["Test"]["actual_income_after_snapshot_gp"], "30.00")
            self.assertEqual(report["estates"]["Test"]["actual_expense_after_snapshot_gp"], "25.00")
            self.assertEqual(report["estates"]["Test"]["inventory_items"]["grain"]["book_quantity"], "3.0000")
            self.assertEqual(report["estates"]["Test"]["inventory_items"]["grain"]["reserved_quantity"], "0.0000")
            self.assertEqual(report["estates"]["Test"]["inventory_items"]["grain"]["verification_status"], "verified")
            self.assertEqual(report["estates"]["Test"]["inventory_items"]["grain"]["in_transit_quantity"], "0.0000")
            self.assertEqual(report["estates"]["Partner"]["projected_cash_gp"], "27.00")
            self.assertEqual(blocked_report["status"], "CHECK")
            self.assertTrue(any(
                "verify its physical count before dispatch or release" in finding
                for finding in blocked_report["findings"]
            ))

    def test_character_event_overlay_matches_snapshot_plus_confirmed_change(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            events = [
                {"event_id": "fixture-hp", "campaign_day": "231", "owner": "Valenthia",
                 "record_type": "stat", "target": "HP", "delta": "-1", "absolute_value": "",
                 "evidence": "synthetic fixture only", "status": "posted"},
                {"event_id": "fixture-resource", "campaign_day": "231", "owner": "Valenthia",
                 "record_type": "resource", "target": "Psi", "delta": "-1", "absolute_value": "",
                 "evidence": "synthetic fixture only", "status": "posted"},
                {"event_id": "fixture-item", "campaign_day": "231", "owner": "Valenthia",
                 "record_type": "inventory", "target": "Arrows", "delta": "-1", "absolute_value": "",
                 "evidence": "synthetic fixture only", "status": "posted"},
            ]
            self.write_csv(
                root / "data" / "characters" / "events.csv",
                ["event_id", "campaign_day", "owner", "record_type", "target", "delta",
                 "absolute_value", "evidence", "status"],
                events,
            )
            payload = {
                "party": [{"name": "Valenthia", "hp": "48", "max_hp": "48",
                           "resources": [{"name": "Psi", "current": "2", "max": "3"}]}],
                "inventory": {"Valenthia": [
                    {"item": "Arrows", "qty": "10", "quantity_display": "10", "detail": "tracked"}
                ]},
            }
            old_root = dashboard.ROOT
            dashboard.ROOT = root
            try:
                dashboard.apply_character_events(payload)
            finally:
                dashboard.ROOT = old_root
            self.assertEqual(payload["party"][0]["hp"], "47.0")
            self.assertEqual(payload["party"][0]["resources"][0]["current"], "1.0")
            self.assertEqual(payload["inventory"]["Valenthia"][0]["qty"], "9.0")

    def test_closed_day_accruals_are_stable_and_idempotent(self):
        rates_path = Path(__file__).parents[1] / "data" / "estate" / "blackthorn-rates.csv"
        with rates_path.open(encoding="utf-8", newline="") as handle:
            rates = list(csv.DictReader(handle))
        historic = routine_accruals.generate(rates, 182, 230)
        self.assertEqual(historic["status"], "PASS")
        self.assertEqual(historic["totals_gp"]["management_payroll"], "336.00")
        self.assertEqual(historic["totals_gp"]["production_payroll"], "364.80")
        self.assertEqual(historic["totals_gp"]["upkeep"], "85.71")
        one_day = routine_accruals.generate(rates, 230, 231)
        self.assertEqual(one_day["event_count"], 3)
        self.assertEqual(one_day["totals_gp"]["management_payroll"], "7.00")
        self.assertEqual(one_day["totals_gp"]["production_payroll"], "7.60")
        self.assertEqual(one_day["totals_gp"]["upkeep"], "1.79")
        ids = {row["event_id"]: row for row in one_day["events"]}
        repeated = routine_accruals.generate(rates, 230, 231, ids)
        self.assertEqual(repeated["event_count"], 0)
        self.assertEqual(repeated["status"], "PASS")
        self.assertTrue(all(row["cash_delta_gp"] == "" for row in one_day["events"]))

    def test_magic_shop_review_queue_uses_confirmed_day_without_resolving_turnover(self):
        dealers = [
            {"Settlement": "Test Market", "Dealer": "Open seller", "Next due": "20",
             "Last review / turnover": "6", "Status": "Established",
             "Review question · preparation": "Check actual buyer."},
            {"Settlement": "Test Market", "Dealer": "Not due", "Next due": "35",
             "Last review / turnover": "10", "Status": "Established",
             "Review question · preparation": "Check staffing."},
            {"Settlement": "UNASSIGNED-CITY-01", "Dealer": "Package", "Next due": "A+28",
             "Last review / turnover": "", "Status": "Unassigned",
             "Review question · preparation": "Bind only on activation."},
        ]
        no_day = magic_shop_review.review_queue(dealers)
        self.assertIsNone(no_day["due_count"])
        due = magic_shop_review.review_queue(dealers, 22)
        self.assertEqual(due["due_count"], 1)
        self.assertEqual(due["due_reviews"][0]["dealer"], "Open seller")
        self.assertEqual(due["unbound_count"], 1)
        self.assertIn("does not roll", due["note"])

    def test_confirmed_closed_day_apply_is_atomic_and_idempotent(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data = root / "data" / "estate"
            reports = root / "reports"
            data.mkdir(parents=True)
            (data / "routine-accrual-meta.json").write_text(
                json.dumps({"last_confirmed_closed_day": 230, "source_opening_day": 182}),
                encoding="utf-8",
            )
            self.write_csv(data / "blackthorn-rates.csv",
                ["type", "cost_family", "rate_gp", "unit", "from_day", "through_day"],
                [{"type": "Payroll", "cost_family": "Management", "rate_gp": "7.00",
                  "unit": "day", "from_day": "1", "through_day": ""},
                 {"type": "Payroll", "cost_family": "Production", "rate_gp": "7.60",
                  "unit": "day", "from_day": "1", "through_day": ""},
                 {"type": "Upkeep", "cost_family": "", "rate_gp": "1.79",
                  "unit": "day", "from_day": "1", "through_day": ""}])
            self.write_csv(data / "events.csv", routine_accruals.EVENT_FIELDS, [])
            old = (routine_accruals.DATA, routine_accruals.REPORT, sys.argv)
            routine_accruals.DATA, routine_accruals.REPORT = data, reports / "preview.json"
            try:
                sys.argv = ["routine_accruals.py", "--closed-through-day", "231", "--apply"]
                with redirect_stdout(io.StringIO()):
                    self.assertEqual(routine_accruals.main(), 0)
                first_report = json.loads((reports / "preview.json").read_text(encoding="utf-8"))
                with (data / "events.csv").open(encoding="utf-8", newline="") as handle:
                    first_events = list(csv.DictReader(handle))
                saved_meta = json.loads((data / "routine-accrual-meta.json").read_text(encoding="utf-8"))
                with redirect_stdout(io.StringIO()):
                    self.assertEqual(routine_accruals.main(), 0)
                second_report = json.loads((reports / "preview.json").read_text(encoding="utf-8"))
                with (data / "events.csv").open(encoding="utf-8", newline="") as handle:
                    second_events = list(csv.DictReader(handle))
            finally:
                routine_accruals.DATA, routine_accruals.REPORT, sys.argv = old
            self.assertEqual(first_report["applied_count"], 3)
            self.assertEqual(len(first_events), 3)
            self.assertEqual(saved_meta["last_confirmed_closed_day"], 231)
            self.assertEqual(second_report["applied_count"], 0)
            self.assertEqual(len(second_events), 3)

    def test_blackthorn_production_dispatch_accept_and_readiness_gate(self):
        opening = [{"Grade": "Dressed stone", "Quantity t": "5.000", "Amount gp": "50.00"}]
        rates = [
            {"Type": "Payroll", "Cost family": "Stone", "Rate gp": "3.50",
             "Unit": "day", "From day": "1", "Through day": ""},
            {"Type": "ProductCost", "Cost family": "Stone", "Product grade": "Dressed stone",
             "Rate gp": "2.50", "Unit": "ton", "From day": "1", "Through day": ""},
        ]
        orders = [{"Order line ID": "ORDER-1", "Status": "Confirmed",
                   "Product grade": "Dressed stone", "Price gp/t": "10.00",
                   "Ordered t": "4.000", "Readiness task ID": "QC-1"}]
        schedule = [{"Task / settlement ID": "QC-1", "Result": "Pass", "Actual day": "10"}]
        operations = [
            {"Event ID": "produce-1", "Day": "10", "Event type": "Produce",
             "Product grade": "Dressed stone", "Quantity t": "2.000",
             "Extra direct gp / labor allocation": "", "Evidence / inspection": "fixture"},
            {"Event ID": "dispatch-1", "Day": "11", "Event type": "Dispatch",
             "Product grade": "Dressed stone", "Quantity t": "3.000",
             "Order line ID": "ORDER-1", "Shipment / transfer ID": "SHIP-1",
             "Evidence / inspection": "fixture"},
            {"Event ID": "accept-1", "Day": "13", "Event type": "Accept",
             "Product grade": "Dressed stone", "Quantity t": "3.000",
             "Order line ID": "ORDER-1", "Shipment / transfer ID": "SHIP-1",
             "Evidence / inspection": "fixture"},
        ]
        result = blackthorn_operations.replay(opening, rates, orders, schedule, operations)
        self.assertEqual(result["status"], "PASS", result["findings"])
        self.assertEqual(result["totals"]["revenue"], "30.00")
        self.assertEqual(result["totals"]["cogs"], "25.07")
        self.assertEqual(result["totals"]["produced_cost"], "8.50")
        self.assertEqual(result["on_site"]["Dressed stone"]["quantity_t"], "4.0000")
        self.assertEqual(result["in_transit"], {})
        blocked = blackthorn_operations.replay(
            opening, rates, orders, [{"Task / settlement ID": "QC-1",
                                      "Result": "Scheduled", "Actual day": "10"}], operations
        )
        self.assertEqual(blocked["status"], "CHECK")
        self.assertTrue(any("readiness task" in finding for finding in blocked["findings"]))

    def test_blackthorn_routine_accrual_and_tax_match_day230_source(self):
        data = Path(__file__).parents[1] / "data" / "estate" / "blackthorn-rates.csv"
        with data.open(encoding="utf-8", newline="") as handle:
            rates = list(csv.DictReader(handle))
        all_payroll = blackthorn_rules.accrue_daily_rates(
            rates, opening_day=182, start_day=183, through_day=230, rate_type="Payroll"
        )
        management = blackthorn_rules.accrue_daily_rates(
            [row for row in rates if row["cost_family"] == "Management"],
            opening_day=182, start_day=183, through_day=230, rate_type="Payroll"
        )
        production = blackthorn_rules.accrue_daily_rates(
            [row for row in rates if row["cost_family"] != "Management"],
            opening_day=182, start_day=183, through_day=230, rate_type="Payroll"
        )
        upkeep = blackthorn_rules.accrue_daily_rates(
            rates, opening_day=182, start_day=183, through_day=230, rate_type="Upkeep"
        )
        self.assertEqual(all_payroll, blackthorn_rules.money("700.80"))
        self.assertEqual(management, blackthorn_rules.money("336.00"))
        self.assertEqual(production, blackthorn_rules.money("364.80"))
        self.assertEqual(upkeep, blackthorn_rules.money("85.71"))
        self.assertEqual(
            blackthorn_rules.accrue_daily_rates(
                rates, opening_day=182, start_day=231, through_day=232, rate_type="Payroll"
            ),
            blackthorn_rules.money("29.20"),
        )
        checkpoint_path = Path(__file__).parents[1] / "data" / "estate" / "blackthorn-tax-checkpoint.csv"
        with checkpoint_path.open(encoding="utf-8", newline="") as handle:
            checkpoint = {row["component"]: row["value_gp"] for row in csv.DictReader(handle)}
        taxable = blackthorn_rules.blackthorn_tax_base(
            taxable_carry=checkpoint["taxable_carry"],
            accepted_revenue=checkpoint["accepted_revenue"],
            cogs=checkpoint["cogs"],
            loss_and_idle=checkpoint["loss_and_idle"],
            management_payroll=checkpoint["management_payroll"],
            upkeep=checkpoint["upkeep"],
            incurred_operating_expenses=checkpoint["incurred_operating_expenses"],
        )
        self.assertEqual(taxable, blackthorn_rules.money(checkpoint["taxable_base"]))
        self.assertEqual(
            blackthorn_rules.blackthorn_tax_assessment(taxable),
            blackthorn_rules.money(checkpoint["tax_assessment"]),
        )
        self.assertEqual(blackthorn_rules.blackthorn_tax_assessment("-10.00"), blackthorn_rules.money("0.00"))

if __name__ == "__main__":
    unittest.main()
