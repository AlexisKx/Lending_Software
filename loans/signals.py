from decimal import Decimal

from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Loan, LoanAudit


def _serialize(loan):
    return {
        "amount": str(loan.amount),
        "interest_rate": str(loan.interest_rate),
        "term_months": loan.term_months,
        "advance_interest": str(loan.advance_interest),
        "fees": str(loan.fees),
        "net_proceeds": str(loan.net_proceeds),
        "release_date": loan.release_date.isoformat() if loan.release_date else None,
        "status": loan.status,
    }


@receiver(pre_save, sender=Loan)
def snapshot_loan_changes(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        previous = Loan.objects.get(pk=instance.pk)
    except Loan.DoesNotExist:
        return

    previous_data = _serialize(previous)
    current_data = _serialize(instance)
    if previous_data == current_data:
        return

    LoanAudit.objects.create(loan=previous, previous_values=previous_data)
