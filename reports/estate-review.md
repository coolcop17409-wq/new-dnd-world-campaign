# Estate Review

Generated from the property workbook CSV snapshot captured 2026-11-19.
Audit/report only: this process does not post wages, income, expenses, transfers, taxes, or campaign decisions.

## Imported historical snapshot reconciliation

- **Miregate: PASS** — cash 501.40 gp − liabilities 14.03 gp = available 487.37 gp.
- **Reedbed: PASS** — cash 63.80 gp − liabilities 8.60 gp = available 55.20 gp.
- **Old Distributary Fort: PASS** — cash 130.00 gp − liabilities 5.00 gp = available 125.00 gp.
- **Blackthorn: PASS** — cash 453.33 gp − liabilities 171.01 gp = available 282.32 gp.
- **Miregate cashbook: PASS** — opening 0.00 gp + net posted changes 501.40 gp = 501.40 gp.
- **Reedbed cashbook: PASS** — opening 0.00 gp + net posted changes 63.80 gp = 63.80 gp.
- **Old Distributary Fort cashbook: PASS** — opening 0.00 gp + net posted changes 130.00 gp = 130.00 gp.
- **Blackthorn cashbook: PASS** — opening 572.11 gp + net posted changes -118.78 gp = 453.33 gp.

All available-cash, cashbook roll-forward, and cashbook ID checks passed.

## Schedule review

The current campaign day could not be read from CAMPAIGN_STATE. Supply it in the manual workflow input to list due and overdue unfinished estate tasks.

## Current owning requests

These owner requests retain their actual dependencies/next triggers; being listed is not evidence of completion or a due payment.

- **Blackthorn — BT-CAERETH-SAMPLES-244** (waiting): Caereth framework sample/freight economics. Dependency/trigger: data/estate/operational-checkpoint.csv.
- **Miregate — MG-INSURANCE-LIVE-244** (waiting): MG-INSURANCE Esgar quote. Dependency/trigger: data/estate/operational-checkpoint.csv.
- **Blackthorn — BT-V-HORSES-244** (open): Four visiting V-owned coachhorses, separatefromHedda pair. Dependency/trigger: data/estate/operational-checkpoint.csv.
- **Blackthorn — R200-BT-F04-FOLLOWUP** (in progress): Pevra F04 shipment and next business. Dependency/trigger: data/estate/operational-checkpoint.csv.
- **Blackthorn — R200-BT-GARRAN-NEXT** (open): Standing ordinary surplus outlet. Dependency/trigger: data/estate/operational-checkpoint.csv.
- **Old Distributary Fort — R200-OF-COLLECT** (open): Crown invoice and unbilled duty. Dependency/trigger: data/estate/operational-checkpoint.csv.
- **Miregate — R200-MG-PILOT-NEXT** (waiting): Pilot sold; future trading terms. Dependency/trigger: data/estate/operational-checkpoint.csv.
- **Miregate — R200-MG-FARM-NEXT** (waiting): Four-acre cereal trial and farmed/milled grain. Dependency/trigger: data/estate/operational-checkpoint.csv.
- **Reedbed — R200-RB-FLEET-NEXT** (open): Qualified BARGE01 upper freight. Dependency/trigger: data/estate/operational-checkpoint.csv.
- **Miregate and Reedbed — R200-RIVER-CUSTOMER-NEXT** (open): Confirmed customer slots and retention. Dependency/trigger: data/estate/operational-checkpoint.csv.
- **Reedbed — R200-RB-WALKIN-NEXT** (open): Passing traffic, bench and storage. Dependency/trigger: data/estate/operational-checkpoint.csv.
- **All properties — R200-DEVELOPMENT-NEXT** (in progress): Ranked development and habitation. Dependency/trigger: data/estate/operational-checkpoint.csv.
- **All registered estates — PS244-ACTIVE-MANDATE** (Open): Continuous all-product/service customer acquisition. Dependency/trigger: data/estate/operational-checkpoint.csv.
- **Miregate — PS-MG-F-NEXT** (Open): Current4t storage and next246handoff. Dependency/trigger: data/estate/operational-checkpoint.csv.

## Source boundary

GitHub is authoritative after owner cutover. The workbook CSVs audited above are immutable historical references; current estate state is data/estate/ and reports/estate-ledger.json. Never write live state back to Drive. Resolved retrospective manifests supersede only their explicit scope and preserve the imported checks.
