from decimal import Decimal

from django.db import models

from loans.models import Loan


class Payment(models.Model):
    loan = models.ForeignKey(
        Loan, on_delete=models.PROTECT, related_name="payments"
    )
    date_paid = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_paid", "-id"]

    def __str__(self):
        return f"Payment {self.amount} on {self.date_paid}"

    def save(self, *args, **kwargs):
        total_paid_before = self.loan.payments.exclude(pk=self.pk).aggregate(
            t=models.Sum("amount")
        )["t"] or Decimal("0")
        self.balance_after = self.loan.total_repayable - (total_paid_before + self.amount)
        super().save(*args, **kwargs)

        if self.balance_after <= Decimal("0") and self.loan.status != Loan.STATUS_PAID:
            self.loan.status = Loan.STATUS_PAID
            self.loan.save(update_fields=["status"])
