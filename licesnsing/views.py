from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST

from .forms import (
    EstablishmentForm,
    InspectionForm,
    EstablishmentRegisterForm,
    EstablishmentLicenceForm,
    InspectionMediaForm,
    InspectionAssignmentForm,
)
from .models import (
    Establishment,
    ArduinoReader,
    EstablishmentLicence,
    EstablishmentRegister,
    InspectionAssignment,
)
from .utils import process_raw_data, process_form_data


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
            return render(request, "licesnsing/add_establishment.html", {"form": form})
        messages.error(request, "حدث خطأ أثناء إضافة المنشأة")

    return render(request, "licesnsing/add_establishment.html", {"form": form})


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


@login_required  # Ensures only authenticated users can access this endpoint
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


@login_required
def reader(request):
    # TODO handle inspection and make the fields non-editable
    """Main view to handle reader requests."""

    form = InspectionForm(request.POST, request.FILES)
    media = InspectionMediaForm(request.POST, request.FILES)

    if form.is_valid():
        form.save()
        rifd = form.cleaned_data["rifd"]
        a_read = (
            ArduinoReader.objects.filter(code=rifd, queried=False, status="processed")
            .order_by("-id")
            .first()
        )

        if a_read:
            a_read.queried = True
            a_read.save()
            # Clean up and provide feedback
            ArduinoReader.objects.filter(queried=True).delete()
            messages.success(request, "تم إرسال المعاينة")
            return redirect("login")

        else:
            ArduinoReader.objects.filter(queried=True).delete()
            messages.warning(request, f"لقد تم معاينة هذا الرمز {rifd} بالفعل")
            return redirect("login")

    # If form is invalid, return to the page with errors
    return render(request, "licesnsing/readRFID.html", {"form": form, "mform": media})


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


def view_inspection_assignments(request):
    assignments = InspectionAssignment.objects.all()
    return render(
        request, "licesnsing/inspectors_assignments.html", {"assignments": assignments}
    )


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
            assignment = form.save()
            messages.success(
                request, "Establishment assigned for inspection successfully."
            )
            # Adjust the redirect URL as needed.
            return redirect("view_assignments")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = InspectionAssignmentForm()

    return render(request, "licesnsing/assign_establishment.html", {"form": form})
