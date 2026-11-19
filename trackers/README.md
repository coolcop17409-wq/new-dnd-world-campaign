# Tracker migration

## Staging rule

These files are snapshots from the live Google Sheets as of 2026-11-19. The corresponding `workbooks/*.xlsx` files preserve workbook formulas and formatting. `csv/` contains displayed-value snapshots split by tab for retrieval and review.

Drive remains authoritative. Do not edit a CSV and treat it as a live campaign update. The GitHub copy is still a staging test.

## What runs today

The estate audit and event-ledger check reconcile cash, recorded liabilities, available balances, cashbook IDs, and due/unfinished estate schedule items. The initial event ledger imports actual cashbook rows and snapshots nonzero liabilities as of Day 230; it does not post new wages, income, costs, taxes, transfers, or inventory changes by itself.

The dashboard assembles read-only party, personal inventory, estate, and magic-shop views from the exported CSVs. It is a snapshot report, not yet a formula-complete replacement for the character or property workbook. Magic-shop rules already use Dealers, Stock, and Events as separate records; current dashboard output shows stock rows only and does not execute turnover or trade.

## Workbook map

| Workbook | Drive source ID | Snapshot |
|---|---|---|
| V Character Sheets | `1JUWWk7DsXt9aNwPsob5Tj3hmk5PvwqWRuQQzKKHlqZM` | `workbooks/v-character-sheets.xlsx` |
| Cirren Character Sheets | `1WcguqV2Uos8NXml0MHEEBR9ztCISWGL2lrClNK2pW-s` | `workbooks/cirren-character-sheets.xlsx` |
| Fenar Character Sheets | `1Zscq-futavtCYv00FDENn3hTKEh8g8YQ1xfOs0ht7zk` | `workbooks/fenar-character-sheets.xlsx` |
| Property | `1VYY8lidhkDe6iiCaY8uEesg1ocxunXIE_Q6Y9-baw9Q` | `workbooks/property.xlsx` |
| Magic Shops | `1lkUMaoPNaIkSVNbE89i8MzbmbBSOufABrAmXNgEyqnY` | `workbooks/magic-shops.xlsx` |

Each CSV path is `csv/<workbook>/<sheet-name>.csv`; formulas remain in the XLSX reference copies. Estate ledger inputs are under `data/estate/`.