from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from user_auth.models import Profiles, Contact, Team


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
            self.add_error("confirm_password", "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        """
        Override save to properly hash the password before saving.
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
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
