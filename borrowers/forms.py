from django import forms

from .models import Borrower


class BorrowerForm(forms.ModelForm):
    class Meta:
        model = Borrower
        fields = ["name", "address", "contact", "valid_id", "source_of_income"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "input"}),
            "address": forms.TextInput(attrs={"class": "input"}),
            "contact": forms.TextInput(attrs={"class": "input"}),
            "valid_id": forms.TextInput(attrs={"class": "input"}),
            "source_of_income": forms.TextInput(attrs={"class": "input"}),
        }
