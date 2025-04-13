"""
This module contains the models for the Licensing app.
The models define the structure of the database tables and the relationships between them.

Models:
- Activity: Represents different types of activities.
- MainCategory: Represents main categories.
- EstablishmentRole: Represents different roles in an establishment.
- SubCategory: Represents subcategories under main categories.
- Establishment: Represents an establishment with various details.
- ArduinoReader: Represents RFID readings received from an Arduino device.
- Inspection: Represents an inspection record with details and photos.
- EstablishmentRegister: Represents registration records for establishments.
- EstablishmentLicence: Represents licence records linked to registrations.
- InspectionAssignment: Represents inspection tasks assigned to inspectors.
"""

import os

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.files.storage import FileSystemStorage

# Create a FileSystemStorage instance pointing to the static folder
static_storage = FileSystemStorage(location=os.path.join(settings.BASE_DIR, "static"))


class Activity(models.Model):
    """
    Model representing different types of activities.

    Fields:
    - ar_name: Arabic name of the activity (unique).
    - en_name: English name of the activity (optional).
    - code: Unique code for the activity.
    """
    ar_name = models.CharField(max_length=250, unique=True)
    en_name = models.CharField(max_length=250, null=True, blank=True)
    code = models.CharField(max_length=250, unique=True)

    def __str__(self):
        """Returns a string representation of the activity."""
        return self.ar_name or "N/A"

    class Meta:
        verbose_name = "Activity"
        verbose_name_plural = "Activities"


class MainCategory(models.Model):
    """
    Model representing main categories.

    Fields:
    - ar_name: Arabic name of the main category (unique).
    - en_name: English name of the main category (optional).
    """
    ar_name = models.CharField(max_length=250, unique=True)
    en_name = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        """Returns a string representation of the main category."""
        return self.ar_name or "N/A"

    class Meta:
        verbose_name = "Main Category"
        verbose_name_plural = "Main Categories"


class EstablishmentRole(models.Model):
    """
    Model representing different roles in an establishment.

    Fields:
    - ar_name: Arabic name of the role (unique).
    - en_name: English name of the role (optional).
    """
    ar_name = models.CharField(max_length=250, unique=True)
    en_name = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        """Returns a string representation of the establishment role."""
        return self.ar_name or "N/A"

    class Meta:
        verbose_name = "Establishment Role"
        verbose_name_plural = "Establishment Roles"


class SubCategory(models.Model):
    """
    Model representing subcategories under main categories.

    Fields:
    - ar_name: Arabic name of the subcategory (unique).
    - en_name: English name of the subcategory (optional).
    """
    ar_name = models.CharField(max_length=250, unique=True)
    en_name = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        """Returns a string representation of the subcategory."""
        return f"{self.id}: {self.ar_name}/{self.en_name or 'N/A'}"

    class Meta:
        verbose_name = "Sub Category"
        verbose_name_plural = "Sub Categories"


class Establishment(models.Model):
    """
    Model representing an establishment with various details.
    
    Includes contact information, location details, and relationships
    to categories and activities.
    """
    id = models.AutoField(primary_key=True)
    rifd = models.CharField(max_length=100, unique=True)
    establishment_name = models.CharField(max_length=200)
    # Foreign key relationships
    main_category = models.ForeignKey(
        MainCategory, on_delete=models.CASCADE, null=True, blank=True
    )
    sub_category = models.ForeignKey(
        SubCategory, on_delete=models.CASCADE, null=True, blank=True
    )
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    
    # Contact information
    owner_name = models.CharField(max_length=200)
    owner_number = models.CharField(max_length=50)
    director_name = models.CharField(max_length=200)
    director_number = models.CharField(max_length=50)
    representative_name = models.CharField(max_length=200)
    representative_number = models.CharField(max_length=200)
    box_O_P = models.BigIntegerField()
    email = models.EmailField(max_length=255, unique=True)
    phone_number = models.CharField(max_length=50)
    
    # Location details
    municipality_name = models.CharField(max_length=200)
    region_number = models.CharField(max_length=50)
    street_number = models.BigIntegerField()
    street_name = models.CharField(max_length=200)
    building_number = models.BigIntegerField()
    block_number = models.BigIntegerField()
    block_name = models.CharField(max_length=200)
    
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.establishment_name}"

    @property
    def get_register(self):
        """Returns the establishment's registration record if it exists."""
        try:
            return EstablishmentRegister.objects.get(establishment_id=self.id)
        except EstablishmentRegister.DoesNotExist:
            return None

    def get_license(self):
        """Returns the establishment's license if it exists."""
        register = self.get_register
        if register:
            try:
                return EstablishmentLicence.objects.get(register_id=register.id)
            except EstablishmentLicence.DoesNotExist:
                return None
        return None

    def get_address(self):
        """Returns the full address of the establishment."""
        return f"{self.street_name} {self.street_number}, {self.municipality_name}, {self.region_number}"


class ArduinoReader(models.Model):
    """
    Stores RFID readings received from an Arduino device.

    Fields:
    - code: RFID card code
    - date_created: Timestamp when the entry was created
    - queried: Flag indicating if the RFID entry has been processed
    - device_id: Optional identifier for the Arduino device
    - status: Processing status of the RFID data
    - last_updated: Timestamp of last modification
    """
    # The unique RFID code sent from Arduino
    code = models.CharField(
        max_length=15, unique=False, help_text="Unique RFID code scanned by the Arduino"
    )

    # The date and time when the RFID data was received
    date_created = models.DateTimeField(
        default=now,
        editable=False,
        help_text="Timestamp when the RFID entry was created",
    )

    # Boolean flag to track if the data has been queried or processed
    queried = models.BooleanField(
        default=False, help_text="Indicates whether the RFID entry has been processed"
    )

    # Additional field to track which Arduino device sent the data
    device_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Optional ID of the Arduino device that sent this data",
    )

    # Status field to track different processing stages
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processed", "Processed"),
        ("error", "Error"),
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pending",
        help_text="Processing status of the RFID data",
    )

    # Timestamp to store the last modification time of the entry
    last_updated = models.DateTimeField(
        auto_now=True, help_text="Timestamp when the record was last updated"
    )

    def __str__(self):
        """Returns a human-readable representation of the RFID entry."""
        return f"RFID: {self.code} | Status: {self.status} | Queried: {self.queried}"

    class Meta:
        ordering = ["-date_created"]  # Orders records with the latest first
        verbose_name = "Arduino RFID Entry"
        verbose_name_plural = "Arduino RFID Entries"


class Inspection(models.Model):
    """
    Model representing an inspection record with details and photos.
    
    Tracks inspection status, location, inspector information, and related media.
    """
    STATUS_CHOICES = (
        (True, "مستوفي الشروط"),
        (False, "غير مستوفي الشروط"),
    )

    # Inspection Details
    register_number = models.CharField(
        max_length=255, blank=True, default="0", verbose_name="Register Number"
    )
    notes = models.TextField(null=True, blank=True, verbose_name="Inspection Notes")
    latitude = models.CharField(verbose_name="Latitude", max_length=20)
    longitude = models.CharField(verbose_name="Longitude", max_length=20)
    status = models.BooleanField(
        choices=STATUS_CHOICES, verbose_name="Inspection Status", default=False
    )
    inspector = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="inspections",
        verbose_name="Inspector",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Date and Time of Inspection"
    )
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)

    # Media fields for inspection documentation
    register_photo = models.ImageField(
        upload_to="inspections/register_photos/",
        null=True,
        blank=True,
        verbose_name="Register Photo",
        storage=static_storage,
    )
    license_photo = models.ImageField(
        upload_to="inspections/license_photos/",
        null=True,
        blank=True,
        verbose_name="License Photo",
        storage=static_storage,
    )
    establishment_photo = models.ImageField(
        upload_to="inspections/establishment_photos/",
        null=True,
        blank=True,
        verbose_name="Establishment Photo",
        storage=static_storage,
    )
    cars_building_photo = models.ImageField(
        upload_to="inspections/cars_building_photos/",
        null=True,
        blank=True,
        verbose_name="Cars Building Photo",
        storage=static_storage,
    )

    def __str__(self):
        return f"Inspection {self.register_number} - {'Accepted' if self.status else 'Refused'}"

    def get_register(self):
        """Returns the establishment register associated with this inspection."""
        try:
            return EstablishmentRegister.objects.get(id=self.register_number)
        except EstablishmentRegister.DoesNotExist:
            return None

    def send_email_notification(self):
        """
        Send an email notification when the inspection status is updated.
        """
        from django.core.mail import send_mail

        subject = "Inspection Update"
        message = (
            f"Inspection for {self.register_number} has been "
            f"{'Accepted' if self.status else 'Refused'}."
        )
        email_recipient = self.inspector.email
        send_mail(subject, message, "noreply@example.com", [email_recipient])


class EstablishmentRegister(models.Model):
    """
    Represents a registration record for an establishment.

    Links an establishment to its registration details including
    issuance and expiration dates.
    """
    # ForeignKey to the Establishment that issues the license.
    establishment = models.ForeignKey(
        Establishment,
        on_delete=models.CASCADE,
        related_name="registers",
        help_text="The establishment issuing this car license registration.",
    )

    # Date when the license was issued.
    issuance_date = models.DateField(
        help_text="The date when the car license was issued."
    )

    # Date when the license will expire.
    expiration_date = models.DateField(
        help_text="The date when the car license expires."
    )

    # Timestamps for record tracking
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the registration record was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the registration record was last updated.",
    )

    def __str__(self):
        return f"{self.establishment.establishment_name} - سجل {self.id}"

    @property
    def licences(self):
        """Returns all licences associated with this registration."""
        return self.licences.all()

    class Meta:
        verbose_name = "Establishment Register"
        verbose_name_plural = "Establishment Registers"
        ordering = ["-issuance_date"]


class EstablishmentLicence(models.Model):
    """
    Represents a licence record linked to a particular establishment registration.
    
    Contains details about the licence including its number, validity dates,
    and associated categories.
    """
    # The primary key for the licence (auto-incremented)
    number = models.AutoField(
        primary_key=True,
        help_text="Auto-incrementing primary key representing the licence number.",
    )

    # Link to the registration record
    register = models.ForeignKey(
        EstablishmentRegister,
        on_delete=models.CASCADE,
        related_name="licences",
        help_text="Reference to the registration record associated with this licence.",
    )

    # Dates for licence creation and expiration
    creation_date = models.DateField(help_text="The date when the licence was created.")
    expiration_date = models.DateField(help_text="The date when the licence expires.")

    # Category and activity relationships
    main_category = models.ForeignKey(
        MainCategory,
        on_delete=models.CASCADE,
        help_text="Reference to the main category associated with this licence.",
    )
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        help_text="Reference to the activity associated with this licence.",
    )
    sub_category = models.ForeignKey(
        SubCategory,
        on_delete=models.CASCADE,
        help_text="Reference to the sub category associated with this licence.",
    )

    # Timestamps for record tracking
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Timestamp when the licence record was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="Timestamp when the licence record was last updated."
    )

    def __str__(self):
        return f"{self.register.establishment.establishment_name} - رخصة {self.number}"

    @property
    def establishment(self):
        """Returns the establishment associated with this licence."""
        return self.register.establishment

    def get_establishment(self):
        """
        Alternative method to retrieve the establishment associated with this licence.
        
        Returns:
            The registration record or an empty list if not found.
        """
        registration = self.register
        if registration:
            print(registration.establishment.id)
            return registration
        return []

    class Meta:
        verbose_name = "Establishment Licence"
        verbose_name_plural = "Establishment Licences"
        ordering = ["-creation_date"]


class InspectionAssignment(models.Model):
    """
    Model for assigning inspection tasks to users (inspectors).
    
    Links an establishment that needs inspection to the assigned inspector
    and tracks the status of the assignment.
    """
    STATUS_CHOICES = (
        ("pending", "أنتظار"),
        ("accepted", "مقبولة"),
        ("in_progress", "قيد المتابعة"),
        ("completed", "مكتملة"),
        ("cancelled", "ملغاة"),
    )

    inspector = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="inspection_assignments",
        verbose_name="Inspector",
    )
    establishment = models.ForeignKey(
        Establishment,
        on_delete=models.CASCADE,
        related_name="inspection_assignments",
        verbose_name="Establishment",
    )
    assigned_at = models.DateTimeField(auto_now_add=True, verbose_name="Assigned At")
    due_date = models.DateTimeField(null=True, blank=True, verbose_name="Due Date")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name="Assignment Status",
    )
    notes = models.TextField(null=True, blank=True, verbose_name="Assignment Notes")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        verbose_name = "Inspection Assignment"
        verbose_name_plural = "Inspection Assignments"
        ordering = ["-assigned_at"]

    def __str__(self):
        return (
            f"Assignment for {self.establishment} to {self.inspector.username} "
            f"({self.get_status_display()})"
        )
