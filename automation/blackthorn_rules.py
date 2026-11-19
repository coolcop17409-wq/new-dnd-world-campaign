#!/usr/bin/env python3
"""Source-checked Blackthorn routine accrual and rolling tax calculations."""
from decimal import Decimal, ROUND_HALF_UP


def money(value):
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def accrue_daily_rates(rates, opening_day, start_day, through_day, rate_type=None):
    """Reproduce Rates & Staff accrued-gp logic for daily Payroll/Upkeep rows.

    Rates are effective on their From day and remain active through their
    optional Through day, inclusive. The opening balance already includes
    activity through opening_day, so accrual begins no earlier than opening_day+1.
    Each rate row is rounded to two decimals before summing, matching the sheet.
    """
    opening_day = int(opening_day)
    start_day = int(start_day)
    through_day = int(through_day)
    result = Decimal("0.00")
    for row in rates:
        kind = str(row.get("type", "")).strip()
        if kind not in {"Payroll", "Upkeep"} or (rate_type and kind != rate_type):
            continue
        unit = str(row.get("unit", "")).strip().lower()
        if unit != "day":
            continue
        rate = Decimal(str(row.get("rate_gp", 0) or 0))
        rate_from = int(row.get("from_day", 0) or 0)
        rate_through = row.get("through_day")
        lower = max(start_day, opening_day + 1, rate_from)
        upper = min(through_day, int(rate_through) if rate_through not in (None, "") else through_day)
        days = max(0, upper - lower + 1)
        result += money(rate * days)
    return result


def blackthorn_tax_base(*, taxable_carry, accepted_revenue, cogs,
                        loss_and_idle, management_payroll, upkeep,
                        incurred_operating_expenses):
    """Reproduce Accounts tax-period T: opening carry + actual operating profit."""
    return money(
        Decimal(str(taxable_carry))
        + Decimal(str(accepted_revenue))
        - Decimal(str(cogs))
        - Decimal(str(loss_and_idle))
        - Decimal(str(management_payroll))
        - Decimal(str(upkeep))
        - Decimal(str(incurred_operating_expenses))
    )


def blackthorn_tax_assessment(taxable_base, tax_rate=Decimal("0.10")):
    """Reproduce Accounts assessment: 10% of positive period base, rounded to gp."""
    taxable_base = Decimal(str(taxable_base))
    return money(max(Decimal("0"), taxable_base) * Decimal(str(tax_rate)))
