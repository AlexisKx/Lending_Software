from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BorrowerForm
from .models import Borrower


@login_required
def borrower_list(request):
    q = request.GET.get("q", "").strip()
    borrowers = Borrower.objects.all()
    if q:
        borrowers = borrowers.filter(Q(name__icontains=q) | Q(contact__icontains=q))
    return render(
        request,
        "borrowers/list.html",
        {"borrowers": borrowers, "q": q},
    )


@login_required
def borrower_create(request):
    if request.method == "POST":
        form = BorrowerForm(request.POST)
        if form.is_valid():
            borrower = form.save()
            messages.success(request, f"Added {borrower.name}.")
            return redirect("borrowers:detail", pk=borrower.pk)
    else:
        form = BorrowerForm()
    return render(request, "borrowers/form.html", {"form": form, "mode": "create"})


@login_required
def borrower_detail(request, pk):
    borrower = get_object_or_404(Borrower, pk=pk)
    loans = borrower.loans.all()
    return render(
        request,
        "borrowers/detail.html",
        {"borrower": borrower, "loans": loans},
    )


@login_required
def borrower_edit(request, pk):
    borrower = get_object_or_404(Borrower, pk=pk)
    if request.method == "POST":
        form = BorrowerForm(request.POST, instance=borrower)
        if form.is_valid():
            form.save()
            messages.success(request, "Borrower updated.")
            return redirect("borrowers:detail", pk=borrower.pk)
    else:
        form = BorrowerForm(instance=borrower)
    return render(
        request,
        "borrowers/form.html",
        {"form": form, "mode": "edit", "borrower": borrower},
    )
