import csv
from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from loans.models import Loan
from payments.models import Payment

from . import services


def _pdf_response(filename, title, headers, rows):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import landscape, letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import (
        Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
    )

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=landscape(letter),
        leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36,
    )
    styles = getSampleStyleSheet()
    story = [
        Paragraph(title, styles["Title"]),
        Paragraph(
            f"Generated {timezone.localtime().strftime('%b %d, %Y %I:%M %p')}",
            styles["Normal"],
        ),
        Spacer(1, 12),
    ]
    table = Table([headers] + rows, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#e2e8f0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(table)
    doc.build(story)

    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


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


@login_required
def export_loans_pdf(request):
    status = request.GET.get("status", "").upper()
    loans = Loan.objects.select_related("borrower").all()
    if status in {"ACTIVE", "PAID", "OVERDUE"}:
        loans = loans.filter(status=status)

    headers = [
        "#", "Borrower", "Amount", "Rate%", "Term",
        "Adv. int.", "Fees", "Net", "Released", "Status",
        "Paid", "Outstanding",
    ]
    rows = [
        [
            l.id, l.borrower.name, f"{l.amount:,.2f}",
            f"{l.interest_rate}", l.term_months,
            f"{l.advance_interest:,.2f}", f"{l.fees:,.2f}",
            f"{l.net_proceeds:,.2f}", l.release_date.strftime("%Y-%m-%d"),
            l.status, f"{l.total_paid:,.2f}", f"{l.outstanding_balance:,.2f}",
        ]
        for l in loans
    ]
    title = f"Loan release report{f' ({status})' if status else ''}"
    return _pdf_response("loans.pdf", title, headers, rows)


@login_required
def export_payments_pdf(request):
    payments = Payment.objects.select_related("loan__borrower").all()
    headers = ["#", "Date", "Borrower", "Loan", "Amount", "Balance after"]
    rows = [
        [
            p.id, p.date_paid.strftime("%Y-%m-%d"), p.loan.borrower.name,
            f"#{p.loan.id}", f"{p.amount:,.2f}", f"{p.balance_after:,.2f}",
        ]
        for p in payments
    ]
    return _pdf_response("payments.pdf", "Payments report", headers, rows)
