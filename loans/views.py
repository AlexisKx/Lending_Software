from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from borrowers.models import Borrower
from borrowers.utils import waiver_recommendation

from .forms import LoanRecordForm
from .models import Loan


def _to_decimal(value, default=Decimal("0")):
    try:
        return Decimal(value or "0")
    except (InvalidOperation, TypeError):
        return default


@login_required
def loan_list(request):
    status = request.GET.get("status", "").upper()
    loans = Loan.objects.select_related("borrower").all()
    if status in {Loan.STATUS_ACTIVE, Loan.STATUS_PAID, Loan.STATUS_OVERDUE}:
        loans = loans.filter(status=status)
    return render(request, "loans/list.html", {"loans": loans, "status": status})


@login_required
def loan_detail(request, pk):
    loan = get_object_or_404(
        Loan.objects.select_related("borrower"), pk=pk
    )
    payments = loan.payments.all()
    return render(
        request,
        "loans/detail.html",
        {"loan": loan, "payments": payments},
    )


@login_required
def loan_record(request):
    if request.method == "POST":
        form = LoanRecordForm(request.POST)
        if form.is_valid():
            loan = form.save()
            messages.success(
                request,
                f"Loan #{loan.pk} recorded for {loan.borrower.name}.",
            )
            return redirect("loans:detail", pk=loan.pk)
    else:
        form = LoanRecordForm()

    advisory = None
    borrower_id = request.GET.get("borrower") or request.POST.get("existing_borrower")
    if borrower_id:
        try:
            advisory = waiver_recommendation(Borrower.objects.get(pk=borrower_id))
        except Borrower.DoesNotExist:
            advisory = None

    return render(
        request,
        "loans/record.html",
        {"form": form, "advisory": advisory},
    )


@login_required
def compute_proceeds(request):
    """HTMX endpoint — returns the proceeds panel partial."""
    amount = _to_decimal(request.POST.get("amount"))
    advance = _to_decimal(request.POST.get("advance_interest"))
    fees = _to_decimal(request.POST.get("fees"))
    rate = _to_decimal(request.POST.get("interest_rate"))
    term = _to_decimal(request.POST.get("term_months"))

    net = amount - advance - fees
    interest_total = amount * (rate / Decimal("100")) * term if term else Decimal("0")
    total_repayable = amount + interest_total
    monthly = (total_repayable / term) if term else Decimal("0")

    return render(
        request,
        "loans/_proceeds.html",
        {
            "amount": amount,
            "advance": advance,
            "fees": fees,
            "net": net,
            "total_repayable": total_repayable,
            "interest_total": interest_total,
            "monthly": monthly,
        },
    )


@login_required
def borrower_advisory(request):
    """HTMX endpoint — returns the co-maker advisory chip for a borrower."""
    borrower_id = request.POST.get("existing_borrower") or request.GET.get("borrower")
    advisory = None
    if borrower_id:
        try:
            advisory = waiver_recommendation(Borrower.objects.get(pk=borrower_id))
        except Borrower.DoesNotExist:
            advisory = None
    return render(request, "loans/_advisory.html", {"advisory": advisory})
