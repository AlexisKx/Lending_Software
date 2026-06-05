from django.contrib import admin

from .models import Comaker, ComakerWaiver, Loan, LoanAudit


class ComakerInline(admin.StackedInline):
    model = Comaker
    extra = 0


class WaiverInline(admin.StackedInline):
    model = ComakerWaiver
    extra = 0
    readonly_fields = ("waived_at",)


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "borrower",
        "amount",
        "interest_rate",
        "term_months",
        "net_proceeds",
        "release_date",
        "status",
    )
    list_filter = ("status", "release_date")
    search_fields = ("borrower__name",)
    readonly_fields = ("net_proceeds", "created_at")
    inlines = [ComakerInline, WaiverInline]


@admin.register(LoanAudit)
class LoanAuditAdmin(admin.ModelAdmin):
    list_display = ("loan", "changed_at")
    readonly_fields = ("loan", "changed_at", "previous_values")
