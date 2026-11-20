# Migration Test Report

Test copy: https://github.com/coolcop17409-wq/new-dnd-world-campaign  
Visibility: Public, as explicitly chosen by the owner.  
Authority: Drive remains authoritative. No live Drive record or Project Source has been changed.

## Confirmed checkpoint

The staged estate opening cash/liability checkpoint reconciles to Day 231 late morning:

| Estate | Cash | Liabilities | Available |
|---|---:|---:|---:|
| Miregate | 501.40 gp | 14.03 gp | 487.37 gp |
| Reedbed | 63.80 gp | 8.60 gp | 55.20 gp |
| Old Distributary Fort | 130.00 gp | 5.00 gp | 125.00 gp |
| Blackthorn | 453.33 gp | 171.01 gp | 282.32 gp |

The opening receivable register is empty because the source showed zero receivables. Blackthorn's Day 230 book inventory is 41.12 t on-site, 13 t reserved and 349.43 gp cost. A Day 231 full physical count matched all six grades with zero variance; the 8 t F03 sublot was separately counted and passed its preload check. Seasoning and any other buyer-specific quality certification remain separate.

## Passed checks

- The source Operations history replayed 283 rows. Revenue 1,161.00 gp, COGS 417.83 gp, loss/idle 53.20 gp and produced cost 679.94 gp match the unrounded source formulas and Day 230 grade balances.
- Per-row comparisons cover prior quantity/cost, unit cost, on-site and transit changes, revenue, COGS, loss/idle labor, production labor and non-labor costs.
- Source fixture tests match payroll accrual 700.80 gp (336.00 management + 364.80 production), upkeep 85.71 gp, taxable base 723.70 gp and 10% assessment 72.37 gp.
- Synthetic operation case passes production → dispatch → acceptance and rejects a shipment without a passed readiness result.
- Estate ledger synthetic cases pass partial liability payment, delayed receivable collection, failed work with no unearned posting, due tax without assessment, paired transfer legs, reservation/release, shipment transit, and blocking dispatch from unverified stock.
- Synthetic character overlay passes HP, resource and inventory changes over a snapshot.
- Recurring accrual tests pass stable ID generation, exact Day 231 values, explicit close posting and rerun idempotency.
- Local verification on the current staging files: eleven unit tests passed, including the integrated post-checkpoint Blackthorn operation → estate ledger → tax chain; Blackthorn historical operation replay passed with no findings; routine-accrual preview passed with no findings; the Day 231 Magic Shops review queue passed with zero due reviews.

The manually triggered accrual posting is opt-in and requires an explicit closed-through day. Ordinary workflow runs are preview only. This staging write path has not yet been reviewed in a successful Actions run.

## Still blocks cutover

- The full operation bridge has synthetic coverage from Day 232 verification through Day 235 receivable collection, including partial acceptance, COGS, cash, remaining transit and a tax assessment delta. No real post-checkpoint campaign operation has run through the bridge or been compared with Drive.
- The estate ledger now blocks earned income/service release without prerequisite references and checks each referenced property schedule task for completed/pass result, actual day and evidence. Synthetic tests cover missing refs and a valid completed prerequisite. A DM still must identify the full set of applicable prerequisites for each actual service; the checker cannot detect an omitted dependency.
- Future Blackthorn operation rows now produce normalized ledger events for production, shipment, acceptance, COGS, loss and stock movements. Acceptance requires explicit cash received and a stable receivable ID for any unpaid remainder; the ledger validates operation-report freshness before importing the event rows. Synthetic tests cover the mapping and ledger import.
- No real campaign change has yet passed the character write → dashboard rebuild → Drive comparison path.
- Magic Shops turnover behavior is specified in its Rules export, including review intervals, odds, eligible outcomes, and recording requirements. Automated checks validate identities and quantities only; no real due review and linked player transaction has been compared.
- The opening-position audit is in [OPENING_POSITION_AUDIT.md](OPENING_POSITION_AUDIT.md), and [fixed-assets.csv](../data/estate/fixed-assets.csv) records source-supported asset components and documented costs. It leaves unknown values blank and does not claim a complete appraisal. The Blackthorn physical stock gap is closed for the Day 230 opening position by the Day 231 full count and separate F03 sublot record. Fixed-assets staging now separates documented historical costs from unknown current values; the original site boundary, base structures/fixtures and bulk tools/stores still need item-by-item inventory, and no current appraisal is recorded. The stale Miregate punt schedule still needs reconciliation (restoration date, cost and capacity remain unknown).
- A complete play → event write → regenerated views → Drive checkpoint comparison has not yet passed.
- GitHub Actions runs 77–81 completed successfully for the prior operation bridge, settlement fields, tests and estate documentation. Local full snapshot checks pass: estate ledger reconciles 121 source events to Day 231; Blackthorn replays 283 historical operations with no findings. No post-checkpoint operation rows are present in campaign data, so Actions has not exercised a real chain. GitHub Actions run 92 completed successfully. It includes the closed tax assessment apply-and-retry test, which confirms one assessment adjustment is appended and a rerun appends no duplicate. Syntax check, all eleven unit tests, operation replay, accrual preview, tax preview, estate reconciliation, tracker validation, dashboard generation and report commit passed. Run 89 failed because the generated tax report was listed in the workflow status check but omitted from `git add`; run 90 fixed that. Run 91 confirmed the final guard requiring a successful accrual close before tax assessment posting. An earlier run 63 failed on a malformed newline in the atomic close-marker write; the correction was committed and run 64 and subsequent runs passed.

## Cutover boundary

Do not move play or Project Sources to GitHub yet. Keep Drive authoritative until each blocker above is resolved and the complete update cycle has passed. Operating details live in [ONGOING_UPDATE_PROTOCOL.md](ONGOING_UPDATE_PROTOCOL.md).
