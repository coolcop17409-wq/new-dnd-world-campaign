# Migration Test Report

Test copy: https://github.com/coolcop17409-wq/new-dnd-world-campaign  
Visibility: Public, as explicitly chosen by the owner.  
Authority: Drive remains authoritative. GitHub is staging only; Project Sources and campaign instructions have not been changed.

## Reconciled checkpoints

- **Campaign state:** Day 235 evening, upper Miregate commercial landing.
- **Financial snapshot:** Day 231 late morning cash, with liabilities seeded at the completed Day 230 close. The source review through Day 235 found no supported post-Day 231 estate cash, liability, receivable, or stock movement. The campaign checkpoint was advanced without fabricating a financial close.
- **Day 233:** Mila secured a conditional allocation of 6 t customer-owned sacked wheat at Aven Marris's Caereth freight store through close Day 236. It is not at the landing; no contract terms were accepted and no cash, inventory, income, expense or receivable was posted.
- **Day 235:** Captain Orla was physically present with the River Heron. Her presence did not activate the charter or establish route clearance, cargo, shipment, or payment.

The financial opening balances therefore remain Miregate 501.40 gp cash / 14.03 gp liabilities; Reedbed 63.80 / 8.60; Old Distributary Fort 130.00 / 5.00; Blackthorn 453.33 / 171.01. These remain Day 231 cash and Day 230 liability values, not Day 235 revaluations.

## Resolved record discrepancies

- The Miregate schedule row for the small punt is now closed under the explicit retroactive ruling that all four estate boats were restored and made operational. The broken/cannibalized and rebuild-pending text is superseded. Punt restoration date, cost and capacity remain unknown; no inferred expense or cash posting was made.
- Blackthorn movable contents are itemized to the level supported by campaign history in `data/estate/movable-assets.csv` and the live **Blackthorn - Movable Assets** tab. Known counts are retained; unknown quantities and ambiguous wording stay explicit. Watchpost weapons/stores with unresolved ownership are listed separately and excluded from owned net worth.
- Fixed assets include the named structures and site improvements. Five known improvements total 191 gp documented historical cost and carrying value under the current no-depreciation/no-impairment basis. This is not a market appraisal. The original parcel boundaries/base fixtures remain incompletely described, and the source has no current valuation method or appraisal amount; complete estate net worth cannot be calculated from the current evidence.

## Previously validated prototype

GitHub Actions run 104 passed against the then-current staging commit: Python syntax checks, synthetic ledger edge cases, estate validation/dashboard generation, and generated-report commit. That run predates this Day 235 reconciliation and updated movable-asset data. Any new automatic workflow result must be checked separately.

The bridge still has no real post-checkpoint operation chain compared with Drive. There has been no real character write-and-compare, no real Magic Shops turnover cycle, and no end-to-end campaign change through event posting and regenerated views. These remain cutover blockers.

## Cutover boundary

Do not move play or Project Sources to GitHub yet. Keep Drive authoritative until the real update cycle is reconciled and complete. See [ONGOING_UPDATE_PROTOCOL.md](ONGOING_UPDATE_PROTOCOL.md).
