from .models import (
    Establishment,
    Activity,
    MainCategory,
    EstablishmentRole,
    SubCategory,
    EstablishmentLicence,
    EstablishmentRegister, InspectionAssignment,

)

from django.utils.translation import gettext_lazy as _
from django.contrib import admin


# Custom admin action to mark selected establishments as 'published'
def make_published(modeladmin, request, queryset):
    """
    Admin action to update the 'sub_category' field of selected records to 'published'.
    Displays a success message with the number of records updated.
    """
    updated_count = queryset.update(sub_category="published")
    modeladmin.message_user(
        request, f"{updated_count} records were successfully marked as published."
    )


make_published.short_description = (
    "Mark selected items as published"  # Description displayed in the admin panel
)


class EstablishmentAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Establishment model.
    Defines the displayed fields, filtering options, search functionality, and available actions.
    """

    # Register custom admin actions
    actions = [make_published]

    # Fields displayed in the list view of the admin panel
    list_display = (
        "rifd",
        "establishment_name",
        "main_category",
        "sub_category",
        "created_at",
    )

    # Fields that can be searched in the admin panel
    search_fields = (
        "rifd",
        "establishment_name",
        "email",
        "owner_name",
    )

    # Filters for easy navigation in the admin panel
    list_filter = (
        "main_category",
        "activity",
        "created_at",
    )

    # Fields displayed in the detailed form view (edit page)
    fields = (
        ("rifd", "establishment_name",),
        ("main_category", "sub_category", "activity"),
        ("owner_name", "owner_number", "director_name", "director_number"),
        ("representative_name", "representative_number", "box_O_P"),
        ("email", "phone_number"),
        ("municipality_name", "region_number", "street_number", "street_name"),
        ("building_number", "block_number", "block_name"),
        "created_at",
    )

    # Fields displayed when adding a new establishment
    add_fieldsets = (
        (
            None,
            {
                "fields": (
                    "rifd",
                    "establishment_name",
                    # "register_number",
                    # "register_issuance_date",
                    # "register_expiration_date",
                    # "license_number",
                    # "license_creation_date",
                    # "license_expiration_date",
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

    # Ordering the list view by 'created_at' in descending order
    ordering = ("-created_at",)

    # Custom display method for activity_name with a descriptive label
    def activity_name_display(self, obj):
        """Custom display for the 'activity_name' field with a proper label."""
        return obj.activity.label

    activity_name_display.short_description = _("Activity Type")

    # Allow clicking on 'rifd' and 'establishment_name' to open the detailed view
    list_display_links = (
        "rifd",
        "establishment_name",
    )

    # Make 'created_at' a read-only field
    readonly_fields = ("created_at",)


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("id", "ar_name", "en_name")
    search_fields = ("ar_name", "en_name")


@admin.register(MainCategory)
class MainCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "ar_name", "en_name")
    search_fields = ("ar_name", "en_name")


@admin.register(EstablishmentRole)
class EstablishmentRoleAdmin(admin.ModelAdmin):
    list_display = ("id", "ar_name", "en_name")
    search_fields = ("ar_name", "en_name")


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "ar_name", "en_name")
    search_fields = ("ar_name", "en_name")


@admin.register(EstablishmentRegister)
class EstablishmentRegisterAdmin(admin.ModelAdmin):
    """
    Admin configuration for the EstablishmentRegister model.

    Customizations include:
      - **list_display**: Columns displayed in the admin list view.
      - **list_filter**: Fields to filter the list view.
      - **search_fields**: Fields available for quick search.
      - **ordering**: Default ordering for the list view.
      - **fieldsets**: Logical grouping of form fields in the detail view.
      - **readonly_fields**: Fields that are read-only in the admin form.
    """
    # Columns to display in the list view
    list_display = (
        'establishment_id',
        'establishment',
        'issuance_date',
        'expiration_date',
        'created_at',
        'updated_at'
    )

    # Allow filtering by these date fields
    list_filter = (
        'issuance_date',
        'expiration_date',
        'created_at'
    )

    # Enable search by RFID and the name of the related establishment
    search_fields = (
        'establishment__rifd',
        'establishment__owner_name'
    )

    # Order the records by issuance date (most recent first)
    ordering = ('-issuance_date',)

    # Grouping of fields on the change form for better readability
    fieldsets = (
        (None, {
            'fields': ('establishment',)
        }),
        ('Dates', {
            'fields': ('issuance_date', 'expiration_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Collapses this section by default
        }),
    )

    # Make the timestamp fields read-only to prevent manual editing
    readonly_fields = ('created_at', 'updated_at')


@admin.register(EstablishmentLicence)
class EstablishmentLicenceAdmin(admin.ModelAdmin):
    """
    Admin configuration for the EstablishmentLicence model.

    Customizations include:
      - **list_display**: Columns displayed in the admin list view, including a custom
        property for the establishment (via the registration).
      - **list_filter**: Fields to filter the list view.
      - **search_fields**: Fields available for quick search, including related model fields.
      - **ordering**: Default ordering for the list view.
      - **fieldsets**: Logical grouping of form fields in the detail view.
      - **readonly_fields**: Fields that are read-only in the admin form.
    """
    # Display columns for licence number, registration, associated establishment, dates, categories, and timestamps
    list_display = (
        'number',
        'register',
        'establishment',
        'creation_date',
        'expiration_date',
        'main_category',
        'activity',
        'sub_category',
        'created_at',
        'updated_at'
    )

    # Allow filtering by dates, categories, and creation timestamp
    list_filter = (
        'creation_date',
        'expiration_date',
        'main_category',
        'activity',
        'sub_category',
        'created_at'
    )

    # Enable search by fields of the related registration and category models
    search_fields = (
        'register__establishment__rifd',
        'register__establishment__owner_name',
        'main_category__ar_name',
        'activity__ar_name',
        'sub_category__ar_name'
    )

    # Order the records by creation date (most recent first)
    ordering = ('-creation_date',)

    # Group the fields into logical sections on the change form
    fieldsets = (
        (None, {
            'fields': ('register',)
        }),
        ('Licence Dates', {
            'fields': ('creation_date', 'expiration_date')
        }),
        ('Categories and Activity', {
            'fields': ('main_category', 'activity', 'sub_category')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    # Make the timestamp fields read-only to prevent manual editing
    readonly_fields = ('created_at', 'updated_at')

    def establishment(self, obj):
        """
        Custom method to display the Establishment related to this licence.

        This method retrieves the establishment via the associated registration record.

        Returns:
            Establishment: The establishment associated with the licence.
        """
        return obj.register.establishment

    # Set the short description for the custom column in the list display.
    establishment.short_description = 'Establishment'


# Register the Establishment model with the custom admin configuration
admin.site.register(Establishment, EstablishmentAdmin)


@admin.register(InspectionAssignment)
class InspectionAssignmentAdmin(admin.ModelAdmin):
    """
    Admin configuration for the InspectionAssignment model.

    Customizations include:
      - list_display: Columns to display in the admin list view.
      - list_filter: Sidebar filters for quick filtering.
      - search_fields: Fields to search in the admin list view.
      - ordering: Default ordering for the list view.
      - fieldsets: Grouping of fields on the detail page.
    """
    list_display = (
        'establishment',
        'inspector',
        'status',
        'assigned_at',
        'due_date',
    )

    list_filter = (
        'status',
        'assigned_at',
        'due_date',
        'inspector',
    )

    search_fields = (
        'establishment__representative_name',  # Assumes the Establishment model has a 'name' field.
        'inspector__username',
        'inspector__first_name',
        'inspector__last_name',
    )

    ordering = ('-assigned_at',)

    fieldsets = (
        (None, {
            'fields': ('establishment', 'inspector', 'status')
        }),
        ('Dates & Times', {
            'fields': ('assigned_at', 'due_date', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('notes',),
        }),
    )

    readonly_fields = ('assigned_at', 'updated_at')
