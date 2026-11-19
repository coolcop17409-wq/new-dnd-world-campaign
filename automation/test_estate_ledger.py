#!/usr/bin/env python3
"""Synthetic rule checks for the estate event ledger; no campaign data is changed."""
import csv
import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

SCRIPT = Path(__file__).with_name("estate_ledger.py")
SPEC = importlib.util.spec_from_file_location("estate_ledger", SCRIPT)
ledger = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ledger)

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
                [{"inventory_id": "grain", "estate": "Test", "item": "Grain", "opening_quantity": "5", "opening_reserved_quantity": "2", "opening_cost_gp": "50", "as_of_day": "10", "verification_status": "verified"}])
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
                  receivable_id="R1", receivable_delta_gp="30", income_delta_gp="30",
                  expense_delta_gp="20", inventory_id="grain", quantity_delta="-2",
                  inventory_cost_delta_gp="-20", shipment_id="SHIP-1", accepted_quantity="2", reserved_quantity_delta="-2")
            event("collect", "Test", 12, event_type="receivable_collection", receivable_id="R1",
                  receivable_delta_gp="-10", cash_delta_gp="10")
            event("dispatch", "Test", 13, event_type="shipment_dispatch", inventory_id="grain", quantity_delta="-1",
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

if __name__ == "__main__":
    unittest.main()
