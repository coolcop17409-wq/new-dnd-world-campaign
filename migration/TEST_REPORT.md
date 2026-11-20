# Migration Test Report

Test copy: https://github.com/coolcop17409-wq/new-dnd-world-campaign  
Visibility: Public, as explicitly chosen by the owner.  
Authority: Drive remains authoritative. GitHub is staging only; Project Sources and campaign instructions have not been changed.

## Reconciled checkpoints

- **Campaign state:** Day 235 evening, upper Miregate commercial landing.
- **Financial snapshot:** Day 231 late morning cash, with liabilities seeded at the completed Day 230 close. The source review through Day 235 found no supported post-Day 231 estate cash, liability, receivable, or stock movement. Hessa's Day 232 and Neris's Day 233 Miregate offers, the Day 233 Neris storage review, and Reedbed's Day 234 Neris cargo call have target dates in the past but no confirmed outcomes; Drive schedules now flag them for review, without treating them as success or failure. The campaign checkpoint was advanced without fabricating a financial close.
- **Day 233:** Mila secured a conditional allocation of 6 t customer-owned sacked wheat at Aven Marris's Caereth freight store through close Day 236. It is not at the landing; no contract terms were accepted and no cash, inventory, income, expense or receivable was posted.
- **Day 235:** Captain Orla was physically present with the River Heron. Her presence did not activate the charter or establish route clearance, cargo, shipment, or payment.

The financial opening balances therefore remain Miregate 501.40 gp cash / 14.03 gp liabilities; Reedbed 63.80 / 8.60; Old Distributary Fort 130.00 / 5.00; Blackthorn 453.33 / 171.01. These remain Day 231 cash and Day 230 liability values, not Day 235 revaluations.

## Resolved record discrepancies

- The Miregate schedule now records the punt as estate-owned, restoration already in progress by Day 231, with a planned Day 231–232 work window. The explicit Day 235 owner ruling treats it as operational; the exact completion day, cost and capacity remain unknown. No labor/material cost or cash posting was inferred.
- Blackthorn movable contents are itemized to the level supported by campaign history in `data/estate/movable-assets.csv` and the live **Blackthorn - Movable Assets** tab. Known counts are retained; unknown quantities and ambiguous wording stay explicit. Watchpost weapons/stores with unresolved ownership are listed separately and excluded from owned net worth.
- Fixed assets include the named structures and site improvements. Five known improvements total 191 gp documented historical cost and carrying value under the current no-depreciation/no-impairment basis. This is not a market appraisal. The owner adopted 8,000 gp as a provisional aggregate going-concern value for Blackthorn on Day 235; it is recorded in the live Property Overview and the staged non-additive valuation register. It is not an independent appraisal. Exact parcel boundaries/base fixtures and values for component items remain unknown. Do not add the aggregate to individual assets or report total net worth until treatment of cash, inventory and liabilities is defined against this aggregate.

## Previously validated prototype

The latest confirmed Actions run in the available history is 44660947398 on commit 09dd3b87, before the current Day 235 / 8,000 gp valuation / character-event commits. It passed on that earlier commit; a successful current-head run has not been verified.

The bridge still has no real post-checkpoint operation chain compared with Drive. The V Day 231 funeral prepayment (−12 gp) is staged as a dated purse event over a pre-event baseline. A local dashboard rebuild applied the event and matched the Drive Inventory row 29 closing purse of 1,185 gp, 3 sp, 8 cp; tracker validation passed with one posted character event. A real due Magic Shops owner review was written to Drive Events row 29 and Dealer row 50, then synced to GitHub; genuine d100 69 vs. 10 produced no change. The dashboard review queue rebuilt at Day235 and now shows four other due reviews, with Dewlight rescheduled for Day260; no V discovery or transaction occurred. There has been no confirmed post-checkpoint Blackthorn operation chain. The current-main Actions result still cannot be verified from the available check/status lookup. These remain cutover blockers.

## Cutover boundary

Do not move play or Project Sources to GitHub yet. Keep Drive authoritative until the real update cycle is reconciled and complete. See [ONGOING_UPDATE_PROTOCOL.md](ONGOING_UPDATE_PROTOCOL.md).
