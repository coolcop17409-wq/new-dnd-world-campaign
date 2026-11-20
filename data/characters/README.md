# Character and inventory event journal

The character Sheets and inventory CSVs are baseline snapshots from 2026-11-19. GitHub is authoritative after the 2026-11-20 cutover. Record confirmed later changes in this GitHub event journal; the old Drive workbooks are historical references only. Current derived values appear in `dashboard/dashboard.json`.

For a confirmed later change, append one event to `events.csv` through the GitHub connector. Use a unique ID, exact campaign day, one owner, one target, and a concise source reference. The dashboard applies that delta to the snapshot and the workflow checks that it remains within the displayed limits.

Supported record types:

- `currency`: `purse_cp` stores the personal purse as copper pieces; deltas preserve exact gp/sp/cp arithmetic. The dashboard formats the resulting purse back to coins.
- `stat`: `HP` or `MAX HP`.
- `resource`: exact live resource name from that character's character sheet.
- `inventory`: exact item name from that character's equipment sheet.
- `inventory_create`: an evidenced item absent from the historical baseline, using a positive integer `absolute_value` and no delta. `evidence` is JSON with nonempty `source_event`, `holder` and `detail` strings. The builder rejects names already in the baseline (including zero-quantity rows) or the overlay. This records a missing acquisition/custody leg once; it does not award another physical item. Later quantity changes use `inventory`.

Use either `delta` or `absolute_value`, never both. Set status to `posted` only when the change actually occurred. Do not enter a forecast, planned use, scheduled recovery, or proposed action. Rest recovery is entered only after the campaign's rest rules say it completed; a long-rest marker alone does not restore a resource.

Inventory quantity deltas require an actual acquire, consume, use, transfer, recovery, or loss with ownership/custody evidence. If an item appears more than once, make the target unique or update its owning sheet snapshot before applying a delta. This ledger does not replace class-feature rules or rest adjudication.

Once a new baseline snapshot includes an event, the event must be archived/rebased before it is replayed against that new baseline. Do not write new campaign state to the historical Drive workbook.

