from django.urls import path
from .views import (
    add_establishment,
    view_establishment,
    delete_establishment,
    edit_establishment,
    reader,
    query,
    api_arduino,
    register_list_create,
    register_delete,
    licence_list_create,
    licence_delete,
    view_inspection_assignments,
    delete_assignment,
    edit_assignment,
    update_assignment_status,
    assign_establishment,
    create_inspection,
    dashboard,
    view_inspections,
    archive_inspection,
    view_archive,
    add_establishment_register,
    add_establishment_licence,
get_inspector_assignments,
get_inspector_inspections
)

urlpatterns = [
    # Handles adding a new establishment (Establishment)
    path("", dashboard, name="dashboard"),
    path("/", dashboard, name="dashboard"),
    path("add_establishment", add_establishment, name="add_establishment"),
    path("view_establishment", view_establishment, name="view_establishment"),
    path(
        "delete_establishment/<int:register_number>",
        delete_establishment,
        name="delete_establishment",
    ),
    path(
        "edit_establishment/<int:register_number>",
        edit_establishment,
        name="edit_establishment",
    ),
    # Handles the reader view
    path("reader", reader, name="reader"),
    path("test", create_inspection, name="test"),
    path("api/query", query, name="query"),
    path("api/arduino", api_arduino, name="api_arduino"),
    # URLs for EstablishmentRegister (Register)
    path("registers/", register_list_create, name="register-list"),
    path("registers/delete/<int:pk>/", register_delete, name="register-delete"),
    path("registers/delete/<int:pk>/", register_delete, name="register-delete"),
    # URLs for EstablishmentLicence (Licence)
    path("licences", licence_list_create, name="licence-list"),
    path("licences/delete/<int:pk>/", licence_delete, name="licence-delete"),
    # URLs for InspectionAssignment
    path("assignments", view_inspection_assignments, name="view_assignments"),
    path("assignments/delete/<int:pk>", delete_assignment, name="delete_assignment"),
    path("assignments/edit/<int:pk>", edit_assignment, name="edit_assignment"),
    path(
        "assignments/update_status/<int:pk>",
        update_assignment_status,
        name="update_assignment_status",
    ),
    path("assign-establishment/", assign_establishment, name="assign_establishment"),
    path("inspections", view_inspections, name="view_inspections"),
    path("archived_inspection", view_archive, name="archived_inspection"),
    path(
        "inspections/<int:pk>/archive/", archive_inspection, name="archive_inspection"
    ),
    path("register/add/", add_establishment_register, name="add_register"),
    path("add_establishment_licence", add_establishment_licence, name="add_licence"),
    path("get_inspector_assignments", get_inspector_assignments, name="get_inspector_assignments"),
    path("get_inspector_inspections", get_inspector_inspections, name="get_inspector_inspections"),

]
