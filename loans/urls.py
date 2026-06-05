from django.urls import path

from . import views

app_name = "loans"

urlpatterns = [
    path("", views.loan_list, name="list"),
    path("record/", views.loan_record, name="record"),
    path("_compute_proceeds/", views.compute_proceeds, name="compute_proceeds"),
    path("_advisory/", views.borrower_advisory, name="advisory"),
    path("<int:pk>/", views.loan_detail, name="detail"),
]
