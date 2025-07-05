import logging
from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg

from ILAS.models import (
    Inspection,
    EstablishmentLicence,
    Activity,
    Establishment,
)
from ILAS.utils import create_license_report
from reports.models import LicenseReport

# Get a logger instance for this module
logger = logging.getLogger(__name__)


def report_index(request):
    """
    Display a list of available reports with their descriptions.
    Each report is represented by a dictionary containing name, description and URL slug.
    """
    logger.info("Accessing report index page")
    reports = [
        {
            "name": "تقرير نظرة عامة على الأنشطة",
            "description": "يقدم نظرة عامة على جميع الأنشطة مع رموزها وأسمائها بالعربية والإنجليزية.",
            "slug": "activity-overview-report",
        },
        {
            "name": "تقرير رموز الأنشطة", 
            "description": "تفصيل دقيق لرموز الأنشطة وإحصاءات استخدامها.",
            "slug": "activity-code-report",
        },
        
        {
            "name": "تقرير دليل المنشآت",
            "description": "يتضمن دليل شامل للمنشآت مع تفاصيل الاتصال والموقع.",
            "slug": "establishment-directory-report",
        },
        {
            "name": "تقرير تفاصيل المنشأة",
            "description": "يقدم معلومات تفصيلية حول المنشآت، بما في ذلك معلومات المالك، المدير، وممثل الاتصال.",
            "slug": "establishment-details-report",
        },
       
        {
            "name": "تقرير المنشآت حسب المنطقة",
            "description": "يعرض المنشآت مصنفة حسب المنطقة والبلدية للتحليل الجغرافي.",
            "slug": "region-based-establishment-report",
        },

        {
            "name": "تقرير ملخص الفحوصات",
            "description": "يقدم نظرة عامة على جميع الفحوصات بما في ذلك الحالة، المفتشين، والملاحظات الرئيسية.",
            "slug": "inspection-summary-report",
        },
        
        {
            "name": "تقرير تسجيل المنشآت",
            "description": "يوضح جميع سجلات التسجيل بما في ذلك تواريخ الإصدار والانتهاء للمنشآت.",
            "slug": "establishment-registration-report",
        },
        {
            "name": "تقرير تراخيص المنشآت",
            "description": "يعرض تراخيص المنشآت مع تواريخ الإنشاء والانتهاء ومعلومات الفئات ذات الصلة.",
            "slug": "establishment-licence-report",
        },
        {
            "name": "تقرير تكليفات الفحوصات",
            "description": "يقدم تقريراً عن تكليفات الفحوصات، مع إبراز أعباء عمل المفتشين والحالات والمواعيد النهائية.",
            "slug": "inspection-assignment-report",
        },
        {
            "name": "تقرير اتجاهات الفحوصات الشهرية",
            "description": "يحلل بيانات الفحوصات شهرياً لتحديد الأنماط والاتجاهات.",
            "slug": "monthly-inspection-trends-report",
        },
        {
            "name": "تقرير نشاط المنشآت الأسبوعي",
            "description": "يتتبع ويلخص الأنشطة الأسبوعية للمنشآت والمؤشرات التشغيلية.",
            "slug": "weekly-establishment-activity-report",
        },
        {
            "name": "تقرير الترخيص الشامل",
            "description": "يجمع البيانات من سجلات التسجيل، التراخيص، والفحوصات للحصول على نظرة شاملة على عمليات الترخيص.",
            "slug": "comprehensive-licensing-report",
        },
    ]
    logger.debug(f"Rendering report index with {len(reports)} available reports")
    return render(request, "reports/report_page.html", {"reports": reports})


def all_establishment_report(request):
    """
    Generate a report for all establishments.
    TODO: Implement report generation logic
    """
    logger.warning("all_establishment_report function is not implemented yet")
    pass


def inspection_report(request, inspection_id):
    """
    Generate an inspection report for a specific inspection.
    
    Args:
        request: HTTP request object
        inspection_id: ID of the inspection to generate report for
        
    Returns:
        Rendered inspection report template with inspection details
    """
    logger.info(f"Generating inspection report for inspection ID: {inspection_id}")
    try:
        inspection = get_object_or_404(Inspection, pk=inspection_id)
        register = inspection.get_register()
        establishment = register.establishment

        context = {
            "current_date": datetime.now(),
            "register": register,
            "establishment": establishment,
            "inspection": inspection,
        }
        logger.debug(f"Inspection report context prepared for inspection ID: {inspection_id}")
        return render(request, "reports/new_report.html", context=context)
    except Exception as e:
        logger.error(f"Error generating inspection report for ID {inspection_id}: {str(e)}", exc_info=True)
        raise


def license_report(request, licence_id):
    """
    Generate and download a PDF license report.
    
    Args:
        request: HTTP request object
        licence_id: ID of the license to generate report for
        
    Returns:
        PDF file response containing the license report
    """
    logger.info(f"Generating license report PDF for license ID: {licence_id}")
    try:
        # Get required data
        licence = get_object_or_404(EstablishmentLicence, number=licence_id)
        register = licence.register
        establishment = licence.establishment
        
        logger.debug(f"Retrieved license data for ID {licence_id}, establishment: {establishment.id}")
        
        # Generate PDF report
        report_path = create_license_report(
            licence_=licence,
            establishment=establishment,
            register=register
        )
        logger.info(f"PDF report generated at: {report_path}")

        # Save report record
        report = LicenseReport(
            establishment=establishment,
            register_number=register.id,
            id_number=establishment.owner_number,
            license_category=licence.main_category,
            issue_date=licence.creation_date,
            expired_date=licence.expiration_date,
            activity=establishment.activity,
            address=establishment.get_address(),
            license_number=licence.number,
            phone_number=establishment.phone_number,
            email=establishment.email,
            created_by=request.user,
        )
        report.save()
        logger.info(f"License report record saved with ID: {report.id}")

        # Return PDF file
        with open(report_path, "rb") as report_file:
            response = HttpResponse(report_file.read(), content_type="application/pdf")
            response["Content-Disposition"] = f'attachment; filename="license_report_{licence_id}.pdf"'
            return response
    except Exception as e:
        logger.error(f"Error generating license report for ID {licence_id}: {str(e)}", exc_info=True)
        raise


def view_exported_report(request):
    """
    Display a list of all exported license reports.
    """
    logger.info("Accessing exported reports list view")
    try:
        reports = LicenseReport.objects.all()
        logger.debug(f"Retrieved {reports.count()} exported license reports")
        return render(request, "reports/view_exported_report.html", {"reports": reports})
    except Exception as e:
        logger.error(f"Error retrieving exported reports: {str(e)}", exc_info=True)
        raise


@login_required
def activity_overview(request):
    """
    View for displaying an overview of all activities with their details.
    """
    activities = Activity.objects.annotate(
        establishment_count=Count('establishment')
    ).order_by('ar_name')
    
    context = {
        'activities': activities,
        'title': 'Activity Overview Report',
        'description': 'Provides an overview of all activities with their codes and names in Arabic and English.'
    }
    
    return render(request, 'reports/activity_overview.html', context)


@login_required
def activity_codes_report(request):
    # Get all activities with their establishment counts
    activities = Activity.objects.annotate(
        establishment_count=Count('establishment')
    ).all()
    
    # Calculate usage levels
    for activity in activities:
        if activity.establishment_count > 10:
            activity.usage_level = 'high'
        elif activity.establishment_count > 5:
            activity.usage_level = 'medium'
        else:
            activity.usage_level = 'low'
    
    # Calculate statistics
    total_activities = activities.count()
    active_activities = activities.filter(establishment_count__gt=0).count()
    total_establishments = sum(activity.establishment_count for activity in activities)
    avg_establishments = round(total_establishments / total_activities if total_activities > 0 else 0, 2)
    
    # Calculate usage distribution
    high_usage = activities.filter(establishment_count__gt=10).count()
    medium_usage = activities.filter(establishment_count__gt=5, establishment_count__lte=10).count()
    low_usage = activities.filter(establishment_count__lte=5).count()
    
    # Get top activities
    top_activities = activities.order_by('-establishment_count')[:5]
    top_activities_labels = [f'"{activity.ar_name}"' for activity in top_activities]
    top_activities_data = [activity.establishment_count for activity in top_activities]
    
    context = {
        'activities': activities,
        'total_activities': total_activities,
        'active_activities': active_activities,
        'total_establishments': total_establishments,
        'avg_establishments': avg_establishments,
        'usage_distribution': {
            'high': high_usage,
            'medium': medium_usage,
            'low': low_usage
        },
        'top_activities_labels': f'[{",".join(top_activities_labels)}]',
        'top_activities_data': top_activities_data,
    }
    
    return render(request, 'reports/activity_codes.html', context)


@login_required
def establishment_directory_report(request):
    """
    View for displaying a comprehensive directory of establishments with contact details and location information.
    """
    # Get all establishments with their related data
    establishments = Establishment.objects.select_related(
        'activity',
        'main_category',
        'sub_category'
    ).all()
    
    # Calculate statistics
    total_establishments = establishments.count()
    # An establishment is considered active if it has a valid license
    active_establishments = EstablishmentLicence.objects.filter(
        register__establishment__in=establishments,
        expiration_date__gt=datetime.now()
    ).values('register__establishment').distinct().count()
    
    # Get unique regions from establishment data
    regions = establishments.values_list('region_number', flat=True).distinct()
    total_regions = len(regions)
    total_activities = Activity.objects.count()
    
    # Add status to each establishment
    for establishment in establishments:
        has_valid_license = EstablishmentLicence.objects.filter(
            register__establishment=establishment,
            expiration_date__gt=datetime.now()
        ).exists()
        establishment.status = 'active' if has_valid_license else 'inactive'
    
    context = {
        'establishments': establishments,
        'total_establishments': total_establishments,
        'active_establishments': active_establishments,
        'total_regions': total_regions,
        'total_activities': total_activities,
        'regions': [{'id': region, 'name': f'منطقة {region}'} for region in regions],
    }
    
    return render(request, 'reports/establishment_directory.html', context)
