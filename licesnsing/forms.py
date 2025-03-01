"""
Forms for adding, editing, and viewing establishments and inspections.

This module contains forms for adding, editing, and viewing establishments and inspections.
The forms are used to collect and validate data from users before saving it to the database.

"""

from django import forms
from django.contrib.admin.widgets import AutocompleteSelect
from django.core.exceptions import ValidationError
from django.forms.widgets import DateInput
from django.contrib import admin
from .models import (
    Establishment,
    Inspection,
    Activity,
    EstablishmentRegister,
    EstablishmentLicence,
    InspectionMedia,
    InspectionAssignment,
)  # Importing the models used in the form
import LTLMS.settings as settings  # Importing settings to use custom date formats


class EstablishmentForm(forms.ModelForm):
    """
    Form for adding, editing, and viewing an establishment.
    It includes fields for establishment details, contact information,
    location details, and activity type.
    """

    class Meta:
        """
        Metaclass to specify the model and fields for the form.

        """

        model = Establishment  # Specifies the model associated with this form
        fields = [
            "rifd",
            "establishment_name",
            "register_issuance_date",
            "register_expiration_date",
            "license_creation_date",
            "license_expiration_date",
            "main_category",
            "sub_category",
            "owner_name",
            "owner_number",
            "director_name",
            "director_number",
            "representative_name",
            "representative_number",
            "box_O_P",
            "email",
            "phone_number",
            "municipality_name",
            "region_number",
            "street_number",
            "street_name",
            "building_number",
            "block_number",
            "block_name",
            "activity",
        ]

    def clean_rifd(self):
        """
        Validates the 'rifd' field to ensure uniqueness.
        """
        rifd = self.cleaned_data.get("rifd")
        if (
            Establishment.objects.exclude(rifd=self.instance.rifd)
            .filter(rifd=rifd)
            .exists()
        ):
            raise ValidationError("Establishment with this Rifd already exists.")
        return rifd

    def clean_email(self):
        """
        Validates the 'email' field to ensure uniqueness.
        """
        email = self.cleaned_data.get("email")
        if (
            Establishment.objects.exclude(rifd=self.instance.rifd)
            .filter(email=email)
            .exists()
        ):
            raise ValidationError("Establishment with this Email already exists.")
        return email

    # Establishment details
    rifd = forms.CharField(label="رقم RFID:", required=True)
    establishment_name = forms.CharField(
        label="اسم المنشأة/Commercial Name:", required=True
    )
    register_number = forms.CharField(
        label="رقم السجل التجاري/Commercial Reg. No:", required=True
    )
    license_number = forms.CharField(label="رقم الرخصة/License No:", required=True)

    # Date fields with date picker widgets
    register_issuance_date = forms.DateField(
        label="تاريخ إصدار السجل/Commercial Reg. Issuance Date:",
        required=True,
        input_formats=settings.DATE_INPUT_FORMATS,
        widget=DateInput(attrs={"type": "date", "class": "form-control"}),
    )
    register_expiration_date = forms.DateField(
        label="تاريخ انتهاء السجل/Commercial Reg. Expiration Date:",
        required=True,
        input_formats=settings.DATE_INPUT_FORMATS,
        widget=DateInput(attrs={"type": "date", "class": "form-control"}),
    )
    license_creation_date = forms.DateField(
        label="تاريخ إنشاء الرخصة/License Issuance Date:",
        required=True,
        input_formats=settings.DATE_INPUT_FORMATS,
        widget=DateInput(attrs={"type": "date", "class": "form-control"}),
    )
    license_expiration_date = forms.DateField(
        label="تاريخ انتهاء الرخصة/License Expiration Date:",
        required=True,
        input_formats=settings.DATE_INPUT_FORMATS,
        widget=DateInput(attrs={"type": "date", "class": "form-control"}),
    )

    # Category details
    # main_category = forms.CharField(label="التصنيف الرئيسي/Main Category:", required=True)
    # sub_category = forms.CharField(label="التصنيف الفرعي/Sub Category:", required=True)

    # Contact details
    owner_name = forms.CharField(label="مالك المنشأة/Owner:", required=True)
    owner_number = forms.CharField(label="الهاتف/Telephone:", required=True)
    director_name = forms.CharField(
        label="المدير التنفيذي للمنشأة/Executive Director:", required=True
    )
    director_number = forms.CharField(label="الهاتف/Telephone:", required=True)
    representative_name = forms.CharField(
        label="مندوب المنشأة/Representative:", required=True
    )
    representative_number = forms.CharField(label="الهاتف/Telephone:", required=True)
    email = forms.EmailField(label="البريد الإلكتروني/Email:", required=True)
    phone_number = forms.CharField(label="رقم هاتف المنشأة/Telephone:", required=True)

    # Location details
    box_O_P = forms.IntegerField(label="صندوق البريد/P.O Box:", required=True)
    municipality_name = forms.CharField(
        label="اسم البلدية/Municipality:", required=True
    )
    region_number = forms.IntegerField(label="رقم المنطقة/Region No:", required=True)
    street_number = forms.IntegerField(label="رقم الشارع/Street No:", required=True)
    street_name = forms.CharField(label="وصف الشارع/Street Name:", required=True)
    block_number = forms.IntegerField(label="رقم الحي/Block No:", required=True)
    block_name = forms.CharField(label="اسم الحي/Block Name:", required=True)
    building_number = forms.IntegerField(label="رقم المبنى/Bldg. No:", required=True)

    # Activity details
    # activity = forms.IntegerField(label="رمز النشاط/Activity Code:", required=True)
    widgets = {
        "activity": AutocompleteSelect(
            Activity._meta.get_field("id").remote_field, admin.site
        ),  # Dropdown for ForeignKey
        "main_category": forms.Select(attrs={"class": "form-control"}),
        "role": forms.Select(attrs={"class": "form-control"}),
        "sub_category": forms.Select(attrs={"class": "form-control"}),
    }


class InspectionForm(forms.ModelForm):
    """
    Form for creating or updating an Inspection.

    This form handles the main inspection details such as register number,
    notes, latitude, longitude, and inspection status.

    The inspector, created_at, is_archived, and archived_at fields are handled
    automatically and are not included in the form.
    """

    class Meta:
        model = Inspection
        fields = [
            "register_number",
            "notes",
            "latitude",
            "longitude",
            "status",
        ]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
        labels = {
            "register_number": "Register Number",
            "notes": "Inspection Notes",
            "latitude": "Latitude",
            "longitude": "Longitude",
            "status": "Inspection Status",
        }


class InspectionMediaForm(forms.ModelForm):
    """
    Form for uploading media related to an Inspection.

    This form allows the user to select a media type and upload an image.
    The 'inspection' field is excluded from the form since it is typically
    assigned in the view after the main Inspection instance is created.
    """

    class Meta:
        model = InspectionMedia
        fields = [
            "media_type",
            "image",
        ]
        labels = {
            "media_type": "Media Type",
            "image": "Upload Image",
        }


class EstablishmentRegisterForm(forms.ModelForm):
    """
    Form for creating a new EstablishmentRegister record.

    Fields:
      - rfid: Unique RFID identifier.
      - establishment: The issuing establishment.
      - issuance_date: The date the license is issued.
      - expiration_date: The date the license expires.
    """

    class Meta:
        model = EstablishmentRegister
        fields = ["establishment", "issuance_date", "expiration_date"]


class EstablishmentLicenceForm(forms.ModelForm):
    """
    Form for creating a new EstablishmentLicence record.

    Fields:
      - register: The associated EstablishmentRegister record.
      - creation_date: The date the licence is created.
      - expiration_date: The date the licence expires.
      - main_category: The main category associated with the licence.
      - activity: The activity associated with the licence.
      - sub_category: The sub category associated with the licence.
    """

    class Meta:
        model = EstablishmentLicence
        fields = [
            "register",
            "creation_date",
            "expiration_date",
            "main_category",
            "activity",
            "sub_category",
        ]


class InspectionAssignmentForm(forms.ModelForm):
    """
    Form for assigning an establishment to inspect.

    Fields:
      - inspector: The inspector (user) who will perform the inspection.
      - establishment: The establishment to be inspected.
      - due_date: The deadline for completing the inspection.
      - notes: Additional information or instructions.
    """

    class Meta:
        model = InspectionAssignment
        fields = ["inspector", "establishment", "due_date", "notes"]
        widgets = {
            # Use a datetime-local widget for due_date if you want a nicer date/time picker.
            "due_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        establishment = cleaned_data.get("establishment")
        if establishment:
            # Check if there is an existing active assignment.
            # Here, active means that the status is not 'completed' or 'cancelled'.
            if (
                InspectionAssignment.objects.filter(establishment=establishment)
                .exclude(status__in=["completed", "cancelled"])
                .exists()
            ):
                raise forms.ValidationError("تم تعيين هذه المنشأة لمفتش بالفعل.")
        return cleaned_data
