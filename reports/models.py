from django.contrib.auth.models import User
from django.db import models
from ILAS.models import Establishment

class LicenseReport(models.Model):
    """
    Model representing a license report for an establishment.
    """

    # Foreign key to the Establishment model, deletes the report if the establishment is deleted
    establishment = models.ForeignKey(Establishment, on_delete=models.CASCADE)

    # License details
    register_number = models.CharField(max_length=255, help_text="Registration number of the license")
    id_number = models.CharField(max_length=255, help_text="Identification number associated with the license")
    license_category = models.CharField(max_length=255, help_text="Category of the license")
    issue_date = models.DateField(help_text="Date when the license was issued")
    expired_date = models.DateField(help_text="Date when the license will expire")
    activity = models.CharField(max_length=255, help_text="Activity associated with the license")
    address = models.TextField(help_text="Address of the establishment")
    license_number = models.CharField(max_length=255, help_text="Unique number of the license")
    phone_number = models.CharField(max_length=255, help_text="Contact phone number for the establishment")
    email = models.EmailField(help_text="Contact email for the establishment")

    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, help_text="User who created the report")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the report was created")

    def __str__(self):
        """
        String representation of the LicenseReport model.
        Returns a string combining the establishment name and license number.
        """
        return f"{self.establishment.establishment_name} - {self.license_number}"
