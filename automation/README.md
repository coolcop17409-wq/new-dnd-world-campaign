# Campaign tracker automation

## Current staging tools

- `estate_audit.py` checks each estate's displayed available balance against cash less recorded liabilities, checks cashbook ID uniqueness and reconciliation flags, and lists unfinished scheduled tasks due on or before the campaign day.
- `estate_ledger.py` rolls forward the normalized event ledger and its opening balances, then compares cash, open liabilities, and available cash to the imported Property overview snapshots.
- `build_dashboard.py` creates `dashboard/dashboard.json` from estate results plus the V, Cirren, Fenar, inventory, and magic-shop CSV snapshots. `dashboard/index.html` presents those values as a searchable-at-a-glance page.
- `.github/workflows/estate-audit.yml` runs these checks when relevant snapshots, ledger data, code, or campaign day change. It records reports even when a check fails, then marks the workflow failed so the discrepancy is visible.

The dashboard is a staged snapshot view. GitHub Pages is not enabled; it is not a campaign website.

## Estate ledger boundary

The seed imports cashbook rows as uniquely identified cash events and records the nonzero Day 230 overview liabilities as opening balances. Blackthorn starts from its reconstructed 572.11 gp opening cash on Day 182; the other estate cashbooks include their funding entries from a zero opening balance. The seed preserves source file, source row, evidence, actual day, amount and signed cash delta.

The opening-liability entries are balance-forward amounts, not a re-posting of historical expenses. New entries must distinguish work/cost incurred from a later payment. Payment reduces cash and the related liability; it does not create a second expense. Matched estate-transfer legs share an ID. Taxes arise only from posted taxable results, and a due date never posts or pays tax.

Inventory and shipment changes require actual evidenced receipt, dispatch, acceptance, damage, or loss. Forecasts and plans have no financial or inventory effect. The estate system introduces no protected reserve or cash hold. It does not assume scheduled work happened.

## Validation status and limits

The staging workflow compares its output to the 2026-11-19 workbook exports and the current campaign-state snapshot. Drive remains authoritative. The engine currently validates balances and stable IDs; it is not yet a complete replacement for every estate-specific formula or transaction worksheet. Wages, production costing, per-period tax calculations, order acceptance, delayed/failed work, cargo ownership/custody, inventory valuation, and all service prerequisites still need complete rule-by-rule checkpoint validation before cutover.

Never update the staging ledger by copying a forecast. Add only a confirmed event and evidence, then let the workflow report whether the staging calculation matches the workbook snapshot. Keep the source workbook unchanged during testing.
