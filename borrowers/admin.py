from django.contrib import admin

from .models import Borrower


@admin.register(Borrower)
class BorrowerAdmin(admin.ModelAdmin):
    list_display = ("name", "contact", "source_of_income", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "contact", "valid_id")
