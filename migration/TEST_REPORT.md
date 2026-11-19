# Migration Test Report

Test copy: https://github.com/coolcop17409-wq/new-dnd-world-campaign
Visibility: Public (confirmed by repository metadata and the owner's instruction).

## Verified

- Fetched representative files through the GitHub connector: README, AGENTS, current campaign state, rules, DM-only prep, world political reference, tracker CSV, and XLSX workbook.
- Checked staged character values against Drive: V 48/48 HP and AC 19; Cirren 51/51 HP and AC 18; Fenar 59/59 HP and AC 14.
- Checked staged estate balances against Drive snapshots: Miregate 501.40 cash / 487.37 after liabilities; Reedbed 63.80 / 55.20; Old Distributary Fort 130.00 / 125.00; Blackthorn 453.33 / 282.32.
- Updated the non-campaign `migration/connector-test.md` file through the GitHub connector and fetched it again. The readback contains `AFTER_UPDATE_VERIFIED`.
- Confirmed repository metadata reports `visibility: public`.

## Staging boundaries

- Drive remains authoritative. No Drive records or ChatGPT Project Sources were changed.
- The workbook files preserve spreadsheet formulas and formatting; CSV files are searchable displayed-value snapshots.
- Maps and large images remain in Drive, with pointers in `assets/README.md`.
- This report covers representative connector and data checks. The live campaign workflow has not been switched to GitHub.
