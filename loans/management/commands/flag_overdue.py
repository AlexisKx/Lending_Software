from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from loans.models import Loan
from loans.utils import months_elapsed


class Command(BaseCommand):
    help = (
        "Flag active loans as OVERDUE when the borrower is behind on monthly "
        "interest. Reducing-balance rule: if at least one full month has passed "
        "since the last payment (or release) and there is accrued unpaid "
        "interest, the loan is overdue."
    )

    def handle(self, *args, **options):
        today = timezone.localdate()
        flipped = 0

        for loan in Loan.objects.filter(status=Loan.STATUS_ACTIVE).select_related("borrower"):
            state = loan.state_as_of(today)
            since = months_elapsed(state["last_event_date"], today)
            if since >= 1 and state["accrued_interest_unpaid"] > Decimal("0.01"):
                loan.status = Loan.STATUS_OVERDUE
                loan.save(update_fields=["status"])
                flipped += 1
                self.stdout.write(self.style.WARNING(
                    f"Loan #{loan.pk} ({loan.borrower.name}) flagged OVERDUE — "
                    f"₱{state['accrued_interest_unpaid']} unpaid interest, "
                    f"{since} month(s) since last activity."
                ))

        self.stdout.write(self.style.SUCCESS(f"Done. {flipped} loan(s) flagged overdue."))
