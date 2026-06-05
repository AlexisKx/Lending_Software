from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from loans.models import Loan

from .forms import PaymentForm
from .models import Payment


@login_required
def payment_list(request):
    payments = Payment.objects.select_related("loan__borrower").all()
    return render(request, "payments/list.html", {"payments": payments})


@login_required
def payment_record(request, loan_pk):
    loan = get_object_or_404(Loan.objects.select_related("borrower"), pk=loan_pk)

    if request.method == "POST":
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.loan = loan
            payment.save()
            messages.success(
                request,
                f"Recorded ₱{payment.amount} payment. Balance: ₱{payment.balance_after}.",
            )
            return redirect("loans:detail", pk=loan.pk)
    else:
        form = PaymentForm()

    return render(
        request,
        "payments/record.html",
        {"form": form, "loan": loan},
    )
