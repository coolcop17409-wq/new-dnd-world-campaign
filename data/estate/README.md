# Estate ledger staging data

This is a staging import from the 2026-11-19 Property workbook export. It is not the live ledger and must be reconciled against Drive before any cutover.

## Files

- `events.csv`: one row per imported cashbook ID. The expanded schema provides fields for cash, liabilities, earned income, incurred expenses, inventory quantities/costs, accepted quantities, shipment IDs, evidence, and status. Historical imported rows preserve the displayed cash movement but leave unverified accrual/profit classifications blank.
- `opening-balances.csv`: estate cash baseline. Blackthorn starts with 572.11 gp reconstructed cash at Day 182; the other estate cashbooks begin at zero and show owner funding as a transaction.
- `opening-liabilities.csv`: stable IDs for nonzero liability categories in the Day 230 overview snapshot. These are balance-forward obligations, not a second posting of old expenses.
- `opening-receivables.csv`: opening balances by stable receivable ID; currently empty because no verified opening receivable schedule has been imported.
- `opening-inventory.csv`: opening physical quantities and cost basis by stable inventory ID; currently empty pending a verified property inventory import.
- `snapshot-meta.json`: the Day 231 comparison cutoff and source snapshot date.
- `task-supersessions.csv`: two Miregate schedule rows verified as handled by the completed Day 229 payroll successor.

## Posting an actual event

Use one unique `event_id` per actual event and retain a precise campaign day, the owning estate, evidence/source, and affected references. For a money event, enter signed `cash_delta_gp`; a receipt is positive and a payment negative. `amount_gp` is the positive transaction amount.

- Work/service completed: record earned income or incurred expense on the event day. If unpaid, create or increase a stable `liability_id`. When paid later, add a separate event with negative cash and a negative liability delta against that same ID; do not record the expense again.
- Immediate cost payment: record the positive `expense_delta_gp` and negative `cash_delta_gp` once. No outstanding liability is needed.
- Accepted sale: enter income only for quantity actually accepted. If the buyer pays then, also enter cash received. If payment is delayed, increase a stable `receivable_id`; record later cash receipt and receivable reduction without recognizing income twice. The ledger rejects collections beyond that receivable.
- Customer advance: cash receipt plus a positive liability delta; on acceptance, recognize earned income and reduce the advance liability. A scheduled arrival or unaccepted cargo remains unchanged.
- Estate transfer: use the same `reference_id` on both source and destination rows. The cash legs must offset; do not enter income or expense.
- Tax: calculate under the estate's actual tax rules from posted results, then record a tax liability. A due day alone creates neither an assessment nor a payment. A payment reduces the relevant tax liability.
- Inventory/shipment: use a stable `inventory_id`, `shipment_id`, actual `quantity_delta` / `inventory_cost_delta_gp`, and evidence for receipt, production, dispatch, acceptance, damage, or loss. Opening stock must be imported before dispatch/loss is posted; the ledger rejects a quantity or cost release below the registered balance. Accepted quantity requires a shipment or transaction reference. Do not recognize a sale from an order or scheduled shipment.
- Service prerequisite: include the linked task/order reference and evidence that all required title, staffing, safety, ownership, capacity, route, inspection, and acceptance gates passed before recognizing a service.

Set status to `posted` only after the event happened. Planned, forecast, scheduled, pending, and unconfirmed rows must have no financial or inventory effects. Do not create a protected reserve. If a row cannot be supported by the existing rule or evidence, leave it out and flag the ambiguity for review.

## Boundary

The staging ledger currently reconciles cash and balance-forward liabilities to Day 231, and supports event-level receivables plus inventory quantities/cost basis once verified opening balances and actual events are entered. It does not rebuild historical accrual/profit, tax assessments, inventory, production, or shipment history from source activity tabs; the opening receivable and inventory registers are deliberately empty until source-backed imports are reconciled. Service prerequisites remain evidence fields rather than an automated rule engine. Drive remains authoritative; do not use this CSV as a replacement record until the missing rules and edge cases are verified.
