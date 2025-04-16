from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
import logging

from user_auth.models import Profiles, Contact, Team

# Configure module-level logger
logger = logging.getLogger(__name__)


class CustomUserCreationForm(UserCreationForm):
    """
    Extends Django's built-in UserCreationForm to include email field.
    This form is used for creating new user accounts with email validation.
    """

    # Add required email field with help text
    email = forms.EmailField(
        required=True, 
        help_text="Required. Enter a valid email address."
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        """Override save to log user creation."""
        user = super().save(commit=False)
        logger.info(f"Creating new user account with username: {user.username}")
        if commit:
            user.save()
            logger.info(f"User account created successfully: {user.username}")
        return user


class ProfileForm(forms.ModelForm):
    """
    Form for managing user profiles.
    Handles occupation and team assignment for users.
    The user and contact fields are excluded as they are set in the view.
    """

    # Commented out code for future image hash implementation
    # def save(self, commit=...):
    #     # Convert image name to MD5 hash for unique filenames
    #     import hashlib
    #     self.data["profile_image"] = hashlib.md5(
    #         self.data["profile_image"].read()
    #     ).hexdigest()
    #     return super(ProfileForm, self).save(commit)

    class Meta:
        model = Profiles
        fields = ("occupation", "team")

    def save(self, commit=True):
        """Override save to log profile creation/updates."""
        profile = super().save(commit=False)
        action = "Creating" if profile.pk is None else "Updating"
        logger.info(f"{action} profile for user: {getattr(profile, 'user', 'New User')}")
        
        if commit:
            profile.save()
            logger.info(f"Profile {action.lower()} successful")
        return profile


class TeamForm(forms.ModelForm):
    """
    Form for creating and editing teams.
    Handles both Arabic and English team names.
    """
    class Meta:
        model = Team
        fields = ["ar_name", "en_name"]

    # Arabic name field (required)
    ar_name = forms.CharField(
        max_length=200, 
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    
    # English name field (optional)
    en_name = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    def save(self, commit=True):
        """Override save to log team creation/updates."""
        team = super().save(commit=False)
        action = "Creating" if team.pk is None else "Updating"
        logger.info(f"{action} team: {team.ar_name} / {team.en_name}")
        
        if commit:
            team.save()
            logger.info(f"Team {action.lower()} successful")
        return team


class ContactForm(forms.ModelForm):
    """
    Form for managing user contact information.
    Includes fields for names in both Arabic and English, phone and email.
    """

    class Meta:
        model = Contact
        fields = (
            "ar_name",
            "en_name",
            "ar_fname",
            "ar_lname", 
            "en_fname",
            "en_lname",
            "phone_number",
            "email",
        )

    def save(self, commit=True):
        """Override save to log contact creation/updates."""
        contact = super().save(commit=False)
        action = "Creating" if contact.pk is None else "Updating"
        logger.info(f"{action} contact information for: {contact.en_name or contact.ar_name}")
        
        if commit:
            contact.save()
            logger.info(f"Contact information {action.lower()} successful")
        return contact


class UserFullForm(forms.ModelForm):
    """
    Comprehensive form for creating/updating Django User instances.
    Includes password validation and all user permission fields.
    """

    # Password fields with confirmation
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label="Password",
        required=True,
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label="Confirm Password", 
        required=True,
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name", 
            "last_name",
            "email",
            "password",
            "confirm_password",
            "is_active",
            "is_staff", 
            "is_superuser",
        ]
        
        # Define widgets with Bootstrap classes
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_staff": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_superuser": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        
        # Custom field labels
        labels = {
            "username": "Username",
            "first_name": "First Name", 
            "last_name": "Last Name",
            "email": "Email Address",
            "is_active": "Active",
            "is_staff": "Staff",
            "is_superuser": "Superuser",
        }

    def clean(self):
        """
        Validate that password and confirm_password match.
        """
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            logger.warning(f"Password mismatch during user creation/update for username: {cleaned_data.get('username')}")
            self.add_error("confirm_password", "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        """
        Override save to properly hash the password before saving.
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        
        action = "Creating" if user.pk is None else "Updating"
        logger.info(f"{action} full user account: {user.username}")
        
        if commit:
            user.save()
            logger.info(f"User {action.lower()} successful with permissions - Staff: {user.is_staff}, Superuser: {user.is_superuser}")
        return user


class UserEditForm(forms.ModelForm):
    """
    Form for editing existing users without password modification.
    Includes all user fields except password-related ones.
    """

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name", 
            "email",
            "is_active",
            "is_staff",
            "is_superuser",
        ]
        
        # Define widgets with Bootstrap classes
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_staff": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_superuser": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        """
        Initialize form and disable username field to prevent changes.
        """
        super().__init__(*args, **kwargs)
        self.fields["username"].disabled = True  # Prevent username modifications
        logger.debug(f"Initializing edit form for user: {kwargs.get('instance')}")

    def save(self, commit=True):
        """Override save to log user updates."""
        user = super().save(commit=False)
        logger.info(f"Updating user account: {user.username}")
        
        if commit:
            user.save()
            logger.info(f"User update successful - Active: {user.is_active}, Staff: {user.is_staff}, Superuser: {user.is_superuser}")
        return user
