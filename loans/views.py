from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Loan


@login_required
def loan_list(request):
    loans = Loan.objects.select_related("borrower").all()
    return render(request, "loans/list.html", {"loans": loans})
