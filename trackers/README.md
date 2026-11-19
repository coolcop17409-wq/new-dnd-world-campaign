# Tracker migration

## Staging rule

These files are snapshots from the live Google Sheets as of 2026-11-19. The corresponding `workbooks/*.xlsx` files preserve formulas and formatting. `csv/` contains displayed-value snapshots split by tab for retrieval and review. Drive remains authoritative; do not edit a CSV and treat it as a live campaign update.

## What runs today

The estate workflow reconciles the staged cashbook event ledger and opening liability balances to the current Property overview, detects duplicate IDs, validates transfer pairs, and lists unfinished schedule tasks due by the campaign day. It does not post transactions or infer that scheduled work happened.

The character staging ledger accepts confirmed HP, resource, and inventory changes. The dashboard applies only entries marked `posted`, then checks them against snapshot maxima and item quantities. The character sheets' formulas and all 2014 class/rest rules have not been fully ported.

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
