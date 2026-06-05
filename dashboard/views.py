import csv

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from loans.models import Loan
from payments.models import Payment

from . import services


@login_required
def dashboard(request):
    period_key, start, end = services.resolve_period(request.GET.get("period", "this_month"))
    ctx = {
        "period_key": period_key,
        "period_choices": services.PERIOD_CHOICES,
        "start": start,
        "end": end,
        "kpi": services.kpi_cards(start, end),
        "monthly": services.monthly_series(6),
        "status": services.status_breakdown(),
        "aging": services.aging_breakdown(),
        "activity": services.recent_activity(8),
    }
    if request.headers.get("HX-Request"):
        return render(request, "dashboard/_panels.html", ctx)
    return render(request, "dashboard/index.html", ctx)


@login_required
def reports(request):
    return render(request, "dashboard/reports.html")


@login_required
def export_loans(request):
    status = request.GET.get("status", "").upper()
    loans = Loan.objects.select_related("borrower").all()
    if status in {"ACTIVE", "PAID", "OVERDUE"}:
        loans = loans.filter(status=status)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="loans.csv"'
    writer = csv.writer(response)
    writer.writerow([
        "ID", "Borrower", "Amount", "Rate (%)", "Term (mo)",
        "Advance interest", "Fees", "Net proceeds",
        "Release date", "Status", "Total paid", "Outstanding",
    ])
    for l in loans:
        writer.writerow([
            l.id, l.borrower.name, l.amount, l.interest_rate, l.term_months,
            l.advance_interest, l.fees, l.net_proceeds,
            l.release_date.isoformat(), l.status,
            l.total_paid, l.outstanding_balance,
        ])
    return response


@login_required
def export_payments(request):
    payments = Payment.objects.select_related("loan__borrower").all()
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="payments.csv"'
    writer = csv.writer(response)
    writer.writerow(["ID", "Date", "Borrower", "Loan ID", "Amount", "Balance after"])
    for p in payments:
        writer.writerow([
            p.id, p.date_paid.isoformat(), p.loan.borrower.name,
            p.loan.id, p.amount, p.balance_after,
        ])
    return response
