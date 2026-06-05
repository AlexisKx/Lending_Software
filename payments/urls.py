from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("", views.payment_list, name="list"),
    path("record/<int:loan_pk>/", views.payment_record, name="record"),
]
