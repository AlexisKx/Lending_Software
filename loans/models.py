from decimal import Decimal

from django.db import models

from borrowers.models import Borrower


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
    term_months = models.PositiveIntegerField()
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
    def total_repayable(self):
        rate = (self.interest_rate or Decimal("0")) / Decimal("100")
        return self.amount + (self.amount * rate * self.term_months)

    @property
    def total_paid(self):
        agg = self.payments.aggregate(total=models.Sum("amount"))
        return agg["total"] or Decimal("0")

    @property
    def outstanding_balance(self):
        return self.total_repayable - self.total_paid


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
