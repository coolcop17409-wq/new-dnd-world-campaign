# Tracker migration

## Staging rule

These files are snapshots from the live Google Sheets as of 2026-11-19. The corresponding `workbooks/*.xlsx` files preserve formulas and formatting. `csv/` contains displayed-value snapshots split by tab for retrieval and review. Drive remains authoritative; do not edit a CSV and treat it as a live campaign update.

## What runs today

The estate workflow reconciles the staged cashbook event ledger and opening liability balances to the current Property overview, detects duplicate IDs, validates transfer pairs, and lists unfinished schedule tasks due by the campaign day. The event engine also supports stable receivable balances and opening inventory quantity/cost basis with evidence checks and prevents over-collection or releasing more stock/cost than registered. The source shows zero opening receivables across all four estates. Blackthorn's Day 230 book inventory is imported by grade with 41.12 t on-site, 13 t reserved, and 349.43 gp book cost; the workbook marks the grade allocation and physical count provisional, so the ledger reports zero eligible-to-ship stock until verification. Synthetic tests exercise partial payment, delayed collection after acceptance, failed work, tax due without assessment, reservations, inventory release, shipment transit, and paired transfers. The engine does not post transactions from forecasts or infer that scheduled work happened.

The character staging ledger accepts confirmed HP, resource, and inventory changes. A synthetic write-and-compare test confirms the dashboard overlays those event types onto the snapshot; the real campaign event log remains empty, so an actual play → write → regenerate → compare cycle is still required. The dashboard applies only entries marked `posted`, then checks them against snapshot maxima and item quantities. The character sheets' formulas and all 2014 class/rest rules have not been fully ported.

Magic Shops already separates Dealers, Stock, and Events, with extensive campaign procedures in its Rules tab. The validation checks stable dealer/lot/event keys and stock quantities; the dashboard shows current nonzero lots. It does not roll business/stock turnover, resolve offers, buy/sell items, or decide hidden availability.

## Workbook map

| Workbook | Drive source ID | Snapshot |
|---|---|---|
| V Character Sheets | `1JUWWk7DsXt9aNwPsob5Tj3hmk5PvwqWRuQQzKKHlqZM` | `workbooks/v-character-sheets.xlsx` |
| Cirren Character Sheets | `1WcguqV2Uos8NXml0MHEEBR9ztCISWGL2lrClNK2pW-s` | `workbooks/cirren-character-sheets.xlsx` |
| Fenar Character Sheets | `1Zscq-futavtCYv00FDENn3hTKEh8g8YQ1xfOs0ht7zk` | `workbooks/fenar-character-sheets.xlsx` |
| Property | `1VYY8lidhkDe6iiCaY8uEesg1ocxunXIE_Q6Y9-baw9Q` | `workbooks/property.xlsx` |
| Magic Shops | `1lkUMaoPNaIkSVNbE89i8MzbmbBSOufABrAmXNgEyqnY` | `workbooks/magic-shops.xlsx` |

Each CSV path is `csv/<workbook>/<sheet-name>.csv`; formulas remain in XLSX reference copies. Estate ledger inputs are under `data/estate/`, and additive character changes are under `data/characters/`.

Forward update behavior, current automation boundaries, and cutover gates are defined in [migration/ONGOING_UPDATE_PROTOCOL.md](../migration/ONGOING_UPDATE_PROTOCOL.md). The protocol keeps event journals and recalculated dashboard views as the write/retrieval model; the workbook exports stay reference snapshots until validation is complete.
