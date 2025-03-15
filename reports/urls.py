from django.urls import path
from .views import all_establishment_report, report_index, inspection_report


urlpatterns = [
    path("report", report_index, name="report_index"),
    path(
        "all-establishment-report/",
        all_establishment_report,
        name="all_establishment_report",
    ),
    path("inspection_report/", inspection_report, name="inspection_report"),
]
