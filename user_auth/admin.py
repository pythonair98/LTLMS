from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django import forms
from django.utils.html import format_html
from .models import Occupation, Contact, Team, Profiles


class CustomUserAdmin(UserAdmin):
    """Enhanced admin interface for User model."""
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'get_status_badge',
        'is_staff',
        'date_joined',
    )
    
    list_filter = (
        'is_staff',
        'is_superuser',
        'is_active',
        'groups',
        'date_joined',
    )
    
    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name',
    )
    
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        (_('Personal Info'), {
            'fields': ('first_name', 'last_name', 'email')
        }),
        (_('Permissions'), {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            ),
            'classes': ('collapse',),
        }),
        (_('Important Dates'), {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',),
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'password1',
                'password2',
                'email',
                'first_name',
                'last_name',
                'is_active',
                'is_staff',
            )
        }),
    )
    
    def get_status_badge(self, obj):
        """Generate a colored badge for the user status."""
        if obj.is_active:
            return format_html('<span class="badge bg-success">Active</span>')
        return format_html('<span class="badge bg-danger">Inactive</span>')
    get_status_badge.short_description = 'Status'


@admin.register(Occupation)
class OccupationAdmin(admin.ModelAdmin):
    """Enhanced admin interface for Occupation model."""
    list_display = (
        'id',
        'ar_name',
        'en_name',
        'power',
        'get_users_count',
    )
    
    search_fields = ('ar_name', 'en_name')
    list_filter = ('power',)
    ordering = ('power', 'ar_name')
    
    def get_users_count(self, obj):
        """Display count of users with this occupation."""
        count = obj.profiles_set.count()
        return format_html(
            '<span class="badge bg-info">{}</span>',
            count
        )
    get_users_count.short_description = 'Users Count'


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """Enhanced admin interface for Contact model."""
    list_display = (
        'id',
        'ar_name',
        'en_name',
        'phone_number',
        'email',
        'full_arabic_name',
        'get_profile_status',
    )
    
    search_fields = (
        'ar_name',
        'en_name',
        'phone_number',
        'email',
    )
    
    list_filter = ('ar_name', 'en_name')
    readonly_fields = ('full_arabic_name', 'get_profile_status')
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'ar_name',
                'en_name',
                'full_arabic_name',
            ),
        }),
        ('Contact Information', {
            'fields': (
                'phone_number',
                'email',
            ),
        }),
        ('Profile Status', {
            'fields': ('get_profile_status',),
        }),
    )
    
    def full_arabic_name(self, obj):
        """Display concatenated Arabic name."""
        return obj.ar_full_name
    full_arabic_name.short_description = 'Full Arabic Name'
    
    def get_profile_status(self, obj):
        """Display profile status with badge."""
        if hasattr(obj, 'profiles'):
            return format_html('<span class="badge bg-success">Assigned</span>')
        return format_html('<span class="badge bg-warning">Unassigned</span>')
    get_profile_status.short_description = 'Profile Status'


class ProfilesForm(forms.ModelForm):
    """Enhanced form for Profile admin."""
    class Meta:
        model = Profiles
        fields = '__all__'
        widgets = {
            'profile_image': forms.FileInput(attrs={'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Show only unassigned contacts in dropdown
        self.fields['contact'].queryset = Contact.objects.filter(profiles__isnull=True)


@admin.register(Profiles)
class ProfilesAdmin(admin.ModelAdmin):
    """Enhanced admin interface for Profiles model."""
    form = ProfilesForm
    
    list_display = (
        'user',
        'occupation',
        'contact',
        'team',
        'profile_image_preview',
        'get_status_badge',
    )
    
    search_fields = (
        'user__username',
        'user__email',
        'user__first_name',
        'user__last_name',
        'team__ar_name',
        'occupation__en_name',
    )
    
    list_filter = (
        'occupation',
        'team',
        'user__is_active',
        'created_at',
    )
    
    readonly_fields = (
        'created_at',
        'profile_image_preview',
        'get_status_badge',
    )
    
    fieldsets = (
        ('User Information', {
            'fields': (
                'user',
                'get_status_badge',
            ),
        }),
        ('Profile Details', {
            'fields': (
                'occupation',
                'contact',
                'team',
            ),
        }),
        ('Profile Image', {
            'fields': (
                'profile_image',
                'profile_image_preview',
            ),
        }),
        ('System Information', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )
    
    def profile_image_preview(self, obj):
        """Generate HTML preview of profile image."""
        if obj.profile_image:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover; border-radius: 4px;" />',
                obj.profile_image.url
            )
        return "No Image"
    profile_image_preview.short_description = 'Profile Image Preview'
    
    def get_status_badge(self, obj):
        """Generate a colored badge for the profile status."""
        if obj.user.is_active:
            return format_html('<span class="badge bg-success">Active</span>')
        return format_html('<span class="badge bg-danger">Inactive</span>')
    get_status_badge.short_description = 'Status'


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """Enhanced admin interface for Team model."""
    list_display = (
        'id',
        'ar_name',
        'en_name',
        'date_created',
        'get_team_members',
        'get_members_count',
    )
    
    search_fields = ('ar_name', 'en_name')
    list_filter = ('date_created',)
    ordering = ('-date_created',)
    
    fieldsets = (
        ('Team Information', {
            'fields': (
                'ar_name',
                'en_name',
            ),
        }),
        ('System Information', {
            'fields': ('date_created',),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ('date_created',)
    
    def get_members_count(self, obj):
        """Display count of team members."""
        count = obj.profiles_set.count()
        return format_html(
            '<span class="badge bg-info">{}</span>',
            count
        )
    get_members_count.short_description = 'Members Count'


# Replace default User admin with custom version
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
