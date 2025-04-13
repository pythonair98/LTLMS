"""
Forms for adding, editing, and viewing establishments and inspections.

This module contains forms for managing establishments, inspections, licenses, 
and related data. Each form handles validation and provides appropriate 
widgets for data entry.
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
    InspectionAssignment,
)
import LTLMS.settings as settings


class EstablishmentForm(forms.ModelForm):
    """
    Form for managing establishment details.
    
    Handles establishment information including contact details,
    location information, and activity classification.
    """

    class Meta:
        model = Establishment
        ordering = ["-id"]
        fields = [
            "rifd",
            "establishment_name",
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

    # Establishment details
    rifd = forms.CharField(label="رقم RFID:", required=True)
    establishment_name = forms.CharField(
        label="اسم المنشأة/Commercial Name:", required=True
    )

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

    # Form widgets
    widgets = {
        "activity": AutocompleteSelect(
            Activity._meta.get_field("id").remote_field, admin.site
        ),
        "main_category": forms.Select(attrs={"class": "form-control"}),
        "sub_category": forms.Select(attrs={"class": "form-control"}),
    }

    def clean_rifd(self):
        """Validates RFID uniqueness."""
        rifd = self.cleaned_data.get("rifd")
        if (
            Establishment.objects.exclude(rifd=self.instance.rifd)
            .filter(rifd=rifd)
            .exists()
        ):
            raise ValidationError("Establishment with this RFID already exists.")
        return rifd

    def clean_email(self):
        """Validates email uniqueness."""
        email = self.cleaned_data.get("email")
        if (
            Establishment.objects.exclude(rifd=self.instance.rifd)
            .filter(email=email)
            .exists()
        ):
            raise ValidationError("Establishment with this Email already exists.")
        return email

    def get_register_number_for_form(self):
        """Returns the register number associated with this establishment."""
        return (
            EstablishmentRegister.objects.filter(establishment=self.instance).first().id
        )


class InspectionForm(forms.ModelForm):
    """
    Form for creating or updating inspection records.
    
    Includes fields for inspection details and photo uploads.
    """

    class Meta:
        model = Inspection
        fields = [
            "register_number",
            "notes",
            "latitude",
            "longitude",
            "status",
            "inspector",
            "register_photo",
            "license_photo",
            "establishment_photo",
            "cars_building_photo",
        ]
        widgets = {
            "register_number": forms.TextInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "latitude": forms.TextInput(attrs={"class": "form-control"}),
            "longitude": forms.TextInput(attrs={"class": "form-control"}),
            "inspector": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "register_number": "Register Number",
            "notes": "Inspection Notes",
            "latitude": "Latitude",
            "longitude": "Longitude",
            "status": "Inspection Status",
            "inspector": "Inspector",
            "register_photo": "Register Photo",
            "license_photo": "License Photo",
            "establishment_photo": "Establishment Photo",
            "cars_building_photo": "Cars Building Photo",
        }


class EstablishmentRegisterForm(forms.ModelForm):
    """
    Form for managing establishment registration details.
    """
    
    class Meta:
        model = EstablishmentRegister
        fields = ["establishment", "issuance_date", "expiration_date"]
        widgets = {
            "issuance_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "expiration_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "establishment": forms.Select(attrs={"class": "form-control"}),
        }


class EstablishmentLicenceForm(forms.ModelForm):
    """
    Form for managing establishment license information.
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
        widgets = {
            "creation_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "expiration_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "register": forms.Select(attrs={"class": "form-control"}),
            "main_category": forms.Select(attrs={"class": "form-control"}),
            "activity": forms.Select(attrs={"class": "form-control"}),
            "sub_category": forms.Select(attrs={"class": "form-control"}),
        }


class InspectionAssignmentForm(forms.ModelForm):
    """
    Form for assigning inspections to inspectors.
    
    Allows selection of inspector, establishment, due date, and notes.
    """
    
    class Meta:
        model = InspectionAssignment
        fields = ["inspector", "establishment", "due_date", "notes"]
        widgets = {
            "due_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
