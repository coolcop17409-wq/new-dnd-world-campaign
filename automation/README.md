# Campaign tracker automation

This toolchain supports the active GitHub campaign source. Live campaign text and structured records are in `campaign/`, routed `trackers/` CSVs, and the owning journals under `data/`; reports and the dashboard are generated outputs. Drive Docs/workbooks are historical references, not write targets. The owner-directed 2026-11-20 cutover left the checks in `migration/TEST_REPORT.md` as post-cutover validation. Do not call untested paths verified or invent campaign events.

## Tools

- `estate_audit.py` checks displayed estate cash against recorded liabilities, cashbook IDs/reconciliation flags, and unfinished schedule items due by the supplied campaign day.
- `estate_ledger.py` rolls normalized cash, liability, receivable and inventory events forward from the dated opening snapshots. It checks the Day 231 cash/liability checkpoint, paired transfers, unique keys, settlements, verified inventory and projected balances. Earned income and shipment/gate-sale release events must reference completed property schedule tasks; the engine checks actual day and evidence.
- `blackthorn_rules.py` reproduces source-checked effective-date payroll/upkeep accrual and rolling 10% tax helper calculations. `blackthorn_tax.py` rolls the Day 230 tax checkpoint forward by source tax period from posted actual events and the Blackthorn operation replay; it previews period assessment deltas and can post them only after an explicitly closed day and matching accrual close marker. Tax payments remain separate actual events.
- `routine_accruals.py` previews deterministic Blackthorn management payroll, production payroll and upkeep accruals through an explicitly confirmed closed day. An Actions checkbox is required to post; preview is default. Posting is stable-ID/idempotent and only writes the campaign event journal and close marker. It does not pay wages or tax.
- `blackthorn_operations.py` replays the 283 source Blackthorn operations rows, checks formulas row-by-row, and calculates production cost, revenue, COGS, stock, shipment transit, loss and labor. Future rows in `data/estate/blackthorn-operations-events.csv` are evidence-gated and must follow the Day 231 checkpoint. Passed future results are normalized into ledger events; sale acceptance requires explicit cash received and a stable receivable ID for any unpaid balance.
- `tracker_validate.py` checks character HP/resource ranges, inventory quantities, shop dealer/lot/event keys and character event IDs.
- `magic_shop_review_queue.py` lists dealer reviews due by an explicitly supplied campaign day. It never rolls or posts outcomes; the DM resolves each through the Magic Shops Rules and records the result once.
- `build_dashboard.py` creates a read-only JSON dashboard from estate, V, Cirren, Fenar, shared inventory and Magic Shops snapshots plus posted character events.
- `.github/workflows/estate-audit.yml` runs tests and audits on relevant changes or manual dispatch. It writes generated reports and dashboard data back to the GitHub repository. GitHub Pages is not enabled.

## Accounting and safeguards

The event ledger keeps earned income/cost separate from later cash movement. Payments settle the same liability; collections reduce the same receivable. Partial payments, transfers, stock quantity/cost, reservations, shipment transit and physical verification have distinct fields and checks. Forecasts and scheduled tasks do not produce transactions. A due date does not itself assess or pay tax. No protected reserve is calculated.

Opening cash is based on 121 actual cashbook rows, with liabilities as a Day 230 balance-forward checkpoint and cash postings through Day 231 late morning. Current opening receivables are zero in the source. The six Blackthorn stock grades are verified against the Day 231 physical count of the Day 230 close. The 8 t F03 lot is separately documented as a memorandum sublot in `data/estate/blackthorn-stocktake.csv`; this detail supports the grade-level opening ledger without double-counting the lot.

## Formula checks currently passed

- Blackthorn history replay: 283 operation rows; revenue 1,161.00 gp, COGS 417.83 gp, loss/idle 53.20 gp and produced cost 679.94 gp. Row-level source formulas and Day 230 grade balances match.
- Blackthorn Day 230 accrued payroll, upkeep, taxable base and 10% assessment fixtures match the workbook.
- Synthetic production → dispatch → acceptance and failed-readiness cases pass.
- Synthetic estate event tests cover partial payment, delayed collection after acceptance, failed work, tax date without assessment, inventory reservation/release, shipment transit and paired transfers. A combined Day 232–235 Blackthorn scenario now passes verification → dispatch → partial acceptance → COGS/revenue → cash plus receivable → later collection, with two tonnes still in transit; it also confirms the first-period tax roll-forward and assessment delta.
- Synthetic character event overlay, recurring-accrual retry, Magic Shops review-queue, operation-to-ledger import and cash/receivable settlement cases pass locally.

## Post-cutover validation

The remaining evidence-dependent checks are tracked in [migration/TEST_REPORT.md](../migration/TEST_REPORT.md). Use that report as the current status; do not reintroduce stale pre-cutover gates or treat synthetic fixtures as real campaign events. The historical Day 231 stocktake and property register remain available in the baseline workbook export.

## Fast-play durability

The active CAMPAIGN_STATE starts with the current DAY heading; the current continuity README contains only live routes (less than 8K characters); recent played SESSION_LOG is kept below 75K by archiving closed evidence. The fast packet generator checks these limits. V's Fighter Battle Master Superiority Dice are read from the separate row in the V character CSV, with actual spends and qualifying recovery applied only by the character event overlay. A failed build is a repair signal: never manufacture rolls/recovery, delete true events or edit generated counters as a workaround.

## Fast-play trigger and freshness contract (2026-11-21)

`.github/workflows/fast-play.yml` automatically runs after the final authoritative CAMPAIGN_STATE update. Intermediate `data/characters/events.csv` writes no longer launch duplicate, potentially future-dated packet builds. At an unchanged checkpoint with journal-only changes, explicitly dispatch and verify the workflow. The packet builder verifies the latest recent SESSION_LOG event ID is reflected in CAMPAIGN_STATE even if both use the same day. Preserve exact accepted sources and use source-targeted repairs, never direct edits of derived dashboard or PLAY_NOW counters.

## Live magic browsing latency guard

For a known market, present existing verified offers from current scene/Stock without rerunning generation, multi-site source lookups or full estate validation. New markets use exactly one permitted local opening/draw with already sourced template candidates; first-time draws stay in the unsynced scene ledger until a natural sync. A magic-shop CSV-only update runs `.github/workflows/magic-shop-check.yml`, a lightweight shop/identity validation without estate ledger/Blackthorn/tax replay or derived dashboard write. The next final campaign checkpoint commit refreshes PLAY_NOW and dashboard, so market changes do not require holding the scene while the estate workflow runs.

## Nonblocking specialist handoff queue

See `automation/handoffs/README.md`. Existing scheduled tasks (shops, quests, estates, atlas, record maintenance) act as separate workers over immutable lane requests and verified result receipts. This does not instantly trigger an arbitrary chat, and does not replace authoritative campaign journals. `automation/handoffs/validate.py` and `.github/workflows/handoff-validate.yml` check file integrity only; they never run gameplay or research.

## Background synchronization repair

See `handoffs/sync-repair/README.md` for the implemented scoped preflight, diagnostics, stable-signature queue/draft-PR collector, Work subscription and scheduled fallback. `sync_validate.py` checks only the requested subsystem; `sync_batch.py` provides strict idempotent append helpers. Generated writes use `publish_generated.py`, rejecting source-head changes instead of rebasing stale output. Verification status is in `handoffs/sync-repair/IMPLEMENTATION_REPORT.md`.
