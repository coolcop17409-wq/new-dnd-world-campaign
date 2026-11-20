# Estate ledger staging data

This is a staging import from the 2026-11-19 Property workbook export, reconciled against the campaign checkpoint through Day 235. Drive remains authoritative; this is not the live ledger. Financial postings remain frozen at the last supported Day 231 snapshot.

## Files

- `events.csv`: one row per imported cashbook ID. The schema supports cash, liabilities, receivables, earned income, incurred expenses, physical stock, reservations, in-transit shipments/costs, accepted quantities, verification status, evidence, and posting status. Historical rows preserve displayed cash movements; unverified accrual/profit classifications remain blank.
- `opening-balances.csv`: estate cash baseline. Blackthorn starts with 572.11 gp reconstructed cash at Day 182; the other estate cashbooks begin at zero and show owner funding as a transaction.
- `opening-liabilities.csv`: stable IDs for nonzero liability categories in the Day 230 overview snapshot. These are balance-forward obligations, not a second posting of old expenses.
- `opening-receivables.csv`: empty because the Day 231 Property workbook reports zero receivables for all four estates.
- `opening-inventory.csv`: six Blackthorn grade rows from the Day 230 Accounts snapshot: 41.12 t book stock, 13 t reserved, 0 t in transit, and 349.43 gp book cost. All six grades are `verified` by the Day 231 full-yard count with zero variance. The separately counted F03 8 t sublot is a non-additive subset of dressed stone and passed its Day 231 preload check.
- `fixed-assets.csv`: evidence-backed fixed asset/component register for all four estates. Documented cost is recorded only where the source classifies it; unknown cost/current value fields stay blank. Repairs are not treated as asset acquisitions, Crown hydraulic controls are excluded, and the Blackthorn movable-asset reference row is non-additive.
- `movable-assets.csv`: source-itemized Blackthorn movable contents, with known counts where history supports them. It separates recorded estate assets from site custody with unresolved title; blank quantities and values remain unknown.
- `operational-checkpoint.csv`: Day 232–235 reconciliation, including unresolved past-target service offers and the conditional Aven Marris cargo allocation / Day 235 captain presence. No unverified offer is posted as inventory or a transaction.
- `blackthorn-rates.csv`: current effective-dated Blackthorn daily payroll and upkeep rates. The initial import is the 13 payroll/upkeep rows in the source sheet; production-cost rates remain in the live workbook until their import is verified.
- `blackthorn-tax-checkpoint.csv`: source-verified unrounded Day 230 formula components and the first rolling tax result. This preserves 417.8297 gp COGS before Accounts rounds it to 417.83 gp.
- `snapshot-meta.json`: latest campaign checkpoint Day 235 and separate financial snapshot cutoff Day 231.
- `task-supersessions.csv`: two Miregate schedule rows verified as handled by the completed Day 229 payroll successor.
- `migration/OPENING_POSITION_AUDIT.md`: audit of rights, customer custody, stock, staffing, and current commitments against the staged Property registers. Those nonfinancial records remain in their owning exported tabs; they are not duplicated in the cash event ledger.

## Posting an actual event

Use one unique `event_id` per actual event and retain a precise campaign day, the owning estate, evidence/source, and affected references. For a money event, enter signed `cash_delta_gp`; a receipt is positive and a payment negative. `amount_gp` is the positive transaction amount.

- Work/service completed: record earned income or incurred expense on the event day. If unpaid, create or increase a stable `liability_id`. When paid later, add a separate event with negative cash and a negative liability delta against that same ID; do not record the expense again.
- Immediate cost payment: record the positive `expense_delta_gp` and negative `cash_delta_gp` once. No outstanding liability is needed.
- Accepted sale: enter income only for quantity actually accepted. If the buyer pays then, also enter cash received. If payment is delayed, increase a stable `receivable_id`; record later cash receipt and receivable reduction without recognizing income twice. The ledger rejects collections beyond that receivable.
- Customer advance: cash receipt plus a positive liability delta; on acceptance, recognize earned income and reduce the advance liability. A scheduled arrival or unaccepted cargo remains unchanged.
- Estate transfer: use the same `reference_id` on both source and destination rows. The cash legs must offset; do not enter income or expense.
- Tax: calculate under the estate's actual tax rules from posted results, then record a tax liability. A due day alone creates neither an assessment nor a payment. A payment reduces the relevant tax liability.
- Inventory/shipment: use a stable `inventory_id`, `shipment_id`, actual `quantity_delta` / `inventory_cost_delta_gp`, and evidence for receipt, production, dispatch, acceptance, damage, or loss. Dispatch moves quantity/cost from on-site to in-transit; arrival moves it back. Reservations are separate from physical quantity. Provisional or unverified stock cannot be released until a separately evidenced inventory verification changes its status to `verified`. The ledger rejects negative on-site, reserved, transit, or cost balances. Accepted quantity requires a shipment or transaction reference. Do not recognize a sale from an order or scheduled shipment.
- Service prerequisite: include the linked task/order reference and evidence that all required title, staffing, safety, ownership, capacity, route, inspection, and acceptance gates passed before recognizing a service.

Set status to `posted` only after the event happened. Planned, forecast, scheduled, pending, and unconfirmed rows must have no financial or inventory effects. Do not create a protected reserve. If a row cannot be supported by the existing rule or evidence, leave it out and flag the ambiguity for review.

## Blackthorn formula port

`automation/blackthorn_rules.py` reproduces two workbook calculations without posting anything: (1) daily Payroll and Upkeep accrual over inclusive effective-date ranges, starting after the opening-balance day; and (2) the 10% rolling tax assessment from actual accepted revenue, COGS, losses/idle costs, management payroll, upkeep, incurred operating expenses, and taxable carry. The Day 230 fixture matches the source: payroll accrued 700.80 gp (336.00 management + 364.80 production), upkeep 85.71 gp, tax base 723.70 gp, assessment 72.37 gp. The aggregate upkeep total is rounded once, as in Accounts; the per-rate display column can differ by 0.01 gp because it rounds each row separately. A live unformatted read of Operations gives COGS 417.8297 gp, which Accounts rounds to 417.83 gp; summing the displayed-value CSV's rounded COGS cells gives 417.82 gp. Exact formula checks therefore must use unrounded source values, not sum the displayed CSV. The forward `blackthorn_tax.py` roll-forward now starts from the verified Day 230 base/assessment and consumes posted actual ledger events plus the validated operation replay. Management payroll and upkeep are accrued from effective-dated rates; production payroll flows through operation COGS or loss and is not deducted twice. The synthetic Day 232–235 operation-to-ledger-to-tax test adds 10.00 gp taxable profit and a 1.00 gp tax assessment adjustment.

## Boundary

The story checkpoint is Day 235 evening. The cash/liability ledger remains reconciled only to the Day 231 late-morning financial snapshot, with liabilities through the completed Day 230 close. The Day 232–235 source review found no supported actual estate cash, liability, receivable, or stock movement; conditional freight and captain availability are recorded separately with no financial effect. Opening receivables are zero in the source. Six Blackthorn book-stock grades are imported through Day 230 and remain provisional. F03’s 8 t order-specific QC pass is documented but not enabled as partial stock verification in the grade-level ledger; no opening stock is eligible to ship until a full physical count or tested lot-level support exists.

Blackthorn's full 283-row production/COGS/shipment replay matches source formula rows and the Day 230 totals. The Day 231 full physical count and separate F03 8 t sublot count are verified for the opening position. The forward operation journal is validated after the Day 231 checkpoint and blocks shipment release from unverified opening stock. Its passed future results now feed normalized events into the estate ledger after the report snapshot and input IDs are checked. Accept/Gate sale rows require explicit cash received (including zero) and a receivable ID for any unpaid amount; later receipts use separate event rows. The bridge has synthetic tests but has not yet processed a real future operation.

Blackthorn management payroll, production payroll and upkeep can be generated through an explicitly closed day. Actions preview by default; an explicit manual checkbox is required to post staging accruals idempotently. This records earned obligations only; it does not pay wages or automatically assess/pay taxes.

Blackthorn readiness has a passed-task gate. The estate ledger now requires and validates referenced prerequisite task IDs for earned income and service/shipment releases. It checks recorded completion, actual day and evidence, but cannot detect a dependency omitted from the event's reference list. Forward Blackthorn tax-base roll-forward and period assessment adjustment posting are implemented and pass the integrated synthetic operation/ledger/tax scenario. They have not been applied to a real post-checkpoint close. Character event overlays and Magic Shops identity/quantity/review-queue checks are tested synthetically; real play writes and a due-turnover cycle remain unverified.

Drive remains authoritative. Do not change live workbooks or Project Sources during staging. For each update type and the cutover criteria, see `migration/ONGOING_UPDATE_PROTOCOL.md`.

## Adopted Blackthorn estimate

The owner adopted 8,000 gp on Day 235 as a provisional aggregate going-concern estimate. It is listed as a separate non-additive line in `fixed-assets.csv`; it is not a sum of the known 191 gp historical-cost improvements. It is not an independent appraisal, and the estimate's treatment of cash, stock and liabilities has not been defined for total net-worth calculations. Keep component values blank where source evidence does not support them.
