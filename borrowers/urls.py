from django.urls import path

from . import views

app_name = "borrowers"

urlpatterns = [
    path("", views.borrower_list, name="list"),
    path("new/", views.borrower_create, name="create"),
    path("<int:pk>/", views.borrower_detail, name="detail"),
    path("<int:pk>/edit/", views.borrower_edit, name="edit"),
]
