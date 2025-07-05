from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import LicenseReport

@admin.register(LicenseReport)
class LicenseReportAdmin(admin.ModelAdmin):
    """Enhanced admin interface for LicenseReport model."""
    list_display = (
        'license_number',
        'establishment',
        'get_status_badge',
        'created_at',
        'get_expiry_status',
    )
    
    list_filter = (
        'created_at',
        'establishment__main_category',
        'establishment__sub_category',
    )
    
    search_fields = (
        'license_number',
        'establishment__establishment_name',
        'establishment__rifd',
        'establishment__owner_name',
        'notes',
    )
    
    readonly_fields = (
        'created_at',
        'get_status_badge',
        'get_expiry_status',
    )
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'license_number',
                'establishment',
                'get_status_badge',
            ),
            'classes': ('wide',),
        }),
        ('Dates', {
            'fields': (
                'created_at',
                'get_expiry_status',
            ),
            'classes': ('collapse',),
        }),
        ('Additional Information', {
            'fields': (
                'notes',
                'attachments',
            ),
            'classes': ('collapse',),
        }),
    )
    
    def get_status_badge(self, obj):
        """Generate a colored badge for the status."""
        status_colors = {
            'active': 'success',
            'expired': 'danger',
            'pending': 'warning',
            'suspended': 'secondary',
        }
        color = status_colors.get(obj.status, 'primary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            obj.get_status_display()
        )
    get_status_badge.short_description = 'Status'
    
    def get_expiry_status(self, obj):
        """Calculate and display expiry status."""
        if hasattr(obj, 'expiry_date') and obj.expiry_date:
            from datetime import date
            today = date.today()
            days_remaining = (obj.expiry_date - today).days
            
            if days_remaining < 0:
                return format_html(
                    '<span class="badge bg-danger">Expired {} days ago</span>',
                    abs(days_remaining)
                )
            elif days_remaining == 0:
                return format_html('<span class="badge bg-warning">Expires today</span>')
            elif days_remaining <= 30:
                return format_html(
                    '<span class="badge bg-warning">{} days remaining</span>',
                    days_remaining
                )
            else:
                return format_html(
                    '<span class="badge bg-success">{} days remaining</span>',
                    days_remaining
                )
        return "No expiry date set"
    get_expiry_status.short_description = 'Expiry Status'
    
    def get_queryset(self, request):
        """Optimize database queries by selecting related fields."""
        return super().get_queryset(request).select_related('establishment')
    
    def save_model(self, request, obj, form, change):
        """Add custom logic when saving the model."""
        if not change:  # If creating new record
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = ('admin/js/custom_admin.js',)
