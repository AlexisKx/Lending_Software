from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def payment_list(request):
    from .models import Payment
    payments = Payment.objects.select_related("loan__borrower").all()
    return render(request, "payments/list.html", {"payments": payments})


@login_required
def payment_record(request, loan_pk):
    return render(request, "payments/list.html", {"payments": []})
