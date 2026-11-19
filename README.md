# New Unnamed World Campaign — GitHub Migration Test

This repository contains the campaign's staged documentation migration. ChatGPT Project Sources still point to Drive while the GitHub copy is tested.

## Authority during testing

Drive remains the live campaign source of truth until the GitHub copy passes retrieval, write, tracker, and continuity checks. Do not resume play from this copy or change Project Sources during staging.

The repository is public by the owner's explicit choice. All content, including DM preparation and unrevealed material, is readable by anyone online. “DM-only” labels are play-reveal guidance, not access controls.

## Repository map

- `AGENTS.md` — startup, source ownership, play authority, and sync procedure
- `campaign/continuity/` — source tabs for current state, rules, quests, NPCs, inventory, and play log
- `prep/dm-only/` — private-prep source tabs, publicly readable in this repository
- `world/politics/` — political-reference topics
- `archive/` — closed campaign history and retired notes
- `trackers/` — workbook exports and searchable CSV value snapshots
- `assets/README.md` — maps and images retained in Drive
- `MIGRATION_MAP.md` — source-to-file index
- `migration/TEST_REPORT.md` — staging checks and cutover boundary

## Current checkpoint in the source

Day 231, late morning, at the Rethwyn rural manor entrance in Crownsunder. The exact pending player action is V's choice of what to say or do after Sela offers to lead Anwen to view Iven's remains. See `campaign/continuity/campaign-state.md`.

## Migration and test status

- [x] GitHub read/write path verified through the connector
- [x] Google Docs tabs copied into retrieval-sized Markdown files
- [x] Workbook exports retained with formulas and formatting
- [x] Readable value snapshots created for each workbook tab
- [x] Representative campaign retrieval and tracker value checks passed
- [x] Non-campaign write/read round trip passed
- [ ] Full play and synchronization workflow tested
- [ ] Project Sources remain pointed to Drive until cutover is separately approved

The campaign has not been switched to GitHub. See `migration/TEST_REPORT.md` for exactly what was checked.
