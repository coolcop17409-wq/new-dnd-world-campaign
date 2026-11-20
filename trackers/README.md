# Tracker migration

## Active GitHub sources

The `workbooks/*.xlsx` files and `csv/` exports are baseline snapshots captured from the Google Sheets on 2026-11-19. The XLSX copies preserve formulas and formatting; CSVs preserve displayed values. GitHub is authoritative after the 2026-11-20 cutover. Do not write new campaign state to the historical Drive workbooks.

Use the Magic Shops CSVs as their routed current records. Property and character CSVs are baselines; apply confirmed subsequent changes through the owning GitHub journals under `data/estate/` and `data/characters/`. Read the generated `dashboard/dashboard.json` for current derived values. Rebuild it with the repository workflow after source changes; do not hand-edit generated dashboard data.

## What runs today

The estate workflow reconciles the staged cashbook event ledger and opening liability balances to the current Property overview, detects duplicate IDs, validates transfer pairs, and lists unfinished schedule tasks due by the campaign day. The event engine also supports stable receivable balances and opening inventory quantity/cost basis with evidence checks and prevents over-collection or releasing more stock/cost than registered. The source shows zero opening receivables across all four estates. Blackthorn's Day 230 book inventory is imported by grade with 41.12 t on-site, 13 t reserved, and 349.43 gp book cost; the workbook marks the grade allocation and physical count provisional, so the ledger reports zero eligible-to-ship stock until verification. Synthetic tests exercise partial payment, delayed collection after acceptance, failed work, tax due without assessment, reservations, inventory release, shipment transit, and paired transfers. The engine does not post transactions from forecasts or infer that scheduled work happened.

The character event journal accepts confirmed HP, resource, currency, and inventory changes. The Day 231 Valenthia purse change is already recorded as a posted event and was applied by a dashboard rebuild, matching the historical inventory row. New confirmed changes use the same journal → rebuild → compare process. The dashboard applies only entries marked `posted` and validates supported ranges and quantities. Character-sheet formulas and some class/rest automation have not been ported; use the 2014 rules and campaign procedures when adjudicating. The Actions workflow also generates a date-driven Magic Shops review queue; it identifies due contacts without resolving random turnover.

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
