from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard, name="index"),
    path("reports/", views.reports, name="reports"),
    path("reports/loans.csv", views.export_loans, name="export_loans"),
    path("reports/payments.csv", views.export_payments, name="export_payments"),
    path("reports/loans.pdf", views.export_loans_pdf, name="export_loans_pdf"),
    path("reports/payments.pdf", views.export_payments_pdf, name="export_payments_pdf"),
]
