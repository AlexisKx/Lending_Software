from datetime import date
from decimal import Decimal

CENTS = Decimal("0.01")


def months_elapsed(start, end):
    """Whole calendar months from start to end, anniversary-based.

    Jan 1 → Feb 1 = 1; Jan 15 → Feb 14 = 0; Jan 15 → Feb 15 = 1.
    """
    if end is None or start is None or end <= start:
        return 0
    m = (end.year - start.year) * 12 + (end.month - start.month)
    if end.day < start.day:
        m -= 1
    return max(0, m)


def add_months(d, months):
    """Add `months` to date d, clamping to the last day if needed."""
    if not d:
        return None
    y = d.year + (d.month - 1 + months) // 12
    m = (d.month - 1 + months) % 12 + 1
    last_day = 31
    while True:
        try:
            return date(y, m, min(d.day, last_day))
        except ValueError:
            last_day -= 1


def q(amount):
    return (Decimal(amount or 0)).quantize(CENTS)
