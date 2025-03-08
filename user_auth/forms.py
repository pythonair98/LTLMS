from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from user_auth.models import Profiles, Contact, Team


class CustomUserCreationForm(UserCreationForm):
    """
    Extends Django's built-in UserCreationForm to include email.
    """

    email = forms.EmailField(
        required=True, help_text="Required. Enter a valid email address."
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class ProfileForm(forms.ModelForm):
    """
    Form for the Profiles model.
    Excludes the user and contact fields because those will be set in the view.
    """

    # def save(self, commit=...):
    #     # CONVERT IMAGE NAME TO MD5 HASH
    #     import hashlib
    #
    #     self.data["profile_image"] = hashlib.md5(
    #         self.data["profile_image"].read()
    #     ).hexdigest()
    #     return super(ProfileForm, self).save(commit)

    class Meta:
        model = Profiles
        fields = ("occupation", "team")
        # You can add widgets or help_text here if desired


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ["ar_name", "en_name"]

    ar_name = forms.CharField(
        max_length=200, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    en_name = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )


class ContactForm(forms.ModelForm):
    """
    Form for the Contact model.
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
        # Include any additional contact-related fields here


class UserFullForm(forms.ModelForm):
    """
    Form for creating or updating a Django User with all relevant fields.

    Includes password input with confirmation. On save, the password is hashed.
    """

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
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_staff": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_superuser": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
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
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        # Save the User instance without the raw password.
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserEditForm(forms.ModelForm):
    """
    Form for creating or updating a Django User with all relevant fields.

    Includes password input with confirmation. On save, the password is hashed.
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
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_staff": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_superuser": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "username": "Username",
            "first_name": "First Name",
            "last_name": "Last Name",
            "email": "Email Address",
            "is_active": "Active",
            "is_staff": "Staff",
            "is_superuser": "Superuser",
        }
