# Migration Test Report

Test copy: https://github.com/coolcop17409-wq/new-dnd-world-campaign  
Visibility: Public, as explicitly chosen by the owner.

## What passed

- GitHub connector reads and writes were verified earlier, including a non-campaign write/read round trip.
- Representative campaign files, including current state, rules, DM preparation, political reference, and workbook snapshots, were retrieved from GitHub.
- Existing Drive checkpoint values checked against the workbook snapshots: V 48/48 HP and AC 19; Cirren 51/51 HP and AC 18; Fenar 59/59 HP and AC 14.
- Estate audit, event ledger, tracker validation, dashboard generation, and the synthetic ledger scenario test all passed in the latest full GitHub Actions run (run 39). The ledger contains 121 unique actual cashbook IDs and reconciles the Day 231 checkpoint:
  - Miregate 501.40 gp cash, 14.03 gp liabilities, 487.37 gp available.
  - Reedbed 63.80 gp cash, 8.60 gp liabilities, 55.20 gp available.
  - Old Distributary Fort 130.00 gp cash, 5.00 gp liabilities, 125.00 gp available.
  - Blackthorn 453.33 gp cash, 171.01 gp liabilities, 282.32 gp available.
- The unfinished-task report was checked against the live Property schedules. It lists 16 current due/overdue/held items. Two stale Miregate payroll task rows are explicitly mapped to their completed Day 229 successor; they are not duplicated as open tasks.
- Tracker validation passed for V, Cirren, Fenar, their inventory snapshots, 89 magic-shop stock rows, dealer keys, and existing shop event IDs.
- A generated Day 231 dashboard was read back. It shows party values, tracked resources, owned-item/custody notes, estate balances, and 57 nonzero shop lots.
- The live Property workbook shows zero receivables across all four estates. Blackthorn's Day 230 Accounts formulas total 41.12 t on-site book stock, 13 t reserved, 0 t in transit, and 349.43 gp book cost. The six opening grade rows were imported as provisional because the workbook explicitly says physical count, seasoning, and buyer certification are unverified; the GitHub ledger reports zero eligible-to-ship stock until verified.
- Synthetic ledger scenarios passed for a partially paid liability, an accepted sale with delayed collection, failed work that posts no amount, a scheduled tax date that posts no assessment, inventory reservations, shipment dispatch/arrival, inventory quantity/cost release, and paired estate-transfer legs. These test the ledger rules in isolation; they do not establish those events happened in the campaign.

## What remains unverified

- No campaign event has yet been written through the character event ledger; the event-log overlay and a complete play → write → regenerate → compare cycle still need an actual confirmed campaign change.
- The dashboard is a repository artifact; GitHub Pages is not enabled.
- The estate seed preserves cashbook history and starts liabilities from an as-of-Day-230 balance-forward snapshot. The receivable register is empty because the source balance is zero; Blackthorn opening book inventory is imported but unverified. Full historical/activity formula parity remains incomplete for wages, operating costs, tax calculations, inventory valuation/COGS, production, shipment and acceptance workflows, and automated service prerequisite checks.
- Character event checks are range checks; no real campaign change has yet been written through that ledger, and the checks do not replace every sheet formula or apply 2014 class/rest mechanics automatically.
- Magic-shop keys and stock rows validate, but its due business reviews and turnover remain DM-resolved under the existing Rules tab.
- Drive remains authoritative. No live Drive record or ChatGPT Project Source was changed, and no cutover was made.


## Work added after the latest verified run

- Added a synthetic guard case that attempts to dispatch provisional Blackthorn stock and expects the ledger to reject the release.
- Imported the Blackthorn daily payroll/upkeep rate rows and added formula helpers for effective-date accrual and the 10% rolling tax assessment. Added Day 230 parity fixtures: 700.80 gp total payroll accrual, split into 336.00 gp management and 364.80 gp production payroll; 85.71 gp upkeep; 723.70 gp tax base; and 72.37 gp assessment.
- Both synthetic tests were rerun locally against the latest staging files and passed. A live unformatted read confirmed Operations COGS is 417.8297 gp, rounded to 417.83 gp in Accounts; the displayed-value CSV rounds individual rows and sums to 417.82 gp, so the CSV alone is not precise enough for cent-level COGS parity. The unrounded source components are captured in `data/estate/blackthorn-tax-checkpoint.csv`. The connector did not expose an updated Actions result, so run 39 remains the latest Actions run I can verify. The formula port does not yet generate recurring posting events or derive tax inputs from the raw activity journal.

The cutover boundary remains unchanged: first finish the rule ports and then test a real campaign update end to end against the source workbook.
