from django.urls import path
from .views import (
    add_establishment,
    view_establishment,
    delete_establishment,
    edit_establishment,
    reader,
    query,
    api_arduino, register_list_create, register_delete, licence_list_create, licence_delete,
    view_inspection_assignments, delete_assignment, edit_assignment, update_assignment_status, assign_establishment
)

urlpatterns = [
    path("add_establishment", add_establishment, name="add_establishment"),
    # Handles adding a new establishment
    path("view_establishment", view_establishment, name="view_establishment"),
    # Displays all registered establishments
    path(
        "delete_establishment/<int:register_number>",
        delete_establishment,
        name="delete_establishment",
    ),
    # Deletes an establishment identified by its register number
    path(
        "edit_establishment/<int:register_number>",
        edit_establishment,
        name="edit_establishment",
    ),
    # Edits an establishment identified by its register number
    path("reader", reader, name="reader"),
    path("api/query", query, name="query"),
    path("api/arduino", api_arduino, name="api_arduino"),
    path('registers/', register_list_create, name='register-list'),
    path('registers/delete/<int:pk>/', register_delete, name='register-delete'),
    path('registers/delete/<int:pk>/', register_delete, name='register-delete'),

    # URLs for EstablishmentLicence (Licence)
    path('licences/', licence_list_create, name='licence-list'),
    path('licences/delete/<int:pk>/', licence_delete, name='licence-delete'),
    path('assignments/', view_inspection_assignments, name='view_assignments'),
    path('assignments/delete/<int:pk>/', delete_assignment, name='delete_assignment'),
    path('assignments/edit/<int:pk>/', edit_assignment, name='edit_assignment'),
    path('assignments/update_status/<int:pk>/', update_assignment_status, name='update_assignment_status'),
path('assign-establishment/', assign_establishment, name='assign_establishment'),

]
