from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from loans.models import Loan


class Command(BaseCommand):
    help = (
        "Flag active loans as OVERDUE when their next installment is past due. "
        "Computes the expected balance at today's date based on a flat monthly "
        "installment of total_repayable / term_months."
    )

    def handle(self, *args, **options):
        today = timezone.localdate()
        flipped = 0

        active = Loan.objects.filter(status=Loan.STATUS_ACTIVE).select_related("borrower")
        for loan in active:
            months_elapsed = max(
                0,
                (today.year - loan.release_date.year) * 12
                + (today.month - loan.release_date.month),
            )
            if months_elapsed == 0:
                continue

            installments_due = min(months_elapsed, loan.term_months)
            monthly = loan.total_repayable / Decimal(loan.term_months)
            expected_paid = monthly * Decimal(installments_due)
            if loan.total_paid + Decimal("0.01") < expected_paid:
                loan.status = Loan.STATUS_OVERDUE
                loan.save(update_fields=["status"])
                flipped += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"Loan #{loan.pk} ({loan.borrower.name}) flagged OVERDUE."
                    )
                )

        self.stdout.write(self.style.SUCCESS(f"Done. {flipped} loan(s) flagged overdue."))
