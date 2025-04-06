from django.contrib.auth.models import User
from django.db import models

from ILAS.models import Establishment


# Create your models here.
class Report(models.Model):
    establishment = models.ForeignKey(Establishment, on_delete=models.CASCADE)
    register_number = models.CharField(max_length=255)
    id_number = models.CharField(max_length=255)
    license_category = models.CharField(max_length=255)
    issue_date = models.DateField()
    expired_date = models.DateField()
    activity = models.CharField(max_length=255)
    address = models.TextField()
    license_number = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)
    email = models.EmailField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.establishment.establishment_name} - {self.license_number}"
