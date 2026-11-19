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

## Current checkpoint in the source

Day 231, late morning, at the Rethwyn rural manor entrance in Crownsunder. V's next speech/action is pending after Sela offers to lead Anwen to view Iven's remains. See `campaign/continuity/campaign-state.md`.

## Migration status

- [x] GitHub connector reads and writes work; earlier non-campaign write/read round trip was verified.
- [x] Google Docs tabs and workbook exports/formula snapshots were migrated for retrieval.
- [x] Estate audit ran and its cash, liability, available-cash, and cashbook checks passed.
- [x] Event ledger seeded with 121 unique actual cashbook IDs; each estate reconciles to the Day 231 snapshot.
- [x] Receivable and inventory event rules have synthetic edge-case checks; their opening registers await verified source imports.
- [x] Due-task output was checked against the live Drive schedules. Two stale Miregate payroll rows are shown as superseded by their completed Day 229 settlement.
- [x] Character, inventory, and magic-shop snapshot checks pass; a read-only dashboard is generated.
- [ ] Complete formula/rule parity for wages, earned costs, taxes, inventory valuation, shipments, acceptance, and service prerequisites.
- [ ] Verify the character event-log write path with a real, confirmed campaign change.
- [ ] Port and verify full magic-shop stock turnover and business review behavior.
- [ ] Test a complete play → event write → regenerated dashboard → Drive checkpoint comparison.
- [ ] Consider cutover only after that workflow passes.

No Drive records or Project Sources have been changed. See `automation/README.md`, `data/estate/README.md`, and `migration/TEST_REPORT.md` for scope and limitations.
