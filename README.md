# New Unnamed World Campaign — GitHub Migration Test

This repository is a public staging copy. ChatGPT Project Sources still point to Drive; Drive remains the live campaign authority.

## Authority during testing

Do not resume play from this copy or change Project Sources during staging. The repository is public by the owner's choice. All files, including DM preparation and unrevealed material, are readable by anyone online; “DM-only” labels are play-reveal guidance, not access controls.

## Repository map

- `AGENTS.md` — startup, source ownership, play authority, and sync procedure
- `campaign/continuity/` — campaign state, rules, quests, NPCs, inventory, and play log
- `prep/dm-only/` — private-prep source tabs, publicly readable in this repo
- `world/politics/` — political-reference topics
- `archive/` — closed campaign history and retired notes
- `trackers/` — workbook exports, formulas, and searchable CSV snapshots
- `data/estate/` — staging event ledger, opening balances, and verified task successors
- `data/characters/` — append-only staging changes to character resources and inventory
- `automation/` — estate reconciliation, tracker validation, and dashboard builder
- `dashboard/` — read-only staged tracker view; GitHub Pages is not enabled
- `reports/` — generated estate and tracker validation output
- `assets/README.md` — maps and images retained in Drive
- `MIGRATION_MAP.md` — source-to-file index
- `migration/TEST_REPORT.md` — staging checks and cutover boundary
- `migration/OPENING_POSITION_AUDIT.md` — opening rights, custody, staffing, inventory, and commitment audit

## Current checkpoint in the source

Day 231, late morning, at the Rethwyn rural manor entrance in Crownsunder. V's next speech/action is pending after Sela offers to lead Anwen to view Iven's remains. See `campaign/continuity/campaign-state.md`.

## Migration status

- [x] GitHub connector reads and writes work; earlier non-campaign write/read round trip was verified.
- [x] Google Docs tabs and workbook exports/formula snapshots were migrated for retrieval.
- [x] Estate audit ran and its cash, liability, available-cash, and cashbook checks passed.
- [x] Event ledger seeded with 121 unique actual cashbook IDs; each estate reconciles to the Day 231 snapshot.
- [x] Source snapshot shows zero receivables; six Blackthorn stock grades are imported as provisional book balances, with reserved amounts and shipment transit supported in the ledger. Unverified stock is not counted as shippable.
- [x] Due-task output was checked against the live Drive schedules. Two stale Miregate payroll rows are shown as superseded by their completed Day 229 settlement.
- [x] Character, inventory, and magic-shop snapshot checks pass; a read-only dashboard is generated.
- [x] Replay Blackthorn production, labor, product cost, COGS, loss, stock, shipment, acceptance and readiness rules against the source activity through Day 230; row-level checks pass.
- [x] Add closed-day Blackthorn accrual preview and explicit idempotent staging-post control; synthetic retry test passes.
- [x] Document character, shop-turnover, service-prerequisite and event-to-checkpoint procedures; generate a due-review queue from confirmed campaign day.
- [x] Bridge validated future Blackthorn operation, shipment, acceptance, COGS and stock events into the estate ledger with explicit immediate cash or receivable treatment; synthetic mapping/import tests pass.
- [x] Require prerequisite references for earned income/service release and validate referenced schedule completion, actual day and evidence.
- [ ] Verify that each service path cites the full applicable dependency set, including legal, staffing, safety, route and capacity conditions.
- [x] Port source-checked forward Blackthorn taxable-base roll-forward and closed-period assessment adjustment posting; integrated synthetic chain test passes. Actual tax close/post has not been run because no real post-checkpoint closed tax period exists.
- [ ] Run a real post-checkpoint Blackthorn operation chain, a confirmed character change, and one due Magic Shops turnover through write → rebuild → compare.
- [x] Audit opening rights, custody, staffing and commitments against the Property registers; see [OPENING_POSITION_AUDIT.md](migration/OPENING_POSITION_AUDIT.md).
- [ ] Resolve the remaining opening-position gaps: Blackthorn physical stock verification, reconcile the explicit Miregate vessel-restoration ruling with the stale Property schedule (without inventing punt cost/capacity), and itemized fixed assets; then compare the checkpoint with Drive.
- [x] Review successful full Actions run 92. Cutover remains blocked by the real post-checkpoint event and source-comparison checks listed above.

No Drive records or Project Sources have been changed. See `migration/ONGOING_UPDATE_PROTOCOL.md`, `automation/README.md`, `data/estate/README.md`, and `migration/TEST_REPORT.md`.
