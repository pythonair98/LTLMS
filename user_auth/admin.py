from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django import forms


class CustomUserAdmin(UserAdmin):
    # Define the fields to display in the list view
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
    )
    # Add search functionality
    search_fields = ("username", "email", "first_name", "last_name")
    # Add filters in the sidebar
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")

    # Custom form layout for the edit view
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal Info"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important Dates"), {"fields": ("last_login", "date_joined")}),
    )

    # Fields for the "Add User" page
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "password1",
                    "password2",
                    "email",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )

    # Default ordering of users
    ordering = ("username",)


from .models import Occupation, Contact, Team, Profiles


@admin.register(Occupation)
class OccupationAdmin(admin.ModelAdmin):
    """
    Admin customization for the Occupation model.
    - Displays all occupation details in the admin panel.
    - Searchable by Arabic and English names.
    - List filter on power levels.
    - Read-only fields for non-editable data.
    """

    list_display = ("id", "ar_name", "en_name", "power")
    search_fields = ("ar_name", "en_name")
    list_filter = ("power",)
    ordering = ("power",)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """
    Admin customization for the Contact model.
    - Displays user details including names, phone, and email.
    - Adds search functionality for names, phone numbers, and emails.
    - Read-only display for full Arabic name.
    - Includes inline editing for a better user experience.
    """

    list_display = (
        "id",
        "ar_name",
        "en_name",
        "phone_number",
        "email",
        "full_arabic_name",
    )
    search_fields = ("ar_name", "en_name", "phone_number", "email")
    list_filter = ("ar_name", "en_name")
    readonly_fields = ("full_arabic_name",)

    def full_arabic_name(self, obj):
        """Returns the full Arabic name in a readable format."""
        return obj.ar_full_name

    full_arabic_name.short_description = "Full Arabic Name"


class ProfilesForm(forms.ModelForm):
    """Custom form to show only unlinked Contacts in the Profiles admin."""

    class Meta:
        model = Profiles
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Exclude Contacts that are already linked to a Profile
        self.fields["contact"].queryset = Contact.objects.filter(profiles__isnull=True)


@admin.register(Profiles)
class ProfilesAdmin(admin.ModelAdmin):
    """
    Custom admin panel for managing user profiles.
    - Displays key user information.
    - Allows inline editing of Contact details.
    - Includes search, filtering, and image preview.
    """

    form = ProfilesForm
    list_display = ("user", "occupation", "contact", "team", "profile_image_preview")
    search_fields = ("user__username", "team__ar_name", "occupation__en_name")
    list_filter = ("occupation", "team", "user__is_active")
    fieldsets = (
        (None, {"fields": ("user", "occupation", "contact", "team")}),
        ("Additional Info", {"fields": ("created_at", "token", "profile_image")}),
    )
    readonly_fields = ("created_at", "profile_image_preview")

    def profile_image_preview(self, obj):
        """Displays a small preview of the profile image in the admin panel."""
        if obj.profile_image:
            return mark_safe(
                f'<img src="{obj.profile_image.url}" width="100" height="100" />'
            )
        return "No Image"

    profile_image_preview.short_description = "Profile Image Preview"


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """
    Admin customization for the Team model.
    - Displays team details such as Arabic & English names and creation date.
    - Searchable by Arabic and English names.
    - Filters by creation date.
    - Displays team members dynamically.
    """

    list_display = ("id", "ar_name", "en_name", "date_created", "get_team_members")
    search_fields = ("ar_name", "en_name")
    list_filter = ("date_created",)
    ordering = ("-date_created",)

    def team_members_count(self, obj):
        """Returns the count of team members."""
        return obj.get_team_members().count()

    team_members_count.short_description = "Team Members Count"


# Unregister the default User admin
admin.site.unregister(User)
# Register the customized User admin
admin.site.register(User, CustomUserAdmin)
