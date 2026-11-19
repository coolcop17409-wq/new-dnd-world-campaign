# Estate automation

## What it does

`estate_audit.py` reads the current Property workbook's four estate overview CSV snapshots, reconciles cash less recorded unpaid liabilities against each displayed available balance, checks for repeated cashbook IDs, and can list unfinished scheduled tasks due by a supplied in-game day.

The GitHub Actions workflow runs the audit when property snapshots or the audit code changes. Use **Actions → Estate audit → Run workflow** and enter the current campaign day to produce a due/overdue task list.

The output is `reports/estate-review.md`.

## Guardrails

- This operates on the 2026-11-19 CSV snapshots in the migration copy. It does not read or edit Google Drive.
- It does not post or pay wages, recognize income, incur costs, transfer money, calculate new taxes, close a campaign day, or decide whether planned work occurred.
- Forecasts and planned tasks do not affect cash reconciliation.
- No reserve or protected-cash hold is introduced.
- A validation finding makes the workflow fail after it records the report, so the discrepancy remains visible.
- Drive remains authoritative until a separate migration and full workflow verification.

## Next implementation stages

1. Compare the audit against each live Property workbook tab and resolve any parser gaps.
2. Move estate activity and cashbook records into versionable transaction data with unique event IDs; preserve the source XLSX snapshots for reference.
3. Port the workbook's formulas and estate rules into calculation code, validating outputs against the Sheets before any cutover.
4. Expand the review to wages, taxes, shipment/stock dependencies, boat traffic, and conditional service tasks. Require confirmed in-game events before posting their financial effects.
