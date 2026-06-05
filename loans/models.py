from decimal import Decimal

from django.db import models, transaction
from django.utils import timezone

from borrowers.models import Borrower

from .utils import add_months, months_elapsed, q


class Loan(models.Model):
    STATUS_ACTIVE = "ACTIVE"
    STATUS_PAID = "PAID"
    STATUS_OVERDUE = "OVERDUE"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_PAID, "Paid"),
        (STATUS_OVERDUE, "Overdue"),
    ]

    borrower = models.ForeignKey(
        Borrower, on_delete=models.PROTECT, related_name="loans"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    term_months = models.PositiveIntegerField(
        help_text="Expected loan duration. Tracking only — does not affect interest math."
    )
    advance_interest = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0")
    )
    fees = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0")
    )
    net_proceeds = models.DecimalField(max_digits=12, decimal_places=2)
    release_date = models.DateField()
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=STATUS_ACTIVE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-release_date", "-id"]

    def __str__(self):
        return f"Loan #{self.pk} · {self.borrower.name}"

    def save(self, *args, **kwargs):
        self.net_proceeds = (
            (self.amount or Decimal("0"))
            - (self.advance_interest or Decimal("0"))
            - (self.fees or Decimal("0"))
        )
        super().save(*args, **kwargs)

    @property
    def monthly_rate(self):
        return (self.interest_rate or Decimal("0")) / Decimal("100")

    @property
    def maturity_date(self):
        return add_months(self.release_date, self.term_months or 0)

    def state_as_of(self, as_of=None):
        """Simulate the reducing-balance ledger up to `as_of`.

        Returns dict with current_principal, accrued_interest_unpaid,
        total_due, total_paid, total_principal_paid, total_interest_paid,
        last_event_date.
        """
        as_of = as_of or timezone.localdate()
        rate = self.monthly_rate
        principal = Decimal(self.amount or 0)
        interest_carried = Decimal("0")
        last_date = self.release_date
        total_paid = Decimal("0")
        total_principal_paid = Decimal("0")
        total_interest_paid = Decimal("0")

        for p in self.payments.order_by("date_paid", "id"):
            months = months_elapsed(last_date, p.date_paid)
            interest_carried += principal * rate * Decimal(months)

            interest_paid = min(p.amount, interest_carried)
            principal_paid = p.amount - interest_paid
            if principal_paid > principal:
                principal_paid = principal

            interest_carried -= interest_paid
            principal -= principal_paid

            total_paid += p.amount
            total_interest_paid += interest_paid
            total_principal_paid += principal_paid
            last_date = p.date_paid

        if as_of > last_date and principal > 0:
            months = months_elapsed(last_date, as_of)
            interest_carried += principal * rate * Decimal(months)

        return {
            "current_principal": q(principal),
            "accrued_interest_unpaid": q(max(interest_carried, Decimal("0"))),
            "total_due": q(max(principal + interest_carried, Decimal("0"))),
            "total_paid": q(total_paid),
            "total_principal_paid": q(total_principal_paid),
            "total_interest_paid": q(total_interest_paid),
            "last_event_date": last_date,
        }

    @transaction.atomic
    def recompute_payments(self, save_status=True):
        """Re-walk the ledger and update every Payment's computed fields.

        Call after creating, editing, or deleting a payment, or after the
        loan's amount / interest_rate / release_date change.
        """
        from payments.models import Payment

        rate = self.monthly_rate
        principal = Decimal(self.amount or 0)
        interest_carried = Decimal("0")
        last_date = self.release_date

        for p in self.payments.order_by("date_paid", "id"):
            months = months_elapsed(last_date, p.date_paid)
            interest_carried += principal * rate * Decimal(months)
            interest_due = interest_carried

            interest_paid = min(p.amount, interest_carried)
            principal_paid = p.amount - interest_paid
            if principal_paid > principal:
                principal_paid = principal

            interest_carried -= interest_paid
            principal -= principal_paid

            Payment.objects.filter(pk=p.pk).update(
                interest_due=q(interest_due),
                interest_paid=q(interest_paid),
                principal_paid=q(principal_paid),
                principal_balance_after=q(principal),
                balance_after=q(principal + interest_carried),
            )
            last_date = p.date_paid

        if save_status:
            paid_off = principal <= Decimal("0") and interest_carried <= Decimal("0")
            if paid_off and self.status != Loan.STATUS_PAID:
                self.status = Loan.STATUS_PAID
                self.save(update_fields=["status"])
            elif not paid_off and self.status == Loan.STATUS_PAID:
                self.status = Loan.STATUS_ACTIVE
                self.save(update_fields=["status"])

    # ---- Display helpers ----
    @property
    def current_principal(self):
        return self.state_as_of()["current_principal"]

    @property
    def accrued_interest_unpaid(self):
        return self.state_as_of()["accrued_interest_unpaid"]

    @property
    def monthly_interest_due(self):
        return q(self.current_principal * self.monthly_rate)

    @property
    def outstanding_balance(self):
        return self.state_as_of()["total_due"]

    @property
    def total_paid(self):
        return self.state_as_of()["total_paid"]

    @property
    def total_principal_paid(self):
        return self.state_as_of()["total_principal_paid"]

    @property
    def total_interest_paid(self):
        return self.state_as_of()["total_interest_paid"]


class Comaker(models.Model):
    loan = models.OneToOneField(
        Loan, on_delete=models.CASCADE, related_name="comaker"
    )
    name = models.CharField(max_length=200)
    contact = models.CharField(max_length=50, blank=True)
    relationship = models.CharField(max_length=100, blank=True)
    source_of_income = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name


class ComakerWaiver(models.Model):
    loan = models.OneToOneField(
        Loan, on_delete=models.CASCADE, related_name="waiver"
    )
    reason = models.CharField(max_length=300)
    waived_at = models.DateTimeField(auto_now_add=True)


class LoanAudit(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name="audits")
    changed_at = models.DateTimeField(auto_now_add=True)
    previous_values = models.JSONField()

    class Meta:
        ordering = ["-changed_at"]
