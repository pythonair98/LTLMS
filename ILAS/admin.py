from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.contrib import admin

from .models import (
    Activity,
    Establishment,
    EstablishmentLicence,
    EstablishmentRegister,
    EstablishmentRole,
    Inspection,
    InspectionAssignment,
    MainCategory,
    SubCategory,
)


def make_published(modeladmin, request, queryset):
    """
    Admin action to mark selected records as 'published'.
    
    Args:
        modeladmin: The ModelAdmin instance
        request: The current request
        queryset: The QuerySet containing the selected objects
    """
    updated_count = queryset.update(sub_category="published")
    modeladmin.message_user(
        request, f"{updated_count} records were successfully marked as published."
    )


make_published.short_description = "Mark selected items as published"


class EstablishmentAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Establishment model.
    Customizes display, filtering, search, and form layout.
    """
    actions = [make_published]
    
    list_display = (
        "rifd",
        "establishment_name",
        "main_category",
        "sub_category",
        "created_at",
    )
    
    search_fields = (
        "rifd",
        "establishment_name",
        "email",
        "owner_name",
    )
    
    list_filter = (
        "main_category",
        "activity",
        "created_at",
    )
    
    fields = (
        (
            "rifd",
            "establishment_name",
        ),
        ("main_category", "sub_category", "activity"),
        ("owner_name", "owner_number", "director_name", "director_number"),
        ("representative_name", "representative_number", "box_O_P"),
        ("email", "phone_number"),
        ("municipality_name", "region_number", "street_number", "street_name"),
        ("building_number", "block_number", "block_name"),
        "created_at",
    )
    
    add_fieldsets = (
        (
            None,
            {
                "fields": (
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
                ),
            },
        ),
    )
    
    ordering = ("-created_at",)
    list_display_links = ("rifd", "establishment_name")
    readonly_fields = ("created_at",)
    
    def activity_name_display(self, obj):
        """Custom display for the activity field with proper label."""
        return obj.activity.label
    
    activity_name_display.short_description = _("Activity Type")


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    """Admin configuration for the Activity model."""
    list_display = ("id", "ar_name", "en_name")
    search_fields = ("ar_name", "en_name")


@admin.register(MainCategory)
class MainCategoryAdmin(admin.ModelAdmin):
    """Admin configuration for the MainCategory model."""
    list_display = ("id", "ar_name", "en_name")
    search_fields = ("ar_name", "en_name")


@admin.register(EstablishmentRole)
class EstablishmentRoleAdmin(admin.ModelAdmin):
    """Admin configuration for the EstablishmentRole model."""
    list_display = ("id", "ar_name", "en_name")
    search_fields = ("ar_name", "en_name")


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    """Admin configuration for the SubCategory model."""
    list_display = ("id", "ar_name", "en_name")
    search_fields = ("ar_name", "en_name")


@admin.register(EstablishmentRegister)
class EstablishmentRegisterAdmin(admin.ModelAdmin):
    """
    Admin configuration for the EstablishmentRegister model.
    Organizes fields into logical groups and customizes the display.
    """
    list_display = (
        "establishment_id",
        "establishment",
        "issuance_date",
        "expiration_date",
        "created_at",
        "updated_at",
    )
    
    list_filter = ("issuance_date", "expiration_date", "created_at")
    search_fields = ("establishment__rifd", "establishment__owner_name")
    ordering = ("-issuance_date",)
    
    fieldsets = (
        (None, {"fields": ("establishment",)}),
        ("Dates", {"fields": ("issuance_date", "expiration_date")}),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )
    
    readonly_fields = ("created_at", "updated_at")


@admin.register(EstablishmentLicence)
class EstablishmentLicenceAdmin(admin.ModelAdmin):
    """
    Admin configuration for the EstablishmentLicence model.
    Includes custom method to display related establishment.
    """
    list_display = (
        "number",
        "register",
        "establishment",
        "creation_date",
        "expiration_date",
        "main_category",
        "activity",
        "sub_category",
        "created_at",
        "updated_at",
    )
    
    list_filter = (
        "creation_date",
        "expiration_date",
        "main_category",
        "activity",
        "sub_category",
        "created_at",
    )
    
    search_fields = (
        "register__establishment__rifd",
        "register__establishment__owner_name",
        "main_category__ar_name",
        "activity__ar_name",
        "sub_category__ar_name",
    )
    
    ordering = ("-creation_date",)
    
    fieldsets = (
        (None, {"fields": ("register",)}),
        ("Licence Dates", {"fields": ("creation_date", "expiration_date")}),
        (
            "Categories and Activity",
            {"fields": ("main_category", "activity", "sub_category")},
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
    
    readonly_fields = ("created_at", "updated_at")
    
    def establishment(self, obj):
        """Get the establishment associated with this licence via registration."""
        return obj.register.establishment
    
    establishment.short_description = "Establishment"


# Register the Establishment model with the custom admin configuration
admin.site.register(Establishment, EstablishmentAdmin)


@admin.register(InspectionAssignment)
class InspectionAssignmentAdmin(admin.ModelAdmin):
    """
    Admin configuration for the InspectionAssignment model.
    Organizes fields into logical groups for better usability.
    """
    list_display = (
        "establishment",
        "inspector",
        "status",
        "assigned_at",
        "due_date",
    )
    
    list_filter = (
        "status",
        "assigned_at",
        "due_date",
        "inspector",
    )
    
    search_fields = (
        "establishment__representative_name",
        "inspector__username",
        "inspector__first_name",
        "inspector__last_name",
    )
    
    ordering = ("-assigned_at",)
    
    fieldsets = (
        (None, {"fields": ("establishment", "inspector", "status")}),
        (
            "Dates & Times",
            {
                "fields": ("assigned_at", "due_date", "updated_at"),
                "classes": ("collapse",),
            },
        ),
        (
            "Additional Information",
            {
                "fields": ("notes",),
            },
        ),
    )
    
    readonly_fields = ("assigned_at", "updated_at")


@admin.register(Inspection)
class InspectionAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Inspection model.
    Includes custom methods for image previews and archiving functionality.
    """
    list_display = (
        "register_number",
        "inspector",
        "created_at",
        "notes",
        "status",
        "is_archived",
        "preview_register_photo",
        "preview_license_photo",
        "preview_establishment_photo",
        "preview_cars_building_photo",
    )
    
    list_filter = ("status", "inspector", "created_at", "is_archived")
    search_fields = ("register_number", "notes")
    ordering = ("-created_at",)
    actions = ["archive_selected"]
    readonly_fields = ("created_at", "archived_at")
    
    fieldsets = (
        (
            "Inspection Details",
            {
                "fields": ("register_number", "inspector", "notes", "status"),
            },
        ),
        (
            "Location",
            {
                "fields": ("latitude", "longitude"),
            },
        ),
        (
            "Media Files",
            {
                "fields": (
                    "register_photo",
                    "license_photo",
                    "establishment_photo",
                    "cars_building_photo",
                ),
            },
        ),
        (
            "Archiving",
            {
                "fields": ("is_archived", "archived_at"),
            },
        ),
    )
    
    def _image_preview(self, image_url):
        """Helper method to generate HTML for image previews."""
        if image_url:
            return format_html(
                '<img src="/static{}" width="80" style="border-radius: 5px;" />',
                image_url,
            )
        return "No Image"
    
    def preview_register_photo(self, obj):
        """Generate preview for register photo."""
        return self._image_preview(obj.register_photo.url)
    
    def preview_license_photo(self, obj):
        """Generate preview for license photo."""
        return self._image_preview(obj.license_photo.url)
    
    def preview_establishment_photo(self, obj):
        """Generate preview for establishment photo."""
        return self._image_preview(obj.establishment_photo.url)
    
    def preview_cars_building_photo(self, obj):
        """Generate preview for cars building photo."""
        return self._image_preview(obj.cars_building_photo.url)
    
    preview_register_photo.short_description = "Register Photo"
    preview_license_photo.short_description = "License Photo"
    preview_establishment_photo.short_description = "Establishment Photo"
    preview_cars_building_photo.short_description = "Cars Building Photo"
    
    def archive_selected(self, request, queryset):
        """Admin action to archive selected inspections."""
        queryset.update(is_archived=True)
        self.message_user(request, "Selected inspections have been archived.")
    
    archive_selected.short_description = "Archive selected inspections"
