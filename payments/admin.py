from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "loan", "date_paid", "amount", "balance_after")
    list_filter = ("date_paid",)
    search_fields = ("loan__borrower__name",)
    readonly_fields = ("balance_after", "created_at")
