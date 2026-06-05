from django.db import models


class Borrower(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=300, blank=True)
    contact = models.CharField(max_length=50, blank=True)
    valid_id = models.CharField(max_length=100, blank=True)
    source_of_income = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
