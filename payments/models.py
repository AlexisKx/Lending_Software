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
