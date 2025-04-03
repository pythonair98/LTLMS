from datetime import date, datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST
from django.db.models.functions import TruncMonth

from user_auth.models import Profiles
from .forms import (
    EstablishmentForm,
    InspectionForm,
    EstablishmentRegisterForm,
    EstablishmentLicenceForm,
    InspectionAssignmentForm,
)
from .models import (
    Establishment,
    ArduinoReader,
    EstablishmentLicence,
    EstablishmentRegister,
    InspectionAssignment,
    Inspection,
)
from .utils import (
    mark_inspection_as_done,
    get_establishment_obj_by_register,
)


@login_required(login_url="login")
def add_establishment(request):
    """
    Handles the creation of a new establishment.

    - If the request method is GET, it renders an empty form.
    - If the request method is POST, it validates and saves the form data.
    - Prints form errors for debugging if the form is invalid.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the 'add_establishment.html' template with the form.
    """
    form = EstablishmentForm()
    if request.method == "POST":
        form = EstablishmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "تم إضافة المنشأة بنجاح")
            return redirect("view_establishment")
        messages.error(request, "حدث خطأ أثناء إضافة المنشأة")

    return render(request, "licesnsing/add_establishment.html", {"form": form})


@login_required(login_url="login")
def dashboard(request):
    """
    Renders a dashboard with key statistics and latest records.
    """
    from django.db.models.functions import TruncMonth
    from django.utils import timezone
    from datetime import timedelta

    # Basic stats
    total_establishments = Establishment.objects.count()
    total_assignments = InspectionAssignment.objects.count()
    total_licenses = EstablishmentLicence.objects.count()
    total_inspections = Inspection.objects.count()

    # Assignment status distribution
    assignments_by_status = (
        InspectionAssignment.objects.values("status")
        .annotate(count=Count("id"))
        .order_by("status")
    )

    # Monthly inspections (last 6 months)
    six_months_ago = timezone.now() - timedelta(days=180)
    monthly_inspections = (
        Inspection.objects.filter(created_at__gte=six_months_ago)
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )

    # Inspection status distribution
    inspection_status = [
        {"status": True, "count": Inspection.objects.filter(status=True).count()},
        {"status": False, "count": Inspection.objects.filter(status=False).count()},
    ]

    # Top 5 municipalities
    municipality_stats = (
        Establishment.objects.values("municipality_name")
        .annotate(count=Count("id"))
        .order_by("-count")[:5]
    )

    # Activity distribution
    activity_stats = (
        Establishment.objects.values("activity__ar_name")
        .annotate(count=Count("id"))
        .order_by("-count")[:3]
    )

    # License status
    today = timezone.now().date()
    active_licenses = EstablishmentLicence.objects.filter(
        expiration_date__gt=today
    ).count()
    expired_licenses = EstablishmentLicence.objects.filter(
        expiration_date__lte=today
    ).count()
    license_status = [
        {"status": "Active", "count": active_licenses},
        {"status": "Expired", "count": expired_licenses},
    ]

    # Get latest records (adjust ordering fields as needed)
    latest_establishments = Establishment.objects.order_by("-created_at")[:5]
    latest_assignments = InspectionAssignment.objects.order_by("-assigned_at")[:5]
    latest_licenses = EstablishmentLicence.objects.order_by("-number")[:5]
    latest_inspections = Inspection.objects.order_by("-created_at")[:5]

    context = {
        "total_establishments": total_establishments,
        "total_assignments": total_assignments,
        "total_licenses": total_licenses,
        "total_inspections": total_inspections,
        "assignments_by_status": assignments_by_status,
        "monthly_inspections": monthly_inspections,
        "inspection_status": inspection_status,
        "municipality_stats": municipality_stats,
        "activity_stats": activity_stats,
        "license_status": license_status,
    }
    return render(request, "licesnsing/index.html", context)


@login_required(login_url="login")
def view_establishment(request):
    """
    Displays a list of all registered establishments.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the 'view_establishment.html' template with all establishments.
    """
    establishments = Establishment.objects.all().order_by("-id")
    paginator = Paginator(establishments, 5)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "licesnsing/view_establishment.html",
        {
            "today": date.today(),
            "page_obj": page_obj,
        },
    )


@login_required(login_url="login")
def delete_establishment(request, register_number):
    """
    Deletes an establishment based on the provided register number.

    - If the establishment exists, it is deleted.
    - If it does not exist, the function handles the exception silently.
    - After deletion, the updated list of establishments is displayed.

    Args:
        request (HttpRequest): The HTTP request object.
        register_number (str): The unique register number of the establishment.

    Returns:
        HttpResponse: Renders the 'view_establishment.html' template with the updated list.
    """
    try:
        establishment = Establishment.objects.get(register_number=register_number)
        establishment.delete()
    except Establishment.DoesNotExist:
        pass  # Silently handle the case where the establishment does not exist

    return render(
        request,
        "licesnsing/view_establishment.html",
        {"establishments": Establishment.objects.all()},
    )


@login_required(login_url="login")
def edit_establishment(request, rifd):
    """
    Edits an existing establishment's details.

    - Retrieves the establishment using the register number.
    - If the request method is POST, updates the establishment with new data.
    - If the form is valid, saves the changes.

    Args:
        request (HttpRequest): The HTTP request object.
        register_number (str): The unique register number of the establishment.

    Returns:
        HttpResponse: Renders the 'edit_establishment.html' template with the form.
    """
    establishment = get_object_or_404(Establishment, rifd=rifd)
    form = EstablishmentForm(request.POST or None, instance=establishment)
    if form.is_valid():
        messages.success(request, "تم تحديث المنشأة بنجاح")
        form.save()

    return render(request, "licesnsing/edit_establishment.html", {"form": form})


@login_required(
    login_url="login"
)  # Ensures only authenticated users can access this endpoint
@require_http_methods(["GET", "POST"])  # Allows only GET and POST requests
def query(request):
    """
    Django view to check for new unread entries from the Arduino device.

    - Fetches the latest unread record from the ArduinoReader model.
    - If an establishment is found that matches the RFID code, a form with the data is rendered.
    - Returns a JSON response containing the rendered template.
    """
    # Fetch the latest unread ArduinoReader entry
    code = (
        ArduinoReader.objects.filter(queried=False, status="pending")
        .order_by("-id")
        .first()
    )

    if code:
        # Look for an establishment with the corresponding RFID code
        establishment = Establishment.objects.filter(rifd=code.code).first()

        if establishment:
            # Render a form pre-filled with the establishment data
            code.status = "processed"
            code.save()
            return JsonResponse(
                {
                    "found": True,
                    "code": code.code,
                    "template": render(
                        request,
                        "licesnsing/query.html",
                        {
                            "eform": EstablishmentForm(instance=establishment),
                            "datafound": True,
                            "iform": InspectionForm(),
                            "found": True,
                            "register_number": establishment.get_register.id,
                        },
                    ).content.decode("utf-8"),
                }
            )

        # If no matching establishment is found, return a 'not found' response
        return JsonResponse(
            {
                "found": False,
                "template": render(
                    request,
                    "licesnsing/query.html",
                    {"found": False},
                ).content.decode("utf-8"),
            }
        )

    # Default response when no new unread record is found
    return JsonResponse(
        {
            "found": False,
            "template": render(
                request,
                "licesnsing/query.html",
                {"found": False},
            ).content.decode("utf-8"),
        }
    )


@login_required(login_url="login")
def reader(request):
    establishments = [
        establsihemnt.establishment
        for establsihemnt in InspectionAssignment.objects.filter(
            inspector=request.user, status="pending"
        )
    ]
    return render(
        request, "licesnsing/readRFID.html", {"establishments": establishments}
    )


@login_required(login_url="login")
def inspect_establishment(request, id):
    establishment = Establishment.objects.get(id=id)
    if request.method == "POST":
        form = InspectionForm(request.POST, request.FILES)
        register_number = request.POST.get("register_number")
        if Inspection.objects.filter(register_number=register_number).exists():
            messages.warning(request, "تم تسجيل معاينة لهذه المنشأة بالفعل")
            return redirect("reader")
        if form.is_valid():
            form.save()
            # mark inspection as done
            mark_inspection_as_done(get_establishment_obj_by_register(register_number))
            messages.success(request, "تم إرسال المعاينة بنجاح")
            return redirect("reader")
    elif request.method == "GET":
        if establishment:
            # Render a form pre-filled with the establishment data
            return JsonResponse(
                {
                    "found": True,
                    "template": render(
                        request,
                        "licesnsing/query.html",
                        {
                            "eform": EstablishmentForm(instance=establishment),
                            "establishment": establishment,
                            "datafound": True,
                            "iform": InspectionForm(),
                            "found": True,
                            "register_number": establishment.get_register.id,
                        },
                    ).content.decode("utf-8"),
                }
            )


@login_required(login_url="login")
def inspection_delete(request, id):
    inspection = Inspection.objects.get(id=id)
    if inspection:
        inspection.delete()
        messages.success(request, "تم حذف المعاينة بنجاح")
    else:
        messages.warning(request, "حدث خطأ اثناء حذف المعاينة")
    return redirect("view_inspections")


# @login_required(login_url="login")
# def reader(request):
#     """
#     Main view to handle inspection (reader) requests.
#
#     Process:
#       1. On POST:
#          - Instantiate InspectionForm with POST and FILES.
#          - Validate the form.
#          - Check if an inspection with the given register_number already exists.
#          - If not, save the inspection.
#          - Retrieve the RFID (assumed to be in the 'rifd' field of the form).
#          - Query the ArduinoReader for a matching record (code == rifd, queried is False, status is "processed").
#          - If found, mark it as queried, clean up all queried records, and show a success message.
#          - If not, clean up and show a warning message.
#       2. On GET:
#          - Display an empty InspectionForm.
#     """
#     if request.method == "POST":
#         form = InspectionForm(request.POST, request.FILES)
#         if form.is_valid():
#             register_number = form.cleaned_data.get("register_number")
#
#             # Check if inspection for this establishment already exists.
#             if Inspection.objects.filter(register_number=register_number).exists():
#                 messages.error(request, "تم تسجيل معاينة لهذه المنشأة بالفعل")
#                 return redirect("reader")
#
#             # Save the inspection record.
#             form.save()
#             # mark inspection as done
#             mark_inspection_as_done(get_establishment_obj_by_register(register_number))
#             messages.success(request, "تم إرسال المعاينة بنجاح")
#             # Retrieve the RFID from the form data.
#             rifd = form.cleaned_data.get("rifd")
#
#             # Query ArduinoReader for a matching record.
#             arduino_record = (
#                 ArduinoReader.objects.filter(
#                     code=rifd, queried=False, status="processed"
#                 )
#                 .order_by("-id")
#                 .first()
#             )
#
#             if arduino_record:
#                 # Mark the ArduinoReader record as queried.
#                 arduino_record.queried = True
#                 arduino_record.save()
#
#                 # Clean up all ArduinoReader records that have been queried.
#                 ArduinoReader.objects.filter(queried=True).delete()
#
#                 messages.success(request, "تم إرسال المعاينة")
#                 return redirect("reader")
#
#         else:
#             messages.warning(request, "الرجاء تصحيح الأخطاء في النموذج.")
#     else:
#         form = InspectionForm()
#
#     return render(request, "ILAS/readRFID.html", {"form": form})


# Main view to handle the POST request from Arduino
# @csrf_exempt
# def api_arduino(request):
#     """
#     This view handles communication with the Arduino and saves the received code.
#     """
#     if request.method == "POST":
#         # Check if there's raw data in the request body
#         if request.body:
#             code = process_raw_data(request)
#             if code:
#                 # Save the code to the database
#                 ArduinoReader.objects.create(code=code)
#                 return JsonResponse(
#                     {"message": "Code received successfully"}, status=200
#                 )
#
#         # Check if there's form data in the request
#         elif "UIDresult" in request.POST:
#             code = process_form_data(request)
#             if code:
#                 # Save the code to the database
#                 ArduinoReader.objects.create(code=code)
#                 return JsonResponse(
#                     {"message": "Code received successfully"}, status=200
#                 )
#
#         # If no valid data found, return an error
#         return JsonResponse({"error": "Invalid request"}, status=400)
#
#     return JsonResponse({"error": "Forbidden method"}, status=403)


@login_required(login_url="login")
def register_list_create(request):
    """
    View to display a list of all EstablishmentRegister records and provide a form
    for adding a new record.

    - GET: Retrieve and display all records along with an empty creation form.
    - POST: Process the form data to create a new EstablishmentRegister record.

    Template:
      'register_list_create.html'

    Context:
      registers - QuerySet of all EstablishmentRegister records.
      form      - The EstablishmentRegisterForm instance.
    """
    if request.method == "POST":
        form = EstablishmentRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            # After saving, redirect to the same view to display the updated list.
            return redirect("register-list")  # Ensure your URL name matches this.
    else:
        form = EstablishmentRegisterForm()

    registers = EstablishmentRegister.objects.all()
    paginator = Paginator(registers, 5)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "today": date.today(),
        "form": form,
    }
    return render(request, "licesnsing/register_list_create.html", context)


@login_required(login_url="login")
def register_delete(request, pk):
    """
    View to delete a specific EstablishmentRegister record.

    The view retrieves the record by its primary key (pk). For GET requests,
    it displays a confirmation page. For POST requests, it deletes the record
    and redirects back to the register list view.

    Template:
      'register_confirm_delete.html'

    Context:
      register - The EstablishmentRegister record to be deleted.
    """
    register = get_object_or_404(EstablishmentRegister, pk=pk)
    if register:
        register.delete()
        return redirect("register-list")  # Ensure your URL name matches this.

    context = {"register": register}
    return render(request, "licesnsing/register_confirm_delete.html", context)


# -------------------------------------------------------------------
# Views for EstablishmentLicence (Licence)
# -------------------------------------------------------------------


@login_required(login_url="login")
def licence_list_create(request):
    """
    View to display a list of all EstablishmentLicence records and provide a form
    for adding a new record.

    - GET: Retrieve and display all licence records along with an empty creation form.
    - POST: Process the form data to create a new EstablishmentLicence record.

    Template:
      'licence_list_create.html'

    Context:
      licences - QuerySet of all EstablishmentLicence records.
      form     - The EstablishmentLicenceForm instance.
    """
    if request.method == "POST":
        form = EstablishmentLicenceForm(request.POST)
        if form.is_valid():
            form.save()
            # After saving, redirect to the same view to display the updated list.
            return redirect("licence-list")  # Ensure your URL name matches this.
    else:
        form = EstablishmentLicenceForm()

    licences = EstablishmentLicence.objects.all()
    paginator = Paginator(licences, 5)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "form": form,
    }
    return render(request, "licesnsing/licence_list_create.html", context)


@login_required(login_url="login")
def licence_delete(request, pk):
    """
    View to delete a specific EstablishmentLicence record.

    The view retrieves the record by its primary key (pk). For GET requests,
    it displays a confirmation page. For POST requests, it deletes the record
    and redirects back to the licence list view.

    Template:
      'licence_confirm_delete.html'

    Context:
      licence - The EstablishmentLicence record to be deleted.
    """
    licence = get_object_or_404(EstablishmentLicence, pk=pk)

    if request.method == "POST":
        licence.delete()
        return redirect("licence-list")  # Ensure your URL name matches this.

    context = {"licence": licence}
    return render(request, "licesnsing/licence_confirm_delete.html", context)


@login_required(login_url="login")
def view_inspection_assignments(request):
    assignments = InspectionAssignment.objects.all()
    return render(
        request, "licesnsing/inspectors_assignments.html", {"assignments": assignments}
    )


@login_required(login_url="login")
def edit_assignment(request, pk):
    """
    Edits an existing InspectionAssignment.

    - Retrieves the assignment using the primary key.
    - If the request method is POST, updates the assignment with new data.
    - If the form is valid, saves the changes.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the InspectionAssignment.

    Returns:
        HttpResponse: Renders the 'edit_assignment.html' template with the form.
    """
    # assignment = get_object_or_404(InspectionAssignment, pk=pk)
    # form = InspectionAssignmentForm(request.POST or None, instance=assignment)
    # if form.is_valid():
    #     form.save()

    return render(request, "licesnsing/edit_assignment.html", {})


@login_required(login_url="login")
def delete_assignment(request, pk):
    """
    Deletes an InspectionAssignment based on the provided primary key.

    - If the assignment exists, it is deleted.
    - If it does not exist, the function handles the exception silently.
    - After deletion, the updated list of assignments is displayed.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the InspectionAssignment.

    Returns:
        HttpResponse: Renders the 'inspectors_assignments.html' template with the updated list.
    """
    try:
        assignment = InspectionAssignment.objects.get(pk=pk)
        assignment.delete()
    except InspectionAssignment.DoesNotExist:
        pass  # Silently handle the case where the assignment does not exist

    return render(
        request,
        "licesnsing/inspectors_assignments.html",
        {"assignments": InspectionAssignment.objects.all()},
    )


@login_required
@require_POST
def update_assignment_status(request, pk):
    """
    Updates the status of an InspectionAssignment.

    Expects a POST request with a 'status' parameter representing the new status.
    Valid statuses are: 'pending', 'accepted', 'in_progress', 'completed', and 'cancelled'.

    On success, updates the assignment and redirects to the assignments list view.
    On failure, displays an error message and redirects back.
    """
    new_status = request.POST.get("status")
    assignment = get_object_or_404(InspectionAssignment, id=pk)

    valid_statuses = ["pending", "accepted", "in_progress", "completed", "cancelled"]
    if new_status not in valid_statuses:
        messages.error(request, "الحالة التي قمت بإدخالها خطأ.")
        return redirect(
            "view_assignments"
        )  # Adjust to your actual URL name for assignments view
    else:
        assignment.status = new_status
        assignment.save()
    messages.success(request, "تم تحديث حالة التكليف بنجاح.")
    return redirect("view_assignments")


@login_required
def assign_establishment(request):
    """
    Handles assigning an establishment for inspection.

    GET:
      - Displays an empty form for creating a new inspection assignment.

    POST:
      - Validates the form and, if valid, creates a new InspectionAssignment.
      - Redirects to a view (e.g., the assignments list) upon success.
    """
    if request.method == "POST":
        form = InspectionAssignmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "تم توجيه التكليف بنجاح")
            # Adjust the redirect URL as needed.
            return redirect("view_assignments")
        else:
            messages.warning(request, form.errors.as_text())
    inspectors = Profiles.objects.filter(occupation__power=6)
    form = InspectionAssignmentForm()
    unassigned_establishments = Establishment.objects.exclude(
        inspection_assignments__isnull=False
    )

    if len(unassigned_establishments) == 0:
        messages.warning(request, "حميع المنشأت قد تم تعيينها.")
    return render(
        request,
        "licesnsing/assign_establishment.html",
        {
            "form": form,
            "unassigned_establishments": unassigned_establishments,
            "inspectors": inspectors,
        },
    )


@login_required(login_url="login")
def create_inspection(request):
    """
    View to create a new Inspection record.
    :param request:
    :return:
    """
    if request.method == "POST":
        form = InspectionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Inspection created successfully!")
            return redirect("reader")  # Change to your desired URL name.
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = InspectionForm()
        registers = EstablishmentRegister.objects.all()
        return render(
            request,
            "licesnsing/create_inspection.html",
            {"form": form, "registers": registers},
        )


@login_required(login_url="login")
def view_inspections(request):
    """
    View to display a list of all Inspection records.

    :param request:
    :return:
    """
    inspections = Inspection.objects.filter(is_archived=False)
    paginator = Paginator(inspections, 5)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request, "licesnsing/view_inspections.html", {"page_obj": page_obj}
    )


@login_required(login_url="login")
def view_inspection_data(request, pk):
    inspection = Inspection.objects.get(id=pk)
    if inspection:
        return render(
            request, "licesnsing/view_inspection_data.html", {"inspection": inspection}
        )


@login_required(login_url="login")
def archive_inspection(request, pk):
    """
    Archive an inspection. Archived inspections are not displayed in the main list.

    :param request:
    :param pk:
    :return:
    """
    inspection = get_object_or_404(Inspection, pk=pk)
    inspection.is_archived = True
    inspection.archived_at = datetime.now()
    inspection.save()
    messages.success(request, "تم أرشفة المعاينة بنجاح!")
    return redirect("view_inspections")


@login_required(login_url="login")
def view_archive(request):
    """
    View to display a list of all archived Inspection records.

    :param request:
    :return:
    """
    inspections = Inspection.objects.filter(is_archived=True)
    return render(
        request, "licesnsing/view_archived.html", {"inspections": inspections}
    )


@login_required
def add_establishment_register(request):
    if request.method == "POST":
        form = EstablishmentRegisterForm(request.POST)
        if form.is_valid():
            establishment = form.cleaned_data["establishment"]

            # Check if this establishment already has a register
            if EstablishmentRegister.objects.filter(
                establishment=establishment
            ).exists():
                messages.error(request, "هذا السجل موجود بالفعل لهذه المؤسسة!")
            else:
                form.save()
                messages.success(request, "تمت إضافة السجل بنجاح!")
                return redirect("register-list")  # Redirect to the register list view

    else:
        form = EstablishmentRegisterForm()
        establishments = Establishment.objects.all()
    return render(
        request,
        "licesnsing/establishment_register_form.html",
        {"form": form, "establishments": establishments},
    )


@login_required
def add_establishment_licence(request):
    """
    View to add a new EstablishmentLicence record.
    :param request:
    :return:
    """
    if request.method == "POST":
        form = EstablishmentLicenceForm(request.POST)
        if form.is_valid():
            register = form.cleaned_data["register"]

            # Check if this register already has a license
            if EstablishmentLicence.objects.filter(register=register).exists():
                messages.error(request, "يوجد بالفعل رخصة لهذا التسجيل!")
            else:
                form.save()
                messages.success(request, "تمت إضافة الرخصة بنجاح!")
                return redirect("licence-list")  # Redirect to the license list view

    else:
        form = EstablishmentLicenceForm()

    return render(request, "licesnsing/establishment_licence_form.html", {"form": form})


@login_required(login_url="login")
def get_inspector_assignments(request):
    """
    View to display all inspection assignments for the currently logged-in inspector.
    :param request:
    :return:
    """
    inspector = request.user
    assignments = InspectionAssignment.objects.filter(inspector=inspector)
    return render(
        request, "licesnsing/inspector_assignments.html", {"assignments": assignments}
    )


@login_required(login_url="login")
def get_inspector_inspections(request):
    """
    View to display all inspections for the currently logged-in inspector.
    :param request:
    :return:
    """
    inspector = request.user
    inspections = Inspection.objects.filter(inspector=inspector)
    return render(
        request, "licesnsing/inspector_inspections.html", {"inspections": inspections}
    )


def not_found404(request, exception):
    return render(request, 'errors/404.html', status=404)


