import os

from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.utils.timezone import now


class OccupationType(models.TextChoices):
    """
    Defines different occupation roles available for users.
    Each occupation has an English identifier and an Arabic description.
    """

    HEAD_OF_LICENSE = "head_of_license", "مدير دائرة التراخيص"
    HEAD_OF_INSPECTION = "head_of_inspection", "رئيس قسم التفتيش"
    HEAD_OF_INSPECTION_TEAM = "head_of_inspection_team", "مسؤول فريق التفتيش"
    INSPECTOR = "inspector", "مفتش (معاين)"


class Occupation(models.Model):
    """
    Represents different occupations within the system.

    Fields:
    - ar_name: Arabic name of the occupation (unique).
    - en_name: English name of the occupation (unique).
    - power: A unique integer representing the power level of the occupation.
    """

    id = models.AutoField(primary_key=True)
    ar_name = models.CharField(max_length=250, unique=True)
    en_name = models.CharField(max_length=250, unique=True)
    power = models.IntegerField(unique=True)

    def __str__(self):
        """Returns the English name of the occupation."""
        return self.en_name


class Contact(models.Model):
    """
    Stores user contact details including names, phone number, and email.

    Fields:
    - ar_name: Full name in Arabic.
    - en_name: Full name in English (optional).
    - ar_fname, ar_lname: First and last names in Arabic.
    - en_fname, en_lname: First and last names in English (optional).
    - phone_number: The user's phone number.
    - email: Unique email address for the user.
    """

    id = models.AutoField(primary_key=True)
    ar_name = models.CharField(max_length=200)
    en_name = models.CharField(max_length=200, null=True, blank=True)
    ar_fname = models.CharField(max_length=100, null=True, blank=True)
    ar_lname = models.CharField(max_length=100, null=True, blank=True)
    en_fname = models.CharField(max_length=100, null=True, blank=True)
    en_lname = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(max_length=255, unique=True)

    def __str__(self):
        """Returns the English name if available, otherwise the Arabic name."""
        return self.en_name if self.en_name else self.ar_name

    @property
    def ar_full_name(self):
        """Returns the full Arabic name of the user."""
        return (
            f"{self.ar_fname} {self.ar_lname}"
            if self.ar_fname and self.ar_lname
            else self.ar_name
        )


class Team(models.Model):
    """
    Represents teams within the organization.

    Fields:
    - ar_name: Arabic name of the team (unique).
    - en_name: English name of the team (optional).
    - date_created: Timestamp for when the team was created.
    - leader: A foreign key linking to the User model to represent the team leader.
    """

    id = models.AutoField(primary_key=True)
    ar_name = models.CharField(max_length=200, unique=True)
    en_name = models.CharField(max_length=200, null=True, blank=True)
    date_created = models.DateTimeField(default=now)

    def __str__(self):
        """Returns the English name if available, otherwise the Arabic name."""
        return self.en_name if self.en_name else self.ar_name

    def get_team_members(self):
        """
        Retrieves all users in this team who have an occupation_id of 4.
        This assumes the occupation_id 4 represents a specific role within the team.
        """
        return Profiles.objects.filter(team_id=self.id).count()


class Profiles(models.Model):
    """
    Custom user model extending Django's AbstractUser.

    Fields:
    - contact: One-to-One relationship with Contact model.
    - occupation: Foreign key to the Occupation model.
    - is_active: Determines if the user account is active.
    - team: Foreign key to the Team model (nullable).
    - created_at: Stores when the user was created.
    - token: Stores authentication or session token.
    - profile_image: Stores profile image filename.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    contact = models.OneToOneField(
        Contact, on_delete=models.CASCADE, null=True, blank=True
    )
    occupation = models.ForeignKey(Occupation, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=now, editable=False)
    token = models.CharField(max_length=255, null=True, blank=True)
    profile_image = models.ImageField(
        upload_to="static/files/profile_images/",
        null=True,
        blank=True,
        default="files/profile_images/default.jpg",  # Optional: specify a default image file
    )

    @property
    def get_user_obj(self):
        return self.user

    def activate(self):
        """Activate the user account."""
        self.user.is_active = True
        self.save()

    def deactivate(self):
        """Deactivate the user account."""
        self.user.is_active = False
        self.save()

    def get_token(self):
        """Retrieve the user's token."""
        return self.token

    @property
    def profile_image_path(self):
        """Returns the full path to the user's profile image."""
        if self.profile_image and hasattr(self.profile_image, "url"):
            return self.profile_image.url
        return "/static/files/profile_images/1.jpg"

    @property
    def occupation_ar_name(self):
        """Returns the Arabic name of the user's occupation."""
        return self.occupation.ar_name

    @property
    def occupation_en_name(self):
        """Returns the English name of the user's occupation."""
        return self.occupation.en_name

    @property
    def power(self) -> int:
        """Returns the power level of the user's occupation."""
        return self.occupation.power

    @property
    def is_admin(self):
        """Checks if the user is an administrator (power level 1)."""
        return self.occupation.power == 1

    @property
    def get_username(self):
        """Returns the user's username."""
        return self.user.username

    def __str__(self):
        """Returns the username."""
        return self.user.first_name

    class Meta:
        permissions = [
            ("change_task_status", "Can change the status of tasks"),
            ("close_task", "Can remove a task by setting its status as closed"),
        ]
