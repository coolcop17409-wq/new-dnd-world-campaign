# Campaign tracker automation

## Current staging tools

- `estate_audit.py` checks displayed estate cash less recorded liabilities, cashbook ID uniqueness/reconciliation flags, and unfinished schedule items due by the in-game day.
- `estate_ledger.py` rolls forward the normalized cash and liability events, checks paired transfers and liability settlements, and compares results through the recorded snapshot day with the Property overview.
- `tracker_validate.py` checks character HP/resource ranges, inventory quantities, magic-shop dealer/stock/event IDs, and the character event log.
- `build_dashboard.py` creates `dashboard/dashboard.json` from the estate report and V, Cirren, Fenar, inventory, and magic-shop CSV snapshots. `dashboard/index.html` presents those staged values.
- `.github/workflows/estate-audit.yml` runs on relevant source/data/code changes. It commits generated reports even if validation fails, then leaves the workflow failed so the discrepancy remains visible.

The dashboard is a static file in the repository. GitHub Pages is not enabled and the page is not a campaign website.

## Estate ledger seed and controls

The event ledger imports 121 actual cashbook rows with stable IDs, dates, signed cash changes, source sheet/row, and evidence. Blackthorn starts from 572.11 gp reconstructed cash on Day 182; the other estates start at zero and include their recorded owner-funding entries. Opening unpaid liabilities are separate balance-forward amounts from the Day 230 overview. The checkpoint metadata records that the source balances include actual cash postings through Day 231 late morning.

The ledger checks the Day 231 checkpoint, then can show later posted entries as a staging projection. Each liability change requires a stable `liability_id`; later payments reduce that liability and cash without recording a second expense. Actual transfers use one shared `reference_id` and both cash legs must net to zero. Event IDs and liability IDs must be unique.

Fields support cash, earned income, incurred expense, liabilities, receivables, accepted quantities, inventory quantities/cost basis, reservations, shipment transit, and verification state. Receivable collections cannot exceed the recorded balance; inventory releases cannot exceed the registered quantity or cost basis. Provisional stock is excluded from eligible-to-ship quantities until a separately evidenced verification. Dispatch/arrival events move stock and cost between on-site and in-transit balances. Records require an actual day and evidence. Forecast, planned, scheduled, pending, and unconfirmed records cannot carry financial, inventory, or acceptance deltas.

No schedule date creates a wage, receipt, expense, tax, transfer, inventory movement, or shipment. Revenue is earned only on actual acceptance under the applicable agreement; payment on another date changes cash/receivable, not income a second time. A due tax is not an accrual or payment. Service receipts require their recorded readiness, ownership, capacity, route, inspection, and acceptance prerequisites. No protected reserve or cash hold is calculated.

## Current verification

The generated checkpoint report reconciles the four estates to their Day 231 displayed balances and verifies the event IDs and transfer legs. The schedule review was compared with the live Property schedules. Two old Miregate payroll rows point to a completed later settlement and are listed separately as verified successors. The character/shop validation passes for the 2026-11-19 exports.

## Not yet a replacement

This is still a staged foundation, not a complete property-workbook rewrite. The historical cashbook import does not classify all past income and incurred expenses, and the opening liability snapshot begins at Day 230. The source reports zero receivables in all four estates. Blackthorn opening book inventory is imported through Day 230, but its grade allocation and physical count remain provisional, so it cannot be treated as shippable stock until verified. Category-level wage accrual, Blackthorn production/COGS and full stock valuation, rolling tax calculations, complete accepted-cargo and delayed/failed work flows, and automated service-prerequisite checks still need rule-by-rule porting and checkpoint tests. Character event entries are additive to the snapshot, not a formula-complete character-sheet engine. Magic-shop tables and rules are validated and visible, but Actions do not roll turnover, execute trade, or decide availability.

Drive remains authoritative. Do not change the live workbook or Project Sources during staging.
