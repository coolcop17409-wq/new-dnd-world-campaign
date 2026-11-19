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

The opening receivable register is empty because the source showed zero receivables. Blackthorn's Day 230 book inventory is 41.12 t on-site, 13 t reserved and 349.43 gp cost; physical count, grade allocation, seasoning and buyer certification remain provisional, so no opening stock is eligible to ship.

## Passed checks

- The source Operations history replayed 283 rows. Revenue 1,161.00 gp, COGS 417.83 gp, loss/idle 53.20 gp and produced cost 679.94 gp match the unrounded source formulas and Day 230 grade balances.
- Per-row comparisons cover prior quantity/cost, unit cost, on-site and transit changes, revenue, COGS, loss/idle labor, production labor and non-labor costs.
- Source fixture tests match payroll accrual 700.80 gp (336.00 management + 364.80 production), upkeep 85.71 gp, taxable base 723.70 gp and 10% assessment 72.37 gp.
- Synthetic operation case passes production → dispatch → acceptance and rejects a shipment without a passed readiness result.
- Estate ledger synthetic cases pass partial liability payment, delayed receivable collection, failed work with no unearned posting, due tax without assessment, paired transfer legs, reservation/release, shipment transit, and blocking dispatch from unverified stock.
- Synthetic character overlay passes HP, resource and inventory changes over a snapshot.
- Recurring accrual tests pass stable ID generation, exact Day 231 values, explicit close posting and rerun idempotency.
- Local verification on the current staging files: six unit tests passed; Blackthorn operation replay passed with no findings; routine-accrual preview passed with no findings.

The manually triggered accrual posting is opt-in and requires an explicit closed-through day. Ordinary workflow runs are preview only. This staging write path has not yet been reviewed in a successful Actions run.

## Still blocks cutover

- Blackthorn operation calculations are not yet integrated with the generic estate ledger. Future accepted sales need an explicit, linked cash-versus-receivable posting, and stock/cost movement must not be entered twice.
- Cross-estate service prerequisites remain a documented manual review. Only Blackthorn's readiness-task gate is automated.
- No real campaign change has yet passed the character write → dashboard rebuild → Drive comparison path.
- Magic Shops turnover behavior is specified in its Rules export, including review intervals, odds, eligible outcomes, and recording requirements. Automated checks validate identities and quantities only; no real due review and linked player transaction has been compared.
- Opening custody, ownership, staff, inventory and commitments need full checkpoint completeness beyond current estate cash/liabilities and Blackthorn book stock.
- A complete play → event write → regenerated views → Drive checkpoint comparison has not yet passed.
- A newer Actions result must be reviewed before cutover. The Actions run from these latest commits is not represented by the local tests and must not be assumed successful.

## Cutover boundary

Do not move play or Project Sources to GitHub yet. Keep Drive authoritative until each blocker above is resolved and the complete update cycle has passed. Operating details live in [ONGOING_UPDATE_PROTOCOL.md](ONGOING_UPDATE_PROTOCOL.md).
