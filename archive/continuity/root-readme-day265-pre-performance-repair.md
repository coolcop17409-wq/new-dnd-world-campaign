# New Unnamed World Campaign

This public repository is the active canonical source for campaign text and structured records. The owner authorized cutover on 2026-11-20 before every migration validation gate had passed. The outstanding checks remain an explicit post-cutover validation backlog in `migration/TEST_REPORT.md`; do not describe them as passed or invent campaign events to satisfy them.

## Authority after cutover

Use this repository for campaign play and record updates. The former Google Drive Docs and workbook exports are historical reference snapshots and must not receive new campaign-state writes. Maps and large images remain in Drive/Library as designated visual assets. The repository is public by the owner's choice; all files, including DM preparation and unrevealed material, are readable by anyone online. “DM-only” labels are play-reveal guidance, not access controls.

## Repository map

- `AGENTS.md` — startup, source ownership, play authority, and sync procedure
- `runtime/PLAY_NOW.md` — generated compact live-play packet; not an independent source of truth
- `archive/continuity/` — preserved historical checkpoints, full pre-fastplay routing and closed session blocks
- `campaign/continuity/` — campaign state, rules, quests, NPCs, inventory, and play log
- `prep/dm-only/` — private-prep source tabs, publicly readable in this repo
- `world/politics/` — political-reference topics
- `archive/` — closed campaign history and retired notes
- `trackers/` — workbook exports, formulas, and searchable CSV snapshots
- `data/estate/` — staging event ledger, opening balances, estate asset register, and verified task successors
- `data/characters/` — append-only staging changes to character resources and inventory
- `automation/` — estate reconciliation, tracker validation, and dashboard builder
- `dashboard/` — read-only staged tracker view; GitHub Pages is not enabled
- `reports/` — generated estate and tracker validation output
- `assets/README.md` — maps and images retained in Drive
- `MIGRATION_MAP.md` — source-to-file index
- `migration/TEST_REPORT.md` — cutover status and post-cutover validation backlog
- `migration/OPENING_POSITION_AUDIT.md` — opening rights, custody, staffing, inventory, and commitment audit

## Current checkpoint in the source

Read `campaign/continuity/campaign-state.md` for the latest **confirmed** pause. Use `runtime/PLAY_NOW.md` for a short generated read and `dashboard/dashboard.json` for journal-overlaid counters; do not use older dated checkpoint prose as current authority.

## Migration status and validation backlog

- [x] GitHub connector reads and writes work; earlier non-campaign write/read round trip was verified.
- [x] Google Docs tabs and workbook exports/formula snapshots were migrated for retrieval.
- [x] Estate audit ran and its cash, liability, available-cash, and cashbook checks passed.
- [x] Event ledger seeded with 121 unique actual cashbook IDs; each estate reconciles to the Day 231 snapshot.
- [x] Source snapshot shows zero receivables; all six Blackthorn grades match the Day 231 full-yard count, and the 8 t F03 lot is verified as a non-additive sublot. Buyer-quality certification remains separate.
- [x] Due-task output was checked against the live Drive schedules. Two stale Miregate payroll rows are shown as superseded by their completed Day 229 settlement.
- [x] Character, inventory, and magic-shop snapshot checks pass; a read-only dashboard is generated.
- [x] Replay Blackthorn production, labor, product cost, COGS, loss, stock, shipment, acceptance and readiness rules against the source activity through Day 230; row-level checks pass.
- [x] Add closed-day Blackthorn accrual preview and explicit idempotent staging-post control; synthetic retry test passes.
- [x] Document character, shop-turnover, service-prerequisite and event-to-checkpoint procedures; generate a due-review queue from confirmed campaign day.
- [x] Bridge validated future Blackthorn operation, shipment, acceptance, COGS and stock events into the estate ledger with explicit immediate cash or receivable treatment; synthetic mapping/import tests pass.
- [x] Require prerequisite references for earned income/service release and validate referenced schedule completion, actual day and evidence.
- [ ] Verify that each service path cites the full applicable dependency set, including legal, staffing, safety, route and capacity conditions.
- [x] Port source-checked forward Blackthorn taxable-base roll-forward and closed-period assessment adjustment posting; integrated synthetic chain test passes. Actual tax close/post has not been run because no real post-checkpoint closed tax period exists.
- [x] Run a real confirmed character purse change and one due Magic Shops review through write → rebuild → compare. The Day 231 V event matches Drive; the Day 232 shop review is recorded and removed from the due queue through Day 235.
- [ ] Run a real post-checkpoint Blackthorn operation chain through event posting and generated-ledger comparison. No post-checkpoint operation outcome is confirmed in the source.
- [x] Audit opening rights, custody, staffing and commitments against the Property registers; see [OPENING_POSITION_AUDIT.md](migration/OPENING_POSITION_AUDIT.md).
- [x] Create an evidence-backed itemized estate asset register; source-unknown cost and valuation fields remain blank.
- [x] Reconcile the Blackthorn stock count, the punt ownership/restoration schedule, and the owner-adopted 8,000 gp aggregate valuation in staging. Remaining valuation limits: no independent appraisal, exact parcel boundary or full component values; see `data/estate/valuations.csv`; do not add the aggregate to component assets.
- [x] GitHub Actions run 44674915090 passed on the post-cutover operations commit `e1043a320d9c34b588b8b5dfc63e917a115955fd`; it verified syntax, ledger edge-case tests, audits, and dashboard generation.

GitHub is the active authority after the owner-directed cutover. The ChatGPT Project instructions now point here; the Sources panel contains a GitHub routing note and the retained world map, with the old Drive campaign Docs/workbooks removed from live-source routing. Continue the documented validation backlog without fabricating evidence. Keep Drive as a historical/reference copy for text and workbooks; continue using its map and large-image assets where designated. See `migration/ONGOING_UPDATE_PROTOCOL.md`, `automation/README.md`, `data/estate/README.md`, and `migration/TEST_REPORT.md`.
