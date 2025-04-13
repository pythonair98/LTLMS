from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from ILAS.models import (
    Inspection,
    EstablishmentLicence,
)
from ILAS.utils import create_license_report
from reports.models import LicenseReport


def report_index(request):
    """
    Display a list of available reports with their descriptions.
    Each report is represented by a dictionary containing name, description and URL slug.
    """
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
            "name": "تقرير الفئات الرئيسية",
            "description": "يعد تقريراً يحتوي على جميع الفئات الرئيسية مع أسمائها بالعربية والإنجليزية.",
            "slug": "main-categories-report",
        },
        {
            "name": "تقرير أدوار المنشأة",
            "description": "يعرض التقرير مختلف الأدوار داخل المنشآت مع تفاصيل الدور.",
            "slug": "establishment-roles-report",
        },
        {
            "name": "تقرير الفئات الفرعية",
            "description": "يعرض جميع الفئات الفرعية تحت كل فئة رئيسية مع أسماء مفصلة.",
            "slug": "sub-categories-report",
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
            "name": "تقرير جهات اتصال المنشأة",
            "description": "يعرض تفاصيل الاتصال الخاصة بالمنشأة بما في ذلك أرقام الهاتف، البريد الإلكتروني، والعناوين.",
            "slug": "establishment-contact-report",
        },
        {
            "name": "تقرير المنشآت حسب المنطقة",
            "description": "يعرض المنشآت مصنفة حسب المنطقة والبلدية للتحليل الجغرافي.",
            "slug": "region-based-establishment-report",
        },
        {
            "name": "تقرير قراءات RFID من أردوينو",
            "description": "يسجل جميع قراءات RFID المستلمة من أجهزة أردوينو مع الحالة والطوابع الزمنية.",
            "slug": "arduino-rfid-readings-report",
        },
        {
            "name": "تقرير ملخص الفحوصات",
            "description": "يقدم نظرة عامة على جميع الفحوصات بما في ذلك الحالة، المفتشين، والملاحظات الرئيسية.",
            "slug": "inspection-summary-report",
        },
        {
            "name": "تقرير صور الفحوصات",
            "description": "يجمع سجلات الفحوصات مع الصور المرفقة وتفاصيل وسائل الإعلام الإضافية.",
            "slug": "inspection-photos-report",
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
    return render(request, "reports/report_page.html", {"reports": reports})


def all_establishment_report(request):
    """
    Generate a report for all establishments.
    TODO: Implement report generation logic
    """
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
    inspection = get_object_or_404(Inspection, pk=inspection_id)
    register = inspection.get_register()
    establishment = register.establishment

    context = {
        "current_date": datetime.now(),
        "register": register,
        "establishment": establishment,
        "inspection": inspection,
    }
    return render(request, "reports/new_report.html", context=context)


def license_report(request, licence_id):
    """
    Generate and download a PDF license report.
    
    Args:
        request: HTTP request object
        licence_id: ID of the license to generate report for
        
    Returns:
        PDF file response containing the license report
    """
    # Get required data
    licence = get_object_or_404(EstablishmentLicence, number=licence_id)
    register = licence.register
    establishment = licence.establishment
    
    # Generate PDF report
    report_path = create_license_report(
        licence_=licence,
        establishment=establishment,
        register=register
    )

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

    # Return PDF file
    with open(report_path, "rb") as report_file:
        response = HttpResponse(report_file.read(), content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="license_report_{licence_id}.pdf"'
        return response


def view_exported_report(request):
    """
    Display a list of all exported license reports.
    """
    reports = LicenseReport.objects.all()
    return render(request, "reports/view_exported_report.html", {"reports": reports})
