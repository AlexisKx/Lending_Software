from decimal import Decimal

from django import forms

from borrowers.models import Borrower

from .models import Comaker, Loan


class LoanRecordForm(forms.Form):
    """Single combined form for the Record Loan screen."""

    # Borrower section
    existing_borrower = forms.ModelChoiceField(
        queryset=Borrower.objects.filter(is_active=True),
        required=False,
        empty_label="— New borrower —",
    )
    borrower_name = forms.CharField(max_length=200, required=False)
    borrower_address = forms.CharField(max_length=300, required=False)
    borrower_contact = forms.CharField(max_length=50, required=False)
    borrower_valid_id = forms.CharField(max_length=100, required=False)
    borrower_source_of_income = forms.CharField(max_length=200, required=False)

    # Loan section
    amount = forms.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("0.01"))
    interest_rate = forms.DecimalField(max_digits=5, decimal_places=2, min_value=Decimal("0"))
    term_months = forms.IntegerField(min_value=1)
    release_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    advance_interest = forms.DecimalField(
        max_digits=12, decimal_places=2, required=False, initial=Decimal("0")
    )
    fees = forms.DecimalField(
        max_digits=12, decimal_places=2, required=False, initial=Decimal("0")
    )

    # Co-maker section
    has_comaker = forms.ChoiceField(
        choices=[("yes", "Include co-maker"), ("waive", "Waive with reason")],
        initial="yes",
        widget=forms.RadioSelect,
    )
    comaker_name = forms.CharField(max_length=200, required=False)
    comaker_contact = forms.CharField(max_length=50, required=False)
    comaker_relationship = forms.CharField(max_length=100, required=False)
    comaker_source_of_income = forms.CharField(max_length=200, required=False)
    waiver_reason = forms.CharField(max_length=300, required=False)

    def clean(self):
        cleaned = super().clean()

        if not cleaned.get("existing_borrower") and not cleaned.get("borrower_name"):
            self.add_error(
                "borrower_name",
                "Enter a name for the new borrower, or pick an existing borrower above.",
            )

        choice = cleaned.get("has_comaker")
        if choice == "yes":
            if not cleaned.get("comaker_name"):
                self.add_error("comaker_name", "Co-maker name is required.")
        elif choice == "waive":
            if not cleaned.get("waiver_reason"):
                self.add_error("waiver_reason", "Provide a reason for waiving the co-maker.")

        return cleaned

    def save(self):
        data = self.cleaned_data
        borrower = data.get("existing_borrower")
        if not borrower:
            borrower = Borrower.objects.create(
                name=data["borrower_name"],
                address=data.get("borrower_address") or "",
                contact=data.get("borrower_contact") or "",
                valid_id=data.get("borrower_valid_id") or "",
                source_of_income=data.get("borrower_source_of_income") or "",
            )

        loan = Loan.objects.create(
            borrower=borrower,
            amount=data["amount"],
            interest_rate=data["interest_rate"],
            term_months=data["term_months"],
            advance_interest=data.get("advance_interest") or Decimal("0"),
            fees=data.get("fees") or Decimal("0"),
            release_date=data["release_date"],
        )

        if data["has_comaker"] == "yes":
            Comaker.objects.create(
                loan=loan,
                name=data["comaker_name"],
                contact=data.get("comaker_contact") or "",
                relationship=data.get("comaker_relationship") or "",
                source_of_income=data.get("comaker_source_of_income") or "",
            )
        else:
            from .models import ComakerWaiver
            ComakerWaiver.objects.create(loan=loan, reason=data["waiver_reason"])

        return loan
