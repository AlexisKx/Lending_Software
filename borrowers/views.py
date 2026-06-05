from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Borrower


@login_required
def borrower_list(request):
    borrowers = Borrower.objects.all()
    return render(request, "borrowers/list.html", {"borrowers": borrowers})
