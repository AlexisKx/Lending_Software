from django import forms

from .models import Payment


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["date_paid", "amount"]
        widgets = {
            "date_paid": forms.DateInput(attrs={"type": "date"}),
        }
