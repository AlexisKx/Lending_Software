from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("borrowers/", include("borrowers.urls")),
    path("loans/", include("loans.urls")),
    path("payments/", include("payments.urls")),
    path("", include("dashboard.urls")),
]
