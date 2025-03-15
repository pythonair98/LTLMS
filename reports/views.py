from django.shortcuts import render
from datetime import datetime

from licesnsing.models import EstablishmentRegister, Inspection


def report_index(request):
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
    # Query the data from the model
    pass


def inspection_report(request):
    register = EstablishmentRegister.objects.all()[0]
    establishment = register.establishment
    inspection = Inspection.objects.all()[0]
    current_date = datetime.now()
    context = {
        "current_date": current_date,
        "register": register,
        "establishment": establishment,
        "inspection": inspection,
    }

    return render(request, "reports/new_report.html", context=context)
