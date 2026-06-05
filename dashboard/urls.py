from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard, name="index"),
    path("reports/", views.reports, name="reports"),
    path("reports/loans.csv", views.export_loans, name="export_loans"),
    path("reports/payments.csv", views.export_payments, name="export_payments"),
]
