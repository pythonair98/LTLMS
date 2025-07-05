from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.db import models
from django import forms

# Import models from all apps
from ILAS.models import (
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
from user_auth.models import Occupation, Contact, Team, Profiles

# Import admin configurations
from ILAS.admin import (
    ActivityAdmin,
    EstablishmentAdmin,
    EstablishmentLicenceAdmin,
    EstablishmentRegisterAdmin,
    EstablishmentRoleAdmin,
    InspectionAdmin,
    InspectionAssignmentAdmin,
    MainCategoryAdmin,
    SubCategoryAdmin,
)
from user_auth.admin import (
    OccupationAdmin,
    ContactAdmin,
    TeamAdmin,
    ProfilesAdmin,
)

# Custom Admin Site
class CustomAdminSite(AdminSite):
    # Text to put at the end of each page's <title>.
    site_title = _('LTLMS Administration')

    # Text to put in each page's <h1> (and above login form).
    site_header = _('LTLMS Administration')

    # Text to put at the top of the admin index page.
    index_title = _('Welcome to LTLMS Administration')

    # URL for the "View site" link at the top of each admin page.
    site_url = '/'

    def get_app_list(self, request):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        app_list = super().get_app_list(request)

        # Customize the order of apps
        app_ordering = {
            'reports': 1,
            'auth': 2,
            'sessions': 3,
        }

        # Sort apps based on custom ordering
        app_list.sort(key=lambda x: app_ordering.get(x['app_label'], 999))

        return app_list

# Create custom admin site instance
admin_site = CustomAdminSite(name='admin')

# Custom Admin Forms
class CustomUserAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'
        widgets = {
            'password': forms.PasswordInput(),
        }

# Custom Model Admins
class CustomUserAdmin(UserAdmin):
    form = CustomUserAdminForm
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )

class CustomGroupAdmin(GroupAdmin):
    list_display = ('name', 'get_user_count')
    search_fields = ('name',)
    ordering = ('name',)

    def get_user_count(self, obj):
        return obj.user_set.count()
    get_user_count.short_description = _('Number of Users')

class CustomLogEntryAdmin(admin.ModelAdmin):
    list_display = ('action_time', 'user', 'content_type', 'object_repr', 'action_flag')
    list_filter = ('action_flag', 'content_type')
    search_fields = ('object_repr', 'change_message')
    date_hierarchy = 'action_time'
    readonly_fields = ('action_time', 'user', 'content_type', 'object_id', 'object_repr', 'action_flag', 'change_message')

# Register models with custom admin site
admin_site.register(User, CustomUserAdmin)
admin_site.register(Group, CustomGroupAdmin)
admin_site.register(LogEntry, CustomLogEntryAdmin)

# Register ILAS models
admin_site.register(Activity, ActivityAdmin)
admin_site.register(Establishment, EstablishmentAdmin)
admin_site.register(EstablishmentLicence, EstablishmentLicenceAdmin)
admin_site.register(EstablishmentRegister, EstablishmentRegisterAdmin)
admin_site.register(EstablishmentRole, EstablishmentRoleAdmin)
admin_site.register(Inspection, InspectionAdmin)
admin_site.register(InspectionAssignment, InspectionAssignmentAdmin)
admin_site.register(MainCategory, MainCategoryAdmin)
admin_site.register(SubCategory, SubCategoryAdmin)

# Register user_auth models
admin_site.register(Occupation, OccupationAdmin)
admin_site.register(Contact, ContactAdmin)
admin_site.register(Team, TeamAdmin)
admin_site.register(Profiles, ProfilesAdmin)

# Custom Admin CSS
class AdminMedia:
    css = {
        'all': (
            'admin/css/custom_admin.css',
        )
    }

# Add custom CSS
admin_site.enable_nav_sidebar = True
admin_site.site_header = 'LTLMS Administration'
admin_site.site_title = 'LTLMS Admin'
admin_site.index_title = 'Welcome to LTLMS Administration'

# Register your models here
# Example:
# from .models import YourModel
# admin_site.register(YourModel) 