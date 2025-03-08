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

"""

import os

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.files.storage import FileSystemStorage

# Create a FileSystemStorage instance pointing to the static folder (or a subfolder of it)
static_storage = FileSystemStorage(location=os.path.join(settings.BASE_DIR, "static"))


class Activity(models.Model):
    """
    Model representing different types of activities.

    Fields:
    - ar_name: Arabic name of the activity (unique).
    - en_name: English name of the activity (optional).
    """

    ar_name = models.CharField(max_length=250, unique=True)
    en_name = models.CharField(max_length=250, null=True, blank=True)
    code = models.CharField(max_length=250, unique=True)

    def __str__(self):
        """Returns a formatted string representation of the activity."""
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
        """Returns a formatted string representation of the main category."""
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
        """Returns a formatted string representation of the establishment role."""
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
        """Returns a formatted string representation of the subcategory."""
        return f"{self.id}: {self.ar_name}/{self.en_name or 'N/A'}"

    class Meta:
        verbose_name = "Sub Category"
        verbose_name_plural = "Sub Categories"


class Establishment(models.Model):
    id = models.AutoField(primary_key=True)
    rifd = models.CharField(max_length=100, unique=True)
    establishment_name = models.CharField(max_length=200)
    # register_number = models.CharField(max_length=100, primary_key=True)
    # register_issuance_date = models.DateField(default=timezone.now)
    # register_expiration_date = models.DateField(default=timezone.now)
    # license_number = models.BigIntegerField()
    # license_creation_date = models.DateField(default=timezone.now)
    # license_expiration_date = models.DateField(default=timezone.now)
    # link main category and sub category to the establishment

    main_category = models.ForeignKey(
        MainCategory, on_delete=models.CASCADE, null=True, blank=True
    )
    sub_category = models.ForeignKey(
        SubCategory, on_delete=models.CASCADE, null=True, blank=True
    )
    owner_name = models.CharField(max_length=200)
    owner_number = models.CharField(max_length=50)
    director_name = models.CharField(max_length=200)
    director_number = models.CharField(max_length=50)
    representative_name = models.CharField(max_length=200)
    representative_number = models.CharField(max_length=200)
    box_O_P = models.BigIntegerField()
    email = models.EmailField(max_length=255, unique=True)
    phone_number = models.CharField(max_length=50)
    municipality_name = models.CharField(max_length=200)
    region_number = models.CharField(max_length=50)
    street_number = models.BigIntegerField()
    street_name = models.CharField(max_length=200)
    building_number = models.BigIntegerField()
    block_number = models.BigIntegerField()
    block_name = models.CharField(max_length=200)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f" {self.establishment_name}"

    def get_register(self):
        return (
            EstablishmentRegister.objects.get(establishment_id=self.id)
            if True
            else None
        )

    def get_license(self):
        return (
            EstablishmentLicence.objects.get(register_id=self.get_register().id)
            if True
            else None
        )


class ArduinoReader(models.Model):
    """
    This model stores RFID readings received from an Arduino device.

    Fields:
    - id: Auto-incremented primary key (automatically created by Django).
    - code: Stores the RFID card code, ensuring a maximum length of 15 characters.
    - date_created: Timestamp when the entry was created, automatically set to the current time.
    - queried: Boolean flag to check if the RFID entry has been processed.
    - device_id: Optional field to track which Arduino device sent the data.
    - status: Stores the processing status of the RFID data.
    - last_updated: Timestamp when the record was last modified.
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
        """
        Returns a human-readable representation of the RFID entry.
        """
        return f"RFID: {self.code} | Status: {self.status} | Queried: {self.queried}"

    class Meta:
        """
        Meta options for the ArduinoReader model.
        """

        ordering = ["-date_created"]  # Orders records with the latest first
        verbose_name = "Arduino RFID Entry"
        verbose_name_plural = "Arduino RFID Entries"


class Inspection(models.Model):
    STATUS_CHOICES = (
        (True, "Accepted"),
        (False, "Refused"),
    )

    # Inspection Details
    register_number = models.CharField(
        max_length=255, unique=True, verbose_name="Register Number"
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

    # Media fields merged from the separate model
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

    def save(self, *args, **kwargs):
        # Optional: Custom actions before saving can be added here.
        super().save(*args, **kwargs)

    def send_email_notification(self):
        """
        Send an email notification when the inspection status is updated.
        (Assumes that the inspector's email should be notified.)
        """
        from django.core.mail import send_mail

        subject = "Inspection Update"
        message = (
            f"Inspection for {self.register_number} has been "
            f"{'Accepted' if self.status else 'Refused'}."
        )
        email_recipient = self.inspector.email
        send_mail(subject, message, "noreply@example.com", [email_recipient])

    def clean(self):
        # Optional: Add any custom validation logic here.
        if self.latitude and self.longitude:
            pass


class EstablishmentRegister(models.Model):
    """
    Represents a registration record for a car license issued by an establishment.

    This model is used to store details such as a unique RFID identifier,
    the issuing establishment, and the issuance/expiration dates for the car license.

    Fields:
        rfid (CharField): A unique RFID string (max 10 characters) used to identify the registration.
        establishment (ForeignKey): A reference to the issuing Establishment. When the establishment is deleted,
                                    all its registration records will be deleted as well.
        issuance_date (DateField): The date on which the car license was issued.
        expiration_date (DateField): The date on which the car license will expire.
        created_at (DateTimeField): Timestamp indicating when this record was created.
        updated_at (DateTimeField): Timestamp indicating the last time this record was updated.

    Properties:
        licences: Returns a QuerySet of all car licences associated with this registration.
                   It assumes that there is a related model (e.g., EstablishmentLicence) with a ForeignKey
                   to this model. If you set a custom `related_name` in that model, update this property accordingly.
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

    # Automatically set the field to now when the object is first created.
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the registration record was created.",
    )

    # Automatically update the field to now every time the object is saved.
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the registration record was last updated.",
    )

    def __str__(self):
        return f"Registration {self.establishment.rifd} for {self.establishment.establishment_name}"

    @property
    def licences(self):
        """
        Returns all car licences associated with this registration.

        Note:
            This property assumes that there is a related model (e.g., EstablishmentLicence)
            that has a ForeignKey to EstablishmentRegister. If that model’s ForeignKey does not
            set a custom related_name, Django will default to using the lowercased model name
            with '_set' appended (i.e. `establishmentlicence_set`). If you have defined a custom
            related_name (e.g. 'licences'), then you should change the return statement accordingly:
                return self.licences.all()
        """
        return self.licences.all()

    class Meta:
        verbose_name = "Establishment Register"
        verbose_name_plural = "Establishment Registers"
        ordering = ["-issuance_date"]


class EstablishmentLicence(models.Model):
    """
    Represents a car licence record linked to a particular establishment registration.

    Fields:
        number (AutoField): Auto-incrementing primary key representing the licence number.
        register (ForeignKey): Reference to the associated EstablishmentRegister record.
        creation_date (DateField): The date when the licence was created.
        expiration_date (DateField): The date when the licence expires.
        main_category (ForeignKey): Reference to the MainCategory record.
        activity (ForeignKey): Reference to the Activity record.
        sub_category (ForeignKey): Reference to the SubCategory record.
        created_at (DateTimeField): Timestamp when the licence record was created.
        updated_at (DateTimeField): Timestamp when the licence record was last updated.

    Properties:
        establishment: Returns the establishment associated with this licence (via its registration).

    Methods:
        get_establishment(): An alternate method to retrieve the establishment, which prints
                             the establishment's identifier before returning it.
    """

    # The primary key for the licence (auto-incremented)
    number = models.AutoField(
        primary_key=True,
        help_text="Auto-incrementing primary key representing the licence number.",
    )

    # ForeignKey to the registration record. Using a related_name allows reverse lookups:
    # e.g., an EstablishmentRegister instance can access its licences via .licences.all()
    register = models.ForeignKey(
        EstablishmentRegister,
        on_delete=models.CASCADE,
        related_name="licences",
        help_text="Reference to the registration record associated with this licence.",
    )

    # Dates for licence creation and expiration
    creation_date = models.DateField(help_text="The date when the licence was created.")
    expiration_date = models.DateField(help_text="The date when the licence expires.")

    # ForeignKeys to category and activity models
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
        return f"Licence #{self.number} for registration {self.register.establishment.rifd}"

    @property
    def establishment(self):
        """
        Retrieves the establishment associated with this licence via its registration record.

        Returns:
            Establishment: The establishment that issued the licence.
        """
        # Because the EstablishmentRegister model has a foreign key to Establishment,
        # we can access it directly:
        return self.register.establishment

    def get_establishment(self):
        """
        An alternative method to retrieve the establishment associated with this licence.

        This method mimics the approach from the Flask model. It prints the establishment's ID
        (if available) and returns the associated registration.

        Returns:
            EstablishmentRegister: The registration record associated with the licence, from which
                                   the establishment can be accessed.
            If not found, returns an empty list.
        """
        registration = self.register  # Already a direct reference via the ForeignKey
        if registration:
            # This print statement assumes that the EstablishmentRegister model (or its related
            # Establishment) has an attribute 'id' or 'establishment_id'. Adjust as needed.
            print(registration.establishment.id)
            return registration
        return []

    class Meta:
        verbose_name = "Establishment Licence"
        verbose_name_plural = "Establishment Licences"
        ordering = ["-creation_date"]


# Replace 'yourapp' with your actual app name if needed.
# If you have an Establishment model, import it or reference it via a string.
# For example:
# from yourapp.models import Establishment
# or use 'Establishment' if using a string reference.


class InspectionAssignment(models.Model):
    """
    Model for assigning inspection tasks to users (inspectors) and linking
    an establishment that needs inspection to the assigned inspector.

    Fields:
        inspector: The user (inspector) assigned the inspection task.
        establishment: The establishment to be inspected.
        assigned_at: Timestamp when the assignment was created.
        due_date: Optional due date for completing the inspection.
        status: The current status of the assignment.
        notes: Any additional information or instructions regarding the assignment.
        updated_at: Timestamp automatically updated whenever the record is modified.
    """

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    )

    inspector = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="inspection_assignments",
        verbose_name="Inspector",
    )
    establishment = models.ForeignKey(
        "Establishment",  # Replace with your actual Establishment model if needed.
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
