from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django import forms
from .models import Occupation, Contact, Team, Profiles


class CustomUserAdmin(UserAdmin):
    """
    Customized admin interface for User model with enhanced display and editing capabilities.
    Extends Django's built-in UserAdmin to provide additional functionality.
    """
    list_display = (
        "username", 
        "email",
        "first_name", 
        "last_name",
        "is_staff",
        "is_active"
    )
    search_fields = ("username", "email", "first_name", "last_name")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    ordering = ("username",)

    # Layout for editing existing users
    fieldsets = (
        (None, {
            "fields": ("username", "password")
        }),
        (_("Personal Info"), {
            "fields": ("first_name", "last_name", "email")
        }),
        (_("Permissions"), {
            "fields": (
                "is_active",
                "is_staff", 
                "is_superuser",
                "groups",
                "user_permissions"
            )
        }),
        (_("Important Dates"), {
            "fields": ("last_login", "date_joined")
        })
    )

    # Layout for adding new users
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "username",
                "password1",
                "password2",
                "email",
                "is_active",
                "is_staff"
            )
        }),
    )


@admin.register(Occupation)
class OccupationAdmin(admin.ModelAdmin):
    """Admin interface for managing occupations/roles."""
    list_display = ("id", "ar_name", "en_name", "power")
    search_fields = ("ar_name", "en_name")
    list_filter = ("power",)
    ordering = ("power",)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """Admin interface for managing contact information."""
    list_display = (
        "id",
        "ar_name", 
        "en_name",
        "phone_number",
        "email",
        "full_arabic_name"
    )
    search_fields = ("ar_name", "en_name", "phone_number", "email")
    list_filter = ("ar_name", "en_name")
    readonly_fields = ("full_arabic_name",)

    def full_arabic_name(self, obj):
        """Display concatenated Arabic name."""
        return obj.ar_full_name
    full_arabic_name.short_description = "Full Arabic Name"


class ProfilesForm(forms.ModelForm):
    """Custom form for Profile admin that filters available contacts."""
    class Meta:
        model = Profiles
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Show only unassigned contacts in dropdown
        self.fields["contact"].queryset = Contact.objects.filter(profiles__isnull=True)


@admin.register(Profiles)
class ProfilesAdmin(admin.ModelAdmin):
    """Admin interface for managing user profiles with enhanced features."""
    form = ProfilesForm
    
    list_display = (
        "user",
        "occupation", 
        "contact",
        "team",
        "profile_image_preview"
    )
    search_fields = (
        "user__username",
        "team__ar_name",
        "occupation__en_name"
    )
    list_filter = ("occupation", "team", "user__is_active")
    
    fieldsets = (
        (None, {
            "fields": ("user", "occupation", "contact", "team")
        }),
        ("Additional Info", {
            "fields": ("created_at", "token", "profile_image")
        })
    )
    readonly_fields = ("created_at", "profile_image_preview")

    def profile_image_preview(self, obj):
        """Generate HTML preview of profile image."""
        if obj.profile_image:
            return mark_safe(
                f'<img src="{obj.profile_image.url}" width="100" height="100" />'
            )
        return "No Image"
    profile_image_preview.short_description = "Profile Image Preview"


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """Admin interface for managing teams."""
    list_display = (
        "id",
        "ar_name",
        "en_name", 
        "date_created",
        "get_team_members"
    )
    search_fields = ("ar_name", "en_name")
    list_filter = ("date_created",)
    ordering = ("-date_created",)


# Replace default User admin with custom version
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
