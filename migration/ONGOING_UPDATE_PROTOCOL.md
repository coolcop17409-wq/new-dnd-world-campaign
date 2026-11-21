# Ongoing update protocol — active GitHub source

This procedure governs live recording and verification of confirmed campaign changes in this repository after the owner-directed 2026-11-20 cutover. GitHub is authoritative for campaign text and structured records. Drive Docs/workbooks are historical references; maps and large images remain in Drive/Library as designated visual assets. The owner authorized cutover with the outstanding items in `migration/TEST_REPORT.md` still open; continue validation without misrepresenting those checks as passed or fabricating campaign evidence.

## Magic-market inquiry latency prevention — 2026-11-21

Discovery-only browsing is a playable read/scene action, not proof that every physical shop ledger must be rewritten before the answer. For known settlement stock, reuse current retained verified offers and named Stock/Dealers/Events; present prices/effects/availability immediately, no repeated vendor draw, blanket web browsing, website-by-website citation hunt, GitHub Actions polling or financial replay. For a previously unprepared market, run one genuine first-preparation draw under Rural market rules, choose grounded preverified candidates and retain stable results in the unsynced ledger; never pretend those events were committed if not. Purchases/holds/custody changes require explicit V choice and eventual linked postings. An actual new local opening may be committed at the next natural boundary, not before presenting the offers; if an end/pause is requested, sync normally.

Magic-shop CSV edits must trigger **magic-shop-only lightweight validation**, not the full estate operations/tax workflow. Do not force game-turn CI pass while showing offers. At a real synchronization boundary write only affected owners, verify event IDs and stock custody, then commit CAMPAIGN_STATE last. The fast-play packet regenerates on that final checkpoint; a temporary before-state standalone market event is expected and is not permission to fabricate a later in-game action. Heavy source breadth checks belong to planned vendor candidate prep or a specifically requested deep item research task.

## Ordinary-play synchronization threshold — 2026-11-21

The full guarded commit/validation path is **not** a per-turn prerequisite for ordinary interactive play. A player's normal shopping/resupply instruction, low-stakes accepted conversation, nearby routine movement, or voluntary companion split may advance actual play without an immediate GitHub write. Track exact accepted outcome and debit/custody/knowledge in an in-conversation unsynchronized ledger; narrate the next actionable scene promptly. A routine 6gp-class provisions purchase (amount illustrative, not an automatic authorization cap) is not a "major transaction" just because currency changes. Never invent a price, expenditure, consent or result; use verified established values and narrow lookup only if a necessary fact is missing.

Flush that ledger at completed consequential combat or substantial exploration, qualifying rests, significant contractual/rare-item/property transactions, quest/NPC milestone, roughly8–12 substantive changed exchanges, explicit pause/end, Sync campaign, or known imminent chat handoff. Not every room change or normal storefront sale is a milestone. Preserve causal order; write affected journals in a guarded batch, verify, finalize CAMPAIGN_STATE last and let the lightweight workflow rebuild views. A routine turn need **zero** connector calls when its facts are already verified. Do not call GitHub merely to check that the cached current scene is still unchanged. Keep unsynced values in this conversation and clearly acknowledge possible persistence limits if the chat closes before a sync. On a player-requested "Sync campaign" do the full safe process, not deferred shorthand.

## Update sequence

1. Confirm the latest played checkpoint and any explicit correction. Use actual in-game day and evidence; do not infer completion from a planned date, scheduled task, forecast, or elapsed time alone.
2. Record each confirmed change once in the owning journal. Keep the event ID stable on retry. Use separate IDs for separate economic legs such as earned income, a receivable, and later cash collection.
3. Recalculate the derived view from journals and dated opening snapshots. Do not hand-edit generated reports or dashboard data.
4. Run the relevant audit, formula replay, and edge-case tests. Resolve or clearly hold discrepancies before presenting any value as current.
5. Update the campaign checkpoint only after all owning ledgers and generated views have been verified. Preserve the previous checkpoint and its evidence.
6. After each update, verify the GitHub commit and affected generated views. Compare with Drive only to investigate historical/source discrepancies; GitHub governs any post-cutover campaign record.

A generated schedule date is a reminder to review. It does not itself post wages, receipts, expenses, taxes, inventory, transfers, or a completed task.

## Estates

### Cash, liabilities, income and taxes

- `data/estate/opening-balances.csv`, `opening-liabilities.csv`, `opening-receivables.csv` and `events.csv` are the normalized ledger. Each actual change needs a unique event ID, estate, actual day, evidence and relevant stable liability, receivable, inventory or transfer key.
- Record an earned cost once when incurred. Record payment later as a cash decrease and reduction of that same liability; do not record a second expense.
- Record earned income at the actual acceptance or other contract trigger. Record a receivable when payment is still owed; later collection reduces that receivable and increases cash without earning the income again. If acceptance is paid immediately, connect the cash to the acceptance event and do not create a lingering receivable.
- Partial payments reduce only the outstanding balance. Failed work posts no unearned service income. Actual costs or wages already incurred remain due even when the job fails.
- A tax date or forecast is not an assessment or payment. `blackthorn_tax.py` uses the Day 230 source-verified base/assessment, source 90-day periods, posted realized income/expense events, operation replay results, and effective-dated management/upkeep rates. The first period rolls forward from Day 230 through Day 271; later periods use their own actual period windows. It computes assessment deltas against already assessed amounts and preserves unpaid liability balances. A manual Actions assessment post requires both an explicit `closed_through_day` and `post_closed_day_accruals=true`; the tax script checks the accrual close marker matches that day. Preview is the default. Payments remain separate, evidence-backed cash/liability events.
- Paired estate transfers share a reference ID and must have equal opposite cash legs. No protected reserve is calculated.

### Recurring Blackthorn accruals

`automation/routine_accruals.py` calculates management payroll, production payroll and upkeep only through an explicitly confirmed closed campaign day. Normal Actions runs create a preview only. To post, run the workflow manually with both `closed_through_day` and `post_closed_day_accruals=true`. The posting action:

- refuses to proceed without the explicit close day or when the preview has conflicts;
- uses deterministic day/category IDs, so a retry cannot duplicate an already posted accrual;
- appends the earned liability rows to the staging event ledger and advances the close marker;
- does not pay wages or create tax-payment entries. Assessment deltas require the separate `assess_closed_tax_periods` checkbox plus a matching explicit accrual close.

Production payroll is a liability when earned. The operation replay allocates that labor cost to actual production or idle loss. Do not also post it as general expense at accrual time. Day 231 remains an open-day checkpoint until an authorized update explicitly confirms its close.

### Blackthorn production, stock, shipment and acceptance

`automation/blackthorn_operations.py` replays the source Operations register against dated payroll/product-cost rates, confirmed orders, readiness tasks, opening stock and append-only staged operation rows. It calculates labor allocation, product cost, on-site and in-transit stock/cost, accepted revenue, COGS, losses and idle labor. It checks row formulas against the Day 230 workbook values and gates dispatch/gate sale on a passed readiness task.

- New operation rows go in `data/estate/blackthorn-operations-events.csv` only after the activity happened and has evidence. A unique event ID is required; all new operation rows must follow the verified Day 230 operations close; the Day 231 cash snapshot is a different boundary. Do not overwrite historical workbook rows.
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

## Post-cutover validation backlog

The owner authorized GitHub cutover before every item below had passed. Keep each item visible and work it only when confirmed campaign evidence and the needed test opportunity exist:

- opening cash, liabilities, receivables, inventory/custody, staff, ownership and outstanding commitments are complete at a confirmed checkpoint;
- a real Blackthorn operation chain is checked through physical verification, dispatch, partial acceptance, COGS, receivable creation and later collection, then compared with the owning Drive workbook;
- service events cite and satisfy the full applicable prerequisites, not merely one valid task ID;
- the recurring close/post/retry path is exercised through the Actions checkbox and does not double-post;
- the forward tax-base roll-forward and closed-period assessment posting are tested against the source rule and use only realized entries; the integrated synthetic chain passes, while an actual closed period still needs Drive comparison before cutover;
- one real campaign update succeeds across estate, character, inventory and shop cases as applicable, then matches the owning source workbook;
- the generated views and sync instructions are usable from the GitHub connector, with failures and conflicts surfaced;
- public repository exposure of DM preparation remains an accepted user choice.

GitHub remains the active source while this validation backlog is resolved.

## Fast-play read and scoped validation (2026-11-20)

At chat startup retrieve the short continuity README, exact active CAMPAIGN_STATE, current rules index, scoped recent SESSION_LOG and relevant scene/prep, plus the generated `runtime/PLAY_NOW.md` when consistent with the checkpoint. The packet is built by `automation/build_play_packet.py` from the **current checkpoint** and the journal-overlaid dashboard, with embedded source hashes and fail-closed day/tracker-status checks. It is **not** a duplicate authority or event journal. If missing, delayed or stale, use owning sources instead and report material mismatch.

The **final CAMPAIGN_STATE commit** triggers `.github/workflows/fast-play.yml` after character/event journals have been verified; intermediate character-event commits deliberately do **not** trigger duplicate or premature runs. A journal-only correction at an unchanged checkpoint requires explicit manual fast-play workflow dispatch and verification. The workflow validates posted trackers, regenerates the dashboard from the last verified estate ledger report, cross-checks the newest session-log event ID against the active checkpoint, rebuilds PLAY_NOW and commits only changed generated views. Estate/property/market/rules-of-accounting changes trigger the comprehensive `estate-audit.yml` with Blackthorn replay, taxes and all ledger checks; that workflow also regenerates the packet. Shared workflow concurrency prevents overlapping generated-view writers. Do not silently treat a later estate action as adjudicated by the character-only path. Both workflows preserve existing post-cutover validation holds.

For actual play writes, retain the existing stable event IDs, expected-SHA safeguards and causal order. Batch related changed owner records at natural boundaries; verify journals and append-only evidence before committing CAMPAIGN_STATE last. No per-round GitHub reads/writes or full estate workflow solely to record a tactical attack. Historical continuity and pre-cutover routing were archived intact; this maintenance did not advance gameplay.


## D244 estate implementation clarification

`data/estate/README.md` and the live continuity README own post-cutover routes and the writer slot. `operational-checkpoint.csv` now supplies live confirmed Blackthorn order overlays and completed prerequisite records, keeping Property snapshot CSVs untouched. Its durable draw records, task dispositions and request dependencies own the new offscreen estate adjudications. The operations opening close is Day230; the imported cash snapshot is Day231 and its exact original event IDs are frozen separately. This permits genuinely missing Day231 operations without changing the opening position. Physical verification is distinct from buyer-quality certification.

The D244 catch-up contains current-day completed work as well as completed prior days. Full calendar close and last accounted activity are separate markers; never infer an unplayed night from a daytime posting. Open-period tax is accrued as profit is earned with daily liability adjustments; the tax-period assessment/payment command does not replace that obligation. Default tax preview can use the separately recorded last accounted day while posting a closed assessment still requires the true close guard. All historical carry and due dates remain unchanged.

The real F03 chain now provides actual full dispatch, acceptance, receivable and later collection evidence. Broader migration validation items, including complete dependency coverage and partial-delivery cases, remain open unless specifically verified. Older pre-cutover Drive-comparison language above is historical validation context, not permission to write there.

## Fast-play regression safeguards (2026-11-20)

Keep one standard CAMPAIGN_STATE — DAY heading at the start of the active state; replace superseded checkpoint prose after archiving it verbatim. This file should hold only present actors, relevant resources, latest accepted corrections and the precise pending V action. Keep the current continuity README under 8K characters, and recent SESSION_LOG under 75K by archiving closed chronological blocks. Do not append maintenance receipts to startup routes. The play generator rejects unsafe growth and outdated parser layouts rather than truncating them.

The owning V Fighter character CSV records Superiority Dice separately from the general resources. The dashboard now reads exactly that Battle Master baseline row and replays posted character-event spends/recovery, validating bounds. Do not delete actual journal entries to quiet validation failures; add narrow explicit mappings/tests for other approved features as needed.

For substantive play synchronization, batch related owning journals in one guarded commit when possible, verify them, then commit CAMPAIGN_STATE last as a separately guarded state commit. Checks of unrelated estates, markets and atlas are not per-action prerequisites. This maintenance changes no played time, events, decisions or dice.

## November 21 fast-play regression fix — current behavior

The live packet compares the ID of the newest accepted `campaign/continuity/session-log.md` entry with the exact CAMPAIGN_STATE checkpoint, not only their calendar day. At startup, read only the newest played journal entry to detect same-day checkpoint drift. Preserve already played events and reconcile the state; never reroll, fake recovery or silently advance V. Keep the fast startup README/AGENTS and active journal compact by archiving original full text before trimming. This change does not affect independent estate/market validation, which continues only on its relevant triggers.
