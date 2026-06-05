from django.urls import path

from . import views

app_name = "borrowers"

urlpatterns = [
    path("", views.borrower_list, name="list"),
]
