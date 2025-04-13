import os
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.utils.timezone import now


class OccupationType(models.TextChoices):
    """Defines different occupation roles available for users."""
    HEAD_OF_LICENSE = "head_of_license", "مدير دائرة التراخيص"
    HEAD_OF_INSPECTION = "head_of_inspection", "رئيس قسم التفتيش" 
    HEAD_OF_INSPECTION_TEAM = "head_of_inspection_team", "مسؤول فريق التفتيش"
    INSPECTOR = "inspector", "مفتش (معاين)"


class Occupation(models.Model):
    """Represents different occupations within the system."""
    id = models.AutoField(primary_key=True)
    ar_name = models.CharField("Arabic Name", max_length=250, unique=True)
    en_name = models.CharField("English Name", max_length=250, unique=True)
    power = models.PositiveIntegerField("Power Level", unique=True)

    def __str__(self):
        return self.en_name

    class Meta:
        ordering = ['power']
        verbose_name = 'Occupation'
        verbose_name_plural = 'Occupations'


class Contact(models.Model):
    """Stores user contact details."""
    id = models.AutoField(primary_key=True)
    ar_name = models.CharField("Arabic Full Name", max_length=200)
    en_name = models.CharField("English Full Name", max_length=200, null=True, blank=True)
    ar_fname = models.CharField("Arabic First Name", max_length=100, null=True, blank=True)
    ar_lname = models.CharField("Arabic Last Name", max_length=100, null=True, blank=True)
    en_fname = models.CharField("English First Name", max_length=100, null=True, blank=True)
    en_lname = models.CharField("English Last Name", max_length=100, null=True, blank=True)
    phone_number = models.CharField("Phone Number", max_length=20)
    email = models.EmailField("Email Address", max_length=255, unique=True)

    def __str__(self):
        return self.en_name if self.en_name else self.ar_name

    @property
    def ar_full_name(self):
        """Returns the full Arabic name."""
        if self.ar_fname and self.ar_lname:
            return f"{self.ar_fname} {self.ar_lname}"
        return self.ar_name

    class Meta:
        ordering = ['ar_name']
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'


class Team(models.Model):
    """Represents teams within the organization."""
    id = models.AutoField(primary_key=True)
    ar_name = models.CharField("Arabic Name", max_length=200, unique=True)
    en_name = models.CharField("English Name", max_length=200, null=True, blank=True)
    date_created = models.DateTimeField("Creation Date", default=now)

    def __str__(self):
        return self.en_name if self.en_name else self.ar_name

    def get_team_members(self):
        """Returns count of team members."""
        return self.profiles_set.count()

    class Meta:
        ordering = ['-date_created']
        verbose_name = 'Team'
        verbose_name_plural = 'Teams'


class Profiles(models.Model):
    """Extended user profile model."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    contact = models.OneToOneField(Contact, on_delete=models.CASCADE, null=True, blank=True)
    occupation = models.ForeignKey(Occupation, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField("Creation Date", default=now, editable=False)
    token = models.CharField("Auth Token", max_length=255, null=True, blank=True)
    profile_image = models.ImageField(
        "Profile Image",
        upload_to="static/files/profile_images/",
        null=True,
        blank=True,
        default="files/profile_images/default.jpg"
    )

    @property
    def get_user_obj(self):
        """Returns associated User object."""
        return self.user

    def activate(self):
        """Activates the user account."""
        self.user.is_active = True
        self.save()

    def deactivate(self):
        """Deactivates the user account."""
        self.user.is_active = False
        self.save()

    def get_token(self):
        """Returns authentication token."""
        return self.token

    @property
    def profile_image_path(self):
        """Returns profile image URL."""
        if self.profile_image and hasattr(self.profile_image, "url"):
            return self.profile_image.url
        return "/static/files/profile_images/1.jpg"

    @property
    def occupation_ar_name(self):
        """Returns occupation Arabic name."""
        return self.occupation.ar_name

    @property
    def occupation_en_name(self):
        """Returns occupation English name."""
        return self.occupation.en_name

    @property
    def power(self) -> int:
        """Returns occupation power level."""
        return self.occupation.power

    @property
    def is_admin(self):
        """Checks if user is admin."""
        return self.occupation.power == 1

    @property
    def get_username(self):
        """Returns username."""
        return self.user.username

    def __str__(self):
        return self.user.first_name

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
        ordering = ['-created_at']
        permissions = [
            ("change_task_status", "Can change the status of tasks"),
            ("close_task", "Can remove a task by setting its status as closed"),
        ]
