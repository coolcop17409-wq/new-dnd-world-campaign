# Campaign tracker automation

This toolchain now supports the active GitHub campaign source. Live source records and event journals are under `trackers/`, `data/`, and `campaign/`; the reports and dashboard are derived outputs. The owner-directed cutover on 2026-11-20 leaves the open validation items in `migration/TEST_REPORT.md` as post-cutover work. Do not call untested paths verified or invent campaign events.

## Tools

- `estate_audit.py` checks displayed estate cash against recorded liabilities, cashbook IDs/reconciliation flags, and unfinished schedule items due by the supplied campaign day.
- `estate_ledger.py` rolls normalized cash, liability, receivable and inventory events forward from the dated opening snapshots. It checks the Day 231 cash/liability checkpoint, paired transfers, unique keys, settlements, verified inventory and projected balances. Earned income and shipment/gate-sale release events must reference completed property schedule tasks; the engine checks actual day and evidence.
- `blackthorn_rules.py` reproduces source-checked effective-date payroll/upkeep accrual and rolling 10% tax helper calculations. `blackthorn_tax.py` rolls the Day 230 tax checkpoint forward by source tax period from posted actual events and the Blackthorn operation replay; it previews period assessment deltas and can post them only after an explicitly closed day and matching accrual close marker. Tax payments remain separate actual events.
- `routine_accruals.py` previews deterministic Blackthorn management payroll, production payroll and upkeep accruals through an explicitly confirmed closed day. An Actions checkbox is required to post; preview is default. Posting is stable-ID/idempotent and only writes the staging event ledger and close marker. It does not pay wages or tax.
- `blackthorn_operations.py` replays the 283 source Blackthorn operations rows, checks formulas row-by-row, and calculates production cost, revenue, COGS, stock, shipment transit, loss and labor. Future rows in `data/estate/blackthorn-operations-events.csv` are evidence-gated and must follow the Day 231 checkpoint. Passed future results are normalized into ledger events; sale acceptance requires explicit cash received and a stable receivable ID for any unpaid balance.
- `tracker_validate.py` checks character HP/resource ranges, inventory quantities, shop dealer/lot/event keys and character event IDs.
- `magic_shop_review_queue.py` lists dealer reviews due by an explicitly supplied campaign day. It never rolls or posts outcomes; the DM resolves each through the Magic Shops Rules and records the result once.
- `build_dashboard.py` creates a read-only JSON dashboard from estate, V, Cirren, Fenar, shared inventory and Magic Shops snapshots plus posted character events.
- `.github/workflows/estate-audit.yml` runs tests and audits on relevant changes or manual dispatch. It writes generated reports to the staging repository. GitHub Pages is not enabled.

## Accounting and safeguards

The event ledger keeps earned income/cost separate from later cash movement. Payments settle the same liability; collections reduce the same receivable. Partial payments, transfers, stock quantity/cost, reservations, shipment transit and physical verification have distinct fields and checks. Forecasts and scheduled tasks do not produce transactions. A due date does not itself assess or pay tax. No protected reserve is calculated.

Opening cash is based on 121 actual cashbook rows, with liabilities as a Day 230 balance-forward checkpoint and cash postings through Day 231 late morning. Current opening receivables are zero in the source. The six Blackthorn stock grades are verified against the Day 231 physical count of the Day 230 close. The 8 t F03 lot is separately documented as a memorandum sublot in `data/estate/blackthorn-stocktake.csv`; this detail supports the grade-level opening ledger without double-counting the lot.

## Formula checks currently passed

- Blackthorn history replay: 283 operation rows; revenue 1,161.00 gp, COGS 417.83 gp, loss/idle 53.20 gp and produced cost 679.94 gp. Row-level source formulas and Day 230 grade balances match.
- Blackthorn Day 230 accrued payroll, upkeep, taxable base and 10% assessment fixtures match the workbook.
- Synthetic production → dispatch → acceptance and failed-readiness cases pass.
- Synthetic estate event tests cover partial payment, delayed collection after acceptance, failed work, tax date without assessment, inventory reservation/release, shipment transit and paired transfers. A combined Day 232–235 Blackthorn scenario now passes verification → dispatch → partial acceptance → COGS/revenue → cash plus receivable → later collection, with two tonnes still in transit; it also confirms the first-period tax roll-forward and assessment delta.
- Synthetic character event overlay, recurring-accrual retry, Magic Shops review-queue, operation-to-ledger import and cash/receivable settlement cases pass locally.

## Remaining cutover blockers

- No real post-Day-231 Blackthorn operation chain has yet run through the bridge. Its payment, receivable and physical-stock treatment has synthetic tests only.
- General service prerequisite checks across Miregate, Reedbed, the Fort and Blackthorn are still a documented manual gate; only Blackthorn readiness has an automated passed-task check.
- Character changes have passed a synthetic overlay only. A real confirmed play change must be written and compared against the owning Drive sheet.
- Magic Shops `Rules` fully describes review/turnover behavior, but software only validates keys/quantities. A real due review and linked player purchase must be run and compared.
- Opening ownership, custody, inventory and commitments need a complete confirmed opening checkpoint for every system.
- A full play → write → rebuild → compare sync and an Actions posting run still need review.

See [ongoing update protocol](../migration/ONGOING_UPDATE_PROTOCOL.md) for the required operating procedure and cutover gates. Drive remains authoritative. The Day 231 stocktake and Blackthorn fixed-assets register are also recorded in the live Property workbook; Project Sources were not changed.
