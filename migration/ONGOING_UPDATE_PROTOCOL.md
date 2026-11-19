# Ongoing update protocol — GitHub staging

This procedure defines how confirmed campaign changes are recorded and checked in this repository. It does not authorize play from GitHub or change the current authority: Drive remains authoritative until the cutover gates in `migration/TEST_REPORT.md` are satisfied.

## Update sequence

1. Confirm the latest played checkpoint and any explicit correction. Use actual in-game day and evidence; do not infer completion from a planned date, scheduled task, forecast, or elapsed time alone.
2. Record each confirmed change once in the owning journal. Keep the event ID stable on retry. Use separate IDs for separate economic legs such as earned income, a receivable, and later cash collection.
3. Recalculate the derived view from journals and dated opening snapshots. Do not hand-edit generated reports or dashboard data.
4. Run the relevant audit, formula replay, and edge-case tests. Resolve or clearly hold discrepancies before presenting any value as current.
5. Update the campaign checkpoint only after all owning ledgers and generated views have been verified. Preserve the previous checkpoint and its evidence.
6. Until cutover, compare the staged result with the Drive checkpoint and keep Drive authoritative.

A generated schedule date is a reminder to review. It does not itself post wages, receipts, expenses, taxes, inventory, transfers, or a completed task.

## Estates

### Cash, liabilities, income and taxes

- `data/estate/opening-balances.csv`, `opening-liabilities.csv`, `opening-receivables.csv` and `events.csv` are the normalized ledger. Each actual change needs a unique event ID, estate, actual day, evidence and relevant stable liability, receivable, inventory or transfer key.
- Record an earned cost once when incurred. Record payment later as a cash decrease and reduction of that same liability; do not record a second expense.
- Record earned income at the actual acceptance or other contract trigger. Record a receivable when payment is still owed; later collection reduces that receivable and increases cash without earning the income again. If acceptance is paid immediately, connect the cash to the acceptance event and do not create a lingering receivable.
- Partial payments reduce only the outstanding balance. Failed work posts no unearned service income. Actual costs or wages already incurred remain due even when the job fails.
- A tax date or forecast is not an assessment or payment. Calculate tax from realized income and incurred deductible costs under the estate's source rule, carry any unpaid assessed balance forward, and post cash only when paid.
- Paired estate transfers share a reference ID and must have equal opposite cash legs. No protected reserve is calculated.

### Recurring Blackthorn accruals

`automation/routine_accruals.py` calculates management payroll, production payroll and upkeep only through an explicitly confirmed closed campaign day. Normal Actions runs create a preview only. To post, run the workflow manually with both `closed_through_day` and `post_closed_day_accruals=true`. The posting action:

- refuses to proceed without the explicit close day or when the preview has conflicts;
- uses deterministic day/category IDs, so a retry cannot duplicate an already posted accrual;
- appends the earned liability rows to the staging event ledger and advances the close marker;
- does not pay wages, post cash, or create tax assessment/payment entries.

Production payroll is a liability when earned. The operation replay allocates that labor cost to actual production or idle loss. Do not also post it as general expense at accrual time. Day 231 remains an open-day checkpoint until an authorized update explicitly confirms its close.

### Blackthorn production, stock, shipment and acceptance

`automation/blackthorn_operations.py` replays the source Operations register against dated payroll/product-cost rates, confirmed orders, readiness tasks, opening stock and append-only staged operation rows. It calculates labor allocation, product cost, on-site and in-transit stock/cost, accepted revenue, COGS, losses and idle labor. It checks row formulas against the Day 230 workbook values and gates dispatch/gate sale on a passed readiness task.

- New operation rows go in `data/estate/blackthorn-operations-events.csv` only after the activity happened and has evidence. A unique event ID is required; all new rows must be after the Day 231 snapshot. Do not overwrite historical workbook rows.
- Opening inventory by grade is provisional. Physical verification is a separate evidenced event. Until verified, no opening stock can be dispatched or sold.
- Dispatch moves stock and cost into transit; acceptance, return, loss, or regrade must reference the same shipment/transfer and cannot exceed the remaining quantity.
- Acceptance earns the confirmed order price only for the accepted quantity. The operations replay now produces normalized ledger events for future production, labor, shipment, acceptance, return, loss and regrade rows. The estate ledger imports them only when the operation report is PASS, its snapshot matches, and its staged event IDs match the operation journal.
- For each future Accept or Gate sale, `Cash received gp` is mandatory, including explicit `0` when unpaid. The bridge records income once, creates a receivable for the unpaid remainder under `Receivable ID`, and records immediate cash only for the stated amount. A later collection is a separate row in `data/estate/events.csv` that reduces the same receivable and increases cash. Do not also copy the acceptance income or stock movement into that file.
- Actual dispatch, arrival, buyer acceptance, payment, partial delivery, rejected cargo, or failed work are separate facts. Enter only the leg that actually occurred and retain any remaining in-transit or receivable balance. The bridge is covered by synthetic mapping and estate-ledger import tests, but a real future operation chain has not yet run.

### Service prerequisites

Before a property service, repair, shipment, or revenue entry is posted, inspect the relevant property schedule and actual evidence. Validate every dependency that applies to that specific service:

- legal authority/title or charter and authorized operator;
- completed inspection, safe access and passed technical readiness;
- actual crew, materials, funding and capacity available for the work;
- route, ownership, custody, quantity and condition of goods;
- customer's actual request, agreed rate/terms, completion and acceptance.

Use the source task IDs in `prerequisite_ref`, separated by semicolons when more than one applies. The estate ledger now requires this field for earned income, service completion and shipment/gate-sale release events. It checks that every referenced ID exists in a property schedule and has a completed/passed result, actual day, and evidence no later than the event day. Blackthorn's production replay separately requires its order's readiness task to have passed before dispatch or gate sale.

This automated check validates only the dependencies that were named. The DM must still identify every applicable legal, staffing, safety, capacity, route, custody and acceptance condition; a missing dependency cannot be inferred from one valid task ID. A hold, missing inspection, failed test, unavailable crew, unaccepted service or planned delivery blocks the dependent income or movement. Record a failed attempt only when it happened; post no unearned income.

## Characters

- Character sheets remain the opening snapshots. Confirmed later changes are additive rows in `data/characters/events.csv`; never invent an event to make a synthetic test look real.
- Use one event per actual change, stable ID, character, campaign day, record type, target, delta or explicit absolute value, evidence and `posted` status. Record inventory custody/ownership changes in the shared inventory source as well as personal quantity changes when relevant.
- Apply actual sheet maximums and current values. Reject impossible HP, resource or item quantities; a rest changes resources only when its confirmed conditions and the campaign's 2014/homebrew rest rule are satisfied.
- The dashboard overlay test currently passes for synthetic HP, resource and inventory changes. A real, confirmed play change still must go through write → rebuild → compare against the owning Drive sheet before cutover. The automated event overlay is not a full character-sheet formula engine and does not adjudicate class, rest, spell, or 2014 mechanics.

## Magic shops

The migrated Magic Shops `Rules` tab is the behavior specification; its searchable export is `trackers/csv/magic-shops/rules.csv`. `Dealers` owns contacts and review dates, `Stock` owns unique physical lots, and `Events` records inquiry, holds, offers, sales, deliveries, and turnover reviews.

- On confirmed campaign time advancement, check each elapsed due review and any independently dated business event once. Resolve established commitments first. Do not roll turnover merely because a chat, unrelated event, or item review occurred.
- Follow the Rules tab's stated base odds, one predeclared pressure adjustment, eligible outcome list and relative weights. Use genuine executed random rolls for uncertain campaign outcomes; a fixture/test seed is never campaign resolution. If genuine RNG is unavailable, disclose that and pause the uncertain result rather than inventing a roll.
- A sale requires a capable buyer, matching lot, and terms; a replacement requires an identifiable source and arrival. A review with no change is still recorded, with covered date(s) and the next review date. Update stock only when custody, availability, quantity or terms actually change.
- Preserve player holds, accepted offers, purchases, seller decisions, prior discoveries and unique-item custody. Never post a shop NPC transaction to V's purse or inventory. A player purchase needs linked, idempotent shop, cash and inventory entries.
- Current automated checks validate dealer/lot/event keys and nonnegative quantities. They do not determine what V knows, execute turnover rolls, or apply a shop event to party cash/inventory. Those are verified by the play-and-sync procedure; a complete linked transaction test remains a cutover gate.

## Cutover checks

Do not point play or Project Sources here until all of these pass:

- opening cash, liabilities, receivables, inventory/custody, staff, ownership and outstanding commitments are complete at a confirmed checkpoint;
- estate activity from the checkpoint forward recalculates correctly, including the Blackthorn operations-to-estate-ledger bridge and general service prerequisite checks;
- the recurring close/post/retry path is tested in Actions and does not double-post; the forward tax-base roll-forward and assessment posting are also checked from realized entries;
- one real campaign update succeeds across estate, character, inventory and shop cases as applicable, then matches the owning source workbook;
- the generated views and sync instructions are usable from the GitHub connector, with failures and conflicts surfaced;
- public repository exposure of DM preparation remains an accepted user choice.

Until then, GitHub is a tested staging copy and Drive remains authoritative.
