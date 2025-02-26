from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from user_auth.models import Profiles, Contact


class CustomUserCreationForm(UserCreationForm):
    """
    Extends Django's built-in UserCreationForm to include email.
    """
    email = forms.EmailField(required=True, help_text="Required. Enter a valid email address.")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

class ProfileForm(forms.ModelForm):
    """
    Form for the Profiles model.
    Excludes the user and contact fields because those will be set in the view.
    """
    def save(self, commit = ...):
        # CONVERT IMAGE NAME TO MD5 HASH
        import hashlib
        self.data['profile_image'] = hashlib.md5(self.data['profile_image'].read()).hexdigest()
        return super(ProfileForm, self).save(commit)

    class Meta:
        model = Profiles
        fields = ("occupation", "team", "profile_image")
        # You can add widgets or help_text here if desired

class ContactForm(forms.ModelForm):
    """
    Form for the Contact model.
    """
    class Meta:
        model = Contact
        fields = ("ar_name", "en_name", "ar_fname", "ar_lname", "en_fname", "en_lname", "phone_number", "email")
        # Include any additional contact-related fields here
