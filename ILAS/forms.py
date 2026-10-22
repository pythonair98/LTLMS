"""
Forms for adding, editing, and viewing establishments and inspections.

This module contains forms for managing establishments, inspections, licenses, 
and related data. Each form handles validation and provides appropriate 
widgets for data entry.
"""

import logging
from django import forms
from django.core.exceptions import ValidationError
from django.forms.widgets import DateInput

from .models import (
    Establishment,
    Inspection,
    Activity,
    EstablishmentRegister,
    EstablishmentLicence,
    InspectionAssignment,
)
import LTLMS.settings as settings

# Configure module-level logger
logger = logging.getLogger(__name__)


class EstablishmentForm(forms.ModelForm):
    """
    Form for managing establishment details.
    
    Handles establishment information including contact details,
    location information, and activity classification.
    """

    # Establishment details
    rifd = forms.CharField(
        label="رقم RFID",
        required=True,
        help_text="أدخل رقم البطاقة التعريفية المخصص للمنشأة.",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "dir": "ltr",
                "autocomplete": "off",
                "placeholder": "مثال: RFID-123456",
            }
        ),
    )
    establishment_name = forms.CharField(
        label="الاسم التجاري للمنشأة",
        required=True,
        help_text="استخدم الاسم الظاهر في الوثائق الرسمية.",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "autocomplete": "organization",
                "placeholder": "اكتب الاسم التجاري",
            }
        ),
    )

    # Contact details
    owner_name = forms.CharField(
        label="اسم مالك المنشأة",
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "autocomplete": "name", "placeholder": "الاسم الكامل"}
        ),
    )
    owner_number = forms.CharField(
        label="رقم هاتف المالك",
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "type": "tel",
                "inputmode": "tel",
                "autocomplete": "tel",
                "placeholder": "مثال: 3XXX XXXX",
                "dir": "ltr",
            }
        ),
    )
    director_name = forms.CharField(
        label="اسم المدير التنفيذي",
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "autocomplete": "name", "placeholder": "الاسم الكامل"}
        ),
    )
    director_number = forms.CharField(
        label="رقم هاتف المدير التنفيذي",
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "type": "tel",
                "inputmode": "tel",
                "autocomplete": "tel",
                "placeholder": "مثال: 3XXX XXXX",
                "dir": "ltr",
            }
        ),
    )
    representative_name = forms.CharField(
        label="اسم مندوب المنشأة",
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "autocomplete": "name", "placeholder": "الاسم الكامل"}
        ),
    )
    representative_number = forms.CharField(
        label="رقم هاتف مندوب المنشأة",
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "type": "tel",
                "inputmode": "tel",
                "autocomplete": "tel",
                "placeholder": "مثال: 3XXX XXXX",
                "dir": "ltr",
            }
        ),
    )
    email = forms.EmailField(
        label="البريد الإلكتروني",
        required=True,
        help_text="سيُستخدم هذا العنوان للتواصل مع المنشأة.",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "type": "email",
                "inputmode": "email",
                "autocomplete": "email",
                "placeholder": "name@example.com",
                "dir": "ltr",
            }
        ),
    )
    phone_number = forms.CharField(
        label="رقم هاتف المنشأة",
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "type": "tel",
                "inputmode": "tel",
                "autocomplete": "tel",
                "placeholder": "مثال: 3XXX XXXX",
                "dir": "ltr",
            }
        ),
    )

    # Location details
    box_O_P = forms.IntegerField(
        label="صندوق البريد",
        required=True,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "inputmode": "numeric", "placeholder": "رقم صندوق البريد"}
        ),
    )
    municipality_name = forms.CharField(
        label="البلدية",
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "autocomplete": "address-level2", "placeholder": "اسم البلدية"}
        ),
    )
    region_number = forms.IntegerField(
        label="رقم المنطقة",
        required=True,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "inputmode": "numeric", "placeholder": "رقم المنطقة"}
        ),
    )
    street_number = forms.IntegerField(
        label="رقم الشارع",
        required=True,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "inputmode": "numeric", "placeholder": "رقم الشارع"}
        ),
    )
    street_name = forms.CharField(
        label="اسم الشارع",
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "autocomplete": "street-address", "placeholder": "اسم الشارع"}
        ),
    )
    block_number = forms.IntegerField(
        label="رقم الحي",
        required=True,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "inputmode": "numeric", "placeholder": "رقم الحي"}
        ),
    )
    block_name = forms.CharField(
        label="اسم الحي",
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "اسم الحي"}
        ),
    )
    building_number = forms.IntegerField(
        label="رقم المبنى",
        required=True,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "inputmode": "numeric", "placeholder": "رقم المبنى"}
        ),
    )

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
        widgets = {
            "activity": forms.Select(attrs={"class": "form-select"}),
            "main_category": forms.Select(attrs={"class": "form-select"}),
            "sub_category": forms.Select(attrs={"class": "form-select"}),
        }

    def clean_rifd(self):
        """Validates RFID uniqueness."""
        rifd = self.cleaned_data.get("rifd")
        if (
            Establishment.objects.exclude(rifd=self.instance.rifd)
            .filter(rifd=rifd)
            .exists()
        ):
            logger.warning(f"Duplicate RFID attempted: {rifd}")
            raise ValidationError("Establishment with this RFID already exists.")
        logger.debug(f"RFID validation passed: {rifd}")
        return rifd

    def clean_email(self):
        """Validates email uniqueness."""
        email = self.cleaned_data.get("email")
        if (
            Establishment.objects.exclude(rifd=self.instance.rifd)
            .filter(email=email)
            .exists()
        ):
            logger.warning(f"Duplicate email attempted: {email}")
            raise ValidationError("Establishment with this Email already exists.")
        logger.debug(f"Email validation passed: {email}")
        return email

    def get_register_number_for_form(self):
        """Returns the register number associated with this establishment."""
        try:
            register = EstablishmentRegister.objects.filter(establishment=self.instance).first()
            if register:
                return register.id
            logger.warning(f"No register found for establishment: {self.instance.id}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving register number: {str(e)}", exc_info=True)
            return None


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

    def clean(self):
        """Validate the inspection form data."""
        cleaned_data = super().clean()
        logger.info(f"Processing inspection form for register: {cleaned_data.get('register_number')}")
        return cleaned_data


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

    def clean(self):
        """Validate establishment register dates."""
        cleaned_data = super().clean()
        issuance_date = cleaned_data.get("issuance_date")
        expiration_date = cleaned_data.get("expiration_date")
        
        if issuance_date and expiration_date and issuance_date > expiration_date:
            logger.warning(f"Invalid date range: issuance {issuance_date} > expiration {expiration_date}")
            raise ValidationError("Issuance date cannot be after expiration date.")
        
        logger.info(f"Register form validated for establishment: {cleaned_data.get('establishment')}")
        return cleaned_data


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

    def clean(self):
        """Validate license dates and related fields."""
        cleaned_data = super().clean()
        creation_date = cleaned_data.get("creation_date")
        expiration_date = cleaned_data.get("expiration_date")
        
        if creation_date and expiration_date and creation_date > expiration_date:
            logger.warning(f"Invalid license date range: creation {creation_date} > expiration {expiration_date}")
            raise ValidationError("Creation date cannot be after expiration date.")
        
        logger.info(f"License form validated for register: {cleaned_data.get('register')}")
        return cleaned_data


class InspectionAssignmentForm(forms.ModelForm):
    """
    Form for assigning inspections to inspectors.
    
    Allows selection of inspector, establishment, due date, and notes.
    """
    
    class Meta:
        model = InspectionAssignment
        fields = ["inspector", "establishment", "due_date", "notes"]
        widgets = {
            "inspector": forms.Select(attrs={"class": "form-select"}),
            "establishment": forms.Select(attrs={"class": "form-select"}),
            "due_date": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"}
            ),
            "notes": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "form-control",
                    "placeholder": "أضف أي تعليمات أو معلومات تساعد المفتش...",
                }
            ),
        }
        
    def save(self, commit=True):
        """Save the assignment and log the action."""
        instance = super().save(commit=False)
        if commit:
            instance.save()
            logger.info(f"Inspection assigned to {instance.inspector} for establishment {instance.establishment}")
        return instance
