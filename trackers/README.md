# Tracker migration

## Staging rule

These files are snapshots from the live Google Sheets as of 2026-11-19. The corresponding `workbooks/*.xlsx` files preserve the full exported workbook, including formulas and formatting. `csv/` contains display-value snapshots split by sheet tab so the GitHub connector can retrieve and review table content directly.

The CSVs are snapshots, not yet an approved replacement for live formula-driven Sheets. Drive remains authoritative during testing. Do not edit a CSV and treat it as a live resource change until the cutover design and formula behavior are verified.

## Workbook map

| Workbook | Drive source ID | Snapshot |
|---|---|---|
| V Character Sheets | `1JUWWk7DsXt9aNwPsob5Tj3hmk5PvwqWRuQQzKKHlqZM` | `workbooks/v-character-sheets.xlsx` |
| Cirren Character Sheets | `1WcguqV2Uos8NXml0MHEEBR9ztCISWGL2lrClNK2pW-s` | `workbooks/cirren-character-sheets.xlsx` |
| Fenar Character Sheets | `1Zscq-futavtCYv00FDENn3hTKEh8g8YQ1xfOs0ht7zk` | `workbooks/fenar-character-sheets.xlsx` |
| Property | `1VYY8lidhkDe6iiCaY8uEesg1ocxunXIE_Q6Y9-baw9Q` | `workbooks/property.xlsx` |
| Magic Shops | `1lkUMaoPNaIkSVNbE89i8MzbmbBSOufABrAmXNgEyqnY` | `workbooks/magic-shops.xlsx` |

Each CSV path is `csv/<workbook>/<sheet-name>.csv`; formula-bearing workbook logic remains in the XLSX snapshot.
