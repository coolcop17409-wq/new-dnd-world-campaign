# Estate ledger staging data

This is a staging import from the 2026-11-19 Property workbook export. It is not the live ledger and must be reconciled against Drive before any cutover.

## Files

- `events.csv`: one row per existing cashbook ID. Signed cash movements, source file, source row, and evidence are preserved. Current rows carry no new liability delta because historical accruals are already represented in the as-of-Day-230 liability opening snapshot.
- `opening-balances.csv`: cash baseline for each estate. Blackthorn's reconstructed Day 182 cash is 572.11 gp. The other estates have zero opening cash and their owner funding is represented as a posted cashbook event.
- `opening-liabilities.csv`: one stable ID per nonzero liability category in the Day 230 overview snapshot. This balance-forward seed prevents old bills from being re-expensed. It includes no forecast, scheduled cost, customer reserve, or protected cash reserve.

## Event rules

For a newly confirmed event, add a unique `event_id`, real in-game day, exact source/evidence, and explicit signed effects.

- Work or service completed and wages/costs incurred: record a liability increase; cash delta remains zero until paid.
- Later payment: record negative cash delta and a matching negative liability delta against the same liability reference. Payment clears the bill; it does not create a second expense.
- Cost incurred and paid immediately: record the cost and cash movement as one event with clear evidence; do not also add a later payment for it.
- Accepted delivery/sale: recognize earned income only for the quantity actually accepted. Record cash only if actually received; otherwise use a receivable event.
- Customer advance: record cash receipt and a corresponding advance liability until earned or refunded.
- Estate transfer: record both actual legs with the same transfer reference; it is neither income nor cost.
- Tax: accrue only from posted actual taxable results under the estate's rules. A due date does not create a tax entry; payment reduces the recorded tax liability.
- Inventory, cargo, and capacity change only on evidenced physical receipt, dispatch, acceptance, damage, or loss. An order or scheduled shipment is not inventory movement.
- `planned`, `forecast`, `scheduled`, `pending`, and `unconfirmed` events cannot carry financial deltas.

No reserve or protected-cash hold is calculated. Forecasts remain separate from actuals. Any delayed/failed work stays open for review until an actual result is recorded.
