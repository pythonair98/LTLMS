from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django.db.models import Count

from user_auth.models import Profiles, Occupation
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
    process_raw_data,
    process_form_data,
    mark_inspection_as_done,
    get_establishment_obj_by_register,
)


@login_required(login_url="login")
def dashboard(request):
    """
    Renders a dashboard with key statistics and latest records.

    Statistics include:
      - Total Establishments
      - Total Inspection Assignments and breakdown by status
      - Total Licenses
      - Total Inspections

    Also, recent (latest) records for each table are shown in tabbed tables.
    """
    total_establishments = Establishment.objects.count()
    total_assignments = InspectionAssignment.objects.count()
    assignments_by_status = (
        InspectionAssignment.objects.values("status")
        .annotate(count=Count("id"))
        .order_by("status")
    )
    total_licenses = EstablishmentLicence.objects.count()
    total_inspections = Inspection.objects.count()

    # Get latest records (adjust ordering fields as needed)
    latest_establishments = Establishment.objects.order_by("-created_at")[:5]
    latest_assignments = InspectionAssignment.objects.order_by("-assigned_at")[:5]
    latest_licenses = EstablishmentLicence.objects.order_by("-number")[:5]
    latest_inspections = Inspection.objects.order_by("-created_at")[:5]

    context = {
        "total_establishments": total_establishments,
        "total_assignments": total_assignments,
        "assignments_by_status": assignments_by_status,
        "total_licenses": total_licenses,
        "total_inspections": total_inspections,
        "latest_establishments": latest_establishments,
        "latest_assignments": latest_assignments,
        "latest_licenses": latest_licenses,
        "latest_inspections": latest_inspections,
    }
    return render(request, "licesnsing/index.html", context)


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
        print(form.errors)  # Debugging: Print form validation errors
        if form.is_valid():
            form.save()
            messages.success(request, "تم إضافة المنشأة بنجاح")
            return redirect("view_establishment")
        messages.error(request, "حدث خطأ أثناء إضافة المنشأة")

    return render(request, "licesnsing/add_establishment.html", {"form": form})


@login_required(login_url="login")
def view_establishment(request):
    """
    Displays a list of all registered establishments.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the 'view_establishment.html' template with all establishments.
    """
    establishments = Establishment.objects.all()
    return render(
        request,
        "licesnsing/view_establishment.html",
        {"establishments": establishments},
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
def edit_establishment(request, register_number):
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
    establishment = get_object_or_404(Establishment, register_number=register_number)
    form = EstablishmentForm(request.POST or None, instance=establishment)
    if form.is_valid():
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
    """
    Main view to handle inspection (reader) requests.

    Process:
      1. On POST:
         - Instantiate InspectionForm with POST and FILES.
         - Validate the form.
         - Check if an inspection with the given register_number already exists.
         - If not, save the inspection.
         - Retrieve the RFID (assumed to be in the 'rifd' field of the form).
         - Query the ArduinoReader for a matching record (code == rifd, queried is False, status is "processed").
         - If found, mark it as queried, clean up all queried records, and show a success message.
         - If not, clean up and show a warning message.
      2. On GET:
         - Display an empty InspectionForm.
    """
    if request.method == "POST":
        form = InspectionForm(request.POST, request.FILES)
        if form.is_valid():
            register_number = form.cleaned_data.get("register_number")

            # Check if inspection for this establishment already exists.
            if Inspection.objects.filter(register_number=register_number).exists():
                messages.error(request, "تم تسجيل معاينة لهذه المنشأة بالفعل")
                return redirect("reader")

            # Save the inspection record.
            form.save()
            # mark inspection as done
            mark_inspection_as_done(get_establishment_obj_by_register(register_number))
            messages.success(request, "تم إرسال المعاينة بنجاح")
            # Retrieve the RFID from the form data.
            rifd = form.cleaned_data.get("rifd")

            # Query ArduinoReader for a matching record.
            arduino_record = (
                ArduinoReader.objects.filter(
                    code=rifd, queried=False, status="processed"
                )
                .order_by("-id")
                .first()
            )

            if arduino_record:
                # Mark the ArduinoReader record as queried.
                arduino_record.queried = True
                arduino_record.save()

                # Clean up all ArduinoReader records that have been queried.
                ArduinoReader.objects.filter(queried=True).delete()

                messages.success(request, "تم إرسال المعاينة")
                return redirect("reader")

        else:
            messages.error(request, "الرجاء تصحيح الأخطاء في النموذج.")
    else:
        form = InspectionForm()

    return render(request, "licesnsing/readRFID.html", {"form": form})


# Main view to handle the POST request from Arduino
@csrf_exempt
def api_arduino(request):
    """
    This view handles communication with the Arduino and saves the received code.
    """
    if request.method == "POST":
        # Check if there's raw data in the request body
        if request.body:
            code = process_raw_data(request)
            if code:
                # Save the code to the database
                ArduinoReader.objects.create(code=code)
                return JsonResponse(
                    {"message": "Code received successfully"}, status=200
                )

        # Check if there's form data in the request
        elif "UIDresult" in request.POST:
            code = process_form_data(request)
            if code:
                # Save the code to the database
                ArduinoReader.objects.create(code=code)
                return JsonResponse(
                    {"message": "Code received successfully"}, status=200
                )

        # If no valid data found, return an error
        return JsonResponse({"error": "Invalid request"}, status=400)

    return JsonResponse({"error": "Forbidden method"}, status=403)


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
    context = {
        "registers": registers,
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
    context = {
        "licences": licences,
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
    if new_status == "accepted" or "completed" or "cancelled":
        assignment.delete()
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
            print(form.errors)
            messages.warning(request, form.errors.as_text())
    inspectors = Profiles.objects.filter(occupation__power=6)
    print(inspectors)
    form = InspectionAssignmentForm()
    unassigned_establishments = Establishment.objects.exclude(
    inspection_assignments__isnull=False
)

    if len(unassigned_establishments) == 0:
        messages.warning(request, "حميع المنشأت قد تم تعيينها.")
    return render(request, "licesnsing/assign_establishment.html", {"form": form, "unassigned_establishments": unassigned_establishments, "inspectors": inspectors})


@login_required(login_url="login")
def create_inspection(request):
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
    inspections = Inspection.objects.all()
    return render(
        request, "licesnsing/view_inspections.html", {"inspections": inspections}
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

    return render(
        request, "licesnsing/establishment_register_form.html", {"form": form}
    )


@login_required
def add_establishment_licence(request):
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
