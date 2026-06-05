from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Count, Q, Sum
from django.utils import timezone

from borrowers.models import Borrower
from loans.models import Loan
from payments.models import Payment


PERIOD_CHOICES = [
    ("this_month", "This month"),
    ("3m", "Last 3 months"),
    ("ytd", "Year to date"),
    ("all", "All time"),
]


def resolve_period(key):
    today = timezone.localdate()
    if key == "3m":
        start = (today.replace(day=1) - timedelta(days=90)).replace(day=1)
    elif key == "ytd":
        start = today.replace(month=1, day=1)
    elif key == "all":
        start = date(2000, 1, 1)
    else:
        key = "this_month"
        start = today.replace(day=1)
    return key, start, today


def kpi_cards(start, end):
    total_borrowers = Borrower.objects.count()
    active_borrowers = Borrower.objects.filter(is_active=True).count()

    active_loans_qs = Loan.objects.filter(status=Loan.STATUS_ACTIVE)
    active_count = active_loans_qs.count()
    active_outstanding = sum(
        (l.outstanding_balance for l in active_loans_qs), Decimal("0")
    )

    collected = Payment.objects.filter(
        date_paid__gte=start, date_paid__lte=end
    ).aggregate(t=Sum("amount"))["t"] or Decimal("0")

    expected = _expected_for_period(start, end)
    rate = (collected / expected * Decimal("100")) if expected else Decimal("0")

    overdue_qs = Loan.objects.filter(status=Loan.STATUS_OVERDUE)
    overdue_count = overdue_qs.count()
    overdue_amount = sum((l.outstanding_balance for l in overdue_qs), Decimal("0"))

    return {
        "total_borrowers": total_borrowers,
        "active_borrowers": active_borrowers,
        "inactive_borrowers": total_borrowers - active_borrowers,
        "active_loans": active_count,
        "active_outstanding": active_outstanding,
        "collected": collected,
        "expected": expected,
        "collection_rate": rate.quantize(Decimal("0.1")),
        "overdue_count": overdue_count,
        "overdue_amount": overdue_amount,
    }


def _expected_for_period(start, end):
    """Expected collection = total interest that should have accrued in the
    window across loans that were live during it. Reducing-balance: at each
    month boundary in the window, add (principal_at_that_moment × rate).
    """
    months_in_window = max(
        0,
        (end.year - start.year) * 12 + (end.month - start.month) + 1,
    )
    if not months_in_window:
        return Decimal("0")

    expected = Decimal("0")
    for loan in Loan.objects.exclude(status=Loan.STATUS_PAID):
        rate = loan.monthly_rate
        principal = loan.state_as_of(start)["current_principal"]
        if principal <= 0:
            continue
        expected += principal * rate * Decimal(months_in_window)
    return expected


def monthly_series(months=6):
    today = timezone.localdate()
    series = []
    year, month = today.year, today.month
    months_back = []
    for _ in range(months):
        months_back.append((year, month))
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    months_back.reverse()

    for y, m in months_back:
        start = date(y, m, 1)
        end = (date(y + (m // 12), (m % 12) + 1, 1) - timedelta(days=1))
        agg = Payment.objects.filter(
            date_paid__gte=start, date_paid__lte=end
        ).aggregate(
            collected=Sum("amount"),
            interest_earned=Sum("interest_paid"),
        )
        series.append({
            "label": start.strftime("%b %Y"),
            "collected": float(agg["collected"] or 0),
            "interest": float(agg["interest_earned"] or 0),
        })
    return series


def status_breakdown():
    counts = (
        Loan.objects.values("status")
        .order_by()
        .annotate(c=Count("id"))
    )
    by_status = {row["status"]: row["c"] for row in counts}
    return {
        "active": by_status.get(Loan.STATUS_ACTIVE, 0),
        "paid": by_status.get(Loan.STATUS_PAID, 0),
        "overdue": by_status.get(Loan.STATUS_OVERDUE, 0),
    }


def aging_breakdown():
    today = timezone.localdate()
    buckets = {"1-30": Decimal("0"), "31-60": Decimal("0"), "61-90": Decimal("0"), "90+": Decimal("0")}
    counts = {k: 0 for k in buckets}

    for loan in Loan.objects.filter(status=Loan.STATUS_OVERDUE):
        days = (today - loan.release_date).days
        if days <= 30:
            bucket = "1-30"
        elif days <= 60:
            bucket = "31-60"
        elif days <= 90:
            bucket = "61-90"
        else:
            bucket = "90+"
        buckets[bucket] += loan.outstanding_balance
        counts[bucket] += 1

    return [
        {"label": k, "amount": float(v), "count": counts[k]}
        for k, v in buckets.items()
    ]


def recent_activity(limit=8):
    items = []
    for loan in Loan.objects.select_related("borrower").order_by("-created_at")[:limit]:
        items.append({
            "kind": "loan",
            "when": loan.created_at,
            "text": f"Loan #{loan.pk} for {loan.borrower.name} (₱{loan.amount})",
            "url": f"/loans/{loan.pk}/",
        })
    for p in Payment.objects.select_related("loan__borrower").order_by("-created_at")[:limit]:
        items.append({
            "kind": "payment",
            "when": p.created_at,
            "text": f"Payment ₱{p.amount} on Loan #{p.loan.pk} ({p.loan.borrower.name})",
            "url": f"/loans/{p.loan.pk}/",
        })
    items.sort(key=lambda x: x["when"], reverse=True)
    return items[:limit]
