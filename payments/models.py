from decimal import Decimal

from django.db import models


class Payment(models.Model):
    loan = models.ForeignKey(
        "loans.Loan", on_delete=models.PROTECT, related_name="payments"
    )
    date_paid = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    # All four below are populated by Loan.recompute_payments(); they are
    # derived state, not user input. Stored so list/detail views and exports
    # don't have to replay the whole ledger.
    interest_due = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0"),
        help_text="Interest that had accrued (including any carry-over) just before this payment was applied.",
    )
    interest_paid = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0"),
    )
    principal_paid = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0"),
    )
    principal_balance_after = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0"),
    )
    balance_after = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0"),
        help_text="Principal remaining plus any unpaid carried interest right after this payment.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_paid", "-id"]

    def __str__(self):
        return f"Payment {self.amount} on {self.date_paid}"
